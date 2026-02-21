"""Short-form: LinkedIn (200–300 words) and Twitter thread (5–8 tweets). Platform-native, same signal/angle."""
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from config.settings import require_google_api_key, settings
from utils.schemas import ExternalSignal, PositioningHooks, StrategyBrief
from utils.logging import get_logger

logger = get_logger(__name__)

_LLM: ChatGoogleGenerativeAI | None = None


def _get_llm() -> ChatGoogleGenerativeAI:
    global _LLM
    if _LLM is None:
        _LLM = ChatGoogleGenerativeAI(
            model=settings.llm_content,
            temperature=0.5,
            google_api_key=require_google_api_key(),
        )
    return _LLM


def generate_linkedin_draft(
    brief: StrategyBrief,
    signal: ExternalSignal,
    positioning: PositioningHooks,
    draft_instruction: str = "",
) -> str:
    """LinkedIn post 200–300 words. Professional, hook-first. Light DataVex mention if natural."""
    system = """You write LinkedIn posts for data/ML professionals. Tone: professional, direct, slightly contrarian.
- 200–300 words
- Strong opening hook
- Same signal and angle as the blog, but condensed
- One short DataVex mention only if it fits naturally (no sales pitch)
- No hype words. No CTAs like "link in comments" unless we explicitly ask."""

    base = f"""Signal: {signal.title} — {signal.summary}
Angle: {brief.chosen_angle}
Core thesis: {brief.core_thesis}
Optional DataVex mention: {positioning.linkedin_mention}
"""
    if draft_instruction:
        base += f"\nRevision: {draft_instruction}\n"
    user = base + "\nWrite the LinkedIn post. Output only the post."

    resp = _get_llm().invoke([SystemMessage(content=system), HumanMessage(content=user)])
    return (resp.content or "").strip()


def generate_twitter_thread_draft(
    brief: StrategyBrief,
    signal: ExternalSignal,
    positioning: PositioningHooks,
    draft_instruction: str = "",
) -> str:
    """Twitter/X thread: 5–8 tweets. Return as single string, one tweet per line (or numbered 1/8, 2/8, etc.)."""
    system = """You write Twitter/X threads for technical audiences. Tone: punchy, direct.
- 5–8 tweets
- First tweet: hook + promise
- Each tweet stands alone but builds the thread
- Max ~280 chars per tweet
- Same signal and angle as blog/LinkedIn
- Final tweet can include a brief DataVex mention if natural
Output format: one tweet per line, optionally numbered (1/8, 2/8, ...). No other commentary."""

    base = f"""Signal: {signal.title} — {signal.summary}
Angle: {brief.chosen_angle}
Core thesis: {brief.core_thesis}
Optional DataVex: {positioning.twitter_mention}
"""
    if draft_instruction:
        base += f"\nRevision: {draft_instruction}\n"
    user = base + "\nWrite the thread. One tweet per line."

    resp = _get_llm().invoke([SystemMessage(content=system), HumanMessage(content=user)])
    return (resp.content or "").strip()
