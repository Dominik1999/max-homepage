# 925law – Kanzlei-Homepage

Zweisprachige Ein-Seiten-Website (Deutsch / Englisch) für Rechtsanwalt Max Englhard, Berlin.
Statisches HTML, selbst gehostete Schriften, ein PHP-Skript für das Kontaktformular.
Produktiv-Hosting: Hetzner Webhosting. Vorschau: GitHub Pages (siehe unten).

## Ordner

| Ordner / Datei | Zweck |
|---|---|
| `website/` | Die fertige Seite. Inhalt 1:1 in den Webroot (`public_html`) bei Hetzner laden. |
| `website/.htaccess` | Server-Einstellungen: HTTPS-Zwang, Sicherheits-Header, Content-Security-Policy, Caching. Wird vom Generator erzeugt. |
| `website/kontakt.php` | Formular-Handler: Benachrichtigung an die Kanzlei + kurze Eingangsbestätigung. |
| `bearbeiten/925law.html` | **Einzige Quelle für die Startseiten-Texte** (Wörterbuch `I18N` im `<script>`, je `de` und `en`). |
| `bearbeiten/build_site.py` | Generator: schreibt `website/index.html`, `website/en/index.html`, `sitemap.xml`, `robots.txt`, `.htaccess`. |
| `bearbeiten/htaccess.template` | Vorlage für `.htaccess`; die CSP-Hashes setzt der Generator ein. |
| `bearbeiten/fetch_fonts.py` | Lädt die Schriftdateien nach und prüft ihre Prüfsummen. Nur nötig, falls `website/fonts/` je leer ist. |
| `tasks/review-2026-11-03.md` | Technischer Review mit allen Befunden (Datei + Zeile). |
| `tasks/todo.md` | Was davon umgesetzt ist und was bewusst offen bleibt. |
| `UEBERGABE.txt` | Ursprüngliche Übergabe-Notiz des Erstellers. |

## Texte ändern

1. `bearbeiten/925law.html` öffnen, im `I18N`-Wörterbuch den Text ändern (beide Sprachen).
2. Neu erzeugen:
   ```sh
   pip install beautifulsoup4      # einmalig
   python3 bearbeiten/build_site.py
   ```
3. `website/` hochladen.

Der Generator bricht ab, wenn die Ausgabe Google Fonts enthalten würde oder ein
Übersetzungsschlüssel fehlt. Impressum, Datenschutz und `kontakt.php` sind eigenständige
Dateien in `website/` und werden direkt bearbeitet. Nach Änderungen an Inline-Scripts oder
`<style>`-Blöcken (auch in Impressum/Datenschutz) den Generator erneut laufen lassen, damit
die CSP-Hashes in `.htaccess` stimmen.

## Vorschau auf GitHub Pages

Jeder Push auf `main` baut eine Vorschau (`.github/workflows/pages.yml`). Sie unterscheidet
sich bewusst von der echten Seite:

- Das Kontaktformular sendet nichts (GitHub Pages kann kein PHP); es zeigt einen Vorschau-Hinweis.
- Der Plausible-Zähler ist entfernt.
- `.htaccess` greift dort nicht (keine Sicherheits-Header in der Vorschau).
- Pfade sind auf das Repo-Unterverzeichnis umgebogen.

## Vor dem Livegang (offen)

Siehe `tasks/todo.md`, Abschnitt „Left open on purpose“: Impressum (ODR-Absatz, Versicherung),
Datenschutzerklärung (Eingangsbestätigung, Mailtransport, englische Fassung), Plausible-AV-Vertrag
oder Entfernen, Telefonnummer/Adresse auf der Startseite, Formular-Test auf dem Hetzner-Server,
SPF/DKIM/DMARC für `925law.de`.
