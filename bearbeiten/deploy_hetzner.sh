#!/bin/bash
# 925law – website/ per FTPS (verschlüsselt) nach Hetzner hochladen.
#
# Das Passwort steht NICHT hier, sondern im macOS-Schlüsselbund. Einmalig anlegen mit:
#   security add-internet-password -s www778.your-server.de -a e3ersy -w
# (fragt nach dem Passwort aus der konsoleH, „FTP-Hauptbenutzer“)
#
# Aufruf:
#   bearbeiten/deploy_hetzner.sh          lädt alle Dateien aus website/ nach public_html/
#                                         und bearbeiten/server/ nach ~/cron/ (Cronjobs)
#   bearbeiten/deploy_hetzner.sh --list   zeigt nur, was auf dem Server liegt
#
# Dateien, die es in website/ nicht mehr gibt, werden auf dem Server NICHT gelöscht.
set -euo pipefail

HOST="www778.your-server.de"
USER_NAME="e3ersy"
REMOTE_DIR="public_html"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SITE="$ROOT/website"

PASS="$(security find-internet-password -s "$HOST" -a "$USER_NAME" -w 2>/dev/null)" || {
  echo "Kein Passwort im Schlüsselbund. Einmalig anlegen mit:" >&2
  echo "  security add-internet-password -s $HOST -a $USER_NAME -w" >&2
  exit 1
}

# Zugangsdaten über stdin an curl geben, damit das Passwort nicht in der Prozessliste steht
ftp() {
  printf 'user = "%s:%s"\n' "$USER_NAME" "${PASS//\"/\\\"}" | \
    curl --silent --show-error --fail --ssl-reqd --config - "$@"
}

if [[ "${1:-}" == "--list" ]]; then
  echo "== Home"; ftp "ftp://$HOST/"
  echo "== $REMOTE_DIR"; ftp "ftp://$HOST/$REMOTE_DIR/"
  exit 0
fi

cd "$SITE"
count=0
while IFS= read -r -d '' f; do
  f="${f#./}"
  ftp --ftp-create-dirs -T "$f" "ftp://$HOST/$REMOTE_DIR/$f"
  count=$((count + 1))
done < <(find . -type f ! -name '.DS_Store' -print0)
echo "$count Dateien nach $HOST:$REMOTE_DIR hochgeladen."

# Server-Skripte (Cronjobs) außerhalb des Webroots nach ~/cron/
for f in "$ROOT"/bearbeiten/server/*; do
  [[ -f "$f" ]] || continue
  ftp --ftp-create-dirs -T "$f" "ftp://$HOST/cron/$(basename "$f")"
done
echo "Server-Skripte nach $HOST:cron/ hochgeladen."
