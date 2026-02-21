# DataVex Growth Intelligence Engine — Architecture

## Overview

Single-keyword pipeline: **Keyword → Signal → Gap → Strategy → Positioning → Content (Blog, LinkedIn, Twitter) → Critique loops → Final state.**

RAG is used **only for grounding** (retrieving external signals and DataVex context). All editorial decisions (angle choice, approval, scoring) are explicit agent logic and LLM calls, not RAG.

## Data flow

```
[User: keyword]
       ↓
1. Load context (brand voice static, DataVex corpus in Chroma)
       ↓
2. Signal discovery (hybrid: live search optional, static cache fallback)
   → ONE primary signal, confidence score
   → If confidence < threshold → ABORT with message
       ↓
3. Gap analysis (LLM): saturated angles, narratives to avoid
       ↓
4. Strategy brief (LLM): chosen angle, why it wins, 2–3 rejected angles, platform strategy
       ↓
5. Positioning engine (RAG: DataVex corpus → hooks for blog tail, LinkedIn, Twitter)
       ↓
6. Content generation (3 assets, platform-native, shared signal/angle)
   - Blog 800–1200 words (DataVex in final 10–15%)
   - LinkedIn 200–300 words
   - Twitter 5–8 tweets
       ↓
7. Critique loop per asset: Draft 1 → Critique 1 → Draft 2 → Critique 2 → Final
   - Scores: hook_strength, authority, differentiation, structure, platform_fit
   - Full trace stored
       ↓
8. Return state: signal, brief, rejected angles, content, critique evolution, latency
```

## Tech stack

- **Backend:** Python 3.11+, FastAPI, LangChain (retrievers only), Chroma, Google Gemini (gemini-2.5-pro strategy/critique, gemini-2.5-flash content).
- **Frontend:** Next.js 14 (App Router), React, Tailwind.
- **Deployment:** Backend → Render; Frontend → Vercel.

## Key decisions

- **No LangGraph:** Explicit function-based pipeline for clarity and judge explainability.
- **Abort on low confidence:** Prevents publishing on weak signals.
- **Rejected angles visible:** Judges see what the system chose not to do.
- **DataVex in tail only:** Enforced in prompts; positioning is philosophy, not sales.

See `docs/decisions.md` for full rationale.
