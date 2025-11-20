# Decision Log — AstraSim

## D-0001 — Monorepo structure and folder layout
- **Date:** 2025-11-20
- **Context:** Need a consistent home for backend, frontend, infra, and shared services while Phase 1 scaffolding is still pending.
- **Decision:** Maintain a single monorepo rooted at `astrasim/` with top-level directories for `backend/`, `frontend/`, `infrastructure/`, `services/`, and `docs/`. Shared utilities (e.g., common models, clients) will live in `backend/shared/` or `services/` as appropriate to avoid duplication.
- **Status:** Accepted
- **Implications:** All future prompts must place assets inside this structure, update `PROJECT_MANIFEST.md`, and avoid parallel repos or duplicate folders.

## D-0002 — Phase 1 tech stack
- **Date:** 2025-11-20
- **Context:** Early clarification of the baseline stack is required so prompts across sub-phases stay aligned.
- **Decision:** Backend services use FastAPI + Python 3.11, Timescale/Postgres for time-series storage, and Next.js 14 + React 18 for the UI. Monte Carlo and analytics modules run in Python, while AI explainers integrate OpenAI/Gemini via server-side services. Infra automation targets uv for Python env management and npm/PNPM for frontend.
- **Status:** Accepted
- **Implications:** Any deviation (e.g., alternate web framework or DB) requires a new decision entry; tooling setup prompts must respect these stack choices.

## D-0003 — Backend/frontend/infra folder layout
- **Date:** 2025-11-20
- **Context:** Environment setup requires an agreed directory convention before code lands.
- **Decision:** Place backend assets in `backend/`, frontend App Router project in `frontend/`, and all container/devops artifacts in `infra/` (with nested `docker/` and configuration files). Scripts live in `scripts/`. Future prompts should extend these folders rather than creating new top-level directories.
- **Status:** Accepted
- **Implications:** Any new components (e.g., workers) must fit this tree or log a new decision.

## D-0004 — Devcontainer stack
- **Date:** 2025-11-20
- **Context:** To standardize contributor environments we need a default devcontainer configuration.
- **Decision:** Use VS Code devcontainers backed by `infra/docker-compose.yml`, targeting the backend service as the primary container. Base features install Python 3.11 and Node 20 with extensions for Python, ESLint, and Prettier. Post-create commands invoke `scripts/setup.sh`.
- **Status:** Accepted
- **Implications:** Future tooling (e.g., Timescale services) must integrate into this devcontainer or document overrides.

## D-0005 — Linting & formatting toolchain
- **Date:** 2025-11-20
- **Context:** Need consistent lint/format rules before teams add code.
- **Decision:** Backend uses Ruff (lint + format) plus Mypy for typing, run via uv/Poetry. Frontend relies on Next.js ESLint preset and Prettier; Tailwind handles styling. Shared scripts (`scripts/format.sh`) orchestrate both sides.
- **Status:** Accepted
- **Implications:** Any adoption of additional tools (e.g., Black, Biome) must be logged with rationale.

## D-0006 — Canonical infra path
- **Date:** 2025-11-20
- **Context:** Documentation previously referenced `infrastructure/` while actual assets live under `infra/`, causing confusion for contributors.
- **Decision:** Standardize on `infra/` as the canonical directory for infrastructure assets (Docker, devcontainer, DB schemas). All references and future files must use this path.
- **Status:** Accepted
- **Implications:** Any lingering `infrastructure/` references must be updated; new prompts should avoid creating parallel directories.

## D-0007 — Timescale schema v1 design
- **Date:** 2025-11-20
- **Context:** Phase 1 requires a minimal yet extensible schema before ingestion prompts begin.
- **Decision:** Adopt SQL-first migrations defining `securities`, `ohlcv_bars` hypertable, `corporate_actions`, plus `ingestion_runs` and `ingestion_errors`. Timescale hypertable chunking defaults to 7 days; ingestion tables capture run status and errors for auditing.
- **Status:** Accepted
- **Implications:** Future schema (options, regimes, factors) must build atop these tables rather than duplicating instruments or OHLCV storage; migration strategy will evolve but continues numeric SQL files for now.

## D-0008 — Backend application architecture
- **Date:** 2025-11-20
- **Context:** The backend needs a scalable structure before we add ingestion, regimes, and simulation endpoints.
- **Decision:** Standardize on a FastAPI app-factory pattern with centralized settings, logging, exception handling, versioned routers, and async DB lifecycle hooks. All future modules plug into this structure rather than creating standalone FastAPI instances.
- **Status:** Accepted
- **Implications:** New endpoints must live under versioned routers, configure dependencies via `app/api/deps`, and reuse shared middleware/hooks defined in `app/main.py`.

## D-0009 — Async DB driver choice
- **Date:** 2025-11-20
- **Context:** Need a single async driver for Timescale/Postgres connections.
- **Decision:** Use `asyncpg` with a shared connection pool managed in `app/db/connection.py`. FastAPI dependencies acquire connections via `get_db_connection`.
- **Status:** Accepted
- **Implications:** Backend code should not open ad-hoc psycopg connections; long-lived tasks must reuse the pool or extend the connection manager if special behavior is needed.

## D-0010 — Frontend application architecture
- **Date:** 2025-11-20
- **Context:** The UI needs a consistent shell before Scenario Builder and Simulation modules land.
- **Decision:** Standardize on Next.js App Router with a global layout (Navbar + optional Sidebar), shared component library under `frontend/components/`, and page-level metadata exports.
- **Status:** Accepted
- **Implications:** Future front-end prompts must plug new views/components into this structure rather than ad-hoc layouts; navigation updates run through `Navbar`.

## D-0011 — Design token and theming strategy
- **Date:** 2025-11-20
- **Context:** Need repeatable styling primitives across Scenario Builder, Dashboard, and AI narrative surfaces.
- **Decision:** Manage design tokens via Tailwind theme extensions (brand colors, radii, fonts) with supporting utilities in `app/globals.css`. Dark mode is default with planned future toggle.
- **Status:** Accepted
- **Implications:** Any new styling work should reuse the defined tokens; additional tokens require updating Tailwind config and documenting changes.

## D-0012 — CI/CD baseline architecture
- **Date:** 2025-11-20
- **Context:** Phase 1 requires automated enforcement of linting, typing, and tests before data ingestion ramps up.
- **Decision:** Use GitHub Actions workflows per stack (`ci-backend.yml`, `ci-frontend.yml`) mirroring the shared scripts. Backend uses uv for dependency management; frontend uses npm with cached installs.
- **Status:** Accepted
- **Implications:** Future pipelines (integration tests, coverage, deploy) build upon these workflows; keep scripts and CI in sync.

## D-0013 — Pre-commit policy
- **Date:** 2025-11-20
- **Context:** Need consistent contributor hygiene to avoid regressions.
- **Decision:** Adopt `.pre-commit-config.yaml` with Ruff, Mypy, Pytest, Prettier, and ESLint hooks. Setup script installs hooks by default.
- **Status:** Accepted
- **Implications:** Contributors must run `./scripts/setup.sh` (or `pre-commit install`) before committing; hook deviations require decision updates.

## D-0014 — Script-first developer experience
- **Date:** 2025-11-20
- **Context:** Reduce drift between local runs and CI.
- **Decision:** Standardize on `scripts/lint.sh`, `scripts/test.sh`, `scripts/check.sh`, `scripts/dev.sh`, and `scripts/format.sh` as canonical entrypoints. CI pipelines call these equivalents to ensure parity.
- **Status:** Accepted
- **Implications:** Any new tooling (e.g., integration tests, coverage) must extend the scripts before touching CI; documentation references scripts rather than raw commands.

## D-0015 — Async ingestion architecture
- **Date:** 2025-11-20
- **Context:** Data ingestion modules must share a consistent pattern for Polygon/corporate action feeds.
- **Decision:** Implement ingestion services as async workflows that pull data via dedicated clients, write to Timescale via asyncpg, and log results through `ingestion_runs`/`ingestion_errors`. API + CLI triggers reuse the same service functions.
- **Status:** Accepted
- **Implications:** Future ingestion modules (indices, options) should reuse this pattern for retries, logging, and DB writes.

## D-0016 — HTTP client & retry strategy
- **Date:** 2025-11-20
- **Context:** Need resilient HTTP integration with Polygon under rate limits.
- **Decision:** Standardize on `httpx.AsyncClient` with Tenacity-based exponential backoff for 429/5xx responses. Settings expose API key, base URL, and retry knobs.
- **Status:** Accepted
- **Implications:** Any new external data client should adopt the same stack; changes to retry policy require updating settings + documentation.

## D-0017 — Corporate actions ingestion architecture
- **Date:** 2025-11-20
- **Context:** Corporate actions (dividends, splits) need the same reliability, logging, and API/CLI entrypoints as OHLCV ingestion.
- **Decision:** Mirror the OHLCV ingestion structure: dedicated Polygon client, service layer handling backfill/update, DB writes to `corporate_actions`, and shared run/error logging.
- **Status:** Accepted
- **Implications:** Any future corp action extensions (adjustment factors, reconciliation) must hook into this service instead of building parallel pipelines.

## D-0018 — Polygon corporate actions endpoint strategy
- **Date:** 2025-11-20
- **Context:** Polygon exposes corporate actions through `v3/reference/dividends` & `v3/reference/splits`; we must decide on versioning & pagination plan.
- **Decision:** Use Polygon v3 reference endpoints with pagination support and store the full raw payload for auditing. Rate-limit handling uses the same tenacity exponential backoff as other clients.
- **Status:** Accepted
- **Implications:** If Polygon changes endpoints or introduces webhooks, update this client + decision log; other ingestion modules should continue using versioned APIs with normalized outputs.

## D-0019 — Index & macro ingestion architecture
- **Date:** 2025-11-20
- **Context:** Index/macro series feed regimes, calibration, and Scenario Builder context and must follow the same ingestion structure as OHLCV/corp actions.
- **Decision:** Introduce a dedicated Polygon aggregates client plus ingestion service that inserts normalized OHLCV rows into `ohlcv_bars`, auto-creates missing securities, and logs via `ingestion_runs`/`ingestion_errors`. API + CLI mirror existing patterns.
- **Status:** Accepted
- **Implications:** Future macro/index additions should plug into this service; regime logic will consume these rows without custom ingestion pathways.

## D-0020 — Polygon aggregate endpoint strategy for macro data
- **Date:** 2025-11-20
- **Context:** VIX, TNX, and sector ETFs are exposed via Polygon’s `/v2/aggs` API with pagination and optional volumes.
- **Decision:** Use Polygon aggregates for all index/macro symbols, treating missing volume as zero and storing raw payload context. Rate limits handled via Tenacity backoff consistent with other clients.
- **Status:** Accepted
- **Implications:** If Polygon offers higher-resolution feeds or webhooks later, extend the client but keep the aggregate ingestion path as the canonical source for 1d series in Phase 1.

## D-0021 — Validation architecture
- **Date:** 2025-11-20
- **Context:** We need consistent validation patterns across OHLCV, corporate actions, and index/macro series.
- **Decision:** Implement a reusable validation engine (row-level + cross-series validators) invoked via API/CLI, with results written to `reconciliation_log`.
- **Status:** Accepted
- **Implications:** Future ingestion modules (options, fundamentals) must hook into this engine; adding validators requires updating the same module.

## D-0022 — Reconciliation logging strategy
- **Date:** 2025-11-20
- **Context:** Validation/reconciliation results must be queryable historically.
- **Decision:** Store every issue in Timescale `reconciliation_log` with severity, issue_type, JSON details, FK to securities and optional ingestion run.
- **Status:** Accepted
- **Implications:** Observability dashboards and alerting can read from this table; new recon checks should log here rather than ad-hoc logs.

## D-0023 — Scheduler strategy (Phase 1)
- **Date:** 2025-11-20
- **Context:** Ingestion + validation modules now require recurring execution, but Phase 1 only needs a lightweight orchestrator.
- **Decision:** Use APScheduler’s `AsyncIOScheduler` embedded in the backend service with cron-based jobs for OHLCV, corporate actions, indexes, and validation sweeps. Manual triggers (API/CLI) reuse the same job functions.
- **Status:** Accepted
- **Implications:** Future production schedulers (e.g., Temporal/Airflow) must either replace or drive the same job functions; until then, APScheduler remains the single source of truth for scheduled jobs.

## D-0024 — Backfill manifest strategy
- **Date:** 2025-11-20
- **Context:** Operators need traceability for orchestrated multi-symbol backfills across ingestion types.
- **Decision:** Persist every orchestrated backfill in `backfill_manifest` with ingestion type, symbol, window, and status so operators can reconcile successes/failures and rerun selectively.
- **Status:** Accepted
- **Implications:** Any new orchestration workflows (options, fundamentals) must log to `backfill_manifest`; dashboards can join manifest rows with `ingestion_runs` for richer telemetry.

## D-0027 — Options schema design
- **Date:** 2025-11-20
- **Context:** SP03 introduces options ingestion and requires canonical storage patterns for raw chains, straddles, and vol surfaces.
- **Decision:** Create dedicated tables `option_chain_raw`, `option_straddles`, and `vol_surface_points` with FK references to `securities`/`ingestion_runs`, plus JSON payload columns for auditing.
- **Status:** Accepted
- **Implications:** All options-related ingestion must normalize into these tables; schema evolution (e.g., extra greeks) extends these files rather than duplicating structures.

## D-0028 — Hypertable strategy for options data
- **Date:** 2025-11-20
- **Context:** Some option datasets are point-in-time snapshots while others are time-series suitable for Timescale optimizations.
- **Decision:** Keep `option_chain_raw` as a standard table (occasional snapshots) but define `option_straddles` and `vol_surface_points` as hypertables on `snapshot_timestamp` for efficient time-series queries.
- **Status:** Accepted
- **Implications:** Future queries and aggregations should leverage hypertable functions; any additional time-series option metrics must follow the same pattern.

## D-0029 — ATM strike selection rule
- **Date:** 2025-11-20
- **Context:** Phase 1 needs a deterministic rule for choosing ATM strikes before more advanced Greeks or skew adjustments exist.
- **Decision:** Select the strike whose absolute distance to the latest underlying close is minimal, requiring both call and put legs at that strike; fall back to the nearest future expiration with at least seven days to expiry.
- **Status:** Accepted
- **Implications:** Future refinements (e.g., spread filters, skew adjustments) must build atop this baseline logic and document deviations.

## D-0030 — Phase-1 IV proxy formula
- **Date:** 2025-11-20
- **Context:** We need an implied-volatility proxy before the full surface/solver work lands later in SP03.
- **Decision:** Approximate IV as `straddle_mid / (underlying_price * sqrt(DTE/365))`, using ATM call/put mids and guarding against invalid inputs.
- **Status:** Accepted
- **Implications:** Monte Carlo calibration should treat this as provisional; a true IV solver will replace the proxy and update downstream consumers.

## D-0031 — Vol surface DTE bucketing
- **Date:** 2025-11-20
- **Context:** Phase-1 needs deterministic expirations for vol surface approximations without full calendar modeling.
- **Decision:** Standardize on fixed buckets `[7, 14, 21, 30, 45, 60]` days; per bucket select the nearest available expiration within ±5 days, otherwise skip with a WARN.
- **Status:** Accepted
- **Implications:** Future prompts can expand the bucket list or make it dynamic, but existing consumers assume this baseline ordering.

## D-0032 — Moneyness grid strategy
- **Date:** 2025-11-20
- **Context:** Need consistent strike coverage for early vol surfaces.
- **Decision:** Use fixed moneyness points `[-0.20, -0.10, -0.05, 0.0, 0.05, 0.10, 0.20]`, selecting nearest available strikes in the option chain for each grid value.
- **Status:** Accepted
- **Implications:** Later phases may introduce interpolation or skew-aware grids, but until then analytics must expect this grid ordering.

## D-0033 — Phase-1 IV approximation
- **Date:** 2025-11-20
- **Context:** Full implied volatility solvers are out of scope for SP03.
- **Decision:** Reuse the straddle IV proxy `mid / (underlying_price * sqrt(DTE/365))` for every grid point, skipping illiquid or invalid options while logging reconciliation warnings.
- **Status:** Accepted
- **Implications:** Upgrading to true IV solutions or arbitrage filters will require recalculating stored surfaces and updating this decision.

## D-0034 — Expected move definition (Phase 1)
- **Date:** 2025-11-20
- **Context:** We need a canonical definition before Monte Carlo calibration consumes options-implied signals.
- **Decision:** Use ATM straddle mid as the absolute expected move and straddle_mid / underlying as the percent move for a given horizon, with surface IV providing a secondary proxy.
- **Status:** Accepted
- **Implications:** Future prompts (SP07/SP08) must extend this definition rather than replace it; any new methodologies must reconcile with stored diagnostics.

## D-0035 — Sanity check tolerance strategy
- **Date:** 2025-11-20
- **Context:** Calibration flags require deterministic thresholds to compare options vs surface vs realized moves.
- **Decision:** Default tolerances: warn at 10%, severe at 25%, and trigger calibration flags when pct_diff exceeds configurable IV or realized tolerances (10% and 15% respectively).
- **Status:** Accepted
- **Implications:** Observability dashboards and Monte Carlo guardrails will rely on these thresholds; adjustments must be reflected in both settings and documentation.

## D-0015 — Async ingestion architecture
- **Date:** 2025-11-20
- **Context:** Data ingestion modules must share a consistent pattern for Polygon/corporate action feeds.
- **Decision:** Implement ingestion services as async workflows that pull data via dedicated clients, write to Timescale via asyncpg, and log results through `ingestion_runs`/`ingestion_errors`. API + CLI triggers reuse the same service functions.
- **Status:** Accepted
- **Implications:** Future ingestion modules (indices, options) should reuse this pattern for retries, logging, and DB writes.

## D-0016 — HTTP client & retry strategy
- **Date:** 2025-11-20
- **Context:** Need resilient HTTP integration with Polygon under rate limits.
- **Decision:** Standardize on `httpx.AsyncClient` with Tenacity-based exponential backoff for 429/5xx responses. Settings expose API key, base URL, and retry knobs.
- **Status:** Accepted
- **Implications:** Any new external data client should adopt the same stack; changes to retry policy require updating settings + documentation.

