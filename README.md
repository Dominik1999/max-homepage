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
| `bearbeiten/build_site.py` | Generator: schreibt `website/index.html`, `website/en/index.html`, die vier Rechtsseiten, `sitemap.xml`, `robots.txt`, `.htaccess`. |
| `bearbeiten/recht/` | **Einzige Quelle für Impressum und Datenschutzerklärung** (deutsch und englisch): eine Vorlage, vier Textdateien. |
| `bearbeiten/build_legal.py` | Teil des Generators: baut aus `bearbeiten/recht/` die vier Rechtsseiten. Wird von `build_site.py` aufgerufen. |
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
Übersetzungsschlüssel fehlt. `kontakt.php` ist eine eigenständige Datei in `website/` und
wird direkt bearbeitet. Nach jeder Änderung an Inline-Scripts oder `<style>`-Blöcken den
Generator erneut laufen lassen, damit die CSP-Hashes in `.htaccess` stimmen.

## Impressum und Datenschutzerklärung ändern

Die vier Rechtsseiten (`website/impressum.html`, `website/datenschutz.html` und die englischen
Fassungen unter `website/en/`) werden erzeugt. **Nicht in `website/` bearbeiten**, die Dateien
werden beim nächsten Lauf überschrieben.

1. Text in `bearbeiten/recht/` ändern: `impressum.de.html`, `impressum.en.html`,
   `datenschutz.de.html`, `datenschutz.en.html`. Die Dateien enthalten nur den Inhalt ab der
   Überschrift, als normales HTML. Jede Änderung am deutschen Text in der englischen Datei
   nachziehen (die englische Fassung ist eine Übersetzung, die deutsche ist maßgeblich).
2. Kopf, Fuß und Gestaltung aller vier Seiten stehen einmal in `bearbeiten/recht/vorlage.html`.
3. `python3 bearbeiten/build_site.py` ausführen, `website/` hochladen.

Offene Punkte stehen als Kommentar `<!-- TODO(Max): … -->` direkt an der betroffenen Stelle
in den Textdateien. Sie erscheinen nicht auf der Website, der Generator listet sie aber bei
jedem Lauf auf. Vor dem Livegang mit `python3 bearbeiten/build_site.py --final` bauen: dieser
Aufruf bricht ab, solange noch ein solcher Punkt offen ist.

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
