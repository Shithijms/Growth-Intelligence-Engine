"""Shared Pydantic models for pipeline state and API."""
from typing import Any

from pydantic import BaseModel, Field


# --- Signal ---
class ExternalSignal(BaseModel):
    title: str
    source: str
    source_type: str  # paper | blog | survey | incident | other
    summary: str
    url: str | None = None
    citation_count: int | None = None
    year: int | None = None
    raw_snippet: str | None = None


class SignalResult(BaseModel):
    signal: ExternalSignal
    confidence_score: float
    confidence_breakdown: dict[str, float] = Field(default_factory=dict)
    from_cache: bool = False
    abort_reason: str | None = None  # set if confidence < threshold


# --- Gap analysis ---
class GapAnalysis(BaseModel):
    saturated_angles: list[str] = Field(default_factory=list)
    common_narratives: list[str] = Field(default_factory=list)
    angles_to_avoid: list[str] = Field(default_factory=list)
    summary: str = ""


# --- Strategy brief ---
class RejectedAngle(BaseModel):
    angle: str
    reason_rejected: str


class StrategyBrief(BaseModel):
    signal_summary: str
    chosen_angle: str
    why_this_angle_wins: str
    rejected_angles: list[RejectedAngle] = Field(default_factory=list)
    platform_strategy: str
    core_thesis: str


# --- Positioning ---
class PositioningHooks(BaseModel):
    blog_tail_insight: str  # for final 10–15% of blog
    linkedin_mention: str
    twitter_mention: str
    philosophy_tie: str  # how it connects to DataVex philosophy


# --- Critique ---
class CritiqueScores(BaseModel):
    hook_strength: float
    authority: float
    differentiation: float
    structure: float
    platform_fit: float

    def average(self) -> float:
        return (
            self.hook_strength + self.authority + self.differentiation + self.structure + self.platform_fit
        ) / 5.0


class CritiqueResult(BaseModel):
    scores: CritiqueScores
    feedback: str
    draft_number: int


class ContentWithCritiqueTrace(BaseModel):
    final_content: str
    drafts: list[str] = Field(default_factory=list)
    critiques: list[CritiqueResult] = Field(default_factory=list)
    score_evolution: list[CritiqueScores] = Field(default_factory=list)


# --- Final content assets ---
class ContentAssets(BaseModel):
    blog: ContentWithCritiqueTrace
    linkedin: ContentWithCritiqueTrace
    twitter_thread: ContentWithCritiqueTrace  # stored as single string, newline-sep tweets


# --- Full pipeline state (for orchestration and API response) ---
class PipelineState(BaseModel):
    keyword: str
    signal_result: SignalResult | None = None
    gap_analysis: GapAnalysis | None = None
    strategy_brief: StrategyBrief | None = None
    positioning: PositioningHooks | None = None
    content_assets: ContentAssets | None = None
    total_latency_seconds: float = 0.0
    aborted: bool = False
    abort_reason: str | None = None
    stage_timings_seconds: dict[str, float] = Field(default_factory=dict)

    model_config = {"arbitrary_types_allowed": True}
