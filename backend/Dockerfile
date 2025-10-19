# ---- build stage (deterministic) ----
FROM python:3.11.9-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VIRTUALENVS_CREATE=false

# system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc netcat-openbsd curl \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# workdir
WORKDIR /app

# copy requirements early for caching
COPY requirements.txt /app/requirements.txt

# pin pip
RUN python -m pip install --upgrade pip==24.2

# install python deps
RUN pip install -r /app/requirements.txt

# copy project
COPY . /app

# create runtime dirs
RUN mkdir -p /app/staticfiles /app/media /app/logs

# environment (default overridable by .env)
ENV DJANGO_SETTINGS_MODULE=backend.settings \
    GUNICORN_WORKERS=3 \
    GUNICORN_TIMEOUT=30

# gunicorn config file lives at /app/gunicorn.conf.py
EXPOSE 8000

# entrypoint handles migrations/collectstatic/launch
ENTRYPOINT ["bash", "scripts/entrypoint.sh"]
