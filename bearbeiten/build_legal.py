#!/usr/bin/env python3
"""
925law – Impressum und Datenschutzerklärung (Deutsch + Englisch).

Wird von build_site.py aufgerufen. Baut aus EINER Vorlage und je einer Textdatei
pro Seite und Sprache die vier Rechtsseiten:

  bearbeiten/recht/vorlage.html            Kopf und Fuß (das CSS steht in website/site.css
                                           und website/legal.css)
  bearbeiten/recht/impressum.de.html       -> website/impressum.html
  bearbeiten/recht/impressum.en.html       -> website/en/impressum.html
  bearbeiten/recht/datenschutz.de.html     -> website/datenschutz.html
  bearbeiten/recht/datenschutz.en.html     -> website/en/datenschutz.html

Die Textdateien enthalten nur den Inhalt (ab <h1>) als normales HTML. Der Text wird
unverändert übernommen; es wird nichts übersetzt oder umformuliert.

Offene Punkte stehen als HTML-Kommentar  <!-- TODO(Max): ... -->  in den Textdateien.
Sie werden NICHT in die fertigen Seiten geschrieben, aber bei jedem Lauf aufgelistet.
`build_site.py --final` bricht ab, solange noch einer offen ist.
"""
import hashlib, pathlib, re, sys

SRC = pathlib.Path(__file__).resolve().parent / "recht"

TODO_RE = re.compile(r"[ \t]*<!--\s*TODO\(Max\):(.*?)-->[ \t]*\n?", re.S)

PAGES = ("impressum", "datenschutz")

# Texte der Vorlage (nicht der Rechtstexte) je Sprache
UI = {
    "de": {
        "home": "/",
        "prefix": "/",
        "skip": "Zum Inhalt springen",
        "back": "Zur Startseite",
        "brand_label": "925law – zur Startseite",
        "footer_brand": "925law — Max Englhard, Rechtsanwalt",
        "titles": {"impressum": "Impressum", "datenschutz": "Datenschutzerklärung"},
        "nav": {"impressum": "Impressum", "datenschutz": "Datenschutz"},
    },
    "en": {
        "home": "/en/",
        "prefix": "/en/",
        "skip": "Skip to content",
        "back": "Back to home page",
        "brand_label": "925law – back to home page",
        "footer_brand": "925law — Max Englhard, Attorney-at-law",
        "titles": {"impressum": "Legal notice", "datenschutz": "Privacy policy"},
        "nav": {"impressum": "Legal notice", "datenschutz": "Privacy"},
    },
}


def version_css(page_html, out_dir):
    """Hängt an jeden Link auf ein eigenes Stylesheet (/fonts.css, /site.css, /legal.css) ein
    ?v=<Prüfsumme der Datei>. Ändert sich die Datei, ändert sich die Adresse, und Browser laden
    sie neu, obwohl .htaccess CSS zwischenspeichern lässt. Bricht ab, wenn die Datei fehlt."""
    def stamp(m):
        f = out_dir / m.group(1)
        if not f.is_file():
            sys.exit("Stylesheet fehlt: %s" % f)
        return 'href="/%s?v=%s"' % (m.group(1), hashlib.sha256(f.read_bytes()).hexdigest()[:10])
    return re.sub(r'href="/([\w./-]+\.css)"', stamp, page_html)


def css_checks(out, sheets):
    """Build-Prüfungen zum CSS, für Startseiten und Rechtsseiten gleich. Die CSP in .htaccess
    erlaubt nur eigene Stylesheet-Dateien (style-src 'self'): <style>-Blöcke und
    style-Attribute würde der Browser verwerfen."""
    checks = {
        "<style>-Block in der Ausgabe (CSP)": "<style" not in out,
        "style-Attribute (CSP) übrig": 'style="' not in out and "style='" not in out,
    }
    for name in sheets:
        checks["%s nicht (mit ?v=) eingebunden" % name] = re.search(
            r'<link [^>]*href="/%s\?v=[0-9a-f]{10}"' % re.escape(name), out) is not None
    return checks


def path_of(page, lang):
    return "%s%s.html" % (UI[lang]["prefix"], page)


def lang_switch(page, lang):
    def a(code):
        active = code == lang
        return '<a %sclass="lang-%s%s" href="%s" hreflang="%s">%s</a>' % (
            'aria-current="true" ' if active else "", code, " lang-active" if active else "",
            path_of(page, code), code, code.upper())
    return a("de") + '<span aria-hidden="true" class="sep">/</span>' + a("en")


def footer_legal(page, lang):
    return "".join(
        '<a %shref="%s">%s</a>' % ('aria-current="page" ' if p == page else "", path_of(p, lang), UI[lang]["nav"][p])
        for p in PAGES)


def render(page, lang, template, domain, plausible_domain, out_dir):
    """Gibt (html, offene_todos) für eine Seite zurück."""
    src = SRC / ("%s.%s.html" % (page, lang))
    content = src.read_text(encoding="utf-8")
    todos = [" ".join(t.split()) for t in TODO_RE.findall(content)]
    content = TODO_RE.sub("", content)
    content = "\n".join(("    " + line) if line.strip() else "" for line in content.strip("\n").split("\n"))

    ui = UI[lang]
    analytics = ('<script defer data-domain="%s" src="https://plausible.io/js/script.js"></script>' % plausible_domain
                 if plausible_domain else "")
    values = {
        "lang": lang,
        "title": ui["titles"][page],
        "url_de": domain + path_of(page, "de"),
        "url_en": domain + path_of(page, "en"),
        "analytics": analytics,
        "skip": ui["skip"],
        "home": ui["home"],
        "brand_label": ui["brand_label"],
        "lang_switch": lang_switch(page, lang),
        "back": ui["back"],
        "content": content,
        "footer_brand": ui["footer_brand"],
        "footer_legal": footer_legal(page, lang),
    }
    out = re.sub(r"\{\{(\w+)\}\}", lambda m: values[m.group(1)], template)
    if not analytics:
        out = out.replace('<link rel="stylesheet" href="/legal.css">\n\n', '<link rel="stylesheet" href="/legal.css">\n')
    out = version_css(out, out_dir)

    checks = {
        "Google Fonts in der Ausgabe": "googleapis" not in out and "gstatic" not in out,
        "TODO in der Ausgabe": "TODO" not in out,
        "noindex fehlt": 'content="noindex, follow"' in out,
        "<h1> fehlt": "<h1>" in out,
        "html lang falsch": '<html lang="%s">' % lang in out,
    }
    checks.update(css_checks(out, ("fonts.css", "site.css", "legal.css")))
    failed = [k for k, ok in checks.items() if not ok]
    if failed:
        sys.exit("Build-Prüfung fehlgeschlagen (%s.%s): %s" % (page, lang, ", ".join(failed)))
    return out, ["%s: %s" % (src.name, t) for t in todos]


def build_legal(out_dir, domain, plausible_domain):
    """Schreibt die vier Rechtsseiten. Gibt (geschriebene Dateien, offene TODOs) zurück."""
    template = (SRC / "vorlage.html").read_text(encoding="utf-8")
    written, todos = [], []
    for lang in ("de", "en"):
        for page in PAGES:
            html, open_items = render(page, lang, template, domain, plausible_domain, out_dir)
            target = out_dir / path_of(page, lang).lstrip("/")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(html, encoding="utf-8")
            written.append(target)
            todos += open_items
    return written, todos
