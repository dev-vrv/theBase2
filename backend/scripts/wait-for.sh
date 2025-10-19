#!/usr/bin/env bash
# wait-for HOST PORT [TIMEOUT]
set -euo pipefail
HOST="$1"
PORT="$2"
TIMEOUT="${3:-30}"

echo "Waiting for ${HOST}:${PORT} for up to ${TIMEOUT}s ..."
for i in $(seq 1 "${TIMEOUT}"); do
  if nc -z "${HOST}" "${PORT}" 2>/dev/null; then
    echo "${HOST}:${PORT} is available."
    exit 0
  fi
  sleep 1
done
echo "Timeout waiting for ${HOST}:${PORT}"
exit 1
