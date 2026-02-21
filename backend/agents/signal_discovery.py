"""Signal Discovery Agent — Tavily search for top 5 signals."""
import json
from tavily import TavilyClient
from config import get_settings
from models import CandidateSignal
from agents.base import BASE_SYSTEM_PROMPT, call_claude

SIGNAL_DISCOVERY_PROMPT = BASE_SYSTEM_PROMPT + """

SIGNAL DISCOVERY AGENT:
Your job is to find the most leverage-rich, underreported signal tied to the keyword. Prioritize primary sources. Reject anything older than 60 days or from low-authority sources. Return structured data only."""


def discover_signals(keyword: str) -> list[CandidateSignal]:
    settings = get_settings()
    client = TavilyClient(api_key=settings.tavily_api_key)

    results = client.search(
        query=f"{keyword} latest news research announcement 2024 2025",
        search_depth="advanced",
        max_results=8,
        include_published_date=True,
    )

    raw_results = results.get("results", [])

    # Use Claude to score and rank the signals
    articles_text = "\n\n".join([
        f"Title: {r.get('title', 'N/A')}\n"
        f"URL: {r.get('url', 'N/A')}\n"
        f"Date: {r.get('published_date', 'Unknown')}\n"
        f"Content: {r.get('content', '')[:500]}"
        for r in raw_results
    ])

    prompt = f"""Given the keyword "{keyword}", evaluate these articles and return the top 5 most relevant signals.

ARTICLES:
{articles_text}

Return a JSON array of exactly 5 objects with this structure:
[
  {{
    "title": "article title",
    "url": "article url",
    "date": "published date or estimated",
    "summary": "2-3 sentence summary of why this signal matters for DataVex audience",
    "relevance_score": 8.5
  }}
]

Prioritize: primary sources, recency, novelty, and relevance to {keyword} for RevOps/growth teams.
Return ONLY the JSON array, no other text."""

    response = call_claude(SIGNAL_DISCOVERY_PROMPT, prompt, max_tokens=2000)

    # Parse JSON from response
    try:
        # Strip any markdown code blocks if present
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        data = json.loads(cleaned)
        return [CandidateSignal(**item) for item in data[:5]]
    except (json.JSONDecodeError, KeyError, TypeError):
        # Fallback: use raw Tavily results
        fallback = []
        for r in raw_results[:5]:
            fallback.append(CandidateSignal(
                title=r.get("title", "Unknown"),
                url=r.get("url", ""),
                date=r.get("published_date", "Unknown"),
                summary=r.get("content", "")[:300],
                relevance_score=5.0,
            ))
        return fallback
