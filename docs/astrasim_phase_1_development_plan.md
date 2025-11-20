# AstraSim Phase 1 Development Plan
## High-Level Structure with 10 Sub‑Phases (Each Containing 5 Prompts)

This document outlines the structured development plan for **Phase 1** of AstraSim, broken into **10 sub‑phases**, each containing **five prompt modules** that we will later refine in depth. The purpose is to provide a clear, end‑to‑end roadmap that moves from environment setup to a fully working Phase 1 system.

---

## **Sub‑Phase 1 — Environment & Core Foundations**
### Goal: Establish all foundational infrastructure for Phase 1 development.
**Prompt Modules:**
1. Environment setup (local + cloud), repo structure, dependency management.
2. Data architecture foundations — Timescale/Postgres schema v1.
3. Backend service scaffold (FastAPI project bootstrap).
4. Frontend scaffold (Next.js/React with UI shell and routing).
5. CI/CD + basic observability (logging, linting, testing, deployment pipeline).

---

## **Sub‑Phase 2 — Market Data Ingestion Layer**
### Goal: Implement the foundational data ingestion pipelines for prices & reference data.
**Prompt Modules:**
1. Polygon.io OHLCV ingestion (1y lookback, daily + intraday rules).
2. Corporate actions ingestion.
3. Index + macro series ingestion (SPX, NDX, VIX, TNX, etc.).
4. Data validation & reconciliation workflow.
5. Scheduled ingestion jobs + backfill logic.

---

## **Sub‑Phase 3 — Options & Implied Volatility Data Layer**
### Goal: Build the minimal viable options ingestion system for ATM straddles.
**Prompt Modules:**
1. ATM straddle extraction for nearest, 30d, 60d, 90d horizons.
2. Vol‑surface approximation module (Phase 1 simplified version).
3. Data normalization + storage schema for options.
4. Sanity‑check analytics (expected move calculations).
5. Options‑data refresh scheduling & fault tolerance.

---

## **Sub‑Phase 4 — Regime Detection Engine (Rule‑Based)**
### Goal: Implement the SPX/NDX + stock‑specific volatility & trend regime classifier.
**Prompt Modules:**
1. Realized volatility calculation utilities.
2. Trend regime classifier (MA crossovers, drawdowns, etc.).
3. Macro regime classifier (risk‑on/off, vol‑compression/expansion states).
4. AI sentiment proxy (heuristic version for Phase 1).
5. Regime storage + real‑time update logic.

---

## **Sub‑Phase 5 — Stock Analysis Engine**
### Goal: Build the per‑ticker analytics layer used by the simulator.
**Prompt Modules:**
1. Technical snapshot module (momentum, volatility, gaps, returns).
2. Light fundamentals snapshot (valuation banding if available).
3. Liquidity profile module.
4. Earnings calendar integration.
5. Consolidated StockAnalysis service API.

---

## **Sub‑Phase 6 — Factor & Event Universe (Phase 1 Limited Scope)**
### Goal: Implement the factor‑based event architecture.
**Prompt Modules:**
1. Factor taxonomy: MacroRegime, AIOutlook, PolicyRisk, EarningsOutcome, ExecutionQuality.
2. State definitions + mutual exclusivity logic.
3. Event templates for each factor state.
4. Probability mapping rules (viewpoint slider → factor state probabilities).
5. Impact mapping rules (T‑shirt size → calibrated impact ranges using vol data).

---

## **Sub‑Phase 7 — Probability & Impact Calibration Engine**
### Goal: Create the quantitative glue between events and the simulation engine.
**Prompt Modules:**
1. Impact type definitions (jump_price, scale_volatility, change_drift).
2. Impact range derivation from realized + implied vol.
3. Probability guards + validation logic.
4. T‑shirt size normalization (mild/standard/explosive mapping).
5. Final calibration API for Monte Carlo engine consumption.

---

## **Sub‑Phase 8 — Monte Carlo Engine (Piecewise Vol + Jumps)**
### Goal: Implement the core simulation engine.
**Prompt Modules:**
1. GBM baseline with piecewise volatility.
2. Jump event injection logic.
3. Horizon options (30/60/90 days) parameterization.
4. Parallelization/optimization for 10k–100k paths.
5. Simulation output packaging (distributions, quantiles, tail risks).

---

## **Sub‑Phase 9 — UI Layer (Phase 1 UX)**
### Goal: Build the core user interface for viewing, configuring, and running simulations.
**Prompt Modules:**
1. S&P 100 Screener.
2. Stock overview page with regime shading & metrics.
3. Scenario Builder with sliders + T‑shirt sizing controls.
4. Event detail panel UI.
5. Simulation dashboard (charts, quantiles, tail risks, comparison vs options).

---

## **Sub‑Phase 10 — AI Narrative & Export Layer**
### Goal: Build the interpretive layer + export capabilities.
**Prompt Modules:**
1. AI explainer for stock context.
2. AI explainer for scenario drivers.
3. AI explainer for simulation results.
4. Export: CSV, PNG charts.
5. Report generator (Markdown + PDF pipeline).

---

## Next Steps
1. Review this structure.
2. Confirm or adjust the list of sub‑phases.
3. Begin refining **each sub‑phase’s 5 prompts** into detailed engineering prompts.

