"""Critique agent: substantive feedback + quantitative scores. No RAG for scoring."""
import json
import re

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from config.settings import require_google_api_key, settings
from utils.schemas import CritiqueResult, CritiqueScores
from utils.logging import get_logger

logger = get_logger(__name__)

_LLM: ChatGoogleGenerativeAI | None = None


def _get_llm() -> ChatGoogleGenerativeAI:
    global _LLM
    if _LLM is None:
        _LLM = ChatGoogleGenerativeAI(
            model=settings.llm_strategy,
            temperature=0.2,
            google_api_key=require_google_api_key(),
        )
    return _LLM


def _parse_scores(data: dict) -> CritiqueScores:
    """Extract 0–10 scores from LLM JSON; clamp to 0–10."""
    def f(key: str, default: float = 5.0) -> float:
        v = data.get(key, default)
        try:
            return min(10.0, max(0.0, float(v)))
        except (TypeError, ValueError):
            return default
    return CritiqueScores(
        hook_strength=f("hook_strength"),
        authority=f("authority"),
        differentiation=f("differentiation"),
        structure=f("structure"),
        platform_fit=f("platform_fit"),
    )


def critique_and_score(
    content: str,
    platform: str,  # "blog" | "linkedin" | "twitter"
    draft_number: int,
) -> CritiqueResult:
    """
    Produce substantive critique and 0–10 scores for hook_strength, authority, differentiation, structure, platform_fit.
    """
    system = """You are an editorial critic. Score the content on five dimensions (0–10 each) and give actionable feedback.
Dimensions:
- hook_strength: Does the opening grab attention and promise value?
- authority: Does it cite specifics, data, or sources (not generic)?
- differentiation: Is it contrarian or distinct vs typical content?
- structure: Is it clear and well-organized?
- platform_fit: Does it match the platform (blog = long-form; LinkedIn = professional; Twitter = punchy thread)?

Output a JSON object with keys: hook_strength, authority, differentiation, structure, platform_fit (numbers 0–10), and "feedback" (string, 2–4 substantive sentences on what to improve). Be specific. Output ONLY valid JSON."""

    user = f"""Platform: {platform}
Draft number: {draft_number}

Content:
{content[:8000]}

Score and critique. Output ONLY valid JSON."""

    try:
        resp = _get_llm().invoke([SystemMessage(content=system), HumanMessage(content=user)])
        text = resp.content.strip()
        if "```" in text:
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        data = json.loads(text)
        scores = _parse_scores(data)
        feedback = data.get("feedback", "")
        return CritiqueResult(scores=scores, feedback=feedback, draft_number=draft_number)
    except Exception as e:
        logger.warning("critique_parse_failed", error=str(e))
        return CritiqueResult(
            scores=CritiqueScores(hook_strength=5, authority=5, differentiation=5, structure=5, platform_fit=5),
            feedback="Could not parse critique; default scores applied.",
            draft_number=draft_number,
        )
