#!/usr/bin/env bash
set -euo pipefail
sudo systemctl stop pcmanager-bot.service || true
sudo systemctl stop pcmanager-server.service || true
