#!/usr/bin/env bash
# Run the Website locally in Docker (same image Railway uses).
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v docker >/dev/null 2>&1; then
  echo "Install Docker Desktop: https://www.docker.com/products/docker-desktop/"
  exit 1
fi

echo "Building image..."
docker build -t vector-website:local .

echo "Starting on http://127.0.0.1:5005"
EXTRA_ARGS=()
if [[ -f .env ]]; then
  EXTRA_ARGS+=(--env-file .env)
fi

docker run --rm -p 5005:8080 \
  -e PORT=8080 \
  -e SESSION_SECRET=local-dev-secret \
  "${EXTRA_ARGS[@]}" \
  vector-website:local
