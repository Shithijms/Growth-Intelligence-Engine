from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel


# ─── Request ──────────────────────────────────────────────────────────────────

class PipelineRequest(BaseModel):
    keyword: str


# ─── Signal Layer ─────────────────────────────────────────────────────────────

class CandidateSignal(BaseModel):
    title: str
    url: str
    date: str
    summary: str
    relevance_score: float


class SignalConfidenceScores(BaseModel):
    authority: float
    recency: float
    relevance: float
    novelty: float
    composite: float


class ValidatedSignal(BaseModel):
    title: str
    url: str
    date: str
    summary: str
    validated_facts: list[str]
    is_ai_generated: bool
    confidence_scores: SignalConfidenceScores


class SignalReport(BaseModel):
    selected_signal: CandidateSignal
    confidence_scores: SignalConfidenceScores
    validated_facts: list[str]
    competitor_angles: list[str]
    identified_gaps: list[str]


# ─── Strategy Brief ───────────────────────────────────────────────────────────

class RejectedAngle(BaseModel):
    angle: str
    reason: str


class PlatformDistributionPlan(BaseModel):
    blog: str
    linkedin: str
    twitter: str


class StrategyBrief(BaseModel):
    signal_summary: str
    chosen_angle: str
    angle_rationale: str
    rejected_angles: list[RejectedAngle]
    competitive_gap_exploited: str
    core_positioning_thesis: str
    platform_distribution_plan: PlatformDistributionPlan
    target_audience: str
    estimated_authority_score: float


# ─── Content Drafts ───────────────────────────────────────────────────────────

class BlogScores(BaseModel):
    hook_strength: float
    clarity: float
    authority_tone: float
    differentiation: float
    logical_structure: float
    datavex_brand_fit: float

    def min_score(self) -> float:
        return min(
            self.hook_strength, self.clarity, self.authority_tone,
            self.differentiation, self.logical_structure, self.datavex_brand_fit
        )

    def all_pass(self, threshold: float = 7.0) -> bool:
        return self.min_score() >= threshold


class BlogDraftEntry(BaseModel):
    draft_number: int
    draft: str
    scores: BlogScores
    key_changes_made: str
    score_delta: Optional[float] = None


class BlogOutput(BaseModel):
    final_draft: str
    meta_title: str
    meta_description: str
    evolution_log: list[BlogDraftEntry]


class ShortFormScores(BaseModel):
    hook_density: float
    platform_native_feel: float
    engagement_trigger_strength: float
    shareability: float
    brand_fit: float

    def min_score(self) -> float:
        return min(
            self.hook_density, self.platform_native_feel,
            self.engagement_trigger_strength, self.shareability, self.brand_fit
        )

    def all_pass(self, threshold: float = 7.0) -> bool:
        return self.min_score() >= threshold


class ShortFormDraftEntry(BaseModel):
    draft_number: int
    draft: str
    scores: ShortFormScores
    key_changes_made: str
    score_delta: Optional[float] = None


class LinkedInOutput(BaseModel):
    final_draft: str
    evolution_log: list[ShortFormDraftEntry]


class TwitterOutput(BaseModel):
    tweets: list[str]
    evolution_log: list[ShortFormDraftEntry]


# ─── Critique Trace ───────────────────────────────────────────────────────────

class CritiqueTrace(BaseModel):
    blog_scores_by_draft: list[BlogScores]
    linkedin_scores_by_draft: list[ShortFormScores]
    twitter_scores_by_draft: list[ShortFormScores]


# ─── Quality Gate ─────────────────────────────────────────────────────────────

class GateDecision(BaseModel):
    asset: str
    gate_passed: bool
    trigger_reason: str
    final_scores: dict[str, float]


# ─── Run Metadata ─────────────────────────────────────────────────────────────

class RunMetadata(BaseModel):
    keyword: str
    timestamp: str
    total_pipeline_duration_seconds: float


# ─── Final Output ─────────────────────────────────────────────────────────────

class PipelineOutput(BaseModel):
    run_metadata: RunMetadata
    signal_report: SignalReport
    strategy_brief: StrategyBrief
    blog: BlogOutput
    linkedin: LinkedInOutput
    twitter_thread: TwitterOutput
    critique_trace: CritiqueTrace
    quality_gate_log: list[GateDecision]
