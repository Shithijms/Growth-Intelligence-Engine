"""Pipeline state schema using TypedDict for LangGraph."""
from __future__ import annotations
from typing import Any, Optional, TypedDict


class PipelineState(TypedDict, total=False):
    # Input
    keyword: str
    start_time: float

    # Layer 2 — Signal Discovery
    candidate_signals: list[dict]
    selected_signal: dict
    confidence_scores: dict
    validated_signal: dict
    competitor_angles: list[str]
    identified_gaps: list[str]

    # Layer 3 — Strategy Brief
    strategy_brief: dict

    # Layer 4A — Blog
    blog_draft_1: dict
    blog_critique_1: dict
    blog_draft_2: dict
    blog_critique_2: dict
    blog_draft_3: dict
    blog_evolution_log: list[dict]
    blog_final: dict

    # Layer 4B — Short Form
    short_form_draft_1: dict
    short_form_critique_1: dict
    short_form_draft_2: dict
    short_form_critique_2: dict
    short_form_draft_3: dict
    linkedin_evolution_log: list[dict]
    twitter_evolution_log: list[dict]
    linkedin_final: str
    twitter_final: list[str]

    # Layer 5 — Quality Gate
    quality_gate_log: list[dict]

    # Layer 6 — Final Output
    pipeline_output: dict

    # Progress tracking
    current_stage: str
    errors: list[str]
