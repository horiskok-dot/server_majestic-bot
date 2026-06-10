#!/usr/bin/env bash
set -euo pipefail
sudo systemctl --no-pager status pcmanager-server.service pcmanager-bot.service
