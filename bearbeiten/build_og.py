#!/usr/bin/env python3
"""Share-Vorschaubilder (Open Graph) für 925law erzeugen.

Schreibt  website/og-image.png  (DE)  und  website/og-image-en.png  (EN),
je 1200 x 630 px, 8-Bit-PNG (Palette), ohne Metadaten.

Aufruf (aus dem Repo-Wurzelverzeichnis):

    python3 -m venv ~/.venvs/925law-assets            # einmalig, außerhalb des Repos
    ~/.venvs/925law-assets/bin/pip install pillow fonttools brotli uharfbuzz
    ~/.venvs/925law-assets/bin/python bearbeiten/build_og.py

Abhängigkeiten: pillow (Zeichnen/PNG), fonttools + brotli (woff2 lesen),
uharfbuzz (Kerning/Zeichenabstände wie im Browser).

Texte ändern: nur die Konstanten im Block TEXTE unten anpassen und das Skript
erneut starten. Zeilenumbrüche werden bewusst von Hand gesetzt (ein Listen-
eintrag = eine Zeile); das Skript bricht ab, wenn eine Zeile nicht in die
Karte passt oder die letzte Zeile nur aus einem einzelnen Wort besteht.

Schriften kommen aus website/fonts/ (woff2, im Speicher entpackt), Farben aus
den CSS-Variablen in bearbeiten/925law.html. Kein Netzwerkzugriff.
"""
import io
import re
import sys
from pathlib import Path

import uharfbuzz as hb
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

# ───────────────────────────── TEXTE ──────────────────────────────
# Quelle: I18N in bearbeiten/925law.html (hero_kicker, hero_h1, hero_sub).
# *Sternchen* markieren das Wort in der Akzentfarbe.
# Ein Listeneintrag = eine Zeile auf der Karte.

BRAND = "925law"
URL = "925law.de"
STAMP_TEXT = "925"

KICKER_DE = "Max Englhard · Rechtsanwalt · Berlin"
HEADLINE_DE = [
    "Erst *recht*, wenn's",
    "drauf ankommt.",
]
TAGLINE_DE = [
    "Arbeits- und Vertragsrecht für Unternehmen,",
    "Führungskräfte und Freelancer. Ohne Umwege.",
]

KICKER_EN = "Max Englhard · Attorney-at-law · Berlin"
HEADLINE_EN = [
    "When it",
    "*counts* most.",
]
TAGLINE_EN = [
    "Employment and contract law —",
    "handled directly, explained plainly.",
]

CARDS = {
    "og-image.png": (KICKER_DE, HEADLINE_DE, TAGLINE_DE),
    "og-image-en.png": (KICKER_EN, HEADLINE_EN, TAGLINE_EN),
}
# ──────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "website" / "fonts"
SOURCE_HTML = ROOT / "bearbeiten" / "925law.html"
OUT_DIR = ROOT / "website"

W, H = 1200, 630
SS = 3  # Supersampling: intern 3600 x 1890, am Ende herunterskaliert


def css_colors():
    """CSS-Variablen (--bg, --ink, ...) aus dem :root-Block der Quelle lesen."""
    css = SOURCE_HTML.read_text(encoding="utf-8")
    root = re.search(r":root\s*\{(.*?)\}", css, re.S)
    if not root:
        sys.exit("FEHLER: :root-Block in 925law.html nicht gefunden")
    found = dict(re.findall(r"--([\w-]+)\s*:\s*(#[0-9A-Fa-f]{6})\b", root.group(1)))
    for key in ("bg", "ink", "ink-soft", "accent", "line"):
        if key not in found:
            sys.exit(f"FEHLER: CSS-Variable --{key} fehlt in 925law.html")
    return {k: tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) for k, v in found.items()}


def mix(fg, bg, alpha):
    return tuple(round(f * alpha + b * (1 - alpha)) for f, b in zip(fg, bg))


class Face:
    """Eine Schrift aus website/fonts/: woff2 im Speicher entpacken, mit HarfBuzz setzen."""

    def __init__(self, name):
        path = FONT_DIR / f"{name}.woff2"
        self.name = name
        self.tt = TTFont(path)
        self.tt.flavor = None
        buf = io.BytesIO()
        self.tt.save(buf)
        self.data = buf.getvalue()
        self.upm = self.tt["head"].unitsPerEm
        self.cmap = self.tt.getBestCmap()
        self.hb = hb.Font(hb.Face(self.data))
        self._pil = {}

    def pil(self, px):
        px = round(px)
        if px not in self._pil:
            self._pil[px] = ImageFont.truetype(
                io.BytesIO(self.data), px, layout_engine=ImageFont.Layout.BASIC)
        return self._pil[px]

    def shape(self, text, tracking=0.0):
        """-> ([(Zeichenindex, Glyphname, x in em)], Breite in em). tracking in em je Zeichen."""
        missing = sorted({c for c in text if ord(c) not in self.cmap})
        if missing:
            sys.exit(f"FEHLER: {self.name} enthält die Zeichen {missing} nicht (Text: {text!r})")
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        # Ligaturen aus: 1 Zeichen = 1 Glyphe (wie im Browser bei letter-spacing)
        hb.shape(self.hb, buf, {"liga": False, "clig": False, "calt": False})
        out, x = [], 0.0
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            out.append((info.cluster, self.hb.glyph_to_string(info.codepoint),
                        x + pos.x_offset / self.upm))
            x += pos.x_advance / self.upm + tracking
        return out, x - (tracking if out else 0.0)

    def width(self, text, size, tracking=0.0):
        return self.shape(text, tracking)[1] * size

    def draw(self, draw, x, baseline, text, size, fill, tracking=0.0, scale=1):
        """Text mit linker Kante x und Grundlinie baseline zeichnen (Einheiten: Karten-px).
        fill: eine Farbe oder eine Liste mit einer Farbe je Zeichen."""
        glyphs, width = self.shape(text, tracking)
        font = self.pil(size * scale)
        for index, _, gx in glyphs:
            if not text[index].isspace():
                color = fill[index] if isinstance(fill, list) else fill
                draw.text(((x + gx * size) * scale, baseline * scale), text[index],
                          font=font, fill=color, anchor="ls")
        return width * size


def parse_accent(line, normal, accent):
    """'Erst *recht*, wenn' -> ('Erst recht, wenn', [Farbe je Zeichen])"""
    plain, fills = "", []
    for i, part in enumerate(line.split("*")):
        plain += part
        fills += [accent if i % 2 else normal] * len(part)
    return plain, fills


def check_lines(label, lines):
    if len(lines) > 1 and len(lines[-1].replace("*", "").split()) < 2:
        sys.exit(f"FEHLER: {label}: letzte Zeile {lines[-1]!r} ist ein einzelnes Wort "
                 "(Hurenkind) – Zeilen anders umbrechen")


def save_png(img, path, exact=()):
    """8-Bit-PNG mit Palette (256 Farben, ohne Dithering), optimiert, ohne Textchunks/EXIF/ICC.
    exact: Markenfarben; der jeweils nächste Paletteneintrag wird exakt auf sie gesetzt."""
    pal = img.convert("RGB").quantize(256, method=Image.Quantize.MAXCOVERAGE,
                                      dither=Image.Dither.NONE)
    flat = pal.getpalette()
    entries = [tuple(flat[i:i + 3]) for i in range(0, len(flat), 3)]
    for color in exact:
        nearest = min(range(len(entries)),
                      key=lambda i: sum((a - b) ** 2 for a, b in zip(entries[i], color)))
        if max(abs(a - b) for a, b in zip(entries[nearest], color)) > 4:
            sys.exit(f"FEHLER: Farbe {color} ging bei der Farbreduktion verloren ({path.name})")
        entries[nearest] = tuple(color)
    pal.putpalette([v for entry in entries for v in entry])
    pal.info.clear()
    pal.save(path, "PNG", optimize=True)


def draw_stamp(draw, cx, cy, diameter, ink, bg, face700, scale):
    """Der 925-Stempel wie im Hero der Seite (SVG-viewBox 120: r=52/42, Schrift 26, y=68)."""
    u = diameter / 105.4  # 1 viewBox-Einheit in Karten-px (Außenring r=52 + halbe Strichstärke)
    for r, sw, color in ((52, 1.4, ink), (42, 0.8, mix(ink, bg, 0.5))):
        ro, wpx = (r + sw / 2) * u * scale, max(1, round(sw * u * scale))
        draw.ellipse([cx * scale - ro, cy * scale - ro, cx * scale + ro, cy * scale + ro],
                     outline=color, width=wpx)
    size = 26 * u
    width = face700.width(STAMP_TEXT, size)
    face700.draw(draw, cx - width / 2, cy + 8 * u, STAMP_TEXT, size, ink, scale=scale)


def build_card(filename, kicker, headline, tagline, colors, faces):
    bg, ink, soft, accent, line = (colors[k] for k in ("bg", "ink", "ink-soft", "accent", "line"))
    img = Image.new("RGB", (W * SS, H * SS), bg)
    d = ImageDraw.Draw(img)

    check_lines(f"{filename} Headline", headline)
    check_lines(f"{filename} Tagline", tagline)

    left, right = 84, W - 84
    stamp_d = 150
    stamp_cx = right - stamp_d / 2 - 2

    # Wortmarke oben links (wie die Seitenleiste: Archivo 800, Akzentfarbe)
    faces["a800"].draw(d, left, 112, BRAND, 36, accent, tracking=-0.01, scale=SS)

    # Kicker
    k_size = 23
    if left + faces["p400"].width(kicker, k_size) > right:
        sys.exit(f"FEHLER: {filename}: Kicker zu lang")
    faces["p400"].draw(d, left, 204, kicker, k_size, soft, scale=SS)

    # Headline (Archivo 900, letter-spacing -0.03em, line-height 1.05 wie #hero h1)
    h_size, h_track = 90, -0.03
    h_max = stamp_cx - stamp_d / 2 - 36
    y = 302
    for text in headline:
        plain, fills = parse_accent(text, ink, accent)
        if left + faces["a900"].width(plain, h_size, h_track) > h_max:
            sys.exit(f"FEHLER: {filename}: Headline-Zeile {plain!r} ist zu breit – kürzer umbrechen")
        faces["a900"].draw(d, left, y, plain, h_size, fills, tracking=h_track, scale=SS)
        y += h_size * 1.05
    last_baseline = y - h_size * 1.05

    # Stempel rechts neben der ersten Headline-Zeile
    cap_top = 302 - 0.686 * h_size
    draw_stamp(d, stamp_cx, cap_top + 6 + stamp_d / 2, stamp_d, ink, bg, faces["a700"], SS)

    # Tagline (IBM Plex Sans 400, weiche Tintenfarbe wie #hero p.sub)
    t_size = 31
    y = last_baseline + 68
    for text in tagline:
        if left + faces["p400"].width(text, t_size) > right:
            sys.exit(f"FEHLER: {filename}: Tagline-Zeile {text!r} ist zu breit – kürzer umbrechen")
        faces["p400"].draw(d, left, y, text, t_size, soft, scale=SS)
        y += t_size * 1.42

    # Fußzeile: Linie + URL
    d.rectangle([left * SS, 552 * SS, right * SS, 552 * SS + SS - 1], fill=line)
    faces["p600"].draw(d, left, 592, URL, 23, ink, scale=SS)

    out = img.resize((W, H), Image.LANCZOS)
    save_png(out, OUT_DIR / filename, exact=(bg, ink, accent))
    return OUT_DIR / filename


def load_faces():
    return {
        "a900": Face("archivo-900"),
        "a800": Face("archivo-800"),
        "a700": Face("archivo-700"),
        "p400": Face("ibmplexsans-400"),
        "p600": Face("ibmplexsans-600"),
    }


def main():
    colors = css_colors()
    faces = load_faces()
    for filename, (kicker, headline, tagline) in CARDS.items():
        path = build_card(filename, kicker, headline, tagline, colors, faces)
        print(f"{path.relative_to(ROOT)}  {path.stat().st_size} Bytes")


if __name__ == "__main__":
    main()
