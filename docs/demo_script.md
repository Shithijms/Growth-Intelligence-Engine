# Demo script (≤2 min for judges)

## 1. One-line pitch (10 s)

"DataVex Growth Intelligence Engine turns one keyword into publish-ready growth content by finding a real signal, picking a contrarian angle, and refining through critique loops—with full visibility into what we chose not to do."

## 2. Show the UI (30 s)

- Open dashboard. Enter keyword **RAG**.
- Click **Run pipeline**. (Explain: backend runs signal → strategy → content → critique.)
- When done, scroll through:
  - **Signal + confidence** — "We only proceed if confidence is above threshold."
  - **Strategy brief** — "Chosen angle and rejected angles are visible."
  - **Content tabs** — Blog, LinkedIn, Twitter; same angle, platform-native.
  - **Critique evolution** — "Each asset went through two critique rounds; scores and feedback are logged."

## 3. Technical differentiators (30 s)

- **RAG for grounding only** — We use RAG to retrieve signals and DataVex context. We do *not* use RAG to decide strategy or approve content.
- **Abort on low confidence** — If the signal isn’t strong enough, we stop and explain why.
- **Rejection visibility** — Rejected angles and weak drafts are stored and shown.
- **DataVex in the tail** — Product philosophy appears only in the final 10–15% of the blog; no sales pitch up front.

## 4. Sample run

- **Keyword:** RAG  
- **Expected:** Signal from cache (e.g. "RAG vs Fine-tuning..."), strategy brief with one chosen angle and 2–3 rejected, three content assets, and critique traces with score evolution.

## 5. Deployment

- Backend: Render (Web Service, `backend/`, `uvicorn main:app`).
- Frontend: Vercel (root `frontend/`, env `NEXT_PUBLIC_API_URL` = Render URL).
