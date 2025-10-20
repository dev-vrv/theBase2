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

# Ensure images are up-to-date
docker compose pull || true
docker compose build

# Start database first
docker compose up -d db

# Wait for DB using the web image's script (has netcat)
docker compose run --rm web bash scripts/wait-for.sh "${POSTGRES_HOST:-db}" "${POSTGRES_PORT:-5432}" 60

# Run migrations and collect static assets
docker compose run --rm web python manage.py migrate --noinput
docker compose run --rm web python manage.py collectstatic --noinput

# Start application stack (web runs via Gunicorn inside container)
docker compose up -d web nginx

docker compose ps
