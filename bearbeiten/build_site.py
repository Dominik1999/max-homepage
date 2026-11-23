#!/usr/bin/env python3
"""
925law – Generator.

Liest bearbeiten/925law.html (eine Quelle, Texte im I18N-Wörterbuch) und schreibt
nach website/:
  index.html        englische Startseite (Standard, 925law.de/)
  de/index.html     deutsche Startseite (925law.de/de/)
  impressum.html, datenschutz.html, de/impressum.html, de/datenschutz.html
                    aus bearbeiten/recht/ (Vorlage + Textdateien, siehe build_legal.py)
  robots.txt, sitemap.xml
  .htaccess         aus bearbeiten/htaccess.template, mit frisch berechneten CSP-Hashes
                    der Inline-Scripts

Aufruf (aus beliebigem Verzeichnis):
    python3 bearbeiten/build_site.py
    python3 bearbeiten/build_site.py --final   # bricht ab, solange in den Rechtstexten
                                               # noch ein <!-- TODO(Max): ... --> steht

Braucht Python 3 und beautifulsoup4 (pip install beautifulsoup4).
kontakt.php, die Stylesheets (site.css, legal.css, fonts.css) und Bilder werden NICHT
erzeugt, sie liegen fertig in website/ und werden direkt bearbeitet. Der Generator liest
die Stylesheets nur, um ihre Prüfsumme als ?v=… an die Links zu hängen; deshalb nach jeder
CSS-Änderung neu generieren.
"""
import base64, hashlib, json, pathlib, re, sys
from bs4 import BeautifulSoup
from bs4.formatter import HTMLFormatter
from bs4.dammit import EntitySubstitution

from build_legal import build_legal, css_checks, version_css

# HTML5-Ausgabe: <meta ...> statt <meta .../>, `required` statt `required=""`,
# Umlaute bleiben Umlaute (nur &, <, > werden maskiert).
HTML5_MINIMAL = HTMLFormatter(
    entity_substitution=EntitySubstitution.substitute_xml,
    void_element_close_prefix="",
    empty_attributes_are_booleans=True,
)

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "bearbeiten" / "925law.html"
HTACCESS_TEMPLATE = ROOT / "bearbeiten" / "htaccess.template"
OUT = ROOT / "website"

DOMAIN = "https://925law.de"
PLAUSIBLE_DOMAIN = "925law.de"   # None = kein Analytics-Script einbinden (dann auch Datenschutz-Absatz entfernen)

# Passwortschutz vor dem Livegang (Login-Fenster „925law - intern“). Die Zugangsdaten liegen
# in public_html/.htpasswd auf dem Server (nicht im Repo). Zum Livegang auf False setzen,
# neu generieren und hochladen.
PASSWORD_PROTECT = True
HTACCESS_AUTH = """# --- Passwortschutz vor dem Livegang (PASSWORD_PROTECT in bearbeiten/build_site.py) ---
AuthUserFile "/usr/www/users/e3ersy/.htpasswd"
AuthName "925law - intern"
AuthType Basic
require valid-user

"""

html = SRC.read_text(encoding="utf-8")


def extract_js_object(name):
    """Liest `var NAME = {...};` aus dem Quell-HTML als JSON (robust gegen '});' im Text)."""
    m = re.search(r"var %s = " % re.escape(name), html)
    if not m:
        sys.exit("Variable %s nicht in %s gefunden" % (name, SRC))
    obj, _ = json.JSONDecoder().raw_decode(html[m.end():])
    return obj


i18n = extract_js_object("I18N")


def warn_drift():
    """Der sichtbare Text im Quell-Markup ist nur Vorschau; maßgeblich ist das Wörterbuch.
    Weichen beide ab, wird hier gewarnt, damit die Quelle nicht wieder auseinanderläuft."""
    soup = BeautifulSoup(html, "html.parser")
    for node in soup.select("[data-i18n]"):
        key = node["data-i18n"]
        want = BeautifulSoup(i18n.get(key, {}).get("de", ""), "html.parser").decode().strip()
        have = node.decode_contents().strip()
        if have and have != want:   # leeres Markup = optionaler Wert (z. B. Telefon), kein Vergleich
            print("Hinweis: Markup-Text weicht vom Wörterbuch ab (Wörterbuch gilt): %s" % key)

# --- SEO-Texte pro Sprache ---
META = {
    "de": {
        "title": "925law – Rechtsanwalt Arbeitsrecht & Vertragsrecht Berlin | Max Englhard",
        # höchstens 155 Zeichen (der Build prüft das), sonst schneidet Google ab
        "desc": ("Rechtsanwalt Max Englhard, Berlin: Arbeits- und Vertragsrecht. Kündigung, Abfindung, "
                 "Aufhebungsvertrag, Verträge, Forderungen. Erstgespräch zum Festpreis."),
        "og_locale": "de_DE",
        "alt_locale": "en_US",
        "og_image": DOMAIN + "/og-image.png",
    },
    "en": {
        "title": "925law – English-speaking Employment & Contract Lawyer in Berlin | Max Englhard",
        "desc": ("English-speaking employment and contract lawyer in Berlin: dismissal, severance, "
                 "contracts and claims. Fixed-fee initial consultation."),
        "og_locale": "en_US",
        "alt_locale": "de_DE",
        "og_image": DOMAIN + "/og-image-en.png",
    },
}
URLS = {"de": DOMAIN + "/de/", "en": DOMAIN + "/"}
DEFAULT_LANG = "en"   # Sprache unter 925law.de/ und Rückfall (x-default) für Suchmaschinen
# Deutsche Fassungen der Rechtstexte: Links der DE-Startseite werden darauf umgebogen
DE_LEGAL = {"/impressum.html": "/de/impressum.html", "/datenschutz.html": "/de/datenschutz.html"}
for _lang, _m in META.items():
    if len(_m["desc"]) > 155:
        sys.exit("Meta-Description (%s) hat %d Zeichen, erlaubt sind 155" % (_lang, len(_m["desc"])))


def tel_href(number):
    """'030 123 45 67' -> 'tel:+49301234567' (führende 0 wird zur deutschen Vorwahl)."""
    digits = re.sub(r"[^\d+]", "", number)
    if digits.startswith("00"):
        digits = "+" + digits[2:]
    elif digits.startswith("0"):
        digits = "+49" + digits[1:]
    return "tel:" + digits


def jsonld(lang):
    data = {
        "@context": "https://schema.org",
        "@type": "Attorney",
        "name": "925law – Max Englhard",
        "url": URLS[lang],
        "image": META[lang]["og_image"],
        "description": META[lang]["desc"],
        "areaServed": "Berlin, Germany",
        "availableLanguage": ["de", "en"],
        "knowsAbout": [
            "Arbeitsrecht", "Kündigungsschutz", "Abfindung", "Aufhebungsvertrag",
            "Vertragsrecht", "Forderungseinzug", "Beamtenrecht",
            "Employment law", "Contract law",
        ],
        "founder": {"@type": "Person", "name": "Max Englhard", "jobTitle": "Rechtsanwalt"},
        "memberOf": {"@type": "Organization", "name": "Rechtsanwaltskammer Berlin"},
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "Kaiserkorso 2",
            "postalCode": "12101",
            "addressLocality": "Berlin",
            "addressCountry": "DE",
        },
        "email": "kontakt@925law.de",
    }
    phone = i18n.get("contact_phone", {}).get(lang, "").strip()
    if phone:
        data["telephone"] = tel_href(phone)[4:]
    return data


FORM_SCRIPT = """
  (function(){
    var form = document.getElementById('contact-form');
    var status = document.getElementById('form-status');
    var ERR = __ERR__;
    var PREVIEW = /\\.github\\.io$/.test(location.hostname);
    var T0 = Date.now();
    function showThanks(){
      if(form) form.hidden = true;
      var i = document.getElementById('contact-intro'); if(i) i.hidden = true;
      var t = document.querySelector('.form-thanks');
      if(t){ t.hidden = false; t.setAttribute('tabindex', '-1'); t.focus(); }
    }
    function showError(msg){ if(status){ status.textContent = msg; status.hidden = false; } }
    try{
      if(/[?&]sent=1/.test(location.search)){
        showThanks();
        history.replaceState(null, '', location.pathname + '#contact');
      } else if(/[?&]error=/.test(location.search)){
        showError(ERR);
        history.replaceState(null, '', location.pathname + '#contact');
      }
    }catch(e){}
    if(form){
      form.addEventListener('submit', function(e){
        e.preventDefault();
        if(PREVIEW){ showError(__PREVIEW__); return; }
        var btn = form.querySelector('button[type=submit]');
        if(btn && btn.disabled) return;
        if(btn) btn.disabled = true;
        if(status) status.hidden = true;
        var fd = new FormData(form);
        fd.append('fill_ms', String(Date.now() - T0));
        fetch(form.action, { method: 'POST', body: fd,
          headers: { 'Accept': 'application/json', 'X-Requested-With': 'XMLHttpRequest' } })
        .then(function(r){ return r.json().catch(function(){ return { ok: r.ok }; }); })
        .then(function(res){
          if(res && res.ok){ showThanks(); }
          else { showError(ERR); if(btn) btn.disabled = false; }
        })
        .catch(function(){ showError(ERR); if(btn) btn.disabled = false; });
      });
    }
  })();
"""


def build(lang):
    soup = BeautifulSoup(html, "html.parser")
    soup.html["lang"] = lang

    # Optionale Elemente: data-i18n-if="schlüssel" -> Element entfällt, wenn der Wert leer ist
    # (Telefonnummer `contact_phone`, Antwortzeit-Zusage `form_response_time`)
    for node in soup.select("[data-i18n-if]"):
        key = node["data-i18n-if"]
        if key not in i18n or lang not in i18n[key]:
            sys.exit("Fehlender Übersetzungsschlüssel: %s (%s)" % (key, lang))
        if not i18n[key][lang].strip():
            node.decompose()
            continue
        del node["data-i18n-if"]
        if node.has_attr("hidden"):
            del node["hidden"]
    # Telefon-Links: href aus der Nummer ableiten
    for node in soup.select("[data-phone]"):
        node["href"] = tel_href(i18n["contact_phone"][lang])
        del node["data-phone"]

    # Texte aller [data-i18n]-Knoten fest in die Sprache schreiben, Attribut entfernen
    for node in soup.select("[data-i18n]"):
        key = node["data-i18n"]
        if key not in i18n or lang not in i18n[key]:
            sys.exit("Fehlender Übersetzungsschlüssel: %s (%s)" % (key, lang))
        frag = BeautifulSoup(i18n[key][lang], "html.parser")
        node.clear()
        for child in list(frag.contents):
            node.append(child)
        del node["data-i18n"]

    # Attribute übersetzen: data-i18n-attr="alt:portrait_alt;aria-label:xyz"
    for node in soup.select("[data-i18n-attr]"):
        for pair in node["data-i18n-attr"].split(";"):
            attr, key = pair.split(":", 1)
            if key not in i18n or lang not in i18n[key]:
                sys.exit("Fehlender Übersetzungsschlüssel: %s (%s)" % (key, lang))
            node[attr.strip()] = i18n[key][lang]
        del node["data-i18n-attr"]

    # --- <head> ---
    head = soup.head
    # Niemals externe Schriften (Datenschutz): Google-Fonts-Links entfernen, falls jemand sie wieder einbaut
    for l in head.find_all("link", href=True):
        if "googleapis" in l["href"] or "gstatic" in l["href"]:
            l.decompose()
    if not head.find("link", href="/fonts.css"):
        fl = soup.new_tag("link", rel="stylesheet", href="/fonts.css")
        soup.title.insert_after(fl)

    # Stylesheet: in der Quelle relativ (so ist 925law.html auch direkt im Browser geöffnet
    # gestaltet), in der Ausgabe absolut wie /fonts.css
    for l in head.find_all("link", href="../website/site.css"):
        l["href"] = "/site.css"

    soup.title.string = META[lang]["title"]

    def meta(attrs):
        m = soup.new_tag("meta")
        for k, v in attrs.items():
            m[k] = v
        return m

    def link(attrs):
        l = soup.new_tag("link")
        for k, v in attrs.items():
            l[k] = v
        return l

    add = []
    add.append(meta({"name": "description", "content": META[lang]["desc"]}))
    add.append(meta({"name": "robots", "content": "index,follow"}))
    add.append(meta({"name": "author", "content": "Max Englhard"}))
    add.append(link({"rel": "canonical", "href": URLS[lang]}))
    add.append(link({"rel": "alternate", "hreflang": "de", "href": URLS["de"]}))
    add.append(link({"rel": "alternate", "hreflang": "en", "href": URLS["en"]}))
    add.append(link({"rel": "alternate", "hreflang": "x-default", "href": URLS[DEFAULT_LANG]}))
    add.append(link({"rel": "icon", "type": "image/svg+xml", "href": "/favicon.svg"}))
    add.append(link({"rel": "icon", "type": "image/png", "sizes": "32x32", "href": "/favicon-32.png"}))
    add.append(link({"rel": "apple-touch-icon", "href": "/apple-touch-icon.png"}))
    og = {
        "og:type": "website", "og:site_name": "925law", "og:title": META[lang]["title"],
        "og:description": META[lang]["desc"], "og:url": URLS[lang],
        "og:image": META[lang]["og_image"], "og:locale": META[lang]["og_locale"],
    }
    for k, v in og.items():
        add.append(meta({"property": k, "content": v}))
    add.append(meta({"property": "og:locale:alternate", "content": META[lang]["alt_locale"]}))
    add.append(meta({"name": "twitter:card", "content": "summary_large_image"}))
    add.append(meta({"name": "twitter:title", "content": META[lang]["title"]}))
    add.append(meta({"name": "twitter:description", "content": META[lang]["desc"]}))
    add.append(meta({"name": "twitter:image", "content": META[lang]["og_image"]}))
    ld = soup.new_tag("script", type="application/ld+json")
    ld.string = json.dumps(jsonld(lang), ensure_ascii=False, indent=2)
    add.append(ld)
    if PLAUSIBLE_DOMAIN:
        pl = soup.new_tag("script", src="https://plausible.io/js/script.js")
        pl["defer"] = ""
        pl["data-domain"] = PLAUSIBLE_DOMAIN
        add.append(pl)
    for tag in add:
        head.append(tag)

    # --- Asset-Pfade absolut (beide Seiten liegen in verschiedenen Tiefen) ---
    for img in soup.find_all("img", src=True):
        if img["src"] == "portrait.webp":
            img["src"] = "/portrait.webp"
    form = soup.find("form", id="contact-form")
    if form and form.get("action") == "kontakt.php":
        form["action"] = "/kontakt.php"
    lang_input = form.find("input", attrs={"name": "lang"}) if form else None
    if lang_input:
        lang_input["value"] = lang

    # --- DE: Impressum/Datenschutz auf die deutschen Fassungen ---
    if lang == "de":
        for a in soup.find_all("a", href=True):
            if a["href"] in DE_LEGAL:
                a["href"] = DE_LEGAL[a["href"]]

    # --- Sprachumschalter: echte Links ---
    sw = soup.select_one(".lang-switch")
    if sw:
        sw.clear()
        de = soup.new_tag("a", href="/de/"); de.string = "DE"
        en = soup.new_tag("a", href="/"); en.string = "EN"
        de["class"] = "lang-de" + (" lang-active" if lang == "de" else "")
        en["class"] = "lang-en" + (" lang-active" if lang == "en" else "")
        de["hreflang"] = "de"; en["hreflang"] = "en"
        if lang == "de":
            de["aria-current"] = "true"
        else:
            en["aria-current"] = "true"
        sep = soup.new_tag("span"); sep["class"] = "sep"; sep["aria-hidden"] = "true"; sep.string = "/"
        sw.append(de); sw.append(sep); sw.append(en)

    # --- Vorschau-Script (setLang/I18N) durch das Formular-Script ersetzen ---
    new_script = soup.new_tag("script")
    new_script.string = (FORM_SCRIPT
                         .replace("__ERR__", json.dumps(i18n["form_error"][lang], ensure_ascii=False))
                         .replace("__PREVIEW__", json.dumps(i18n["form_preview"][lang], ensure_ascii=False)))
    for s in soup.find_all("script"):
        if s.string and "var I18N" in s.string:
            s.replace_with(new_script)
            break

    out = version_css(soup.decode(formatter=HTML5_MINIMAL), OUT)

    # --- Sicherheitsnetz: Build bricht ab, wenn die Ausgabe Datenschutz-Versprechen verletzt ---
    checks = {
        "Google Fonts in der Ausgabe": "googleapis" not in out and "gstatic" not in out,
        "data-i18n übrig": "data-i18n" not in out and "data-phone" not in out,
        "DE verlinkt englische Rechtstexte": lang != "de" or ('href="/impressum.html"' not in out
                                                              and 'href="/datenschutz.html"' not in out),
        "EN verlinkt deutsche Rechtstexte": lang != "en" or "/de/impressum.html" not in out
                                            and "/de/datenschutz.html" not in out,
        "leerer Telefon-Link": 'href="tel:"' not in out,
        "Sprachfeld falsch": 'name="lang" type="hidden" value="%s"' % lang in out or 'name="lang" value="%s"' % lang in out,
    }
    checks.update(css_checks(out, ("fonts.css", "site.css")))
    failed = [k for k, ok in checks.items() if not ok]
    if failed:
        sys.exit("Build-Prüfung fehlgeschlagen (%s): %s" % (lang, ", ".join(failed)))
    return out


def csp_hashes(files):
    """SHA-256 aller Inline-<script>-Blöcke (CSP 'sha256-…') aus den fertigen Dateien.
    Für CSS gibt es keine Hashes: style-src ist 'self', die Seiten dürfen keinen
    <style>-Block enthalten (das prüft der Generator hier noch einmal an den fertigen Dateien)."""
    scripts = []
    for f in files:
        txt = f.read_text(encoding="utf-8")
        if re.search(r"<style\b", txt):
            sys.exit("<style>-Block in %s: CSS gehört nach website/site.css bzw. legal.css "
                     "(die CSP erlaubt nur style-src 'self')" % f)
        for m in re.finditer(r"<script(?P<attrs>[^>]*)>(?P<body>.*?)</script>", txt, re.S):
            attrs = m.group("attrs")
            if "src=" in attrs or "ld+json" in attrs:
                continue
            scripts.append(m.group("body"))

    def h(body):
        return "'sha256-%s'" % base64.b64encode(hashlib.sha256(body.encode("utf-8")).digest()).decode()

    return sorted({h(b) for b in scripts})


if __name__ == "__main__":
    warn_drift()
    (OUT / "de").mkdir(parents=True, exist_ok=True)
    (OUT / "index.html").write_text(build("en"), encoding="utf-8")
    (OUT / "de" / "index.html").write_text(build("de"), encoding="utf-8")

    # Impressum + Datenschutz, deutsch und englisch (noindex, deshalb nicht in der Sitemap)
    legal_pages, legal_todos = build_legal(OUT, DOMAIN, PLAUSIBLE_DOMAIN)

    (OUT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % DOMAIN, encoding="utf-8")
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
               'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n')
    for lang in ("de", "en"):
        sitemap += "  <url>\n    <loc>%s</loc>\n" % URLS[lang]
        sitemap += '    <xhtml:link rel="alternate" hreflang="de" href="%s"/>\n' % URLS["de"]
        sitemap += '    <xhtml:link rel="alternate" hreflang="en" href="%s"/>\n' % URLS["en"]
        sitemap += '    <xhtml:link rel="alternate" hreflang="x-default" href="%s"/>\n' % URLS[DEFAULT_LANG]
        sitemap += "  </url>\n"
    sitemap += "</urlset>\n"
    (OUT / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    # .htaccess mit CSP-Hashes aller sechs Seiten
    pages = [OUT / "index.html", OUT / "de" / "index.html"] + legal_pages
    missing = [str(p) for p in pages if not p.exists()]
    if missing:
        sys.exit("Seiten fehlen für die CSP-Hashes: " + ", ".join(missing))
    sh = csp_hashes(pages)
    tpl = HTACCESS_TEMPLATE.read_text(encoding="utf-8")
    if "__SCRIPT_HASHES__" not in tpl or "style-src 'self';" not in tpl:
        sys.exit("htaccess.template: __SCRIPT_HASHES__ oder \"style-src 'self';\" fehlt")
    htaccess = tpl.replace("__SCRIPT_HASHES__", " ".join(sh))
    if PASSWORD_PROTECT:
        htaccess = HTACCESS_AUTH + htaccess
    (OUT / ".htaccess").write_text(htaccess, encoding="utf-8")

    print("generated: index.html, de/index.html, %s, robots.txt, sitemap.xml, .htaccess "
          "(%d pages hashed: %d script hashes; no inline styles)"
          % (", ".join(str(p.relative_to(OUT)) for p in legal_pages), len(pages), len(sh)))

    if PASSWORD_PROTECT:
        print("\nHinweis: .htaccess enthält den Passwortschutz (PASSWORD_PROTECT = True).")
    if legal_todos:
        print("\n!!! %d OFFENE PUNKTE in den Rechtstexten (bearbeiten/recht/), vor dem Livegang klären:"
              % len(legal_todos))
        for t in legal_todos:
            print("  - " + t)
        if "--final" in sys.argv[1:]:
            sys.exit("--final: Abbruch, solange TODO(Max)-Punkte offen sind.")
