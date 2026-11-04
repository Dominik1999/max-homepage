#!/usr/bin/env python3
"""
925law – Schriften selbst hosten.
Lädt die exakten woff2-Dateien (Latin) von Google Fonts herunter und legt sie
unter site/fonts/ mit den Namen ab, die fonts.css erwartet.

Auf DEINEM Rechner ausführen (offenes Netz), im Ordner, der "site/" enthält:
    python3 fetch_fonts.py
Danach: den kompletten "site/"-Ordner hochladen – fertig.

Kein-Code-Alternative: https://gwfh.mranftl.com/fonts
  -> Archivo (500,700,800,900) und IBM Plex Sans (400,500,600), Charset "latin",
     woff2 herunterladen, Dateien in site/fonts/ genau so benennen wie in fonts.css.
"""
import os, re, urllib.request

CSS = ("https://fonts.googleapis.com/css2?"
       "family=Archivo:wght@500;700;800;900&"
       "family=IBM+Plex+Sans:wght@400;500;600&display=swap")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")  # erzwingt woff2

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site", "fonts")
os.makedirs(OUT, exist_ok=True)

# Zielnamen: (CSS-font-family, weight) -> Dateiname
NAMES = {
    ("Archivo", "500"): "archivo-500.woff2",
    ("Archivo", "700"): "archivo-700.woff2",
    ("Archivo", "800"): "archivo-800.woff2",
    ("Archivo", "900"): "archivo-900.woff2",
    ("IBM Plex Sans", "400"): "ibmplexsans-400.woff2",
    ("IBM Plex Sans", "500"): "ibmplexsans-500.woff2",
    ("IBM Plex Sans", "600"): "ibmplexsans-600.woff2",
}

def get(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read() if binary else r.read().decode("utf-8")

css = get(CSS)
# @font-face-Blöcke zerlegen; nur den "latin"-Block je (family,weight) nehmen
blocks = re.split(r"(?=/\*\s*[\w-]+\s*\*/)", css)
got = {}
current_subset = None
for b in blocks:
    ms = re.match(r"/\*\s*([\w-]+)\s*\*/", b.strip())
    subset = ms.group(1) if ms else None
    fam = re.search(r"font-family:\s*'([^']+)'", b)
    wgt = re.search(r"font-weight:\s*(\d+)", b)
    url = re.search(r"src:\s*url\(([^)]+)\)\s*format\('woff2'\)", b)
    if subset == "latin" and fam and wgt and url:
        key = (fam.group(1), wgt.group(1))
        if key in NAMES and key not in got:
            got[key] = url.group(1)

missing = [k for k in NAMES if k not in got]
if missing:
    print("WARN: keine latin-URL gefunden für:", missing)

for key, url in got.items():
    data = get(url, binary=True)
    path = os.path.join(OUT, NAMES[key])
    with open(path, "wb") as f:
        f.write(data)
    print("gespeichert:", NAMES[key], f"({len(data)//1024} KB)")

print("\nFertig. %d/%d Dateien in %s" % (len(got), len(NAMES), OUT))
