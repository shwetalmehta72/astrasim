# Product Requirements Document (PRD)
## AstraSim – Event‑Driven Monte Carlo Stock Simulation & Forecasting System (v0.2)

---

## 1. Overview

### 1.1 Product Name (Working Title)
**AstraSim: AI‑Driven Event‑Based Market Simulator**

### 1.2 Purpose & Vision

AstraSim is an advanced, **calibrated**, event‑aware stock forecasting engine that models the future price distribution of any liquid, publicly traded stock **30 / 60 / 90 days ahead**.

Unlike conventional “random walk” tools, AstraSim explicitly bridges:
- The **narrative of the market** (macro, sector, stock‑level events, news, regime) and
- The **math of the market** (Monte Carlo, volatility surfaces, jump processes).

The core objective is not just to generate paths, but to:
- Encode realistic **event structures and factor states** (Macro, AI outlook, earnings outcomes, execution risk),
- Calibrate **probabilities and impacts** using **real data** (realized vol, options‑implied vol, historical reactions) with strict guardrails, and
- Provide **transparent, explainable scenario distributions** that traders can interrogate and adjust.

The end result: a **scenario‑driven, risk‑aware price forecast** that helps users:
- Understand upside/downside distributions,
- See where tail risks actually sit,
- Compare their own views vs the options market, and
- Eventually design and manage trades.

---

## 2. Problem Statement

Existing tools fall roughly into two camps:

1. **Purely statistical models** (historical vol, simple GBM, linear factor models):
   - Easy to compute but blind to real‑world events and changing regimes.
   - Cannot answer: *“What if AI spending collapses?”* or *“What if earnings surprise to the upside?”*

2. **Narrative / discretionary thinking** (news, opinions, macro views):
   - Rich in context but unstructured, non‑quantified, and impossible to backtest.

AstraSim’s thesis:
> **The future price distribution should be a function of both the statistical regime and a structured universe of events that can occur.**

Key gaps we address:
- Lack of **regime‑aware models** (vol/trend/context).
- Lack of **event‑driven structure** (earnings, policy, AI cycle, company execution).
- Lack of **calibration** to real‑world risk signals (options‑implied moves, realized volatility, historical reactions).
- Heavy reliance on **arbitrary user intuition** for probabilities and impacts.

AstraSim solves this by:
1. Building a **factor‑based event universe** (Macro, AI outlook, earnings, execution) rather than dozens of independent events.
2. Estimating **base probabilities and impact ranges** using:
   - Realized volatility and historical moves,
   - Options‑implied volatility and ATM straddles,
   - News‑derived historical events (later phases).
3. Modeling **mutually exclusive factor states** (e.g., AI up vs AI down, Beat vs Miss) instead of independent toggles.
4. Running a **GBM + jump** Monte Carlo with a **simple term‑structure of volatility** (elevated vol into known events like earnings, lower vol afterward).
5. Providing **transparent UX** that separates:
   - **Trend/Drift** (baseline regime view) from
   - **Events/Jumps** (discrete shocks), to avoid double‑counting.

---

## 3. Goals & Non‑Goals

### 3.1 Goals (Phase 1)

1. **Realistic Distributions**
   - Generate realistic 30/60/90‑day price distributions for individual large‑cap stocks.
   - Reflect both continuous market noise and discrete event risks.

2. **Data‑Calibrated, Not Purely Opinion‑Driven**
   - Anchor volatility and baseline move expectations to:
     - Historical realized volatility,
     - Options‑implied volatility (e.g., ATM straddles for relevant tenors).
   - Use simple, explainable rules for mapping user opinions to factor probabilities.

3. **Factor‑Based Event Modeling**
   - Represent macro/AI/earnings/execution as **factors with states** (e.g., AI_Boom vs AI_Cooldown), not a flat list of 50 toggles.
   - Model **mutual exclusivity** at the factor level (a factor has one state per path).

4. **Usable UX**
   - Users never have to set 20 individual probability/impact numbers.
   - They instead choose **T‑shirt sizes and viewpoints**, e.g.:
     - Earnings impact: Mild / Normal / Explosive
     - AI trend: Bearish / Neutral / Bullish
   - The system translates these to numeric ranges using data‑driven defaults.

5. **Explainability & Narrative Layer**
   - Use OpenAI and Gemini to:
     - Summarize regime & stock context.
     - Explain why the distribution looks the way it does.
     - Describe key upside/downside scenarios.
   - **Not** to directly output numeric probabilities.

6. **Performance**
   - Run 10k‑path simulations for a 90‑day horizon in < 1s on a typical server.
   - Support up to 100k paths interactively; larger runs via async jobs.

### 3.2 Non‑Goals (Phase 1)

- Trade execution or broker integration.
- Full options pricing suite or greeks engine.
- Portfolio‑level multi‑asset Monte Carlo.
- Automated alpha model / auto‑trading.
- Fully automated news‑to‑event base‑rate labeling (this is a Phase 2 path).

---

## 4. User Personas

(Same personas as v0.1, with emphasis tweaks.)

### 4.1 Active Trader / Options Trader
- Wants probability‑aware, scenario‑driven distributions.
- Wants to compare simulation outputs vs implied moves from options.

### 4.2 Quant‑Minded Investor
- Wants regime detection and factor‑based event structure.
- Cares that probabilities/impacts are **calibrated**, not arbitrary.

### 4.3 Fundamental Investor
- Wants AI‑generated explanations tied to fundamentals and events.

### 4.4 Strategist / PM
- Wants scenario analysis for major macro & thematic shifts (e.g., AI cycle, policy risk).

---

## 5. High‑Level Architecture (Updated)

### 5.1 Data Ingestion Layer (Polygon.io & Others)

Inputs:
- Historical OHLCV (up to 1 year) for large‑cap universe.
- Corporate actions.
- Company fundamentals (EPS, revenue, margins, valuation metrics where available).
- Real‑time quotes (for UI and spot S₀).
- Market indices: SPX, NDX, sector ETFs, VIX, key rates.
- Options snapshot data (minimally ATM straddles for near‑term and 30/60/90d equivalent tenors).
- News headlines & metadata (Polygon X or equivalent).

New Phase 1.5+ component:
- **NewsParserService (Batch, Offline)**
  - Pulls news headlines & price reactions.
  - Uses LLM to tag coarse event categories and sentiment.
  - Writes to a `HistoricalEvents` store for future base‑rate estimation.

> Phase 1: news‑driven base‑rates are aspirational; options‑implied and realized vol drive calibration.

### 5.2 Analytics Layer

1. **Regime Detection** (Rule‑First, ML‑later)
   - Vol regime (low/normal/high) from SPX & stock realized vol.
   - Trend regime (bull/bear/sideways) from moving average & drawdown rules.
   - Macro flags: risk‑on/off, inflation risk, AI sentiment (initially rule/heuristic based).

2. **Stock Analysis Engine**
   - Technical signals: trend, momentum, volatility, gaps.
   - Fundamental snapshot: valuation band, earnings surprise, growth direction (if data available).
   - Liquidity profile: ADV and rough microstructure proxies.

3. **Options/Vol Surface Approximation**
   - Ingest ATM straddle prices for key expiries.
   - Infer implied move distributions over 30/60/90d horizons.
   - Use these as **constraints** on the MC output:
     - Example: MC distribution’s 1‑week expected move should be broadly compatible with the ATM straddle (within tolerance), or we re‑scale σ.

4. **Event Universe Builder (Factor‑Based)**
   - For Phase 1:
     - **Macro factors**: MacroRegime, AIOutlook (global), PolicyRisk.
     - **Stock factors**: EarningsOutcome, ExecutionQuality.
   - Sector‑level factors are **Phase 2+** (defer to reduce complexity).
   - Each factor has discrete states (e.g., AI_Boom / AI_Stable / AI_Cooldown).
   - Event templates are attached to **factor states**, not free‑floating.

5. **Event Probability & Impact Engine**
   - Uses realized vol + options‑implied vol + simple historical analogs to anchor:
     - Baseline factor state probabilities.
     - Baseline event impact ranges.
   - Supports multiple **impact types**:
     - `jump_price` (discrete price move),
     - `scale_volatility` (e.g., regime of elevated uncertainty),
     - `change_drift` (persistent directional bias).

6. **Dependency Engine (Simplified)**
   - Enforces mutual exclusivity at the factor level:
     - One state per factor per path.
   - Encodes simple conditional logic between factors (Phase 1.5):
     - e.g., high macro stress increases probability of negative earnings state.
   - Users do **not** manage dependency graphs directly; this is internal.

### 5.3 Monte Carlo Engine

- Baseline: GBM with a **piecewise volatility term structure**:
  - Higher σ into scheduled events like earnings or macro announcements.
  - Lower σ afterward (e.g., vol crush).
- Jumps:
  - Derived from factor states and their attached events.
  - Applied via multiplicative log‑normal or uniform log‑jump distributions.
- Impact types:
  - Price jumps, volatility scaling, drift shifts.
- Horizons: 30 / 60 / 90 days.
- Paths: 10k–100k interactive.

### 5.4 AI Layer (OpenAI + Gemini)

Roles (refined):
- **Interpretive & Explanatory, not Numeric**:
  - Explain regimes, factors, and distributions.
  - Summarize what the model is implying about upside/downside.
- **Tagging & Classification**:
  - Classify news into coarse factor states (e.g., RegulatoryRisk = High/Med/Low).
  - Map natural language headlines to AstraSim’s internal factor taxonomy.

Numeric probabilities remain the domain of the **deterministic factor mapping rules**, not the LLM.

---

## 6. Core Features – Phase 1 (Re‑Scoped)

### 6.1 Stock Screener (Simplified)

- Universe: Start with **S&P 100** (or similar large‑cap index) only.
- Rationale: Higher data quality, fewer corporate action edge cases.
- Columns:
  - Ticker, Name, Sector
  - Market Cap
  - 30/60/90d realized vol
  - YTD % change
  - Upcoming earnings date flag
- Phase 2:
  - Add dynamic signal picks (unusual volume, options activity, etc.).

### 6.2 Stock Overview Page

- Real‑time price and intraday chart.
- 90–180 day historical chart with regime shading (bull/bear/high‑vol segments).
- Snapshot metrics:
  - Realized vol, implied vol (from ATM straddles), beta.
  - Basic valuations if available.
- AI narrative summary (OpenAI/Gemini) of “what’s going on with this stock and environment.”

### 6.3 Scenario Builder – Viewpoint‑First UX

- User chooses:
  - Horizon: 30, 60, 90 days.
  - Viewpoint sliders:
    - Macro Risk: Low ↔ High
    - AI Trend: Bearish ↔ Bullish
    - Earnings Risk: Bearish ↔ Bullish
    - Company Execution: Weak ↔ Strong
- User chooses **T‑shirt sizes** instead of raw numbers for key sensitivities:
  - Earnings Impact: Mild / Standard / Explosive
  - Macro Shock Impact: Mild / Standard / Severe
- Backend maps these to:
  - Factor state prior probabilities.
  - Event impact ranges, scaled by realized & implied vol.
- Advanced mode (for power users):
  - Inspect (and lightly tweak) a subset of event probabilities & impacts with guardrails and warnings.

### 6.4 Event Detail Panel (Constrained)

- Show factor → state → event mapping:
  - Example: `EarningsOutcome = Beat` implies one or two canonical earnings events, not ten.
- For each event:
  - Description (with ticker and context filled in).
  - Impact type: jump_price / scale_volatility / change_drift.
  - Impact range band (derived from data + T‑shirt sizing).
  - Probability (derived from factor state and view; read‑only in basic mode).
- Explicitly show:
  - This event is part of factor `EarningsOutcome` and is mutually exclusive with `EarningsOutcome = Miss`.

### 6.5 Monte Carlo Simulation Dashboard

- Run simulation with clear decomposition:
  - Baseline (trend + vol) vs event‑driven delta.
- Outputs:
  - Histogram + **KDE plot** of final prices to reveal bi‑modal or multi‑modal structure.
  - Quantile table (1/5/10/25/50/75/90/95/99%).
  - Tail probabilities: P(R ≤ −20%), P(R ≤ −40%), P(R ≥ +20%), etc.
  - A small number of sample paths with event markers on the timeline.
- Comparison vs options market:
  - Show implied move from ATM straddle for comparable horizon.
  - Indicate if MC is materially more bullish or bearish than options.
- AI narrative:
  - “What is driving upside?”
  - “What is driving downside?”
  - “How does this compare to implied expectations?”

### 6.6 Export & Reports

- Export distributions and quantiles to CSV.
- Export charts (price/return distribution) as PNG.
- Export a scenario report (PDF or Markdown) summarizing:
  - Viewpoint configuration,
  - Factor states & event set,
  - Simulation statistics,
  - High‑level AI explanation.

---

## 7. Phase 2+ Features (Updated Roadmap)

- **Sector Factor Layer**:
  - Add sector‑specific factors/events once Macro + Stock layers are proven.
- **NewsParserService & HistoricalEvents**:
  - Nightly processing of news to build structured event dataset.
  - Use for refining base‑rates and impact distributions.
- **Options & Strategy Layer**:
  - Overlay option structures (calls, puts, spreads) on top of price distributions.
  - Simulate P&L distributions for strategies.
- **Portfolio & Multi‑Asset Simulation**.
- **More Sophisticated Vol Models**:
  - Stochastic vol (Heston‑lite) or regime‑switching volatility.

---

## 8. KPIs & Success Metrics (Refined)

- **Performance**: 10k path, 90‑day simulation completes < 1 second.
- **Calibration Quality**:
  - For a set of benchmark stocks, MC short‑horizon expected moves roughly align with options‑implied moves (within agreed bands).
- **User Adoption & Engagement**:
  - Repeat simulations per user.
  - Time spent in Scenario Builder & Simulation Dashboard.
- **Perceived Quality**:
  - User feedback on:
    - Plausibility of distributions.
    - Usefulness of AI explanations.
    - UX around sliders and T‑shirt sizing.

---

## 9. Risks & Constraints (Updated)

### 9.1 Technical Risks

- **Calibration Risk**: If probability/impact mapping is poor, outputs become “quantified guessing.”
- **Volatility Term Structure**: Approximating vol around events may still be simplistic.
- **Data Engineering Load**: Options & news ingestion require careful rate‑limit handling and cleaning.

### 9.2 Product Risks

- Users may misinterpret probabilities as predictions rather than scenario outputs.
- If UI exposes too many knobs, users may overfit or confuse themselves.

### 9.3 Data Risks

- Polygon quotas / limits.
- Options & news coverage gaps.
- Limited historical depth for some names, affecting analog quality.

Mitigation: Start with S&P 100; log model uncertainty explicitly in the UI.

---

## 10. Open Questions (v0.2)

1. What tolerance band should we enforce between options‑implied move vs simulated move (per horizon) before re‑scaling σ?
2. How many factors & states is the sweet spot for Phase 1 (to avoid combinatorial explosion but still capture richness)?
3. Do we want to expose **volatility impact events** to the user in the UI, or treat them as internal mechanics only?
4. How much offline precomputation (e.g., regime detection, vol surfaces) should be done nightly vs on‑demand?
5. How explicitly do we show “model uncertainty” (e.g., confidence in calibration) in the UI?

---

## 11. Phase 1 Scope (Revalidated)

Phase 1 will deliver:
- Screener for S&P 100.
- Data ingestion & cleaning (prices, basics, ATM options, indices).
- Rule‑based regime detection.
- Stock analysis engine (technical + basic fundamentals where available).
- Factor‑based event universe (Macro + Stock factors only).
- Viewpoint sliders + T‑shirt sizing UX.
- Monte Carlo engine with piecewise volatility and jump events.
- Simulation dashboard with KDE, quantiles, tail probabilities, and options‑implied comparison.
- AI explanation layer for stock, scenario, and results.
- Export capabilities (CSV, PNG, scenario report).

## 12. Multi‑Phase Roadmap to a Fully Autonomous Trading System

This roadmap outlines how AstraSim evolves from a **single‑stock, event‑driven simulator** into a **fully autonomous trading system** with live execution, risk management, and continual learning.

Each phase is designed to be **useful on its own**, de‑risk the next phase, and allow you to pause or pivot based on results.

---

### Phase 1 – Event‑Driven Monte Carlo Simulator (Current Scope)

**Objective:** Build a robust, calibrated, factor‑based Monte Carlo engine and UI for single‑stock 30/60/90‑day scenario analysis.

**Core Capabilities (from PRD v0.2):**
- S&P 100 screener and stock overview page.
- Rule‑based regime detection and stock analysis.
- Factor‑based event universe (Macro + Stock factors).
- Viewpoint sliders + T‑shirt sizing UX for impact intensity.
- GBM + jump Monte Carlo with piecewise volatility and options‑implied move sanity checks.
- Distribution outputs (histogram + KDE, quantiles, tail probabilities).
- AI explanations of context and results.
- Export of data, charts, and scenario reports.

**Success Criteria / Exit:**
- Engine is numerically stable and performant (10k paths < 1s).
- Simulated near‑term move ranges are broadly consistent with options‑implied moves for benchmark tickers.
- UX is usable and produces distributions that “feel” plausible under different viewpoints.

---

### Phase 2 – Strategy & Options Layer (Advisory, No Live Execution)

**Objective:** Move from “price distribution only” to **strategy‑aware analytics**, still fully offline/advisory.

**New Capabilities:**
- Options & strategy overlay on top of simulated price distributions:
  - Long/short stock, calls, puts, vertical spreads, collars, covered calls.
- P&L distribution simulation for a given strategy and horizon:
  - Expected return, variance, downside risk metrics.
- Simple **position sizing helpers** based on risk tolerance (e.g., max drawdown or VaR budget).
- Scenario comparison:
  - Base case vs bullish vs bearish vs user‑defined scenarios.

**Tech Additions:**
- Options snapshot ingestion extended (basic chain, not just ATM) for S&P 100.
- Strategy evaluator module that maps price paths → P&L paths.
- Additional analytics in UI (P&L histogram, payoff diagrams, risk vs reward views).

**Success Criteria / Exit:**
- System produces coherent strategy P&L distributions across scenarios.
- You can answer: *“If I sell this call spread under this view, what does my downside look like?”*
- Still **no trade routing**; user manually executes decisions elsewhere.

---

### Phase 3 – Signal Engine & Semi‑Automated Trade Workflow

**Objective:** Turn AstraSim into a **signal‑producing decision engine** with structured workflows, but keep **human in the loop** for execution.

**New Capabilities:**
- **Signal Engine:**
  - Periodic scans (e.g., daily/weekly) over S&P 100 to identify:
    - Asymmetric opportunity: high upside / limited downside (distribution‑based).
    - Misalignment vs options‑implied moves (e.g., MC more bearish than IV).
  - Rank and score trade ideas.
- **Playbook Templates:**
  - Predefined strategy templates per signal type (e.g., mean‑reversion, breakout, earnings play).
- **Trade Idea Dashboard:**
  - List of active candidates with:
    - View assumptions,
    - Suggested strategies,
    - Risk/return metrics.
- **Manual Execution Workflow:**
  - User confirms, edits, or rejects each suggested trade.
  - System tracks: *“proposed vs accepted vs rejected”* and resulting P&L.

**Tech Additions:**
- Scheduler for periodic batch runs (e.g., nightly/weekly job).
- Persistent storage for generated ideas and their outcomes.
- Basic performance attribution (per signal type, per factor view).

**Success Criteria / Exit:**
- You can run AstraSim daily/weekly and get **ranked trade ideas**.
- Human‑approved trades show coherent performance patterns (some edges, some duds) that can be analyzed.
- Still no auto‑sending of orders; integration is advisory & tracking only.

---

### Phase 4 – Broker Integration & Risk‑Controlled Auto‑Execution (Single‑Strategy)

**Objective:** Move from advisory to **semi‑autonomous trading** for a carefully limited subset of strategies, with strict risk controls.

**New Capabilities:**
- **Broker/API Integration** (e.g., IBKR, Alpaca, or equivalent):
  - Paper trading first, then small‑capital live trading.
- **Execution Engine:**
  - Converts approved strategy templates into actual orders.
  - Handles order placement, position tracking, and basic monitoring (fills, slippage, cancels).
- **Risk Manager (Global & Strategy‑Level):**
  - Max notional exposure per ticker and per day.
  - Max portfolio drawdown limits.
  - Kill‑switch conditions (stop trading if breached).
- **One or Few Canonical Strategies:**
  - Start with a very narrow scope (e.g., event‑driven options spreads on 5–10 names).

**Tech Additions:**
- Secure credential storage and broker connectivity modules.
- Real‑time position and P&L tracking.
- Alerting and logging for all trading operations.

**Human‑in‑the‑Loop:**
- You still approve classes of trades or strategy templates in advance.
- System auto‑executes within pre‑defined rules and risk limits.

**Success Criteria / Exit:**
- Stable end‑to‑end pipeline: idea → strategy → order → position → P&L.
- No unexpected positions beyond defined risk constraints.
- Paper/live results roughly align with simulated expectations over a non‑trivial sample.

---

### Phase 5 – Multi‑Strategy, Multi‑Asset Autonomous Trading with Feedback Loops

**Objective:** Generalize from a single‑strategy, single‑asset focus to a **multi‑strategy, multi‑asset autonomous system** that learns from its own performance and adapts calibration over time.

**New Capabilities:**
- **Multi‑Asset & Portfolio View:**
  - Extend universe beyond S&P 100 (carefully), add ETFs, indices, and possibly futures.
  - Support multiple concurrent strategies with portfolio‑level risk constraints.
- **Performance Feedback & Calibration Loop:**
  - Continuously compare realized outcomes vs simulated distributions.
  - Adjust factor priors, impact ranges, and vol parameters based on performance.
  - Maintain versioned models & backtests.
- **Advanced Modeling (Optional / Iterative):**
  - Stochastic volatility or regime‑switching vol models where justified.
  - More sophisticated news/event parsing for better base‑rate estimates.
  - Possible RL or bandit‑style allocation across strategies (careful, data‑hungry).
- **Governance & Observability:**
  - Full audit trails for decisions, simulations, and executions.
  - Dashboards showing strategy‑level and portfolio‑level metrics.

**Success Criteria / Exit:**
- System can run with **minimal day‑to‑day human intervention**, within predefined risk and governance boundaries.
- Clear evidence that feedback loops improve calibration and/or strategy performance over time.

---

### Phase 6 – Productization & External Users (Optional)

**Objective:** Turn the internal autonomous system into a **commercial‑grade platform** for other traders/investors.

**Focus Areas:**
- Multi‑tenant architecture, authentication, and permissions.
- Configurable strategy templates and risk profiles per user.
- Billing, sandbox/live environments, support workflows.
- Regulatory and compliance considerations depending on jurisdiction.

---

This roadmap is intentionally **modular**. You can stop at:
- Phase 1–2 if you only want a world‑class scenario/strategy lab.
- Phase 3–4 if you want semi‑autonomous assistance.
- Phase 5+ if you want a true autonomous system with adaptive feedback.


**End of PRD v0.2 (Draft)**

