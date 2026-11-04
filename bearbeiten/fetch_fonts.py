#!/usr/bin/env python3
"""
925law – Schriften selbst hosten.
Lädt die exakten woff2-Dateien (Latin) von Google Fonts herunter und legt sie
unter website/fonts/ mit den Namen ab, die fonts.css erwartet, und prüft die
SHA-256-Prüfsummen gegen die bekannten Dateien (Schutz vor manipulierten Downloads).

Nur nötig, falls website/fonts/ je leer sein sollte:
    python3 bearbeiten/fetch_fonts.py

Kein-Code-Alternative: https://gwfh.mranftl.com/fonts
  -> Archivo (500,700,800,900) und IBM Plex Sans (400,500,600), Charset "latin",
     woff2 herunterladen, Dateien in website/fonts/ genau so benennen wie in fonts.css.
"""
import hashlib, os, re, sys, urllib.request

CSS = ("https://fonts.googleapis.com/css2?"
       "family=Archivo:wght@500;700;800;900&"
       "family=IBM+Plex+Sans:wght@400;600&display=swap")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")  # erzwingt woff2

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "website", "fonts")
os.makedirs(OUT, exist_ok=True)

# Zielnamen: (CSS-font-family, weight) -> Dateiname
NAMES = {
    ("Archivo", "500"): "archivo-500.woff2",
    ("Archivo", "700"): "archivo-700.woff2",
    ("Archivo", "800"): "archivo-800.woff2",
    ("Archivo", "900"): "archivo-900.woff2",
    ("IBM Plex Sans", "400"): "ibmplexsans-400.woff2",
    ("IBM Plex Sans", "600"): "ibmplexsans-600.woff2",
}

# Bekannte Prüfsummen der ausgelieferten Dateien (shasum -a 256 website/fonts/*.woff2)
SHA256 = {
    "archivo-500.woff2": "ab74eca5ad115fe4cfec82ba641e5d37e4d92c58dfb1bfc1e464e9039c9d17cf",
    "archivo-700.woff2": "abada6cd4c92a9a706f6d7ed3189f322ff43dd78b9402c7d1137465b861d2a04",
    "archivo-800.woff2": "c26cda2400b374eb1adb6e0973c86f455e2df17ca57c6755eb37d7bde47663fb",
    "archivo-900.woff2": "e915040a27c5310623be7ae57b6e4c508e8800206dcc37abe99984510e74a66d",
    "ibmplexsans-400.woff2": "3b646991d30055a93a4ecc499713d4347953a74a947ecab435ab72070cbdab0e",
    "ibmplexsans-600.woff2": "8960851d691c054ed38e259bdcf1a6190d157b4203ed5bb32c632a863fb8ec2f",
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

bad = False
for key, url in got.items():
    data = get(url, binary=True)
    digest = hashlib.sha256(data).hexdigest()
    if digest != SHA256.get(NAMES[key]):
        print("FEHLER: Prüfsumme weicht ab für", NAMES[key], "- Datei NICHT gespeichert.")
        print("        (Google liefert evtl. eine neue Version; dann Hash in SHA256 prüfen und aktualisieren.)")
        bad = True
        continue
    path = os.path.join(OUT, NAMES[key])
    with open(path, "wb") as f:
        f.write(data)
    print("gespeichert:", NAMES[key], f"({len(data)//1024} KB)")

print("\nFertig. %d/%d Dateien in %s" % (len(got), len(NAMES), OUT))
if bad:
    sys.exit(1)
