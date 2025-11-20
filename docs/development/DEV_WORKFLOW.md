# AstraSim Developer Workflow

## Branching & Prompts

- Every chunk of work is tied to a Prompt ID (e.g., `P1-SP01-PR05`). Reference the ID in PR titles, commits, and documentation.
- Use short-lived feature branches named after the prompt (e.g., `feature/P1-SP01-PR05`).
- Update meta files (`docs/meta/PROJECT_MANIFEST.md`, `PROMPT_LOG.md`, `DECISION_LOG.md`, `TASK_BACKLOG.md`) before opening a PR.

## Local Setup

```bash
./scripts/setup.sh   # installs backend (uv) + frontend (npm) deps and pre-commit hooks
```

The script expects Python 3.11, Node 20, uv (or Poetry fallback), and npm/pnpm on your PATH.

## Day-to-Day Commands

| Command               | Description                                            |
| --------------------- | ------------------------------------------------------ |
| `./scripts/dev.sh`    | Runs FastAPI + Next.js dev servers                     |
| `./scripts/lint.sh`   | Ruff lint + ESLint + Prettier checks                   |
| `./scripts/test.sh`   | Backend pytest + (future) frontend tests               |
| `./scripts/check.sh`  | Lint + mypy + tsc + pytest                             |
| `./scripts/format.sh` | Ruff format + Prettier write                           |

These scripts mirror the CI pipeline; run `./scripts/check.sh` before pushing.

## Pre-commit Hooks

Install via `scripts/setup.sh` or manually with `pre-commit install`. Hooks run:
- Ruff lint/format on backend
- Mypy
- Backend pytest
- Prettier + ESLint on frontend

Commit only passes when hooks succeed. To skip temporarily (not recommended), use `SKIP=hookname git commit ...`.

## GitHub Actions

- `.github/workflows/ci-backend.yml` runs uv + Ruff + Mypy + Pytest.
- `.github/workflows/ci-frontend.yml` runs npm install + ESLint + Prettier check + `tsc --noEmit` + `next build`.
- Both trigger on pushes/PRs to `main`.

Monitor workflow logs under the “Actions” tab. Fix failures locally using the scripts above.

## Optional: Run CI Locally with `act`

```bash
brew install act   # or use Docker
act push -j backend
act push -j frontend
```

Requires Docker. Use this to validate workflow changes before pushing.

## Commit Hygiene

- Use descriptive commits tied to the prompt (e.g., `P1-SP01-PR05: add backend CI workflow`).
- Avoid committing generated assets or `.env` files.
- Ensure VSCode settings and `.pre-commit-config.yaml` stay in sync with actual tooling versions.

## Support & Questions
- ## Manual data ingestion checks

- OHLCV: `python -m app.cli.run_ingestion backfill AAPL 2023-01-01 2023-01-31`
- Corporate actions: `python -m app.cli.run_corp_actions_ingestion update AAPL`

These hit live Polygon + Timescale instances; ensure `POLYGON_API_KEY` and database services are running first.


- For architecture decisions, consult `docs/meta/DECISION_LOG.md`.
- For upcoming work, check `docs/meta/TASK_BACKLOG.md`.
- If tooling fails, update the relevant scripts and documentation, then log the change in the manifest.

