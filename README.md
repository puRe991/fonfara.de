# fonfara.de – neue Website von Teflon Fonfara

Moderne, schnelle und datenschutzfreundliche Neufassung von **www.fonfara.de** –
mit **allen Inhalten der bisherigen Website** (Texte, Bilder, Videos, Hörproben,
Rezepte, Impressum/Datenschutz).

## Was ist drin?

| Bereich | Seiten |
|---|---|
| Start | `index.html` |
| Person | Biografie als Zeitstrahl (Deutsch + English) |
| Musik | Album & Einzeltitel, ASIAN STARS (+ Live-Archiv), Sirius-Engel, Das Summen der Honigbiene, Musik-Comedy |
| Video | rund 50 Videos, nach Rubriken |
| Comedy | Frau Kächele & Frau Peters: Daheim, Fakten, **Audio-Archiv (113 Sketche & Songs)**, Videos, CD & Buch, Live-Show, Die schwäbische Seite, 25 Hefezopf-Rezepte, Humor, Impressum |
| Meditation | Online-Meditation, Fragen & Antworten, Dienstagstreff, CD & Download |
| Bücher | alle 7 Bücher + Hörspiel |
| Kreatives | Comedy & Werbung, Werkbeispiel, Hauszeitung, Impressum |
| Rechtliches | Impressum, Haftungsausschluss, Datenschutzerklärung |

**Alle alten Adressen bleiben gleich** (z. B. `kp/cd.html`, `teflon/index.html`),
damit Google-Einträge, Lesezeichen und Links von anderen Seiten weiter funktionieren.
Alte Sonder-Adressen (`index.htm`, `siriusengel/index.htm`, `meditation.html` …)
leiten automatisch weiter.

### Modern & datenschutzfreundlich
- Responsive (Handy, Tablet, Desktop), Hell-/Dunkelmodus, barrierearm
- **Keine Cookies, kein Tracking, keine Google Fonts** – Schriften liegen auf dem eigenen Server
- YouTube, SoundCloud & Co. werden **erst nach Klick** geladen (youtube-nocookie.com)
- Eigener Audio-Player für das Kächele-&-Peters-Archiv
- Sitemap, robots.txt, saubere Titel/Beschreibungen für Suchmaschinen

## Veröffentlichen (Upload)

Der fertige Webauftritt liegt im Ordner **`public/`**.
Einfach den **Inhalt** von `public/` per FTP in das Hauptverzeichnis des Webspace laden
(alte Dateien mit gleichem Namen werden überschrieben).

**Bitte auf dem Server behalten / nicht löschen:**
- die MP3-Dateien unter `kp/player/` und `kp/internetstanze_Frau_Kaechele_Frau_Peters.mp3`
  (Audio-Archiv, ca. 245 MB – nicht im Repository)
- die Ordner `maggie/` und `roland-bentz/` (eigenständige Seiten, werden weiter verlinkt)

## Bearbeiten

Inhalte liegen in `src/pages/` (eine Datei je Seite), Layout in `src/templates/`,
Design in `src/static/css/site.css`, Bilder in `src/media/`.
Nach Änderungen neu bauen:

```bash
pip install -r requirements.txt
python3 build.py              # erzeugt public/
tools/fetch-audio.sh          # optional: MP3s für lokale Vorschau laden
cd public && python3 -m http.server 8000   # Vorschau: http://localhost:8000
```

Daten-Dateien: `src/data/player.json` (Audio-Archiv), `src/data/recipes.json` (Hefezopf-Rezepte),
`src/fragments/datenschutz.html` (Datenschutzerklärung).
