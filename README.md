# Hospital AI Survival Lab

A production-ready prototype for ER operations + economic survival simulation where multiple AI agents compete under capital constraints.

## Project Structure

```text
backend/            # FastAPI API server and orchestration service
frontend/           # React (Vite) dashboard template
agents/             # Agent classes and decision logic
economic_engine/    # Capital accounting and reward/payment engine
simulation/         # ER simulation entities and time loop
configs/            # JSON configuration for economy/simulation knobs
tests/              # Validation tests
```

## Core Capabilities

- Multi-agent rounds with configurable participant list.
- Time-based ER simulation:
  - patient arrivals with acuity
  - capacity-constrained queueing
  - random events: mass casualty + system outage
- KPI tracking:
  - Door-to-Doctor Time
  - Length of Stay
  - Throughput
  - Error Rate
- Economic survival mechanics:
  - starting capital
  - token/API/simulation charges
  - operational burn rate
  - skill upgrade investments + ROI history
  - payment model: `payment = quality_score × impact_factor`
  - bankruptcy when balance ≤ 0

## Config

All economic and simulation parameters are centralized in:

- `configs/economic_config.json`

## Run Locally

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=.. uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

### CLI simulation loop

```bash
python simulation/simulation_loop.py
```

### Tests

```bash
python -m pytest tests
```

## API

### `POST /api/simulate`

Request example:

```json
{
  "rounds": 3,
  "agent_names": ["Triage Optimizer", "Flow Marshal"],
  "beds": 20,
  "nurses": 12,
  "doctors": 6,
  "tokens_used": 1500,
  "api_calls": 15,
  "simulation_runs": 1,
  "seed": 42
}
```

Response includes:

- per-agent per-round decisions
- KPI and cost breakdowns
- leaderboard by survival/economic performance
