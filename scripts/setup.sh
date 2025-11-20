#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🛠  Setting up AstraSim workspace at ${ROOT_DIR}"

echo "📦 Backend dependencies (uv sync)…"
cd "${ROOT_DIR}/backend"
if command -v uv >/dev/null 2>&1; then
  uv sync
else
  poetry install
fi

echo "📦 Frontend dependencies (npm install)…"
cd "${ROOT_DIR}/frontend"
if command -v pnpm >/dev/null 2>&1; then
  pnpm install
else
  npm install
fi

echo "🔧 Installing pre-commit hooks…"
cd "${ROOT_DIR}"
if command -v pre-commit >/dev/null 2>&1; then
  pre-commit install
else
  pip install pre-commit
  pre-commit install
fi

echo "✅ Setup complete"

