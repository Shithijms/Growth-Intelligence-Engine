"""Signal Validator — URL reachability + fact extraction."""
import json
import httpx
from models import CandidateSignal, SignalConfidenceScores
from agents.base import BASE_SYSTEM_PROMPT, call_claude


def validate_signal(
    signal: CandidateSignal,
    confidence_scores: SignalConfidenceScores,
) -> dict:
    """Validate signal URL and extract key facts."""
    # Check URL reachability
    url_reachable = False
    page_content = ""
    try:
        resp = httpx.get(signal.url, timeout=10, follow_redirects=True)
        url_reachable = resp.status_code == 200
        # Grab first 3000 chars of text for fact extraction
        page_content = resp.text[:3000]
    except Exception:
        url_reachable = False

    # Extract facts via Claude
    content_for_extraction = page_content if page_content else signal.summary

    prompt = f"""Analyze this article content and extract key facts, statistics, and quotes.

Article Title: {signal.title}
Content: {content_for_extraction[:2000]}

Tasks:
1. Extract 3-6 specific facts, stats, or quotes (prefer numbers and specifics)
2. Flag if this appears AI-generated or unreliable (check for vague claims, no specifics, inconsistent dates)

Return ONLY JSON:
{{
  "validated_facts": [
    "Specific fact 1 with number or concrete detail",
    "Specific quote or statistic 2",
    "Key finding 3"
  ],
  "is_ai_generated": false,
  "reliability_note": "brief note on source reliability"
}}"""

    response = call_claude(BASE_SYSTEM_PROMPT, prompt, max_tokens=600)

    try:
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        data = json.loads(cleaned)
        validated_facts = data.get("validated_facts", [signal.summary])
        is_ai_generated = data.get("is_ai_generated", False)
    except (json.JSONDecodeError, KeyError):
        validated_facts = [signal.summary]
        is_ai_generated = False

    return {
        "title": signal.title,
        "url": signal.url,
        "date": signal.date,
        "summary": signal.summary,
        "validated_facts": validated_facts,
        "is_ai_generated": is_ai_generated,
        "url_reachable": url_reachable,
        "confidence_scores": confidence_scores,
    }
