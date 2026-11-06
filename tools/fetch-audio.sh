#!/usr/bin/env bash
# Lädt die MP3-Dateien des Frau-Kächele-&-Frau-Peters-Archivs (ca. 245 MB) von der
# bisherigen Website nach public/kp/player/ – nur nötig für eine lokale Vorschau.
# Auf dem Webserver liegen die Dateien bereits unter /kp/player/ und /kp/ und
# müssen beim Hochladen der neuen Seite einfach dort bleiben.
set -euo pipefail
cd "$(dirname "$0")/.."
BASE="${1:-https://fonfara.de}"
mkdir -p public/kp/player
python3 -c "import json;[print(i['file']) for s in json.load(open('src/data/player.json')) for i in s['items']]" | sort -u |
while read -r f; do
  [ -s "public/kp/player/$f" ] && continue
  echo "lade $f"
  curl -sSfL "$BASE/kp/player/$f" -o "public/kp/player/$f" || echo "FEHLT: $f"
done
[ -s public/kp/internetstanze_Frau_Kaechele_Frau_Peters.mp3 ] || curl -sSfL "$BASE/kp/internetstanze_Frau_Kaechele_Frau_Peters.mp3" -o public/kp/internetstanze_Frau_Kaechele_Frau_Peters.mp3
echo fertig
