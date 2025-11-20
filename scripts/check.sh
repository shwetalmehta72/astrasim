#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"${ROOT_DIR}/scripts/lint.sh"

echo "🔠 Backend type checks (mypy)…"
cd "${ROOT_DIR}/backend"
if command -v uv >/dev/null 2>&1; then
  uv run mypy app
else
  poetry run mypy app
fi

echo "🔠 Frontend type checks (tsc)…"
cd "${ROOT_DIR}/frontend"
if command -v pnpm >/dev/null 2>&1; then
  pnpm exec tsc --noEmit
else
  npx tsc --noEmit
fi

"${ROOT_DIR}/scripts/test.sh"

echo "✅ Check pipeline complete"

