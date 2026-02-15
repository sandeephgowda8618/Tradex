# Tradex

A deterministic financial intelligence system with an LLM narration layer. The backend computes fundamentals and technicals deterministically, caches market data, stores immutable analysis snapshots, and asynchronously produces LLM interpretations. The frontend is a lightweight React UI that submits symbols, polls results, and renders scores with a professional layout.

---

## What This Project Does

### Core Capabilities
- Deterministic fundamental analysis (12 key metrics, trend stability, risk model, category scoring)
- Deterministic technical analysis (trend, momentum, volume, volatility, entry/exit bias)
- Combined intelligence layer (60/40 fundamental/technical weighting)
- Redis cache for market data + combined results + LLM output
- Celery worker to generate LLM summaries asynchronously
- Persistent snapshots in SQL database (no raw API payloads stored)
- FastAPI routes for analysis creation + retrieval
- Vite + React frontend for submission + polling + interpretation display

### Design Principles
- Engines are pure computation (no API calls)
- Orchestrator controls fetch/caching/selection logic
- LLM is strictly a narrator (never computes metrics)
- All analysis snapshots are immutable
- Caching is used for rate-limit safety and latency reduction

---

## Architecture Overview

```
Client
  ↓
FastAPI
  ↓
AnalysisOrchestrator
  ↓
Redis (cache check)
  ↓
AlphaVantageService (if cache miss)
  ↓
FundamentalEngine / TechnicalEngine
  ↓
Database (snapshot)
  ↓
Celery Task → Redis → LLM → DB update
  ↓
Response
```

### Layers
1. **Engines**: Deterministic scoring and signals
2. **Orchestrator**: Data fetching, caching, selection, combination
3. **Persistence**: Immutable analysis + result snapshot
4. **LLM**: Narrative layer, async via Celery

---

## Key Components

### `AlphaVantageService`
- Single responsibility: external API calls
- Uses `_make_request(function_name, symbol, extra_params)`
- No business logic or calculations

### `FundamentalEngine`
- Extracts annual series (4 years minimum)
- Computes 12 core metrics
- Trend analysis with stability bonus + volatility penalty
- Adaptive scoring via ranges
- Category aggregation + risk model

**Metrics**
- Profitability: ROE, ROA, Net Margin, Operating Margin
- Growth: Revenue CAGR, EPS CAGR, FCF CAGR
- Financial Strength: Debt/Equity, Current Ratio, Interest Coverage
- Valuation: P/E, EV/EBITDA

### `TechnicalEngine`
- Indicators: SMA50, SMA200, EMA20, RSI, MACD, Stoch, OBV, Volume Spike, ATR, BBands
- Trend detection: price vs SMA200, SMA50 vs SMA200, EMA20 vs SMA50
- Momentum/volatility regimes, entry/exit bias

### `AnalysisOrchestrator`
- Validates input
- Selective API calls based on requested indicators
- Redis caching (market data, combined, LLM)
- Returns final structured output

### `InterpretationEngine`
- Uses Ollama local API (`/api/generate`)
- Strict JSON-only output
- Summaries persisted in DB

---

## Redis Caching Strategy

**Market cache**
- Key: `market:{symbol}:{function}:{param_hash}`
- TTL: 1 hour

**Combined analysis cache**
- Key: `analysis:{symbol}:{fund_hash}:{tech_hash}`
- TTL: 20 minutes

**LLM cache**
- Key: `llm:{symbol}:{payload_hash}`
- TTL: 24 hours

---

## Database Schema

Tables:
- `users`
- `threads`
- `analyses`
- `analysis_results`

**analysis_results** stores deterministic JSON + LLM fields:
- `fundamental_json`
- `technical_json`
- `combined_json`
- `llm_summary`, `llm_bull_case`, `llm_bear_case`, `llm_risk_assessment`, `llm_confidence`, `llm_status`

---

## API Routes

### `POST /analysis`
Creates a new analysis run and queues LLM task.

**Query Params**
- `symbol` (required)
- `selected_fundamentals` (optional, repeated)
- `selected_technicals` (optional, repeated)
- `include_llm` (optional, default true)
- `thread_id` (optional)

**Response**
```json
{
  "analysis_id": "uuid",
  "thread_id": "uuid",
  "status": "processing"
}
```

### `GET /analysis/{analysis_id}`
Fetches stored results.

**Response (LLM pending)**
```json
{
  "fundamental": {...},
  "technical": {...},
  "combined": {...},
  "llm_status": "pending",
  "llm_summary": null,
  "llm_ready": false
}
```

**Response (LLM completed)**
```json
{
  "fundamental": {...},
  "technical": {...},
  "combined": {...},
  "llm_status": "completed",
  "llm_summary": "...",
  "llm_bull_case": "...",
  "llm_bear_case": "...",
  "llm_risk_assessment": "...",
  "llm_confidence": "Medium",
  "llm_ready": true
}
```

---

## LLM Prompt Format

**Strict JSON-only output**
```json
{
  "executive_summary": "...",
  "bull_case": "...",
  "bear_case": "...",
  "risk_assessment": "...",
  "confidence": "Low/Medium/High"
}
```

The LLM never computes metrics or recommends trades. It only narrates computed results.

---

## Frontend

Vite + React UI includes:
- Symbol input
- Indicator selection chips
- Polling loop until `llm_ready=true`
- Sections for combined score, fundamentals, technicals, LLM

---

## Installation

### Backend
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Frontend
```bash
cd frontend
npm install
```

---

## Run Locally

### Backend API
```bash
make run-api
```

### Celery Worker
```bash
make run-worker
```

### Frontend
```bash
make run-frontend
```

### Docker Compose (full stack)
```bash
make docker-up
```

---

## Tests

### Unit
- Fundamental engine (strong/neutral/bad cases)
- Technical engine (bull/bear cases)
- Orchestrator with fake Alpha service
- Combine logic
- LLM parsing + Celery task

### Integration
- Analysis route creation + retrieval

Run:
```bash
make test
make test-cov
```

---

## Environment Variables

Create `.env` with:
```
ALPHA_VANTAGE_API_KEY=...
DATABASE_URL=sqlite:///./app.db
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
OLLAMA_BASE_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=llama3:8b
```

---

## Notes
- Engines are deterministic. LLM is a narrative layer only.
- Redis caching prevents Alpha Vantage rate-limit failures.
- Analysis results are immutable for auditability.
- Celery handles LLM inference asynchronously.
