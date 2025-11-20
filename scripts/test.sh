#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🧪 Backend tests (pytest)…"
cd "${ROOT_DIR}/backend"
if command -v uv >/dev/null 2>&1; then
  uv run pytest
else
  poetry run pytest
fi

echo "🧪 Frontend tests (placeholder)…"
cd "${ROOT_DIR}/frontend"
if [[ -f package.json ]]; then
  if grep -q "\"test\"" package.json; then
    if command -v pnpm >/dev/null 2>&1; then
      pnpm run test
    else
      npm run test
    fi
  else
    echo "No frontend test script defined yet – skipping."
  fi
fi

echo "✅ Tests complete"

