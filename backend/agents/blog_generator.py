"""Blog Generator Agent — 800-1200 word SEO blog post."""
import json
from agents.base import BASE_SYSTEM_PROMPT, call_claude

BLOG_GEN_SYSTEM = BASE_SYSTEM_PROMPT + """

BLOG GENERATOR AGENT:
Write a high-authority, signal-backed SEO blog post. The first two sentences must hook the reader immediately. Weave in DataVex positioning naturally — never salesy. Use H1/H2/H3 structure. Every claim must connect to the signal data. Write for data-literate RevOps and growth practitioners."""


def generate_blog_draft(
    strategy_brief: dict,
    validated_signal: dict,
    draft_number: int = 1,
    critique_instructions: str = "",
) -> dict:
    facts_text = "\n".join(f"- {f}" for f in validated_signal.get("validated_facts", []))

    rewrite_section = ""
    if critique_instructions:
        rewrite_section = f"""
CRITIQUE INSTRUCTIONS FROM EDITOR (apply all of these):
{critique_instructions}
"""

    prompt = f"""Write an 800-1200 word SEO blog post about the following topic.

KEYWORD: {strategy_brief.get('core_positioning_thesis', '')}
CHOSEN ANGLE: {strategy_brief.get('chosen_angle', '')}
TARGET AUDIENCE: {strategy_brief.get('target_audience', '')}

SIGNAL TO CITE:
Title: {validated_signal['title']}
URL: {validated_signal['url']}
Date: {validated_signal['date']}

KEY FACTS TO INCORPORATE:
{facts_text}

POSITIONING THESIS:
{strategy_brief.get('core_positioning_thesis', '')}

DISTRIBUTION CONTEXT:
{strategy_brief.get('platform_distribution_plan', {}).get('blog', '')}
{rewrite_section}

BLOG REQUIREMENTS:
- First 2 sentences: problem-first hook that grabs immediately (no warm-up, no context-setting)
- H1 + at least 3 H2s + H3s where appropriate
- At least 2 specific data points from the signal (cite title and URL inline)
- DataVex positioning woven in naturally in 1-2 places (not salesy — show the insight, not the product)
- CTA at the end: specific, non-salesy, practitioner-focused
- No buzzwords, no passive voice, no hedging

Return ONLY JSON:
{{
  "draft": "# H1 Title\\n\\nFull blog post in markdown...",
  "meta_title": "SEO meta title under 60 characters",
  "meta_description": "SEO meta description 140-160 characters"
}}"""

    response = call_claude(BLOG_GEN_SYSTEM, prompt, max_tokens=4096)

    try:
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        data = json.loads(cleaned)
        return {
            "draft": data.get("draft", response),
            "meta_title": data.get("meta_title", "DataVex Intelligence Report"),
            "meta_description": data.get("meta_description", strategy_brief.get("signal_summary", "")[:160]),
        }
    except (json.JSONDecodeError, KeyError):
        return {
            "draft": response,
            "meta_title": "DataVex Intelligence Report",
            "meta_description": strategy_brief.get("signal_summary", "")[:160],
        }
