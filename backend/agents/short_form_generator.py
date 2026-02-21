"""Short Form Generator Agent — LinkedIn post + Twitter/X thread."""
import json
from agents.base import BASE_SYSTEM_PROMPT, call_claude

SHORT_FORM_SYSTEM = BASE_SYSTEM_PROMPT + """

SHORT FORM GENERATOR AGENT:
Generate platform-native content. LinkedIn rewards vulnerability + insight. Twitter rewards specificity + controversy. Write natively for each platform — not just a reformatted blog excerpt."""


def generate_short_form(
    strategy_brief: dict,
    validated_signal: dict,
    draft_number: int = 1,
    linkedin_critique: str = "",
    twitter_critique: str = "",
) -> dict:
    facts = validated_signal.get("validated_facts", [])
    facts_text = "\n".join(f"- {f}" for f in facts[:3])
    signal_title = validated_signal.get("title", "")
    signal_url = validated_signal.get("url", "")

    linkedin_rewrite = f"\nLINKEDIN REWRITE INSTRUCTIONS:\n{linkedin_critique}" if linkedin_critique else ""
    twitter_rewrite = f"\nTWITTER REWRITE INSTRUCTIONS:\n{twitter_critique}" if twitter_critique else ""

    prompt = f"""Generate both a LinkedIn post and a Twitter/X thread about the following topic.

CHOSEN ANGLE: {strategy_brief.get('chosen_angle', '')}
TARGET AUDIENCE: {strategy_brief.get('target_audience', '')}
CORE THESIS: {strategy_brief.get('core_positioning_thesis', '')}
SIGNAL: {signal_title} ({signal_url})

KEY FACTS:
{facts_text}

LINKEDIN STRATEGY: {strategy_brief.get('platform_distribution_plan', {}).get('linkedin', '')}
TWITTER STRATEGY: {strategy_brief.get('platform_distribution_plan', {}).get('twitter', '')}
{linkedin_rewrite}
{twitter_rewrite}

LINKEDIN POST REQUIREMENTS:
- 200-300 words total
- First line: standalone hook that stops the scroll (no emojis, no "I want to share")
- 3-5 insight paragraphs (single-line paragraphs, white space between)
- Include one specific data point from the signal
- Subtle DataVex mention (practitioner voice, not ad)
- 3 relevant hashtags at the end
- CTA: ask a question or invite perspective (not "book a demo")

TWITTER THREAD REQUIREMENTS:
- 6-8 tweets
- Tweet 1: Hook tweet — bold claim or counterintuitive statement (standalone value)
- Tweets 2-6: One sharp insight per tweet, numbered format (2/8, 3/8...)
- Tweet 7: DataVex angle — what DataVex sees/measures, practitioner POV
- Tweet 8: CTA tweet with [LINK] placeholder
- Each tweet MUST be under 280 characters (strict)

Return ONLY JSON:
{{
  "linkedin": "Full LinkedIn post text...",
  "twitter_tweets": [
    "Tweet 1 text (hook)",
    "2/8 Tweet 2 text",
    "3/8 Tweet 3 text",
    "4/8 Tweet 4 text",
    "5/8 Tweet 5 text",
    "6/8 Tweet 6 text",
    "7/8 DataVex angle tweet",
    "8/8 CTA tweet [LINK]"
  ]
}}"""

    response = call_claude(SHORT_FORM_SYSTEM, prompt, max_tokens=3000)

    try:
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        data = json.loads(cleaned)
        return {
            "linkedin": data.get("linkedin", ""),
            "twitter_tweets": data.get("twitter_tweets", []),
        }
    except (json.JSONDecodeError, KeyError):
        return {
            "linkedin": response[:600],
            "twitter_tweets": [response[:280]],
        }
