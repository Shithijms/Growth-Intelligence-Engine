"""Long-form blog generator (800–1200 words). Platform-native, same signal/angle; DataVex in final 10–15%."""
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from config import settings
from utils.schemas import ExternalSignal, PositioningHooks, StrategyBrief
from utils.logging import get_logger

logger = get_logger(__name__)

LLM = ChatGoogleGenerativeAI(
    model=settings.llm_content,
    temperature=0.5,
    google_api_key=settings.google_api_key or None,
)


def generate_blog_draft(
    brief: StrategyBrief,
    signal: ExternalSignal,
    positioning: PositioningHooks,
    draft_instruction: str = "",
) -> str:
    """
    Generate one blog draft. If draft_instruction is set, it's critique feedback for a revision.
    Blog: 800–1200 words, problem-first, data-backed. DataVex only in final 10–15%.
    """
    system = """You write technical long-form blog posts for data/ML engineers. Tone: direct, contrarian, no hype.
Requirements:
- 800–1200 words
- Problem-first, then signal, then argument
- Cite the signal/source; no generic claims
- DataVex or product mention ONLY in the final 10–15% of the post (one short section)
- No "revolutionary", "game-changing", or sales CTAs
- Clear structure: hook, context, signal, argument, implication, optional DataVex tie-in at end"""

    base_user = f"""Signal: {signal.title}
Source: {signal.source}
Summary: {signal.summary}

Chosen angle: {brief.chosen_angle}
Why this angle wins: {brief.why_this_angle_wins}
Core thesis: {brief.core_thesis}

DataVex tail section (use only at end, in final 10–15%): {positioning.blog_tail_insight}
"""

    if draft_instruction:
        base_user += f"\nRevision request (incorporate this feedback):\n{draft_instruction}\n"

    user = base_user + "\nWrite the full blog post now. Output only the post, no meta commentary."

    resp = LLM.invoke([SystemMessage(content=system), HumanMessage(content=user)])
    return (resp.content or "").strip()
