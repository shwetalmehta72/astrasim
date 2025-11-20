#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🧹 Backend lint (ruff)…"
cd "${ROOT_DIR}/backend"
if command -v uv >/dev/null 2>&1; then
  uv run ruff check .
else
  poetry run ruff check .
fi

echo "🔍 Frontend lint (eslint)…"
cd "${ROOT_DIR}/frontend"
if command -v pnpm >/dev/null 2>&1; then
  pnpm run lint
else
  npm run lint
fi

echo "💅 Prettier check…"
if command -v pnpm >/dev/null 2>&1; then
  pnpm exec prettier --check .
else
  npx prettier --check .
fi

echo "✅ Lint complete"

