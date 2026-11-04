#!/usr/bin/env python3
# Generator: liest 925law.html (mit I18N-Dict) und erzeugt zwei statische,
# indexierbare Sprachseiten + SEO-Kopf. Einzige Quelle bleibt 925law.html.
import re, json, pathlib, shutil
from bs4 import BeautifulSoup

SRC = pathlib.Path("/mnt/user-data/outputs/925law.html")
OUT = pathlib.Path("/mnt/user-data/outputs/site")
DOMAIN = "https://925law.de"

html = SRC.read_text(encoding="utf-8")

# --- I18N + TITLES aus dem JS herausziehen ---
i18n = json.loads(re.search(r"var I18N = (\{.*?\});", html, re.S).group(1))
titles = json.loads(re.search(r"var TITLES = (\{.*?\});", html, re.S).group(1))

# --- SEO-Texte pro Sprache ---
META = {
  "de": {
    "title": "925law – Rechtsanwalt Arbeitsrecht & Vertragsrecht Berlin | Max Englhard",
    "desc": ("Rechtsanwalt Max Englhard (925law): Arbeitsrecht und Vertragsrecht in Berlin. "
             "Kündigungsschutz, Abfindung, Aufhebungsvertrag, Verträge und Forderungen – "
             "für Unternehmen, Führungskräfte, Angestellte und Freelancer. Erstgespräch zum Festpreis."),
    "og_locale": "de_DE",
    "alt_locale": "en_US",
  },
  "en": {
    "title": "925law – English-speaking Employment & Contract Lawyer in Berlin | Max Englhard",
    "desc": ("Max Englhard (925law): English-speaking German employment and contract lawyer in Berlin. "
             "Protection against dismissal, severance, termination agreements, contracts and claims – "
             "for companies, executives, employees and freelancers. Fixed-fee initial consultation."),
    "og_locale": "en_US",
    "alt_locale": "de_DE",
  },
}
URLS = {"de": DOMAIN + "/", "en": DOMAIN + "/en/"}

# --- JSON-LD (Attorney) – ohne Straße/Telefon, solange Impressum Platzhalter hat ---
JSONLD = {
  "@context": "https://schema.org",
  "@type": "Attorney",
  "name": "925law – Max Englhard",
  "url": DOMAIN + "/",
  "description": META["en"]["desc"],
  "areaServed": "Berlin, Germany",
  "availableLanguage": ["de", "en"],
  "knowsAbout": [
    "Arbeitsrecht", "Kündigungsschutz", "Abfindung", "Aufhebungsvertrag",
    "Vertragsrecht", "Forderungseinzug", "Beamtenrecht",
    "Employment law", "Contract law"
  ],
  "founder": {"@type": "Person", "name": "Max Englhard", "jobTitle": "Rechtsanwalt"},
  "memberOf": {"@type": "Organization", "name": "Rechtsanwaltskammer Berlin"},
  "address": {"@type": "PostalAddress", "addressLocality": "Berlin", "addressCountry": "DE"},
  "email": "kontakt@925law.de",
  "inLanguage": ["de", "en"],
}

def build(lang):
    soup = BeautifulSoup(html, "html.parser")

    # <html lang>
    soup.html["lang"] = lang

    # Text aller [data-i18n]-Knoten fest in die Sprache schreiben, Attribut entfernen
    for node in soup.select("[data-i18n]"):
        key = node.get("data-i18n")
        if key in i18n and lang in i18n[key]:
            frag = BeautifulSoup(i18n[key][lang], "html.parser")
            node.clear()
            for child in list(frag.contents):
                node.append(child)
        del node["data-i18n"]

    # --- <head> neu aufbauen (SEO) ---
    head = soup.head
    # vorhandenen Title ersetzen
    soup.title.string = META[lang]["title"]

    def meta(attrs):
        m = soup.new_tag("meta");
        for k,v in attrs.items(): m[k]=v
        return m
    def link(attrs):
        l = soup.new_tag("link")
        for k,v in attrs.items(): l[k]=v
        return l

    add = []
    add.append(meta({"name":"description","content":META[lang]["desc"]}))
    add.append(meta({"name":"robots","content":"index,follow"}))
    add.append(meta({"name":"author","content":"Max Englhard"}))
    add.append(link({"rel":"canonical","href":URLS[lang]}))
    # hreflang
    add.append(link({"rel":"alternate","hreflang":"de","href":URLS["de"]}))
    add.append(link({"rel":"alternate","hreflang":"en","href":URLS["en"]}))
    add.append(link({"rel":"alternate","hreflang":"x-default","href":URLS["de"]}))
    # Favicons
    add.append(link({"rel":"icon","type":"image/svg+xml","href":"/favicon.svg"}))
    add.append(link({"rel":"icon","type":"image/png","sizes":"32x32","href":"/favicon-32.png"}))
    add.append(link({"rel":"apple-touch-icon","href":"/apple-touch-icon.png"}))
    # Open Graph
    og = {
        "og:type":"website","og:site_name":"925law","og:title":META[lang]["title"],
        "og:description":META[lang]["desc"],"og:url":URLS[lang],
        "og:image":DOMAIN+"/og-image.png","og:locale":META[lang]["og_locale"],
    }
    for k,v in og.items(): add.append(meta({"property":k,"content":v}))
    add.append(meta({"property":"og:locale:alternate","content":META[lang]["alt_locale"]}))
    # Twitter
    add.append(meta({"name":"twitter:card","content":"summary_large_image"}))
    add.append(meta({"name":"twitter:title","content":META[lang]["title"]}))
    add.append(meta({"name":"twitter:description","content":META[lang]["desc"]}))
    add.append(meta({"name":"twitter:image","content":DOMAIN+"/og-image.png"}))
    # JSON-LD
    ld = soup.new_tag("script", type="application/ld+json")
    ld.string = json.dumps(JSONLD, ensure_ascii=False, indent=2)
    add.append(ld)

    # vor </head> einhängen (nach bestehenden meta/fonts)
    for tag in add:
        head.append(tag)

    # --- Asset-Pfade absolut machen (beide Seiten liegen in verschiedenen Tiefen) ---
    for img in soup.find_all("img", src=True):
        if img["src"] == "portrait.webp": img["src"] = "/portrait.webp"
    form = soup.find("form", id="contact-form")
    if form and form.get("action") == "kontakt.php":
        form["action"] = "/kontakt.php"

    # Brand-Logo-Link oben links -> auf Sprachwurzel zeigen
    brand = soup.select_one("a.logo, .sidebar-top a")
    # (Anker bleiben #..., funktionieren auf beiden Seiten)

    # --- Sprachumschalter zu echten Links machen ---
    sw = soup.select_one(".lang-switch")
    if sw:
        sw.clear()
        de = soup.new_tag("a", href="/"); de.string = "DE"
        en = soup.new_tag("a", href="/en/"); en.string = "EN"
        de["class"] = "lang-de" + (" lang-active" if lang=="de" else "")
        en["class"] = "lang-en" + (" lang-active" if lang=="en" else "")
        if lang=="de": de["aria-current"]="true"
        else: en["aria-current"]="true"
        sep = soup.new_tag("span"); sep["class"]="sep"; sep.string="/"
        sw.append(de); sw.append(sep); sw.append(en)

    # --- Script: setLang/I18N raus, nur Formular-Logik behalten (lokalisiert) ---
    alert_txt = {
        "de": "Es gab ein Problem beim Senden. Bitte schreiben Sie direkt an kontakt@925law.de.",
        "en": "Something went wrong while sending. Please email kontakt@925law.de directly.",
    }[lang]
    new_script = soup.new_tag("script")
    new_script.string = """
  (function(){
    var form = document.getElementById('contact-form');
    function showThanks(){
      if(form) form.style.display='none';
      var i=document.getElementById('contact-intro'); if(i) i.style.display='none';
      var t=document.querySelector('.form-thanks'); if(t) t.style.display='block';
    }
    try{
      if(/[?&]sent=1/.test(location.search)){
        showThanks();
        if(window.history && history.replaceState){ history.replaceState(null,'',location.pathname+'#contact'); }
      }
    }catch(e){}
    if(form){
      form.addEventListener('submit', function(e){
        e.preventDefault();
        fetch(form.action, { method:'POST', body:new FormData(form),
          headers:{ 'Accept':'application/json','X-Requested-With':'XMLHttpRequest' } })
        .then(function(r){ return r.json().catch(function(){ return { ok:r.ok }; }); })
        .then(function(res){ if(res && res.ok){ showThanks(); } else { alert(__ALERT__); } })
        .catch(function(){ alert(__ALERT__); });
      });
    }
  })();
""".replace("__ALERT__", json.dumps(alert_txt, ensure_ascii=False))
    # alten Script-Block (der letzte) ersetzen
    scripts = soup.find_all("script")
    old = None
    for s in scripts:
        if s.string and "var I18N" in s.string:
            old = s; break
    if old: old.replace_with(new_script)

    out = str(soup)
    return out

OUT.mkdir(parents=True, exist_ok=True)
(OUT/"en").mkdir(parents=True, exist_ok=True)
(OUT/"index.html").write_text(build("de"), encoding="utf-8")
(OUT/"en"/"index.html").write_text(build("en"), encoding="utf-8")

# --- robots.txt + sitemap.xml ---
(OUT/"robots.txt").write_text(
    "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % DOMAIN, encoding="utf-8")
sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n' \
  '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" ' \
  'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
for lang in ("de","en"):
    sitemap += '  <url>\n    <loc>%s</loc>\n' % URLS[lang]
    sitemap += '    <xhtml:link rel="alternate" hreflang="de" href="%s"/>\n' % URLS["de"]
    sitemap += '    <xhtml:link rel="alternate" hreflang="en" href="%s"/>\n' % URLS["en"]
    sitemap += '    <xhtml:link rel="alternate" hreflang="x-default" href="%s"/>\n' % URLS["de"]
    sitemap += '  </url>\n'
sitemap += '</urlset>\n'
(OUT/"sitemap.xml").write_text(sitemap, encoding="utf-8")

# --- vorhandene Assets in den Deploy-Ordner kopieren ---
for f in ("portrait.webp","kontakt.php"):
    p = pathlib.Path("/mnt/user-data/outputs")/f
    if p.exists(): shutil.copy(p, OUT/f)

print("generated:", *(str(p) for p in OUT.rglob("*")), sep="\n  ")
