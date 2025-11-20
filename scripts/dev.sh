#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

terminate() {
  echo "Stopping dev processes…"
  pkill -P $1 || true
}

trap 'terminate $$' INT TERM

echo "🚀 Starting backend (FastAPI)…"
(
  cd "${ROOT_DIR}/backend"
  if command -v uv >/dev/null 2>&1; then
    uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  else
    poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  fi
) &

BACKEND_PID=$!

echo "🌐 Starting frontend (Next.js)…"
(
  cd "${ROOT_DIR}/frontend"
  if command -v pnpm >/dev/null 2>&1; then
    pnpm run dev
  else
    npm run dev
  fi
) &

FRONTEND_PID=$!

wait "${BACKEND_PID}" "${FRONTEND_PID}"

