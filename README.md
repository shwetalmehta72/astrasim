# AstraSim

Event-driven Monte Carlo simulator for large-cap equities. Phase 1 focuses on establishing data ingestion, regimes, factor modeling, Monte Carlo with jumps, scenario UX, explainability, and exports.

## Monorepo Structure

```
backend/    # FastAPI services, analytics, Monte Carlo engine
frontend/   # Next.js App Router UI (Screener, Scenario Builder, Simulation)
infra/      # Docker + devcontainer + Timescale schema
docs/       # PRD, phase plans, meta logs, dev workflow
scripts/    # Tooling entrypoints (lint, test, check, dev)
.github/    # CI workflows
```

## Getting Started

1. Install prerequisites: Python 3.11, Node 20, uv (recommended), npm/pnpm, Docker (optional for Timescale).
2. Run the setup script:
   ```bash
   ./scripts/setup.sh
   ```
   This installs backend + frontend dependencies and registers pre-commit hooks.
3. Launch dev services:
   ```bash
   ./scripts/dev.sh
   ```

Full workflow details live in `docs/development/DEV_WORKFLOW.md`.

## Tooling Commands

| Command                | Description                                     |
| ---------------------- | ----------------------------------------------- |
| `./scripts/lint.sh`    | Ruff + ESLint + Prettier check                  |
| `./scripts/test.sh`    | Backend pytest + frontend placeholder tests     |
| `./scripts/check.sh`   | lint + mypy + tsc + tests                       |
| `./scripts/format.sh`  | Ruff format + Prettier write                    |
| `./scripts/dev.sh`     | Runs backend + frontend in watch mode           |

CI/CD mirrors these commands via GitHub Actions (`ci-backend.yml`, `ci-frontend.yml`).

## Documentation

- `docs/meta/` — Manifest, prompt log, decisions, backlog
- `docs/development/DEV_WORKFLOW.md` — Branching, scripts, CI instructions
- `docs/astrasim_phase_1_development_plan.md` — Phase roadmap
- `docs/stock_simulator_prd (2).md` — Product requirements

Always update the meta logs when structural changes occur and follow the Prompt ID workflow defined in `docs/meta/PROMPT_LOG.md`.

