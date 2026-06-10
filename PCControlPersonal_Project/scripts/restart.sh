#!/usr/bin/env bash
set -euo pipefail
sudo systemctl restart pcmanager-server.service
sudo systemctl restart pcmanager-bot.service
sudo systemctl --no-pager status pcmanager-server.service pcmanager-bot.service
