"""Signal Confidence Scorer — 4-dimension scoring + composite."""
import json
from models import CandidateSignal, SignalConfidenceScores
from agents.base import BASE_SYSTEM_PROMPT, call_claude


def score_signals(candidates: list[CandidateSignal]) -> tuple[CandidateSignal, SignalConfidenceScores]:
    """Score all candidates and return the best one with its scores."""
    best_signal = None
    best_scores = None
    best_composite = -1.0

    for candidate in candidates:
        scores = _score_single_signal(candidate)
        if scores.composite > best_composite:
            best_composite = scores.composite
            best_signal = candidate
            best_scores = scores

    return best_signal, best_scores


def _score_single_signal(signal: CandidateSignal) -> SignalConfidenceScores:
    prompt = f"""Score this signal across 4 dimensions for a B2B RevOps/data intelligence audience.

SIGNAL:
Title: {signal.title}
URL: {signal.url}
Date: {signal.date}
Summary: {signal.summary}

Score each dimension 0-10:
1. Source Authority (0-10): Is it from a known publication, research institution, or credible company?
2. Recency (0-10): How recent? Prefer < 30 days. >60 days = score 0-3.
3. Keyword Relevance (0-10): How tightly tied to RevOps/growth/data intelligence?
4. Novelty (0-10): Is this underreported or already saturated?

Composite = (authority * 0.3) + (recency * 0.25) + (relevance * 0.3) + (novelty * 0.15)

Return ONLY JSON:
{{
  "authority": 8.0,
  "recency": 7.5,
  "relevance": 9.0,
  "novelty": 6.0,
  "composite": 7.9
}}"""

    response = call_claude(BASE_SYSTEM_PROMPT, prompt, max_tokens=300)

    try:
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        data = json.loads(cleaned)
        authority = float(data.get("authority", 5.0))
        recency = float(data.get("recency", 5.0))
        relevance = float(data.get("relevance", 5.0))
        novelty = float(data.get("novelty", 5.0))
        composite = (authority * 0.3) + (recency * 0.25) + (relevance * 0.3) + (novelty * 0.15)
        return SignalConfidenceScores(
            authority=authority,
            recency=recency,
            relevance=relevance,
            novelty=novelty,
            composite=round(composite, 2),
        )
    except (json.JSONDecodeError, KeyError, ValueError):
        return SignalConfidenceScores(
            authority=5.0, recency=5.0, relevance=5.0, novelty=5.0, composite=5.0
        )
