"""Blog Critique Agent — 6-dimension scoring and rewrite loop."""
import json
from agents.base import BASE_SYSTEM_PROMPT, call_claude
from models import BlogScores

BLOG_CRITIQUE_SYSTEM = BASE_SYSTEM_PROMPT + """

CRITIQUE AGENT (BLOG):
You are a demanding editorial director. You do not accept generic hooks, vague data references, or salesy tone. Score ruthlessly. Your rewrite instructions must be specific — not 'improve the hook' but 'rewrite the opening sentence to lead with the specific stat from the signal.'"""


def critique_blog(blog_draft: str, draft_number: int) -> dict:
    prompt = f"""Critique this blog post draft ruthlessly. Score each dimension 0-10.

BLOG DRAFT {draft_number}:
{blog_draft[:4000]}

Score across these 6 dimensions (0-10 each):
1. Hook Strength: Do the first 2 sentences grab immediately without warm-up?
2. Clarity: Is every sentence clear, direct, and jargon-free?
3. Authority Tone: Does this read like an expert practitioner, not a vendor?
4. Differentiation: Is this angle something a competitor could NOT publish?
5. Logical Structure: Does the H1/H2/H3 structure flow logically to the CTA?
6. DataVex Brand Fit: Is DataVex positioned as practitioner, not salesperson?

For any dimension scoring below 8, provide specific rewrite instructions (not generic advice).

Return ONLY JSON:
{{
  "scores": {{
    "hook_strength": 7.5,
    "clarity": 8.0,
    "authority_tone": 7.0,
    "differentiation": 6.5,
    "logical_structure": 8.5,
    "datavex_brand_fit": 7.0
  }},
  "rewrite_instructions": [
    "Hook: Rewrite sentence 1 to open with the specific [X%] stat from the signal instead of the setup question.",
    "Differentiation: In section 2, replace the generic market overview with a specific before/after scenario from a RevOps team perspective."
  ],
  "overall_verdict": "Brief overall assessment"
}}"""

    response = call_claude(BLOG_CRITIQUE_SYSTEM, prompt, max_tokens=1500)

    try:
        cleaned = response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        data = json.loads(cleaned)
        scores_raw = data.get("scores", {})
        scores = BlogScores(
            hook_strength=float(scores_raw.get("hook_strength", 5.0)),
            clarity=float(scores_raw.get("clarity", 5.0)),
            authority_tone=float(scores_raw.get("authority_tone", 5.0)),
            differentiation=float(scores_raw.get("differentiation", 5.0)),
            logical_structure=float(scores_raw.get("logical_structure", 5.0)),
            datavex_brand_fit=float(scores_raw.get("datavex_brand_fit", 5.0)),
        )
        instructions = "\n".join(data.get("rewrite_instructions", []))
        verdict = data.get("overall_verdict", "")
        return {"scores": scores, "rewrite_instructions": instructions, "verdict": verdict}
    except (json.JSONDecodeError, KeyError, ValueError):
        scores = BlogScores(
            hook_strength=5.0, clarity=5.0, authority_tone=5.0,
            differentiation=5.0, logical_structure=5.0, datavex_brand_fit=5.0
        )
        return {"scores": scores, "rewrite_instructions": "", "verdict": "Critique failed to parse"}
