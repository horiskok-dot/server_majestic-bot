#!/usr/bin/env bash
set -euo pipefail

ARCHIVE="${1:-}"
if [ -z "$ARCHIVE" ] || [ ! -f "$ARCHIVE" ]; then
  echo "Usage: scripts/restore.sh /home/pc/backups/pcmanager-YYYYmmdd-HHMMSS.tar.gz"
  exit 2
fi

echo "Restore archive: $ARCHIVE"
echo "This can overwrite project/state files. Type RESTORE to continue:"
read -r CONFIRM
if [ "$CONFIRM" != "RESTORE" ]; then
  echo "Cancelled"
  exit 1
fi

STAMP="$(date +%Y%m%d-%H%M%S)"
SAFETY="/home/pc/backups/pre_restore_${STAMP}.tar.gz"
mkdir -p /home/pc/backups
sudo tar --warning=no-file-changed --ignore-failed-read -czf "$SAFETY" /home/pc/PCControlPersonal_Project /etc/pcmanager /var/lib/pcmanager
echo "Safety backup: $SAFETY"

echo "Keep existing /etc/pcmanager/pcmanager.env? Type KEEP to preserve it, anything else to restore archive copy:"
read -r KEEP_ENV
if [ "$KEEP_ENV" = "KEEP" ] && [ -f /etc/pcmanager/pcmanager.env ]; then
  sudo cp /etc/pcmanager/pcmanager.env "/tmp/pcmanager.env.keep.${STAMP}"
fi

sudo tar -xzf "$ARCHIVE" -C /

if [ "$KEEP_ENV" = "KEEP" ] && [ -f "/tmp/pcmanager.env.keep.${STAMP}" ]; then
  sudo cp "/tmp/pcmanager.env.keep.${STAMP}" /etc/pcmanager/pcmanager.env
fi

sudo systemctl daemon-reload
sudo systemctl restart pcmanager-server pcmanager-bot
echo "Restore complete."
