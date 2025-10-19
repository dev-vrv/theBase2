#!/usr/bin/env bash
set -euo pipefail

# usage: ./deploy.sh user@server:/path/to/app

TARGET="${1:-}"

if [ -z "$TARGET" ]; then
  echo "Usage: $0 user@server:/var/www/thebase"
  exit 1
fi

# upload (rsync preserves perms and is efficient)
HOST="${TARGET%%:*}"
REMOTE_DIR="${TARGET#*:}"

if [ -z "$HOST" ] || [ -z "$REMOTE_DIR" ] || [ "$HOST" = "$REMOTE_DIR" ]; then
  echo "Invalid target. Expected format user@server:/path/to/app"
  exit 1
fi

rsync -az --delete \
  --exclude '.venv' \
  --exclude '.git' \
  --exclude '__pycache__' \
  ./ "${HOST}:${REMOTE_DIR}/"

# remote deploy
ssh "$HOST" bash -s -- "$REMOTE_DIR" <<'SSH'
set -e

APP_DIR="$1"

cd "$APP_DIR"

docker compose pull || true
docker compose build
docker compose up -d
docker compose exec web python manage.py migrate --noinput
docker compose exec web python manage.py collectstatic --noinput
docker compose ps
SSH
