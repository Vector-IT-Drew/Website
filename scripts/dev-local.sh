#!/usr/bin/env bash
# Fastest loop: no Docker. Flask debug reload on file save.
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ ! -d venv ]]; then
  echo "Creating venv..."
  python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt

echo "Starting Flask (debug) at http://127.0.0.1:5005 — Ctrl+C to stop"
echo "Edits to .py / templates reload automatically."
export FLASK_APP=app.py
python main.py
