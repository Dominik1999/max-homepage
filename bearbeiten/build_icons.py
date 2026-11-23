#!/usr/bin/env python3
"""Browser-Icons für 925law aus EINER Quelle erzeugen.

Die kleine Bildmarke: Fläche in der Akzentfarbe, darauf weiß "925" aus
Archivo 900 (leicht schmaler gestellt) – ohne Ring, damit sie bei 16 px lesbar bleibt. Die Ziffern werden
als Vektorpfade aus website/fonts/archivo-900.woff2 übernommen; die fertigen
Dateien brauchen keine Schrift.

Schreibt:
    website/favicon.svg            (viewBox 64, abgerundetes Quadrat, Pfade)
    website/favicon-32.png         (32 x 32, transparente Ecken)
    website/apple-touch-icon.png   (180 x 180, deckend, ohne Rundung – iOS rundet selbst)

Aufruf (aus dem Repo-Wurzelverzeichnis, venv siehe build_og.py):

    ~/.venvs/925law-assets/bin/python bearbeiten/build_icons.py
    ~/.venvs/925law-assets/bin/python bearbeiten/build_icons.py --preview /tmp/icons
        # zusätzlich Kontrollbilder (16/32 px, vergrößert) in den Ordner schreiben

Abhängigkeiten: pillow, fonttools, brotli, uharfbuzz (wie build_og.py).
Kein Netzwerkzugriff, keine Metadaten in den Ausgaben.
"""
import sys
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from PIL import Image, ImageDraw

from build_og import OUT_DIR, Face, css_colors

# ─────────────────────────── EINSTELLUNGEN ───────────────────────────
MARK_TEXT = "925"
MARK_FONT = "archivo-900"
MARK_TRACKING = 0.0      # Zeichenabstand in em
MARK_CONDENSE = 0.78     # Ziffernbreite relativ zur Höhe (1.0 = unverzerrt); schmaler =
                         # höhere Ziffern, bei 16 px deutlich besser lesbar
WHITE = (255, 255, 255)

VIEWBOX = 64             # favicon.svg
CORNER_RADIUS = 10       # in viewBox-Einheiten (bei 16 px = 2,5 px)
FAVICON_INK_WIDTH = 0.88   # Breite der Ziffern relativ zur Kante (Favicon)
TOUCH_INK_WIDTH = 0.60     # dito fürs Apple-Touch-Icon (Sicherheitsabstand)
# ─────────────────────────────────────────────────────────────────────

SS = 16  # Supersampling für die PNGs


class Mark:
    """Geometrie der Ziffern in Font-Einheiten (y nach oben)."""

    def __init__(self):
        self.face = Face(MARK_FONT)
        self.glyphs, width_em = self.face.shape(MARK_TEXT, MARK_TRACKING)
        self.glyph_set = self.face.tt.getGlyphSet()
        pen = BoundsPen(self.glyph_set)
        for _, name, x_em in self.glyphs:
            self.glyph_set[name].draw(TransformPen(pen, (1, 0, 0, 1, x_em * self.face.upm, 0)))
        self.xmin, self.ymin, self.xmax, self.ymax = pen.bounds

    def placement(self, edge, ink_share):
        """-> (Maßstab x, Maßstab y in px je Font-Einheit, x des Ursprungs, y der Grundlinie)."""
        sx = edge * ink_share / (self.xmax - self.xmin)
        sy = sx / MARK_CONDENSE
        x0 = (edge - (self.xmax - self.xmin) * sx) / 2 - self.xmin * sx
        baseline = (edge + (self.ymax - self.ymin) * sy) / 2 + self.ymin * sy
        return sx, sy, x0, baseline

    def svg_path(self, edge, ink_share):
        sx, sy, x0, baseline = self.placement(edge, ink_share)
        pen = SVGPathPen(self.glyph_set, ntos=lambda v: f"{v:.2f}".rstrip("0").rstrip("."))
        for _, name, x_em in self.glyphs:
            t = (sx, 0, 0, -sy, x0 + x_em * self.face.upm * sx, baseline)
            self.glyph_set[name].draw(TransformPen(pen, t))
        return pen.getCommands()

    def raster(self, edge, ink_share, radius, bg, opaque):
        """PNG-Fassung derselben Geometrie (großflächig gezeichnet, dann verkleinert)."""
        big = edge * SS
        img = Image.new("RGBA", (big, big), bg + (255,) if opaque else (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        if not opaque:
            d.rounded_rectangle([0, 0, big - 1, big - 1], radius=radius * SS, fill=bg + (255,))
        sx, sy, x0, baseline = self.placement(edge, ink_share)
        # Ziffern unverzerrt auf eigene Ebene zeichnen, dann in x auf MARK_CONDENSE stauchen
        size = sy * self.face.upm
        layer_w = round((self.xmax - self.xmin) * sy * SS) + 2 * SS
        layer = Image.new("L", (layer_w, big), 0)
        ld = ImageDraw.Draw(layer)
        font = self.face.pil(size * SS)
        for index, _, x_em in self.glyphs:
            ld.text((SS + (x_em * size - self.xmin * sy) * SS, baseline * SS), MARK_TEXT[index],
                    font=font, fill=255, anchor="ls")
        layer = layer.resize((max(1, round(layer_w * MARK_CONDENSE)), big), Image.LANCZOS)
        left = round(((edge - (self.xmax - self.xmin) * sx) / 2 - MARK_CONDENSE) * SS)
        img.paste(WHITE + (255,), (left, 0), layer)
        out = img.reduce(SS)
        return out.convert("RGB") if opaque else out


def save_png(img, path):
    img.info.clear()
    img.save(path, "PNG", optimize=True)


def main():
    accent = css_colors()["accent"]
    hex_accent = "#%02X%02X%02X" % accent
    mark = Mark()

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEWBOX} {VIEWBOX}">\n'
        f'  <rect width="{VIEWBOX}" height="{VIEWBOX}" rx="{CORNER_RADIUS}" fill="{hex_accent}"/>\n'
        f'  <path fill="#fff" d="{mark.svg_path(VIEWBOX, FAVICON_INK_WIDTH)}"/>\n'
        "</svg>\n"
    )
    (OUT_DIR / "favicon.svg").write_text(svg, encoding="utf-8")

    fav32 = mark.raster(32, FAVICON_INK_WIDTH, CORNER_RADIUS * 32 / VIEWBOX, accent, opaque=False)
    save_png(fav32, OUT_DIR / "favicon-32.png")
    touch = mark.raster(180, TOUCH_INK_WIDTH, 0, accent, opaque=True)
    save_png(touch, OUT_DIR / "apple-touch-icon.png")

    for name in ("favicon.svg", "favicon-32.png", "apple-touch-icon.png"):
        print(f"website/{name}  {(OUT_DIR / name).stat().st_size} Bytes")

    if "--preview" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--preview") + 1])
        out.mkdir(parents=True, exist_ok=True)
        fav16 = mark.raster(16, FAVICON_INK_WIDTH, CORNER_RADIUS * 16 / VIEWBOX, accent, opaque=False)
        # Kontrollblatt: 16 und 32 px in Originalgröße und pixelgenau vergrößert,
        # je auf hellem und dunklem Tab-Hintergrund
        sheet = Image.new("RGB", (16 * 20 + 32 * 10 + 180 + 160, 2 * 360), (255, 255, 255))
        for row, back in enumerate(((241, 243, 244), (53, 54, 58))):
            y = row * 360
            ImageDraw.Draw(sheet).rectangle([0, y, sheet.width, y + 360], fill=back)
            x = 20
            for icon, zoom in ((fav16, 1), (fav32, 1), (fav16, 20), (fav32, 10)):
                tile = icon.resize((icon.width * zoom, icon.height * zoom), Image.NEAREST)
                sheet.paste(tile, (x, y + 20), tile)
                x += tile.width + 20
            sheet.paste(touch, (x, y + 20))
        sheet.save(out / "icons-kontrollblatt.png")
        fav16.save(out / "favicon-16.png")
        print(f"Kontrollbilder in {out}")


if __name__ == "__main__":
    main()
