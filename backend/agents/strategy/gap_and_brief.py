"""Competitive gap analysis and strategy brief (editorial judgment). Uses LLM only; no RAG for decisions."""
import json
import re

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from config.settings import require_google_api_key, settings
from utils.schemas import (
    ExternalSignal,
    GapAnalysis,
    RejectedAngle,
    StrategyBrief,
)
from utils.logging import get_logger

logger = get_logger(__name__)

_LLM: ChatGoogleGenerativeAI | None = None


def _get_llm() -> ChatGoogleGenerativeAI:
    global _LLM
    if _LLM is None:
        _LLM = ChatGoogleGenerativeAI(
            model=settings.llm_strategy,
            temperature=0.3,
            google_api_key=require_google_api_key(),
        )
    return _LLM


def run_gap_analysis(keyword: str, signal: ExternalSignal) -> GapAnalysis:
    """
    Analyze existing content landscape for the keyword. Identify saturated angles and narratives to avoid.
    """
    system = """You are an editorial strategist. Given a keyword and a real-world signal, analyze the competitive content landscape.
Output a JSON object with these exact keys:
- saturated_angles: list of 3-5 angles that are already overused in content for this keyword
- common_narratives: list of 2-4 narrative clichés to avoid
- angles_to_avoid: list of 2-4 specific angles we should NOT use (with brief reason implied)
- summary: 2-3 sentence summary of the gap opportunity

Be specific and actionable. No hype."""

    user = f"""Keyword: {keyword}
Signal we have: {signal.title}
Source: {signal.source}
Summary: {signal.summary}

Analyze the content landscape for "{keyword}". What angles are saturated? What should we avoid? Output ONLY valid JSON, no markdown."""

    try:
        resp = _get_llm().invoke([SystemMessage(content=system), HumanMessage(content=user)])
        text = resp.content.strip()
        # Strip markdown code block if present
        if "```" in text:
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        data = json.loads(text)
        return GapAnalysis(
            saturated_angles=data.get("saturated_angles", []),
            common_narratives=data.get("common_narratives", []),
            angles_to_avoid=data.get("angles_to_avoid", []),
            summary=data.get("summary", ""),
        )
    except Exception as e:
        logger.warning("gap_analysis_parse_failed", error=str(e))
        return GapAnalysis(
            saturated_angles=[],
            common_narratives=[],
            angles_to_avoid=[],
            summary="Gap analysis unavailable.",
        )


def run_strategy_brief(
    keyword: str,
    signal: ExternalSignal,
    gap: GapAnalysis,
) -> StrategyBrief:
    """
    Generate strategy brief: signal summary, chosen angle, why it wins, rejected angles with reasons, platform strategy.
    """
    system = """You are a growth editor. Produce a strategy brief for a single piece of content (blog + LinkedIn + Twitter).
Output a JSON object with these exact keys:
- signal_summary: 2-3 sentence summary of the external signal
- chosen_angle: one contrarian, defensible, actionable angle (one sentence)
- why_this_angle_wins: 2-3 sentences on why this angle differentiates
- rejected_angles: list of objects, each with "angle" and "reason_rejected" (2-3 items)
- platform_strategy: how we'll adapt the same angle for blog (long), LinkedIn (professional), Twitter (thread)
- core_thesis: one sentence core message

Be contrarian and specific. No hype. No sales CTAs."""

    user = f"""Keyword: {keyword}
Signal: {signal.title} — {signal.summary}
Source: {signal.source}

Gap analysis (avoid these):
Saturated angles: {gap.saturated_angles}
Common narratives to avoid: {gap.common_narratives}
Angles to avoid: {gap.angles_to_avoid}
Summary: {gap.summary}

Generate the strategy brief. Output ONLY valid JSON, no markdown."""

    try:
        resp = _get_llm().invoke([SystemMessage(content=system), HumanMessage(content=user)])
        text = resp.content.strip()
        if "```" in text:
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        data = json.loads(text)
        rejected = [
            RejectedAngle(angle=x.get("angle", ""), reason_rejected=x.get("reason_rejected", ""))
            for x in data.get("rejected_angles", [])
        ]
        return StrategyBrief(
            signal_summary=data.get("signal_summary", ""),
            chosen_angle=data.get("chosen_angle", ""),
            why_this_angle_wins=data.get("why_this_angle_wins", ""),
            rejected_angles=rejected,
            platform_strategy=data.get("platform_strategy", ""),
            core_thesis=data.get("core_thesis", ""),
        )
    except Exception as e:
        logger.warning("strategy_brief_parse_failed", error=str(e))
        return StrategyBrief(
            signal_summary=signal.summary[:300],
            chosen_angle="Use the signal to argue a contrarian, technical angle.",
            why_this_angle_wins="Differentiation through specificity.",
            rejected_angles=[],
            platform_strategy="Blog: long-form; LinkedIn: professional take; Twitter: thread.",
            core_thesis=signal.summary[:200],
        )
