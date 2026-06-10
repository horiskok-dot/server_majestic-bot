#!/usr/bin/env bash
set -euo pipefail
sudo systemctl start pcmanager-server.service
sudo systemctl start pcmanager-bot.service
sudo systemctl --no-pager status pcmanager-server.service pcmanager-bot.service
