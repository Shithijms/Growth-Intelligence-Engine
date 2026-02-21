# Design decisions

## LLM split: Gemini 2.5 Pro vs 2.5 Flash

- **Strategy, critique, positioning:** gemini-2.5-pro — judgment and scoring benefit from stronger reasoning.
- **Content generation:** gemini-2.5-flash — draft writing is more token-heavy; Flash keeps cost and latency lower while staying good enough for the critique loop to improve.

## RAG only for grounding

- RAG retrieves: (1) external signals (when using a vector index of signals), (2) DataVex corpus (blogs, philosophy, positioning).
- We do *not* use RAG to decide the strategy, choose the angle, or approve content. Those are explicit LLM calls and logic so that reasoning is auditable and the system is explainable.

## Hybrid signal discovery

- Primary: real web sources (papers, surveys, blogs) when available (e.g. Tavily or similar).
- Fallback: static curated signal cache (JSON) checked into the repo so the pipeline runs without external search APIs.
- Confidence score is always computed and shown; abort if below threshold.

## Chroma for vector store

- Chroma is simple to run locally and on Render, persists to disk, and works well with LangChain. FAISS could be swapped in later if we want a file-only store.

## No LangGraph

- The pipeline is linear and deterministic per keyword. Explicit function-based stages are easier to explain to judges and debug. LangGraph would add abstraction without a clear need for branching or cycles.

## Critique: two iterations per asset

- Draft 1 → Critique 1 → Draft 2 → Critique 2 → Final (Draft 2). This meets "at least 2 critique iterations" and keeps latency reasonable. Scores are stored so judges can see evolution (or trade-offs).

## DataVex in final 10–15% of blog

- Enforced in the long-form prompt and optional post-check. Positioning engine produces a "blog_tail_insight" used only at the end, so the narrative leads with the signal and angle; DataVex appears as philosophy, not a sales CTA.

## Pipeline run in thread (FastAPI)

- The full pipeline is synchronous and can take 1–2 minutes. We run it with `asyncio.to_thread()` so the event loop is not blocked and the API stays responsive.

## Static DataVex corpus

- Seed corpus (brand philosophy, past blog angle, LinkedIn-style post, product positioning) is checked into `backend/data/datavex_corpus/`. No DB required for hackathon; RAG indexes these at startup.
