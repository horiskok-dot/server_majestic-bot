#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/home/pc/PCControlPersonal_Project}"

chmod +x "$PROJECT_DIR/scripts/local_check.sh"
sudo cp "$PROJECT_DIR/systemd/pcmanager-local-check.service" /etc/systemd/system/
sudo cp "$PROJECT_DIR/systemd/pcmanager-local-check.timer" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now pcmanager-local-check.timer
systemctl list-timers | grep pcmanager-local-check || true
sudo systemctl status pcmanager-local-check.timer --no-pager
