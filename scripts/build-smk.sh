#!/usr/bin/env bash
# Rebuild SMK React app into react-pages/smk/build/
set -euo pipefail
cd "$(dirname "$0")/../react-pages/smk"

if ! command -v npm >/dev/null 2>&1; then
  echo "Install Node.js: https://nodejs.org/"
  exit 1
fi

[[ -d node_modules ]] || npm install
npm run build

echo "Done. Commit react-pages/smk/build/ then push."
