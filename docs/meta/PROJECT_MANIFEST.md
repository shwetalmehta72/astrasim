# Project Manifest — AstraSim

## Overview
AstraSim is an event-driven Monte Carlo stock simulation and forecasting platform that ties rule-based regimes, factor-driven events, and AI explainability into a calibrated GBM+jump engine. Phase 1 focuses on S&P 100 coverage, disciplined data ingestion, probabilistic calibration, and a scenario-first UX.

## Phase 1 Components
| Layer | Path | Description | Phase/Sub-Phase | Status |
| --- | --- | --- | --- | --- |
| Backend service scaffold | `backend/` | FastAPI service hosting data APIs, regime utilities, and simulation orchestration endpoints. | P1-SP01 / SP04 / SP08 | Planned |
| Frontend scaffold | `frontend/` | Next.js UI shell for screener, scenario builder, and dashboards. | P1-SP01 / SP09 | Planned |
| Data layer (Timescale schema) | `infra/db/timescale/` | Core Timescale/Postgres schema for OHLCV, options, regimes, and event metadata. | P1-SP01 / SP02 / SP03 / SP04 | Started |
| Monte Carlo engine | `backend/simulation/` | Piecewise-volatility GBM with jump injection, calibrated via impact engine. | P1-SP08 | Planned |
| UI Scenario Builder | `frontend/app/scenario-builder/` | Viewpoint sliders, T-shirt sizing controls, and event detail panels. | P1-SP09 | Planned |
| AI Narrative layer | `services/ai/` | OpenAI/Gemini explainers for stock context, scenario drivers, and distribution summaries. | P1-SP10 | Planned |

## P1-SP01 Asset Inventory
| File | Description | Phase/Sub-Phase | Status |
| --- | --- | --- | --- |
| `backend/app/main.py` | FastAPI factory with `/health` route. | P1-SP01 | Completed |
| `backend/app/api/__init__.py` | Placeholder module for future routers. | P1-SP01 | Completed |
| `backend/app/core/__init__.py` | Placeholder for config/utilities. | P1-SP01 | Completed |
| `backend/tests/test_health.py` | Pytest covering `/health` endpoint. | P1-SP01 | Completed |
| `backend/pyproject.toml` | Poetry project + tooling config. | P1-SP01 | Completed |
| `backend/ruff.toml` | Ruff lint preset. | P1-SP01 | Completed |
| `backend/mypy.ini` | Mypy strict typing config. | P1-SP01 | Completed |
| `backend/.env.example` | Backend environment template. | P1-SP01 | Completed |
| `backend/README.md` | Backend setup & commands. | P1-SP01 | Completed |
| `frontend/package.json` | Next.js package definition. | P1-SP01 | Completed |
| `frontend/app/layout.tsx` | Root layout with metadata + Tailwind wiring. | P1-SP01 | Completed |
| `frontend/app/page.tsx` | Placeholder landing page. | P1-SP01 | Completed |
| `frontend/app/globals.css` | Tailwind base styles. | P1-SP01 | Completed |
| `frontend/tailwind.config.js` | Tailwind theme config. | P1-SP01 | Completed |
| `frontend/postcss.config.js` | PostCSS pipeline definition. | P1-SP01 | Completed |
| `frontend/tsconfig.json` | TS config tuned for Next. | P1-SP01 | Completed |
| `frontend/README.md` | Frontend setup & commands. | P1-SP01 | Completed |
| `infra/docker/backend/Dockerfile` | Dev Dockerfile for FastAPI. | P1-SP01 | Completed |
| `infra/docker/frontend/Dockerfile` | Dev Dockerfile for Next.js. | P1-SP01 | Completed |
| `infra/docker-compose.yml` | Compose stack for dev services. | P1-SP01 | Completed |
| `infra/devcontainer.json` | VS Code devcontainer definition. | P1-SP01 | Completed |
| `scripts/setup.sh` | Workspace bootstrap script. | P1-SP01 | Completed |
| `scripts/dev.sh` | Concurrent backend/frontend launcher. | P1-SP01 | Completed |
| `scripts/format.sh` | Formatting + lint helper. | P1-SP01 | Completed |
| `infra/db/timescale/README.md` | Documentation for schema layout and init workflow. | P1-SP01 | Completed |
| `infra/db/timescale/schema/001_base_schema.sql` | Timescale extension, securities, OHLCV hypertable, corporate actions. | P1-SP01 | Completed |
| `infra/db/timescale/schema/002_ingestion_logging.sql` | Ingestion runs and error tracking tables. | P1-SP01 | Completed |
| `backend/app/core/config.py` | Centralized Pydantic settings for app + DB. | P1-SP01 | Completed |
| `backend/app/core/logging.py` | Logging configuration + middleware. | P1-SP01 | Completed |
| `backend/app/core/exceptions.py` | Structured FastAPI exception handlers. | P1-SP01 | Completed |
| `backend/app/db/connection.py` | Asyncpg connection pool management. | P1-SP01 | Completed |
| `backend/app/db/deps.py` | FastAPI dependency for DB connections. | P1-SP01 | Completed |
| `backend/app/api/v1/__init__.py` | API v1 router assembly. | P1-SP01 | Completed |
| `backend/app/api/v1/routes/health.py` | API v1 health + DB readiness endpoints. | P1-SP01 | Completed |
| `backend/app/api/v1/routes/meta.py` | API v1 meta/info endpoint. | P1-SP01 | Completed |
| `backend/app/api/v1/routes/__init__.py` | Package marker for v1 routes. | P1-SP01 | Completed |
| `backend/app/main.py` | FastAPI app factory with CORS, logging, DB lifecycle. | P1-SP01 | Completed |
| `backend/app/api/deps/__init__.py` | Placeholder for shared API dependencies. | P1-SP01 | Completed |
| `backend/app/services/__init__.py` | Placeholder for future services. | P1-SP01 | Completed |
| `backend/tests/conftest.py` | Shared pytest fixtures for backend app. | P1-SP01 | Completed |
| `backend/tests/test_app_health.py` | Tests for health and database readiness endpoints. | P1-SP01 | Completed |
| `backend/tests/test_app_meta.py` | Tests for metadata endpoint responses. | P1-SP01 | Completed |
| `backend/tests/test_db_dependency.py` | Unit tests for DB dependency generator. | P1-SP01 | Completed |
| `frontend/components/Navbar.tsx` | Persistent top navigation for the UI shell. | P1-SP01 | Completed |
| `frontend/components/Sidebar.tsx` | Placeholder sidebar for dashboard contexts. | P1-SP01 | Completed |
| `frontend/components/Card.tsx` | Reusable card component for panels. | P1-SP01 | Completed |
| `frontend/components/Container.tsx` | Max-width wrapper to center content. | P1-SP01 | Completed |
| `frontend/components/PageHeader.tsx` | Standardized title/subtitle block. | P1-SP01 | Completed |
| `frontend/app/screener/page.tsx` | Placeholder S&P 100 screener route. | P1-SP01 | Completed |
| `frontend/app/stock/[symbol]/page.tsx` | Dynamic stock overview placeholder. | P1-SP01 | Completed |
| `frontend/app/scenario-builder/page.tsx` | Placeholder Scenario Builder view. | P1-SP01 | Completed |
| `frontend/app/simulation/page.tsx` | Placeholder Simulation dashboard. | P1-SP01 | Completed |
| `.github/workflows/ci-backend.yml` | Backend lint/type/test CI workflow. | P1-SP01 | Completed |
| `.github/workflows/ci-frontend.yml` | Frontend lint/type/build CI workflow. | P1-SP01 | Completed |
| `.pre-commit-config.yaml` | Repo-wide hook definitions. | P1-SP01 | Completed |
| `.vscode/extensions.json` | Recommended VSCode extensions. | P1-SP01 | Completed |
| `.vscode/settings.json` | Workspace settings for lint/format. | P1-SP01 | Completed |
| `scripts/lint.sh` | Unified lint entrypoint. | P1-SP01 | Completed |
| `scripts/test.sh` | Unified test entrypoint. | P1-SP01 | Completed |
| `scripts/check.sh` | Meta pipeline (lint+type+tests). | P1-SP01 | Completed |
| `README.md` | Root project overview + tooling. | P1-SP01 | Completed |
| `docs/development/DEV_WORKFLOW.md` | Developer workflow guide. | P1-SP01 | Completed |
| `backend/app/clients/polygon.py` | Polygon OHLCV client wrapper. | P1-SP02 | Completed |
| `backend/app/services/ingestion/ohlcv.py` | OHLCV ingestion service (backfill/update). | P1-SP02 | Completed |
| `backend/app/api/v1/routes/ingestion.py` | API routes for triggering ingestion. | P1-SP02 | Completed |
| `backend/app/cli/run_ingestion.py` | CLI entrypoint for OHLCV ingestion. | P1-SP02 | Completed |
| `backend/tests/test_polygon_client.py` | Tests for Polygon client behavior. | P1-SP02 | Completed |
| `backend/tests/test_ohlcv_ingestion.py` | Tests for ingestion workflow & logging. | P1-SP02 | Completed |
| `backend/tests/test_ingestion_api.py` | Tests for ingestion API endpoints. | P1-SP02 | Completed |
| `backend/app/clients/polygon_corp_actions.py` | Polygon dividends & splits client. | P1-SP02 | Completed |
| `backend/app/services/ingestion/corp_actions.py` | Corporate actions ingestion service. | P1-SP02 | Completed |
| `backend/app/api/v1/routes/corp_actions_ingestion.py` | API routes for corporate actions ingestion. | P1-SP02 | Completed |
| `backend/app/cli/run_corp_actions_ingestion.py` | CLI runner for corporate actions ingestion. | P1-SP02 | Completed |
| `backend/tests/test_polygon_corp_actions_client.py` | Tests for corporate actions client. | P1-SP02 | Completed |
| `backend/tests/test_corp_actions_ingestion.py` | Tests for corporate actions ingestion workflow. | P1-SP02 | Completed |
| `backend/tests/test_corp_actions_ingestion_api.py` | Tests for corporate actions ingestion API. | P1-SP02 | Completed |
| `backend/app/clients/polygon_indexes.py` | Polygon aggregates client for indexes/macros. | P1-SP02 | Completed |
| `backend/app/services/ingestion/indexes.py` | Index & macro series ingestion service. | P1-SP02 | Completed |
| `backend/app/api/v1/routes/indexes_ingestion.py` | API routes for index/macro ingestion. | P1-SP02 | Completed |
| `backend/app/cli/run_indexes_ingestion.py` | CLI runner for index/macro ingestion. | P1-SP02 | Completed |
| `backend/tests/test_polygon_indexes_client.py` | Tests for index client. | P1-SP02 | Completed |
| `backend/tests/test_indexes_ingestion.py` | Tests for index ingestion workflow. | P1-SP02 | Completed |
| `backend/tests/test_indexes_ingestion_api.py` | Tests for index ingestion API. | P1-SP02 | Completed |
| `infra/db/timescale/schema/003_reconciliation_log.sql` | Reconciliation log table for validation issues. | P1-SP02 | Completed |
| `backend/app/services/validation/validators.py` | Validation rules (missing timestamps, price anomalies, etc.). | P1-SP02 | Completed |
| `backend/app/services/validation/reconciliation.py` | Reconciliation orchestrator writing to `reconciliation_log`. | P1-SP02 | Completed |
| `backend/app/api/v1/routes/validation.py` | API routes for validation/reconciliation. | P1-SP02 | Completed |
| `backend/app/cli/run_validation.py` | CLI entrypoint for validation runs. | P1-SP02 | Completed |
| `backend/app/cli/run_reconciliation.py` | CLI entrypoint for reconciliation runs. | P1-SP02 | Completed |
| `backend/tests/test_validation_engine.py` | Unit tests for validator functions. | P1-SP02 | Completed |
| `backend/tests/test_reconciliation_engine.py` | Tests for reconciliation logging. | P1-SP02 | Completed |
| `infra/db/timescale/schema/004_backfill_manifest.sql` | Backfill manifest table for orchestrated jobs. | P1-SP02 | Completed |
| `backend/app/services/scheduler/scheduler.py` | Async scheduler registration + lifecycle. | P1-SP02 | Completed |
| `backend/app/services/scheduler/backfill.py` | Backfill orchestrator writing manifest rows. | P1-SP02 | Completed |
| `backend/app/services/scheduler/jobs.py` | Scheduled job definitions for ingestion + validation. | P1-SP02 | Completed |
| `backend/app/api/v1/routes/scheduler.py` | API routes for scheduler status, manual runs, and backfills. | P1-SP02 | Completed |
| `backend/app/cli/run_scheduler.py` | CLI to launch the background scheduler loop. | P1-SP02 | Completed |
| `backend/app/cli/run_backfill.py` | CLI to trigger orchestrated backfills. | P1-SP02 | Completed |
| `backend/tests/test_backfill_orchestration.py` | Tests covering manifest writes + orchestration summaries. | P1-SP02 | Completed |
| `backend/tests/test_scheduler_registration.py` | Tests ensuring scheduler registers all required jobs. | P1-SP02 | Completed |
| `backend/tests/test_scheduler_jobs.py` | Tests verifying scheduler jobs call ingestion/validation hooks. | P1-SP02 | Completed |
| `backend/tests/test_scheduler_api.py` | Tests for scheduler API endpoints. | P1-SP02 | Completed |
| `infra/db/timescale/schema/005_option_chain_raw.sql` | Raw option chain snapshots. | P1-SP03 | Completed |
| `infra/db/timescale/schema/006_option_straddles.sql` | Hypertable for normalized ATM straddles. | P1-SP03 | Completed |
| `infra/db/timescale/schema/007_vol_surface_points.sql` | Hypertable for vol surface points. | P1-SP03 | Completed |
| `backend/app/core/config.py` | Settings extended with OPTIONS_SCHEMA_VERSION. | P1-SP03 | Completed |
| `backend/.env.example` | Added POLYGON_OPTIONS_API_KEY placeholder. | P1-SP03 | Completed |
| `backend/app/clients/polygon_options.py` | Polygon v3 options client for chain + expiration data. | P1-SP03 | Completed |
| `backend/app/services/options/atm_straddle.py` | ATM straddle ingestion + normalization pipeline. | P1-SP03 | Completed |
| `backend/app/api/v1/routes/atm_straddles.py` | API endpoints for ingesting and listing ATM straddles. | P1-SP03 | Completed |
| `backend/app/cli/run_atm_straddle_ingestion.py` | CLI entrypoint for ATM straddle ingestion. | P1-SP03 | Completed |
| `backend/tests/test_polygon_options_client.py` | Unit tests for Polygon options client normalization. | P1-SP03 | Completed |
| `backend/tests/test_atm_straddle_service.py` | Tests for ATM straddle service logic + persistence. | P1-SP03 | Completed |
| `backend/tests/test_atm_straddle_api.py` | API tests covering ingest + listing endpoints. | P1-SP03 | Completed |
| `backend/tests/test_atm_straddle_cli.py` | Tests for ATM straddle CLI wiring. | P1-SP03 | Completed |
| `backend/app/services/options/vol_surface.py` | Vol surface approximation engine (DTE buckets × moneyness grid). | P1-SP03 | Completed |
| `backend/app/api/v1/routes/vol_surface.py` | API endpoints for computing and retrieving vol surfaces. | P1-SP03 | Completed |
| `backend/app/cli/run_vol_surface.py` | CLI entrypoint for vol surface computation. | P1-SP03 | Completed |
| `backend/tests/test_vol_surface_service.py` | Tests for vol surface computation + persistence. | P1-SP03 | Completed |
| `backend/tests/test_vol_surface_api.py` | Tests for vol surface API routes. | P1-SP03 | Completed |
| `backend/tests/test_vol_surface_cli.py` | Tests for vol surface CLI wiring. | P1-SP03 | Completed |
| `backend/tests/test_vol_surface_client_helpers.py` | Tests for Polygon options helper functions. | P1-SP03 | Completed |

_Last updated: 2025-11-20_

