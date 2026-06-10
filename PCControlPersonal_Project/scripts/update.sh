#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/pc/PCControlPersonal_Project"
RUNTIME_DIR="/opt/pcmanager"

cd "$PROJECT_DIR"
BACKUP_PATH="$(bash scripts/backup.sh | tail -n 1)"
echo "Backup created: $BACKUP_PATH"

sudo systemctl stop pcmanager-bot.service pcmanager-server.service || true

sudo rsync -a --delete \
  --exclude '.git' --exclude '.venv' --exclude 'venv' --exclude '__pycache__' \
  --exclude 'node_modules' --exclude 'build' --exclude 'dist' --exclude 'backup_*' \
  "$PROJECT_DIR/backend" "$RUNTIME_DIR/"
sudo rsync -a "$PROJECT_DIR/pc-agent" "$RUNTIME_DIR/"
sudo rsync -a "$PROJECT_DIR/scripts" "$RUNTIME_DIR/"
sudo rsync -a "$PROJECT_DIR/systemd" "$RUNTIME_DIR/"
sudo rsync -a "$PROJECT_DIR/tools" "$RUNTIME_DIR/" 2>/dev/null || true
sudo cp "$PROJECT_DIR/requirements.txt" "$PROJECT_DIR/README.md" "$PROJECT_DIR/PROJECT_HANDOFF.md" "$PROJECT_DIR/MIGRATION_WINDOWS_TO_UBUNTU.md" "$RUNTIME_DIR/" 2>/dev/null || true
sudo cp "$PROJECT_DIR/.env.example" "$RUNTIME_DIR/.env.example" 2>/dev/null || true
sudo chown -R pcmanager:pcmanager "$RUNTIME_DIR/backend" "$RUNTIME_DIR/pc-agent" "$RUNTIME_DIR/scripts" "$RUNTIME_DIR/systemd" "$RUNTIME_DIR/tools" 2>/dev/null || true
sudo chmod +x "$RUNTIME_DIR"/scripts/*.sh 2>/dev/null || true
sudo mkdir -p /data/files /data/backups /data/screenshots /data/uploads /data/media/movies /data/media/music /data/media/photos
sudo chown -R pcmanager:pcmanager /data
sudo chmod -R 0775 /data

sudo -u pcmanager /opt/pcmanager/venv/bin/python -m pip install -r "$RUNTIME_DIR/requirements.txt"
sudo systemctl daemon-reload
sudo systemctl start pcmanager-server.service pcmanager-bot.service

sleep 3
if ! curl -fsS http://127.0.0.1:8765/api/ping >/dev/null; then
  echo "Update health-check failed. Rollback from $BACKUP_PATH is required."
  sudo systemctl status pcmanager-server.service pcmanager-bot.service --no-pager || true
  exit 1
fi

sudo systemctl --no-pager status pcmanager-server.service pcmanager-bot.service
echo "Update completed successfully."
