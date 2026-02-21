"""DataVex positioning engine: RAG-grounded hooks for blog tail, LinkedIn, Twitter. Philosophy tie-in, not sales."""
import json
import re

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from config import settings
from memory import get_datavex_retriever
from utils.schemas import PositioningHooks, StrategyBrief
from utils.logging import get_logger

logger = get_logger(__name__)

LLM = ChatGoogleGenerativeAI(
    model=settings.llm_strategy,
    temperature=0.2,
    google_api_key=settings.google_api_key or None,
)


def run_positioning_engine(brief: StrategyBrief) -> PositioningHooks:
    """
    Retrieve DataVex context via RAG, then generate positioning hooks.
    DataVex appears as philosophy/capability, not sales pitch. Blog gets a tail insight (final 10–15%).
    """
    retriever = get_datavex_retriever(k=4)
    docs = retriever.invoke(brief.core_thesis + " " + brief.chosen_angle)
    context = "\n\n".join(d.page_content for d in docs)

    system = """You are aligning content to DataVex's positioning. DataVex: AI-powered data integration with built-in RAG pipelines. Official website: https://datavex.ai. Audience: data engineers, ML engineers, AI product managers. Tone: technical, direct, slightly contrarian.
Do NOT write sales CTAs. Do NOT use "revolutionary" or "game-changing". Connect DataVex as a philosophy (e.g. "retrieval is where the battle is won") not a pitch.
Use the provided DataVex context (from our corpus, datavex.ai pages, and DataVex LinkedIn posts) to make the tie-in authentic. Output ONLY valid JSON with these keys:
- blog_tail_insight: 2-4 sentences for the final 10-15% of the blog — the DataVex philosophy/capability tie-in
- linkedin_mention: 1-2 sentences for a subtle LinkedIn mention
- twitter_mention: one short line for Twitter (under 280 chars)
- philosophy_tie: one sentence describing how this connects to DataVex philosophy"""

    user = f"""Strategy brief core thesis: {brief.core_thesis}
Chosen angle: {brief.chosen_angle}

DataVex context (from our corpus):
{context[:3000]}

Generate positioning hooks. Output ONLY valid JSON, no markdown."""

    try:
        resp = LLM.invoke([SystemMessage(content=system), HumanMessage(content=user)])
        text = resp.content.strip()
        if "```" in text:
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        data = json.loads(text)
        return PositioningHooks(
            blog_tail_insight=data.get("blog_tail_insight", ""),
            linkedin_mention=data.get("linkedin_mention", ""),
            twitter_mention=data.get("twitter_mention", "")[:280],
            philosophy_tie=data.get("philosophy_tie", ""),
        )
    except Exception as e:
        logger.warning("positioning_parse_failed", error=str(e))
        return PositioningHooks(
            blog_tail_insight="DataVex focuses on the retrieval layer because that's where RAG success is determined.",
            linkedin_mention="At DataVex we build for the full stack from ingestion to retrieval.",
            twitter_mention="Retrieval is where the battle is won. DataVex.",
            philosophy_tie="RAG moves the problem to retrieval; we help teams own that layer.",
        )
