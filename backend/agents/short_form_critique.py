"""Short Form Critique Agent — 5-dimension scoring for LinkedIn + Twitter."""
import json
from agents.base import BASE_SYSTEM_PROMPT, call_claude
from models import ShortFormScores

SHORT_FORM_CRITIQUE_SYSTEM = BASE_SYSTEM_PROMPT + """

CRITIQUE AGENT (SHORT FORM):
You are a platform-native content strategist. You know that LinkedIn rewards vulnerability + insight, and Twitter rewards specificity + controversy. Score for platform fit above all. A brilliant insight in the wrong format fails."""


def critique_short_form(
    linkedin_draft: str,
    twitter_tweets: list[str],
    draft_number: int,
) -> dict:
    tweets_text = "\n".join([f"[{i+1}] {t}" for i, t in enumerate(twitter_tweets)])

    prompt = f"""Critique this LinkedIn post and Twitter thread. Score each platform's content across 5 dimensions.

--- LINKEDIN POST (Draft {draft_number}) ---
{linkedin_draft[:1500]}

--- TWITTER THREAD (Draft {draft_number}) ---
{tweets_text[:1500]}

Score each asset (LinkedIn and Twitter) separately across 5 dimensions (0-10 each):
1. Hook Density: Does the opening line immediately deliver value/tension?
2. Platform Native Feel: Does it feel native to the platform (not a reformatted blog)?
3. Engagement Trigger Strength: Does it make people want to comment or share?
4. Shareability: Would a RevOps lead reshare this to their team?
5. Brand Fit: Does DataVex come across as a practitioner, not an advertiser?

For any dimension under 8, give SPECIFIC rewrite instructions (not vague guidance).

Return ONLY JSON:
{{
  "linkedin_scores": {{
    "hook_density": 7.0,
    "platform_native_feel": 8.0,
    "engagement_trigger_strength": 6.5,
    "shareability": 7.5,
    "brand_fit": 8.0
  }},
  "twitter_scores": {{
    "hook_density": 8.0,
    "platform_native_feel": 7.5,
    "engagement_trigger_strength": 7.0,
    "shareability": 6.5,
    "brand_fit": 7.5
  }},
  "linkedin_rewrite_instructions": [
    "Hook: Replace opening line with a specific stat + counterintuitive claim, e.g. '73% of RevOps teams track pipeline health weekly. 91% still miss churn signals the week it matters.'"
  ],
  "twitter_rewrite_instructions": [
    "Tweet 1: Make it more controversial — lead with what everyone is doing wrong, not what you're going to share."
  ]
}}"""

    response = call_claude(SHORT_FORM_CRITIQUE_SYSTEM, prompt, max_tokens=1800)

    try:
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        data = json.loads(cleaned)

        def parse_scores(raw: dict) -> ShortFormScores:
            return ShortFormScores(
                hook_density=float(raw.get("hook_density", 5.0)),
                platform_native_feel=float(raw.get("platform_native_feel", 5.0)),
                engagement_trigger_strength=float(raw.get("engagement_trigger_strength", 5.0)),
                shareability=float(raw.get("shareability", 5.0)),
                brand_fit=float(raw.get("brand_fit", 5.0)),
            )

        li_scores = parse_scores(data.get("linkedin_scores", {}))
        tw_scores = parse_scores(data.get("twitter_scores", {}))
        li_instructions = "\n".join(data.get("linkedin_rewrite_instructions", []))
        tw_instructions = "\n".join(data.get("twitter_rewrite_instructions", []))

        return {
            "linkedin_scores": li_scores,
            "twitter_scores": tw_scores,
            "linkedin_rewrite_instructions": li_instructions,
            "twitter_rewrite_instructions": tw_instructions,
        }
    except (json.JSONDecodeError, KeyError, ValueError):
        default = ShortFormScores(
            hook_density=5.0, platform_native_feel=5.0,
            engagement_trigger_strength=5.0, shareability=5.0, brand_fit=5.0
        )
        return {
            "linkedin_scores": default,
            "twitter_scores": default,
            "linkedin_rewrite_instructions": "",
            "twitter_rewrite_instructions": "",
        }
