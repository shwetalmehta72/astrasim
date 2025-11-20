# AstraSim Backend

FastAPI service powering the AstraSim event-driven Monte Carlo simulator. This package provides the API surface for data ingestion, regime detection, factor modeling, and simulation orchestration.

## Requirements

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) for dependency management (recommended) or Poetry

## Setup

```powershell
# PowerShell
cd backend
uv sync
```

```bash
# Bash / Git Bash / WSL
cd backend
uv sync
```

This will create a virtual environment under `.venv/` and install all dependencies.

## Running the app

```bash
uv run uvicorn app.main:app --reload
```

Visit <http://localhost:8000/health> to confirm the service is up.

## Linting & Tests

Use the shared scripts from the repository root:

```bash
./scripts/lint.sh    # Ruff lint + ESLint
./scripts/test.sh    # Pytest (frontend tests later)
./scripts/check.sh   # Lint + type checks + tests
```

Or run individual commands:

```bash
uv run ruff check .
uv run mypy app
uv run pytest
```

## CI/CD

GitHub Actions (`.github/workflows/ci-backend.yml`) mirrors the `scripts/check.sh` pipeline: install via uv, run Ruff, Mypy, and Pytest on every push/PR.

## Environment Variables

Copy `.env.example` to `.env` and fill in secrets such as `OPENAI_API_KEY` and `DATABASE_URL`. Never commit `.env` files.

