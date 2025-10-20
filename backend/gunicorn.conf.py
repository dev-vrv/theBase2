import multiprocessing
import os

bind = "0.0.0.0:8000"

# From env or sensible defaults
_env_workers = os.getenv("GUNICORN_WORKERS")
workers = int(_env_workers) if _env_workers and _env_workers.isdigit() else min(4, max(2, multiprocessing.cpu_count()))
timeout = int(os.getenv("GUNICORN_TIMEOUT", 30))
worker_class = "sync"

# Log to stdout/stderr so `docker logs` shows output
accesslog = "-"
errorlog = "-"
capture_output = True
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")

graceful_timeout = 30
keepalive = 5
