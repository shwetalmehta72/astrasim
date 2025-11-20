#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "✨ Formatting backend code…"
cd "${ROOT_DIR}/backend"
if command -v uv >/dev/null 2>&1; then
  uv run ruff format .
else
  poetry run ruff format .
fi

echo "🎨 Formatting frontend code…"
cd "${ROOT_DIR}/frontend"
if command -v pnpm >/dev/null 2>&1; then
  pnpm run format
else
  npm run format
fi

echo "✅ Formatting complete"

