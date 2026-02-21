"""Strategy Brief Generator Agent."""
import json
from agents.base import BASE_SYSTEM_PROMPT, call_claude

STRATEGY_BRIEF_SYSTEM = BASE_SYSTEM_PROMPT + """

STRATEGY BRIEF AGENT:
Your job is editorial judgment. Do not just pick the obvious angle. Think about what top 10 SERP results are NOT saying and position DataVex to fill that gap. Show your rejected angles and reasoning — this is as important as the chosen angle."""


def generate_strategy_brief(
    keyword: str,
    validated_signal: dict,
    identified_gaps: list[str],
    competitor_angles: list[str],
) -> dict:
    facts_text = "\n".join(f"- {f}" for f in validated_signal.get("validated_facts", []))
    gaps_text = "\n".join(f"- {g}" for g in identified_gaps)
    angles_text = "\n".join(f"- {a}" for a in competitor_angles)

    prompt = f"""Generate a comprehensive Strategy Brief for a DataVex content piece targeting the keyword "{keyword}".

VALIDATED SIGNAL:
Title: {validated_signal['title']}
URL: {validated_signal['url']}
Date: {validated_signal['date']}
Summary: {validated_signal['summary']}

KEY FACTS FROM SIGNAL:
{facts_text}

WHAT COMPETITORS ARE COVERING:
{angles_text}

CONTENT GAPS TO EXPLOIT:
{gaps_text}

Generate the Strategy Brief. Think like a demanding editorial director who rejects obvious angles.

Return ONLY JSON matching this exact structure:
{{
  "signal_summary": "2-3 sentence summary of the signal and why it matters now",
  "chosen_angle": "The specific underreported angle we will take",
  "angle_rationale": "Why this angle wins: specific reasoning tied to gaps and DataVex positioning",
  "rejected_angles": [
    {{"angle": "rejected angle 1", "reason": "why rejected"}},
    {{"angle": "rejected angle 2", "reason": "why rejected"}},
    {{"angle": "rejected angle 3", "reason": "why rejected"}}
  ],
  "competitive_gap_exploited": "Specific gap we are filling that no top-10 result addresses",
  "core_positioning_thesis": "The central argument DataVex will own with this piece",
  "platform_distribution_plan": {{
    "blog": "How the blog version will be positioned and targeted",
    "linkedin": "LinkedIn strategy: who we target, what action we want",
    "twitter": "Twitter strategy: hook type, controversy level, CTA"
  }},
  "target_audience": "Specific role and company type this piece is written for",
  "estimated_authority_score": 82
}}"""

    response = call_claude(STRATEGY_BRIEF_SYSTEM, prompt, max_tokens=2000)

    try:
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        return json.loads(cleaned)
    except (json.JSONDecodeError, KeyError):
        return {
            "signal_summary": validated_signal["summary"],
            "chosen_angle": f"How {keyword} reveals a gap in traditional analytics",
            "angle_rationale": "This angle is underreported and aligns with DataVex's signal-first positioning.",
            "rejected_angles": [
                {"angle": "General overview", "reason": "Already covered by 8 of top 10 results"},
                {"angle": "Vendor comparison", "reason": "Drives no authority for DataVex"},
            ],
            "competitive_gap_exploited": "No one is covering the revenue impact for RevOps teams specifically",
            "core_positioning_thesis": f"DataVex shows you the {keyword} signals before they become problems.",
            "platform_distribution_plan": {
                "blog": "Long-form technical guide for RevOps leads",
                "linkedin": "Insight-driven post targeting VP Growth",
                "twitter": "Controversial take thread targeting data practitioners",
            },
            "target_audience": "RevOps leads and VP Growth at B2B SaaS companies (50-500 employees)",
            "estimated_authority_score": 75,
        }
