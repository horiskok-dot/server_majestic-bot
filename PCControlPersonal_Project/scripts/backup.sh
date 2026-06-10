#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=false
if [ "${1:-}" = "--dry-run" ]; then
  DRY_RUN=true
fi

STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="/data/backups"
TARGET="${BACKUP_DIR}/pcmanager-${STAMP}.tar.gz"
SOURCES=(
  "/home/pc/PCControlPersonal_Project"
  "/etc/pcmanager/pcmanager.env"
  "/var/lib/pcmanager"
  "/data/files"
  "/data/screenshots"
  "/data/uploads"
  "/etc/systemd/system/pcmanager-server.service"
  "/etc/systemd/system/pcmanager-bot.service"
  "/etc/systemd/system/pcmanager-local-check.service"
  "/etc/systemd/system/pcmanager-local-check.timer"
)

echo "Backup target: $TARGET"
printf 'Sources:\n'
printf -- '- %s\n' "${SOURCES[@]}"

if [ "$DRY_RUN" = true ]; then
  echo "Dry run only, no files written."
  exit 0
fi

sudo mkdir -p "$BACKUP_DIR"
sudo tar --warning=no-file-changed --ignore-failed-read -czf "$TARGET" "${SOURCES[@]}"
sudo chown pcmanager:pcmanager "$TARGET" 2>/dev/null || true
sudo chmod 0640 "$TARGET" 2>/dev/null || true
echo "$TARGET"
