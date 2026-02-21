"""Single pipeline: keyword → signal → gap → brief → positioning → content (blog, LinkedIn, Twitter) → critique loops → final state."""
import time

from agents.critique import critique_and_score
from agents.long_form import generate_blog_draft
from agents.positioning import run_positioning_engine
from agents.short_form import generate_linkedin_draft, generate_twitter_thread_draft
from agents.signal import run_signal_discovery
from agents.strategy import run_gap_analysis, run_strategy_brief
from config import settings
from utils.logging import get_logger
from utils.schemas import (
    ContentAssets,
    ContentWithCritiqueTrace,
    PipelineState,
)

logger = get_logger(__name__)


def _run_blog_with_critique_loop(
    brief,
    signal,
    positioning,
) -> ContentWithCritiqueTrace:
    """Draft 1 → Critique 1 → Draft 2 (with feedback) → Critique 2 → Final = Draft 2."""
    drafts = []
    critiques = []
    score_evolution = []

    # Draft 1
    d1 = generate_blog_draft(brief, signal, positioning)
    drafts.append(d1)
    c1 = critique_and_score(d1, "blog", 1)
    critiques.append(c1)
    score_evolution.append(c1.scores)

    # Draft 2 with feedback
    d2 = generate_blog_draft(brief, signal, positioning, draft_instruction=c1.feedback)
    drafts.append(d2)
    c2 = critique_and_score(d2, "blog", 2)
    critiques.append(c2)
    score_evolution.append(c2.scores)

    return ContentWithCritiqueTrace(
        final_content=d2,
        drafts=drafts,
        critiques=[c1, c2],
        score_evolution=score_evolution,
    )


def _run_linkedin_with_critique_loop(
    brief,
    signal,
    positioning,
) -> ContentWithCritiqueTrace:
    d1 = generate_linkedin_draft(brief, signal, positioning)
    c1 = critique_and_score(d1, "linkedin", 1)
    d2 = generate_linkedin_draft(brief, signal, positioning, draft_instruction=c1.feedback)
    c2 = critique_and_score(d2, "linkedin", 2)
    return ContentWithCritiqueTrace(
        final_content=d2,
        drafts=[d1, d2],
        critiques=[c1, c2],
        score_evolution=[c1.scores, c2.scores],
    )


def _run_twitter_with_critique_loop(
    brief,
    signal,
    positioning,
) -> ContentWithCritiqueTrace:
    d1 = generate_twitter_thread_draft(brief, signal, positioning)
    c1 = critique_and_score(d1, "twitter", 1)
    d2 = generate_twitter_thread_draft(brief, signal, positioning, draft_instruction=c1.feedback)
    c2 = critique_and_score(d2, "twitter", 2)
    return ContentWithCritiqueTrace(
        final_content=d2,
        drafts=[d1, d2],
        critiques=[c1, c2],
        score_evolution=[c1.scores, c2.scores],
    )


def run_pipeline(keyword: str) -> PipelineState:
    """
    Run full pipeline. Aborts if signal confidence below threshold.
    Records stage timings and total latency.
    """
    state = PipelineState(keyword=keyword)
    t0 = time.perf_counter()
    stage_timings = {}

    # 1) Signal discovery
    t = time.perf_counter()
    signal_result = run_signal_discovery(keyword)
    state.signal_result = signal_result
    stage_timings["signal"] = round(time.perf_counter() - t, 2)

    if signal_result.abort_reason or signal_result.confidence_score < settings.signal_confidence_threshold:
        state.aborted = True
        state.abort_reason = signal_result.abort_reason or (
            f"Signal confidence {signal_result.confidence_score} below threshold {settings.signal_confidence_threshold}"
        )
        state.total_latency_seconds = round(time.perf_counter() - t0, 2)
        state.stage_timings_seconds = stage_timings
        return state

    signal = signal_result.signal

    # 2) Gap analysis
    t = time.perf_counter()
    gap = run_gap_analysis(keyword, signal)
    state.gap_analysis = gap
    stage_timings["gap_analysis"] = round(time.perf_counter() - t, 2)

    # 3) Strategy brief
    t = time.perf_counter()
    brief = run_strategy_brief(keyword, signal, gap)
    state.strategy_brief = brief
    stage_timings["strategy_brief"] = round(time.perf_counter() - t, 2)

    # 4) Positioning
    t = time.perf_counter()
    positioning = run_positioning_engine(brief)
    state.positioning = positioning
    stage_timings["positioning"] = round(time.perf_counter() - t, 2)

    # 5) Content + critique loops (all three assets)
    t = time.perf_counter()
    blog_trace = _run_blog_with_critique_loop(brief, signal, positioning)
    stage_timings["blog"] = round(time.perf_counter() - t, 2)

    t = time.perf_counter()
    linkedin_trace = _run_linkedin_with_critique_loop(brief, signal, positioning)
    stage_timings["linkedin"] = round(time.perf_counter() - t, 2)

    t = time.perf_counter()
    twitter_trace = _run_twitter_with_critique_loop(brief, signal, positioning)
    stage_timings["twitter"] = round(time.perf_counter() - t, 2)

    state.content_assets = ContentAssets(
        blog=blog_trace,
        linkedin=linkedin_trace,
        twitter_thread=twitter_trace,
    )
    state.total_latency_seconds = round(time.perf_counter() - t0, 2)
    state.stage_timings_seconds = stage_timings
    return state
