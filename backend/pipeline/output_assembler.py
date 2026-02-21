"""Final output assembler — builds the complete PipelineOutput JSON."""
import time
from models import (
    RunMetadata, SignalReport, CandidateSignal, SignalConfidenceScores,
    StrategyBrief, RejectedAngle, PlatformDistributionPlan,
    BlogOutput, BlogScores, BlogDraftEntry,
    LinkedInOutput, TwitterOutput, ShortFormScores, ShortFormDraftEntry,
    CritiqueTrace, GateDecision, PipelineOutput,
)


def assemble_output(state: dict, start_time: float) -> dict:
    keyword = state.get("keyword", "")
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    duration = round(time.time() - start_time, 2)

    # ─── Signal Report ────────────────────────────────────────────────────────
    vs = state.get("validated_signal", {})
    cs = state.get("confidence_scores", {})
    selected_raw = state.get("selected_signal", {})

    selected_signal = CandidateSignal(
        title=selected_raw.get("title", vs.get("title", "")),
        url=selected_raw.get("url", vs.get("url", "")),
        date=selected_raw.get("date", vs.get("date", "")),
        summary=selected_raw.get("summary", vs.get("summary", "")),
        relevance_score=selected_raw.get("relevance_score", 5.0),
    )
    confidence_scores = SignalConfidenceScores(
        authority=cs.get("authority", 5.0),
        recency=cs.get("recency", 5.0),
        relevance=cs.get("relevance", 5.0),
        novelty=cs.get("novelty", 5.0),
        composite=cs.get("composite", 5.0),
    )
    signal_report = SignalReport(
        selected_signal=selected_signal,
        confidence_scores=confidence_scores,
        validated_facts=vs.get("validated_facts", []),
        competitor_angles=state.get("competitor_angles", []),
        identified_gaps=state.get("identified_gaps", []),
    )

    # ─── Strategy Brief ───────────────────────────────────────────────────────
    sb = state.get("strategy_brief", {})
    dist_plan = sb.get("platform_distribution_plan", {})
    rejected_raw = sb.get("rejected_angles", [])

    strategy_brief = StrategyBrief(
        signal_summary=sb.get("signal_summary", ""),
        chosen_angle=sb.get("chosen_angle", ""),
        angle_rationale=sb.get("angle_rationale", ""),
        rejected_angles=[RejectedAngle(**r) for r in rejected_raw],
        competitive_gap_exploited=sb.get("competitive_gap_exploited", ""),
        core_positioning_thesis=sb.get("core_positioning_thesis", ""),
        platform_distribution_plan=PlatformDistributionPlan(
            blog=dist_plan.get("blog", ""),
            linkedin=dist_plan.get("linkedin", ""),
            twitter=dist_plan.get("twitter", ""),
        ),
        target_audience=sb.get("target_audience", ""),
        estimated_authority_score=float(sb.get("estimated_authority_score", 75)),
    )

    # ─── Blog ─────────────────────────────────────────────────────────────────
    blog_log = state.get("blog_evolution_log", [])
    blog_final_data = state.get("blog_final", {})

    def make_blog_entry(entry: dict) -> BlogDraftEntry:
        scores_raw = entry.get("scores", {})
        if isinstance(scores_raw, BlogScores):
            scores = scores_raw
        else:
            scores = BlogScores(
                hook_strength=scores_raw.get("hook_strength", 5.0),
                clarity=scores_raw.get("clarity", 5.0),
                authority_tone=scores_raw.get("authority_tone", 5.0),
                differentiation=scores_raw.get("differentiation", 5.0),
                logical_structure=scores_raw.get("logical_structure", 5.0),
                datavex_brand_fit=scores_raw.get("datavex_brand_fit", 5.0),
            )
        return BlogDraftEntry(
            draft_number=entry.get("draft_number", 1),
            draft=entry.get("draft", ""),
            scores=scores,
            key_changes_made=entry.get("key_changes_made", "Initial draft"),
            score_delta=entry.get("score_delta"),
        )

    blog_output = BlogOutput(
        final_draft=blog_final_data.get("draft", ""),
        meta_title=blog_final_data.get("meta_title", ""),
        meta_description=blog_final_data.get("meta_description", ""),
        evolution_log=[make_blog_entry(e) for e in blog_log],
    )

    # ─── Short Form ───────────────────────────────────────────────────────────
    li_log = state.get("linkedin_evolution_log", [])
    tw_log = state.get("twitter_evolution_log", [])

    def make_sf_entry(entry: dict) -> ShortFormDraftEntry:
        scores_raw = entry.get("scores", {})
        if isinstance(scores_raw, ShortFormScores):
            scores = scores_raw
        else:
            scores = ShortFormScores(
                hook_density=scores_raw.get("hook_density", 5.0),
                platform_native_feel=scores_raw.get("platform_native_feel", 5.0),
                engagement_trigger_strength=scores_raw.get("engagement_trigger_strength", 5.0),
                shareability=scores_raw.get("shareability", 5.0),
                brand_fit=scores_raw.get("brand_fit", 5.0),
            )
        return ShortFormDraftEntry(
            draft_number=entry.get("draft_number", 1),
            draft=entry.get("draft", ""),
            scores=scores,
            key_changes_made=entry.get("key_changes_made", "Initial draft"),
            score_delta=entry.get("score_delta"),
        )

    linkedin_output = LinkedInOutput(
        final_draft=state.get("linkedin_final", ""),
        evolution_log=[make_sf_entry(e) for e in li_log],
    )
    twitter_output = TwitterOutput(
        tweets=state.get("twitter_final", []),
        evolution_log=[make_sf_entry(e) for e in tw_log],
    )

    # ─── Critique Trace ───────────────────────────────────────────────────────
    def extract_blog_scores(log: list[dict]) -> list[BlogScores]:
        result = []
        for e in log:
            s = e.get("scores", {})
            if isinstance(s, BlogScores):
                result.append(s)
            else:
                result.append(BlogScores(
                    hook_strength=s.get("hook_strength", 5.0),
                    clarity=s.get("clarity", 5.0),
                    authority_tone=s.get("authority_tone", 5.0),
                    differentiation=s.get("differentiation", 5.0),
                    logical_structure=s.get("logical_structure", 5.0),
                    datavex_brand_fit=s.get("datavex_brand_fit", 5.0),
                ))
        return result

    def extract_sf_scores(log: list[dict]) -> list[ShortFormScores]:
        result = []
        for e in log:
            s = e.get("scores", {})
            if isinstance(s, ShortFormScores):
                result.append(s)
            else:
                result.append(ShortFormScores(
                    hook_density=s.get("hook_density", 5.0),
                    platform_native_feel=s.get("platform_native_feel", 5.0),
                    engagement_trigger_strength=s.get("engagement_trigger_strength", 5.0),
                    shareability=s.get("shareability", 5.0),
                    brand_fit=s.get("brand_fit", 5.0),
                ))
        return result

    critique_trace = CritiqueTrace(
        blog_scores_by_draft=extract_blog_scores(blog_log),
        linkedin_scores_by_draft=extract_sf_scores(li_log),
        twitter_scores_by_draft=extract_sf_scores(tw_log),
    )

    # ─── Quality Gate Log ─────────────────────────────────────────────────────
    gate_log_raw = state.get("quality_gate_log", [])
    quality_gate_log = [
        GateDecision(
            asset=g.get("asset", ""),
            gate_passed=g.get("gate_passed", False),
            trigger_reason=g.get("trigger_reason", ""),
            final_scores=g.get("final_scores", {}),
        )
        for g in gate_log_raw
    ]

    # ─── Final Assembly ───────────────────────────────────────────────────────
    output = PipelineOutput(
        run_metadata=RunMetadata(
            keyword=keyword,
            timestamp=now,
            total_pipeline_duration_seconds=duration,
        ),
        signal_report=signal_report,
        strategy_brief=strategy_brief,
        blog=blog_output,
        linkedin=linkedin_output,
        twitter_thread=twitter_output,
        critique_trace=critique_trace,
        quality_gate_log=quality_gate_log,
    )

    return output.model_dump()
