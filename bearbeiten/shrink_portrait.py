#!/usr/bin/env python3
"""website/portrait.webp auf die doppelte Anzeigegröße verkleinern.

Die Seite zeigt das Porträt in einer 220 x 280 px großen Box (object-fit: cover);
2x davon sind 440 px Breite. Das Skript skaliert nur (kein Zuschnitt, keine
Retusche), behält das Seitenverhältnis und schreibt ohne Metadaten.

Einmalige Aufgabe: Ist das Bild schon höchstens 440 px breit, passiert nichts
(kein erneutes verlustbehaftetes Speichern). Ein neues, größeres Originalfoto
einfach als website/portrait.webp ablegen und das Skript noch einmal starten.

    ~/.venvs/925law-assets/bin/python bearbeiten/shrink_portrait.py

Abhängigkeit: pillow (mit WebP-Unterstützung). Kein Netzwerkzugriff.
"""
from pathlib import Path

from PIL import Image

PORTRAIT = Path(__file__).resolve().parent.parent / "website" / "portrait.webp"
TARGET_WIDTH = 440   # 2 x 220 px Anzeigebreite
QUALITY = 84


def main():
    img = Image.open(PORTRAIT)
    old_size, old_bytes = img.size, PORTRAIT.stat().st_size
    if img.width <= TARGET_WIDTH:
        print(f"portrait.webp ist bereits {img.width} x {img.height} px – nichts zu tun")
        return
    height = round(img.height * TARGET_WIDTH / img.width)
    small = img.convert("RGB").resize((TARGET_WIDTH, height), Image.LANCZOS)
    small.info.clear()
    small.save(PORTRAIT, "WEBP", quality=QUALITY, method=6, exif=b"", icc_profile=None, xmp=b"")
    print(f"portrait.webp: {old_size[0]} x {old_size[1]} px, {old_bytes} Bytes"
          f"  ->  {TARGET_WIDTH} x {height} px, {PORTRAIT.stat().st_size} Bytes")


if __name__ == "__main__":
    main()
