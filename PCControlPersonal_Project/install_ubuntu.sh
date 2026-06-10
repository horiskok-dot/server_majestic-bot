#!/usr/bin/env bash
set -euo pipefail

if ! command -v apt-get >/dev/null 2>&1; then
  echo "This installer supports Ubuntu/Debian only." >&2
  exit 1
fi

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root: sudo bash install_ubuntu.sh" >&2
  exit 1
fi

PROJECT_SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

apt-get update
apt-get install -y python3 python3-venv python3-pip git curl rsync

if ! id pcmanager >/dev/null 2>&1; then
  useradd --system --home /opt/pcmanager --shell /usr/sbin/nologin pcmanager
fi

mkdir -p /opt/pcmanager /etc/pcmanager /var/log/pcmanager /var/lib/pcmanager /var/lib/pcmanager/backups
mkdir -p /var/lib/pcmanager/storage/uploads /var/lib/pcmanager/storage/photos /var/lib/pcmanager/storage/screenshots /var/lib/pcmanager/storage/videos /var/lib/pcmanager/storage/telegram_files /var/lib/pcmanager/storage/temp
mkdir -p /var/lib/pcmanager/storage/screenshots/server /var/lib/pcmanager/storage/screenshots/agents
mkdir -p /var/lib/pcmanager/storage/photos/server_webcam /var/lib/pcmanager/storage/photos/agents_camera
mkdir -p /var/lib/pcmanager/storage/videos/server_webcam /var/lib/pcmanager/storage/videos/agents_camera
rsync -a --delete \
  --exclude "android-app/.gradle" \
  --exclude "android-app/app/build" \
  --exclude "backend/.env" \
  --exclude ".env" \
  --exclude "backend/data" \
  --exclude "backend/logs" \
  "$PROJECT_SRC/" /opt/pcmanager/

python3 -m venv /opt/pcmanager/venv
/opt/pcmanager/venv/bin/python -m pip install --upgrade pip
/opt/pcmanager/venv/bin/python -m pip install -r /opt/pcmanager/requirements.txt

if [ ! -f /etc/pcmanager/pcmanager.env ]; then
  cp /opt/pcmanager/.env.example /etc/pcmanager/pcmanager.env
  chmod 640 /etc/pcmanager/pcmanager.env
fi

if [ ! -f /etc/pcmanager/config.json ]; then
  cp /opt/pcmanager/config.example.json /etc/pcmanager/config.json
  chmod 640 /etc/pcmanager/config.json
fi

cp /opt/pcmanager/systemd/pcmanager-server.service /etc/systemd/system/pcmanager-server.service
cp /opt/pcmanager/systemd/pcmanager-bot.service /etc/systemd/system/pcmanager-bot.service

chown -R pcmanager:pcmanager /opt/pcmanager /etc/pcmanager /var/log/pcmanager /var/lib/pcmanager
chmod +x /opt/pcmanager/scripts/*.sh

systemctl daemon-reload
systemctl enable pcmanager-server.service pcmanager-bot.service
systemctl restart pcmanager-server.service
systemctl restart pcmanager-bot.service

echo "Installed. Edit /etc/pcmanager/pcmanager.env, then run: sudo systemctl restart pcmanager-server pcmanager-bot"
