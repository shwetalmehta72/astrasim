# Task Backlog — AstraSim

| Task ID | Related Prompt | Description | Priority | Status |
| --- | --- | --- | --- | --- |
| T-1001 | P1-SP02-PR02 | Model and implement the initial Timescale/Postgres schema for OHLCV, indices, and corp actions. | High | Completed |
| T-1002 | P1-SP02-PR02 | Build corporate actions ingestion pipeline. | High | Completed |
| T-1003 | P1-SP04-PR02 | Implement volatility & trend regime detection utilities and persistence. | High | Not Started |
| T-1004 | P1-SP08-PR01 | Scaffold the Monte Carlo engine module with piecewise volatility controls. | High | Not Started |
| T-1005 | P1-SP09-PR03 | Deliver Scenario Builder UI shell with viewpoint sliders and T-shirt sizing. | Medium | Not Started |
| T-1006 | P1-SP10-PR01 | Create AI narrative service that summarizes stock context and drivers. | Medium | Not Started |
| T-1007 | P1-SP01-PR02 | Implement Timescale DB schema bootstrap inside infra automation. | High | Completed |
| T-1008 | P1-SP01-PR05 | Add CI/CD pipeline (lint, test, build) for backend & frontend. | High | Completed |
| T-1009 | P1-SP01-PR05 | Add dedicated backend test harness workflow (pytest, coverage). | Medium | Completed |
| T-1010 | P1-SP01-PR05 | Add frontend test harness (Playwright / Vitest) scaffolding. | Medium | Not Started |
| T-1011 | P1-SP01-PR06 | Improve Docker dev performance (caching, mount optimizations). | Low | Not Started |
| T-1012 | P1-SP03-PR02 | Design options/IV schema tables (straddles, surfaces, normalization). | High | Not Started |
| T-1013 | P1-SP04-PR01 | Define regime/event/factor schema (states, dependencies, storage). | High | Not Started |
| T-1014 | P1-SP01-PR07 | Establish migration/versioning strategy beyond init scripts (e.g., Alembic or Sqitch). | Medium | Not Started |
| T-1015 | P1-SP01-PR08 | Add structured logging with correlation/trace IDs per request. | Medium | Not Started |
| T-1016 | P1-SP01-PR09 | Integrate backend observability (Prometheus/OpenTelemetry metrics). | Medium | Not Started |
| T-1017 | P1-SP01-PR04 | Implement dark/light mode switcher for the frontend shell. | Medium | Not Started |
| T-1018 | P1-SP01-PR04 | Add skeleton loaders and shimmer components for pending data states. | Medium | Not Started |
| T-1019 | P1-SP01-PR04 | Build shared chart container wrappers for Simulation dashboards. | Medium | Not Started |
| T-1020 | P1-SP01-PR05 | Add backend integration test suite (services + DB). | Medium | Not Started |
| T-1021 | P1-SP01-PR05 | Add frontend Playwright/Vitest test coverage. | Medium | Not Started |
| T-1022 | P1-SP01-PR05 | Enable coverage reporting + upload in CI. | Medium | Not Started |
| T-1026 | P1-SP02-PR02 | Generate adjustment factors combining splits/dividends for price restatement. | Medium | Not Started |
| T-1027 | P1-SP02-PR02 | Corporate actions data reconciliation & alerting. | Medium | Not Started |
| T-1028 | P1-SP02-PR02 | Optimize corporate actions ingestion batching/performance. | Low | Not Started |
| T-1029 | P1-SP02-PR03 | Define index vs equity reconciliation rules (beta alignment). | Medium | Not Started |
| T-1030 | P1-SP02-PR03 | Build macro-series smoothing utilities for regime detection. | Medium | Not Started |
| T-1031 | P1-SP02-PR03 | Implement missing-day interpolation for indexes/macros. | Medium | Not Started |
| T-1032 | P1-SP02-PR04 | Advanced statistical outlier detection (z-score, EWMA bands). | Medium | Not Started |
| T-1033 | P1-SP02-PR04 | Multi-symbol temporal validation (cross-asset anomalies). | Medium | Not Started |
| T-1034 | P1-SP02-PR04 | Corporate-action-driven price adjustment sanity checker. | Medium | Not Started |
| T-1023 | P1-SP02-PR04 | Implement OHLCV reconciliation + validation alerts. | Medium | Not Started |
| T-1024 | P1-SP02-PR05 | Emit ingestion metrics to Prometheus/OpenTelemetry. | Medium | Not Started |
| T-1025 | P1-SP02-PR06 | Provide batch aggregation helpers (1m → 5m, etc.). | Medium | Not Started |
| T-1035 | P1-SP02-PR05 | Plan production-grade scheduler orchestration (Temporal/Airflow). | Medium | Not Started |
| T-1036 | P1-SP02-PR05 | Add parallel ingestion batching for orchestrated backfills. | Medium | Not Started |
| T-1037 | P1-SP02-PR05 | Publish scheduler/backfill metrics to Prometheus/OpenTelemetry. | Medium | Not Started |

_Add tasks as new needs emerge; keep IDs sequential._

