"""SERP Scanner + Competitive Gap Analyzer."""
import json
from tavily import TavilyClient
from config import get_settings
from agents.base import BASE_SYSTEM_PROMPT, call_claude


def scan_serp_and_find_gaps(keyword: str) -> dict:
    settings = get_settings()
    client = TavilyClient(api_key=settings.tavily_api_key)

    results = client.search(
        query=keyword,
        search_depth="advanced",
        max_results=10,
    )

    raw_results = results.get("results", [])
    articles_text = "\n\n".join([
        f"Title: {r.get('title', 'N/A')}\n"
        f"URL: {r.get('url', 'N/A')}\n"
        f"Snippet: {r.get('content', '')[:400]}"
        for r in raw_results
    ])

    prompt = f"""Analyze these top 10 SERP results for the keyword "{keyword}" and identify:

TOP 10 SERP RESULTS:
{articles_text}

Tasks:
1. Identify the 5-7 angles/narratives these results ARE covering (competitor_angles)
2. Identify 4-6 angles these results are NOT covering — gaps a DataVex-positioned piece could own (identified_gaps)

Focus on what's missing for a RevOps/growth/data team audience.

Return ONLY JSON:
{{
  "competitor_angles": [
    "angle 1 being covered",
    "angle 2 being covered"
  ],
  "identified_gaps": [
    "gap 1 not covered — opportunity description",
    "gap 2 not covered — opportunity description"
  ]
}}"""

    response = call_claude(BASE_SYSTEM_PROMPT, prompt, max_tokens=1000)

    try:
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        data = json.loads(cleaned)
        return {
            "competitor_angles": data.get("competitor_angles", []),
            "identified_gaps": data.get("identified_gaps", []),
        }
    except (json.JSONDecodeError, KeyError):
        return {
            "competitor_angles": ["General overviews", "Vendor comparisons"],
            "identified_gaps": ["RevOps-specific implementation guide", "ROI measurement framework"],
        }
