#!/usr/bin/env bash
set -euo pipefail

# If a command is provided, optionally wait for DB for manage.py and execute it
if [ "$#" -gt 0 ]; then
  if [ "$1" = "python" ] || [ "$1" = "manage.py" ] || [ "$1" = "bash" ] || [ "$1" = "sh" ] || [ "$1" = "pip" ]; then
    if [ "$1" = "manage.py" ] || { [ "$1" = "python" ] && [ "${2:-}" = "manage.py" ]; }; then
      bash scripts/wait-for.sh "${POSTGRES_HOST:-db}" "${POSTGRES_PORT:-5432}" 60
    fi
    exec "$@"
  fi
fi

# Default path: wait for DB, run migrations and collectstatic, then start Gunicorn
bash scripts/wait-for.sh "${POSTGRES_HOST:-db}" "${POSTGRES_PORT:-5432}" 60
python manage.py migrate --noinput
python manage.py collectstatic --noinput
exec gunicorn backend.wsgi:application -c /app/gunicorn.conf.py
