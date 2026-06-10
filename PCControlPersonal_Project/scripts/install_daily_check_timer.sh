#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/pc/PCControlPersonal_Project"
chmod +x "$PROJECT_DIR/scripts/server_daily_self_check.sh"
sudo cp "$PROJECT_DIR/systemd/pcmanager-daily-check.service" /etc/systemd/system/
sudo cp "$PROJECT_DIR/systemd/pcmanager-daily-check.timer" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now pcmanager-daily-check.timer
systemctl list-timers | grep pcmanager-daily-check || true
sudo systemctl status pcmanager-daily-check.timer --no-pager
