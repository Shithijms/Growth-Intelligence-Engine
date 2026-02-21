# DataVex Growth Intelligence Engine

A production-grade, autonomous content intelligence system that converts a keyword into publish-ready, multi-platform content assets through signal discovery, strategic positioning, iterative critique loops, and a scored quality gate.

## Architecture

```
keyword → Signal Discovery (Tavily) → Signal Scoring → Validation → SERP Gap Analysis
       → Strategy Brief (Claude) → Blog Engine (2 iterations + quality gate)
                                 → Short Form Engine (LinkedIn + Twitter, 2 iterations + gate)
       → Final Output JSON
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14 (App Router) + Tailwind CSS |
| Backend | FastAPI (Python) + SSE streaming |
| AI Agents | Claude claude-sonnet-4-6 via Anthropic SDK |
| Search | Tavily API |
| Orchestration | LangGraph |

## Project Structure

```
Growth-Intelligence-Engine/
├── backend/
│   ├── main.py              # FastAPI app (SSE + sync endpoints)
│   ├── config.py            # Settings (API keys)
│   ├── models.py            # Pydantic models
│   ├── agents/              # 10 AI agents
│   │   ├── base.py
│   │   ├── signal_discovery.py
│   │   ├── signal_scorer.py
│   │   ├── signal_validator.py
│   │   ├── serp_scanner.py
│   │   ├── strategy_brief.py
│   │   ├── blog_generator.py
│   │   ├── blog_critique.py
│   │   ├── short_form_generator.py
│   │   └── short_form_critique.py
│   └── pipeline/            # LangGraph orchestration
│       ├── graph.py         # 16-node state machine
│       ├── state.py         # TypedDict state schema
│       ├── quality_gate.py  # 7/10 threshold, max 3 iters
│       └── output_assembler.py
└── frontend/
    ├── app/
    │   ├── dashboard/page.tsx  # Main dashboard (8 panels)
    │   └── layout.tsx
    ├── components/panels/   # All 8 dashboard panels
    └── lib/
        ├── api.ts           # SSE streaming client
        └── types.ts         # TypeScript types
```

## Setup

### Backend

```bash
cd backend
cp .env.example .env
# Fill in ANTHROPIC_API_KEY and TAVILY_API_KEY in .env

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
# .env.local already configured for localhost:8000

npm install
npm run dev
```

Open [http://localhost:3000/dashboard](http://localhost:3000/dashboard)

## API Keys Required

- **Anthropic API Key** — [console.anthropic.com](https://console.anthropic.com) — Claude claude-sonnet-4-6
- **Tavily API Key** — [app.tavily.com](https://app.tavily.com) — Signal discovery + SERP scanning

## Pipeline Flow

1. **Signal Discovery** — Tavily searches for real articles/signals (top 5 candidates)
2. **Signal Scoring** — 4-dimension confidence scoring (authority, recency, relevance, novelty)
3. **Signal Validation** — URL reachability + fact extraction
4. **SERP Scan** — Competitor angle mapping + gap identification
5. **Strategy Brief** — Editorial positioning with rejected angle reasoning
6. **Blog Engine** — 800-1200 word post → Critique → Rewrite → Quality Gate
7. **Short Form Engine** — LinkedIn (200-300w) + Twitter Thread (6-8 tweets) → Critique → Rewrite → Gate
8. **Final Output** — Structured JSON with all assets, scores, and critique trace

## Dashboard Panels

| Panel | Description |
|-------|-------------|
| 1 | Keyword Input + Live Progress (stage pills) |
| 2 | Signal Intelligence Report (scores + gaps) |
| 3 | Strategy Brief (angle, thesis, distribution plan) |
| 4 | Blog Output (markdown preview + score chart) |
| 5 | LinkedIn Output (formatted post preview) |
| 6 | Twitter Thread (per-tweet cards) |
| 7 | Critique Trace (draft evolution diffs + score deltas) |
| 8 | Quality Gate Log (pass/fail table) |

## Sample Keywords

- `revenue intelligence`
- `data warehouse cost optimization`
- `AI in RevOps`
