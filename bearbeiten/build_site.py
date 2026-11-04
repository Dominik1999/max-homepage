#!/usr/bin/env python3
"""
925law – Generator.

Liest bearbeiten/925law.html (eine Quelle, Texte im I18N-Wörterbuch) und schreibt
nach website/:
  index.html        deutsche Startseite
  en/index.html     englische Startseite
  robots.txt, sitemap.xml
  .htaccess         aus bearbeiten/htaccess.template, mit frisch berechneten CSP-Hashes

Aufruf (aus beliebigem Verzeichnis):
    python3 bearbeiten/build_site.py

Braucht Python 3 und beautifulsoup4 (pip install beautifulsoup4).
Impressum, Datenschutz, kontakt.php, fonts.css und Bilder werden NICHT erzeugt,
sie liegen fertig in website/ und werden direkt bearbeitet.
"""
import base64, hashlib, json, pathlib, re, sys
from bs4 import BeautifulSoup
from bs4.formatter import HTMLFormatter
from bs4.dammit import EntitySubstitution

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

html = SRC.read_text(encoding="utf-8")


def extract_js_object(name):
    """Liest `var NAME = {...};` aus dem Quell-HTML als JSON (robust gegen '});' im Text)."""
    m = re.search(r"var %s = " % re.escape(name), html)
    if not m:
        sys.exit("Variable %s nicht in %s gefunden" % (name, SRC))
    obj, _ = json.JSONDecoder().raw_decode(html[m.end():])
    return obj


i18n = extract_js_object("I18N")

# --- SEO-Texte pro Sprache ---
META = {
    "de": {
        "title": "925law – Rechtsanwalt Arbeitsrecht & Vertragsrecht Berlin | Max Englhard",
        "desc": ("Rechtsanwalt Max Englhard (925law): Arbeitsrecht und Vertragsrecht in Berlin. "
                 "Kündigungsschutz, Abfindung, Aufhebungsvertrag, Verträge und Forderungen – "
                 "für Unternehmen, Führungskräfte, Angestellte und Freelancer. Erstgespräch zum Festpreis."),
        "og_locale": "de_DE",
        "alt_locale": "en_US",
        "og_image": DOMAIN + "/og-image.png",
    },
    "en": {
        "title": "925law – English-speaking Employment & Contract Lawyer in Berlin | Max Englhard",
        "desc": ("Max Englhard (925law): English-speaking German employment and contract lawyer in Berlin. "
                 "Protection against dismissal, severance, termination agreements, contracts and claims – "
                 "for companies, executives, employees and freelancers. Fixed-fee initial consultation."),
        "og_locale": "en_US",
        "alt_locale": "de_DE",
        "og_image": DOMAIN + "/og-image-en.png",
    },
}
URLS = {"de": DOMAIN + "/", "en": DOMAIN + "/en/"}


def jsonld(lang):
    return {
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


FORM_SCRIPT = """
  (function(){
    var form = document.getElementById('contact-form');
    var status = document.getElementById('form-status');
    var ERR = __ERR__;
    var PREVIEW = /\\.github\\.io$/.test(location.hostname);
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
        fetch(form.action, { method: 'POST', body: new FormData(form),
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
    add.append(link({"rel": "alternate", "hreflang": "x-default", "href": URLS["de"]}))
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

    # --- Sprachumschalter: echte Links ---
    sw = soup.select_one(".lang-switch")
    if sw:
        sw.clear()
        de = soup.new_tag("a", href="/"); de.string = "DE"
        en = soup.new_tag("a", href="/en/"); en.string = "EN"
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

    out = soup.decode(formatter=HTML5_MINIMAL)

    # --- Sicherheitsnetz: Build bricht ab, wenn die Ausgabe Datenschutz-Versprechen verletzt ---
    checks = {
        "Google Fonts in der Ausgabe": "googleapis" not in out and "gstatic" not in out,
        "fonts.css fehlt": '/fonts.css' in out,
        "data-i18n übrig": "data-i18n" not in out,
        "style-Attribute (CSP) übrig": 'style="' not in out,
        "Sprachfeld falsch": 'name="lang" type="hidden" value="%s"' % lang in out or 'name="lang" value="%s"' % lang in out,
    }
    failed = [k for k, ok in checks.items() if not ok]
    if failed:
        sys.exit("Build-Prüfung fehlgeschlagen (%s): %s" % (lang, ", ".join(failed)))
    return out


def csp_hashes(files):
    """SHA-256 aller Inline-<script>/<style>-Blöcke (CSP 'sha256-…') aus den fertigen Dateien."""
    scripts, styles = [], []
    for f in files:
        txt = f.read_text(encoding="utf-8")
        for m in re.finditer(r"<script(?P<attrs>[^>]*)>(?P<body>.*?)</script>", txt, re.S):
            attrs = m.group("attrs")
            if "src=" in attrs or "ld+json" in attrs:
                continue
            scripts.append(m.group("body"))
        for m in re.finditer(r"<style[^>]*>(?P<body>.*?)</style>", txt, re.S):
            styles.append(m.group("body"))

    def h(body):
        return "'sha256-%s'" % base64.b64encode(hashlib.sha256(body.encode("utf-8")).digest()).decode()

    return sorted({h(b) for b in scripts}), sorted({h(b) for b in styles})


if __name__ == "__main__":
    (OUT / "en").mkdir(parents=True, exist_ok=True)
    (OUT / "index.html").write_text(build("de"), encoding="utf-8")
    (OUT / "en" / "index.html").write_text(build("en"), encoding="utf-8")

    (OUT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % DOMAIN, encoding="utf-8")
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
               'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n')
    for lang in ("de", "en"):
        sitemap += "  <url>\n    <loc>%s</loc>\n" % URLS[lang]
        sitemap += '    <xhtml:link rel="alternate" hreflang="de" href="%s"/>\n' % URLS["de"]
        sitemap += '    <xhtml:link rel="alternate" hreflang="en" href="%s"/>\n' % URLS["en"]
        sitemap += '    <xhtml:link rel="alternate" hreflang="x-default" href="%s"/>\n' % URLS["de"]
        sitemap += "  </url>\n"
    sitemap += "</urlset>\n"
    (OUT / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    # .htaccess mit CSP-Hashes aller vier Seiten
    pages = [OUT / "index.html", OUT / "en" / "index.html", OUT / "impressum.html", OUT / "datenschutz.html"]
    sh, st = csp_hashes([p for p in pages if p.exists()])
    tpl = HTACCESS_TEMPLATE.read_text(encoding="utf-8")
    (OUT / ".htaccess").write_text(
        tpl.replace("__SCRIPT_HASHES__", " ".join(sh)).replace("__STYLE_HASHES__", " ".join(st)),
        encoding="utf-8")

    print("generated: index.html, en/index.html, robots.txt, sitemap.xml, .htaccess "
          "(%d script hashes, %d style hashes)" % (len(sh), len(st)))
