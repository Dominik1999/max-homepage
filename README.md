# 925law – Kanzlei-Homepage

Zweisprachige Ein-Seiten-Website (Deutsch / Englisch) für Rechtsanwalt Max Englhard, Berlin.
Statisches HTML, selbst gehostete Schriften, ein PHP-Skript für das Kontaktformular.
Produktiv-Hosting: Hetzner Webhosting. Vorschau: GitHub Pages (siehe unten).
Englisch ist die Standardsprache unter `925law.de/`, Deutsch liegt unter `925law.de/de/`
(seit 2026-11-23; `.htaccess` leitet alte `/en/`-Adressen weiter).

## Ordner

| Ordner / Datei | Zweck |
|---|---|
| `website/` | Die fertige Seite. Inhalt 1:1 in den Webroot (`public_html`) bei Hetzner laden. |
| `website/.htaccess` | Server-Einstellungen: HTTPS-Zwang, Sicherheits-Header, Content-Security-Policy, Caching. Wird vom Generator erzeugt. |
| `website/site.css` | **Einzige Quelle für die Gestaltung** aller sechs Seiten: Farben, Schriften, Marke, Sprachumschalter, Footer (Abschnitt „Gemeinsam“) und das Layout der Startseite. Wird direkt bearbeitet. |
| `website/legal.css` | Ergänzung für die vier Rechtsseiten (Kopfzeile, Textspalte, Überschriften). Wird nach `site.css` geladen und direkt bearbeitet. |
| `website/fonts.css` | Einbindung der selbst gehosteten Schriften aus `website/fonts/`. |
| `website/kontakt.php` | Formular-Handler: Benachrichtigung an die Kanzlei + kurze Eingangsbestätigung. |
| `bearbeiten/925law.html` | **Einzige Quelle für die Startseiten-Texte** (Wörterbuch `I18N` im `<script>`, je `de` und `en`). |
| `bearbeiten/build_site.py` | Generator: schreibt `website/index.html` (Englisch, Startseite), `website/de/index.html` (Deutsch), die vier Rechtsseiten, `sitemap.xml`, `robots.txt`, `.htaccess`. |
| `bearbeiten/recht/` | **Einzige Quelle für Impressum und Datenschutzerklärung** (deutsch und englisch): eine Vorlage, vier Textdateien. |
| `bearbeiten/build_legal.py` | Teil des Generators: baut aus `bearbeiten/recht/` die vier Rechtsseiten. Wird von `build_site.py` aufgerufen. |
| `bearbeiten/htaccess.template` | Vorlage für `.htaccess`; die CSP-Hashes der Inline-Scripts setzt der Generator ein. |
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

Zwei Wörterbuch-Einträge sind optional; ist der Wert leer (`""`), erscheint die Zeile gar nicht:

- `contact_phone` – Telefonnummer (Seitenleiste, Kopfzeile, Kontaktblock, strukturierte Daten). Derzeit leer.
- `form_response_time` – Zusage „Antwort innerhalb eines Werktags.“ unter dem Senden-Button. Leeren, falls die Zusage nicht gelten soll.

Die Anschrift (Kaiserkorso 2, 12101 Berlin) steht fest im Markup von `925law.html` (Seitenleiste, Kontaktblock, Footer)
und in `build_site.py` (strukturierte Daten); bei einem Umzug an allen Stellen und im Impressum ändern.

Der Generator bricht ab, wenn die Ausgabe Google Fonts enthalten würde oder ein
Übersetzungsschlüssel fehlt. `kontakt.php` ist eine eigenständige Datei in `website/` und
wird direkt bearbeitet. Nach jeder Änderung an Inline-Scripts den Generator erneut laufen
lassen, damit die CSP-Hashes in `.htaccess` stimmen.

### Gestaltung ändern (CSS)

Das CSS steht nicht mehr in den HTML-Dateien, sondern einmal in `website/site.css` (alle
Seiten) und `website/legal.css` (nur Rechtsseiten). Eine Farbe, Schrift oder Abstandsregel
wird dort an einer Stelle geändert und gilt für alle Seiten, die sie betrifft.

1. `website/site.css` bzw. `website/legal.css` bearbeiten. Regeln, die mit `.home` beginnen,
   gelten nur für die Startseiten (der Kommentar am Dateianfang erklärt den Aufbau).
2. `python3 bearbeiten/build_site.py` ausführen. Der Generator hängt die Prüfsumme jeder
   CSS-Datei als `?v=…` an die Links in den sechs Seiten. Ohne diesen Schritt zeigen Browser
   von wiederkehrenden Besuchern bis zu einem Tag lang das alte CSS.
3. `website/` hochladen (die CSS-Dateien und die HTML-Dateien).

Im HTML sind weder `<style>`-Blöcke noch `style="…"`-Attribute erlaubt: die
Content-Security-Policy lässt nur die eigenen CSS-Dateien zu (`style-src 'self'`), und der
Generator bricht ab, falls doch eines in der Ausgabe steht.

## Impressum und Datenschutzerklärung ändern

Die vier Rechtsseiten (englisch: `website/impressum.html`, `website/datenschutz.html`;
deutsch: `website/de/impressum.html`, `website/de/datenschutz.html`) werden erzeugt. **Nicht in `website/` bearbeiten**, die Dateien
werden beim nächsten Lauf überschrieben.

1. Text in `bearbeiten/recht/` ändern: `impressum.de.html`, `impressum.en.html`,
   `datenschutz.de.html`, `datenschutz.en.html`. Die Dateien enthalten nur den Inhalt ab der
   Überschrift, als normales HTML. Jede Änderung am deutschen Text in der englischen Datei
   nachziehen (die englische Fassung ist eine Übersetzung, die deutsche ist maßgeblich).
2. Kopf und Fuß aller vier Seiten stehen einmal in `bearbeiten/recht/vorlage.html`, die
   Gestaltung in `website/site.css` und `website/legal.css` (siehe „Gestaltung ändern“).
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
oder Entfernen, Telefonnummer (`contact_phone`) und Bestätigung der Antwortzeit-Zusage (`form_response_time`), Formular-Test auf dem Hetzner-Server,
SPF/DKIM/DMARC für `925law.de`.
