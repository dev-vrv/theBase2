#!/usr/bin/env bash
set -euo pipefail

# wait for db
bash scripts/wait-for.sh "${POSTGRES_HOST:-db}" "${POSTGRES_PORT:-5432}" 60

# Django prep
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Run server
exec gunicorn backend.wsgi:application -c /app/gunicorn.conf.py
