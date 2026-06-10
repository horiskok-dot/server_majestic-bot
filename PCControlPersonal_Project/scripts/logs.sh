#!/usr/bin/env bash
set -euo pipefail
sudo journalctl -u pcmanager-server.service -u pcmanager-bot.service -f
