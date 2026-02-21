"""LangGraph state machine — connects all 6 pipeline layers."""
import time
import sys
import os

# Add backend root to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.graph import StateGraph, END
from pipeline.state import PipelineState
from pipeline.quality_gate import check_blog_gate, check_short_form_gate
from pipeline.output_assembler import assemble_output
from agents.signal_discovery import discover_signals
from agents.signal_scorer import score_signals
from agents.signal_validator import validate_signal
from agents.serp_scanner import scan_serp_and_find_gaps
from agents.strategy_brief import generate_strategy_brief
from agents.blog_generator import generate_blog_draft
from agents.blog_critique import critique_blog
from agents.short_form_generator import generate_short_form
from agents.short_form_critique import critique_short_form


# ─── Node Functions ───────────────────────────────────────────────────────────

def node_discover_signals(state: PipelineState) -> dict:
    keyword = state["keyword"]
    candidates = discover_signals(keyword)
    # Convert to dicts for state storage
    return {
        "candidate_signals": [c.model_dump() for c in candidates],
        "current_stage": "signal_discovery",
    }


def node_score_signals(state: PipelineState) -> dict:
    from models import CandidateSignal
    candidates = [CandidateSignal(**c) for c in state["candidate_signals"]]
    best_signal, best_scores = score_signals(candidates)
    return {
        "selected_signal": best_signal.model_dump(),
        "confidence_scores": best_scores.model_dump(),
        "current_stage": "signal_scoring",
    }


def node_validate_signal(state: PipelineState) -> dict:
    from models import CandidateSignal, SignalConfidenceScores
    signal = CandidateSignal(**state["selected_signal"])
    scores = SignalConfidenceScores(**state["confidence_scores"])
    validated = validate_signal(signal, scores)
    # Convert scores to dict for storage
    validated["confidence_scores"] = validated["confidence_scores"].model_dump()
    return {
        "validated_signal": validated,
        "current_stage": "signal_validation",
    }


def node_scan_serp(state: PipelineState) -> dict:
    result = scan_serp_and_find_gaps(state["keyword"])
    return {
        "competitor_angles": result["competitor_angles"],
        "identified_gaps": result["identified_gaps"],
        "current_stage": "serp_scan",
    }


def node_strategy_brief(state: PipelineState) -> dict:
    brief = generate_strategy_brief(
        keyword=state["keyword"],
        validated_signal=state["validated_signal"],
        identified_gaps=state.get("identified_gaps", []),
        competitor_angles=state.get("competitor_angles", []),
    )
    return {
        "strategy_brief": brief,
        "current_stage": "strategy_brief",
    }


def node_generate_blog_draft1(state: PipelineState) -> dict:
    result = generate_blog_draft(
        strategy_brief=state["strategy_brief"],
        validated_signal=state["validated_signal"],
        draft_number=1,
    )
    return {
        "blog_draft_1": result,
        "current_stage": "blog_draft_1",
    }


def node_critique_blog_1(state: PipelineState) -> dict:
    critique = critique_blog(state["blog_draft_1"]["draft"], draft_number=1)
    scores = critique["scores"]
    log_entry = {
        "draft_number": 1,
        "draft": state["blog_draft_1"]["draft"],
        "scores": scores,
        "key_changes_made": "Initial draft",
        "score_delta": None,
    }
    return {
        "blog_critique_1": critique,
        "blog_evolution_log": [log_entry],
        "current_stage": "blog_critique_1",
    }


def node_generate_blog_draft2(state: PipelineState) -> dict:
    instructions = state["blog_critique_1"].get("rewrite_instructions", "")
    result = generate_blog_draft(
        strategy_brief=state["strategy_brief"],
        validated_signal=state["validated_signal"],
        draft_number=2,
        critique_instructions=instructions,
    )
    return {
        "blog_draft_2": result,
        "current_stage": "blog_draft_2",
    }


def node_critique_blog_2(state: PipelineState) -> dict:
    critique = critique_blog(state["blog_draft_2"]["draft"], draft_number=2)
    scores_1 = state["blog_evolution_log"][0]["scores"]
    scores_2 = critique["scores"]

    # Calculate average score delta
    avg_1 = (scores_1.hook_strength + scores_1.clarity + scores_1.authority_tone +
             scores_1.differentiation + scores_1.logical_structure + scores_1.datavex_brand_fit) / 6
    avg_2 = (scores_2.hook_strength + scores_2.clarity + scores_2.authority_tone +
             scores_2.differentiation + scores_2.logical_structure + scores_2.datavex_brand_fit) / 6
    delta = round(avg_2 - avg_1, 2)

    log_entry = {
        "draft_number": 2,
        "draft": state["blog_draft_2"]["draft"],
        "scores": scores_2,
        "key_changes_made": "Applied critique: " + critique.get("rewrite_instructions", "")[:200],
        "score_delta": delta,
    }

    existing_log = state.get("blog_evolution_log", [])
    return {
        "blog_critique_2": critique,
        "blog_evolution_log": existing_log + [log_entry],
        "current_stage": "blog_critique_2",
    }


def node_blog_quality_gate(state: PipelineState) -> dict:
    critique_2 = state.get("blog_critique_2", {})
    scores = critique_2.get("scores")
    if not scores:
        return {"blog_final": state.get("blog_draft_2", state.get("blog_draft_1", {})),
                "current_stage": "blog_gate"}

    gate_result = check_blog_gate(scores, iteration=2)
    gate_log = state.get("quality_gate_log", [])

    if gate_result["needs_rewrite"]:
        # Trigger a 3rd draft targeting weak dimensions
        instructions = critique_2.get("rewrite_instructions", "")
        result = generate_blog_draft(
            strategy_brief=state["strategy_brief"],
            validated_signal=state["validated_signal"],
            draft_number=3,
            critique_instructions=f"FINAL TARGETED FIX: {instructions}",
        )
        final_critique = critique_blog(result["draft"], draft_number=3)
        final_scores = final_critique["scores"]

        scores_2 = state["blog_evolution_log"][-1]["scores"]
        avg_2 = (scores_2.hook_strength + scores_2.clarity + scores_2.authority_tone +
                 scores_2.differentiation + scores_2.logical_structure + scores_2.datavex_brand_fit) / 6
        avg_3 = (final_scores.hook_strength + final_scores.clarity + final_scores.authority_tone +
                 final_scores.differentiation + final_scores.logical_structure + final_scores.datavex_brand_fit) / 6
        delta = round(avg_3 - avg_2, 2)

        log_entry = {
            "draft_number": 3,
            "draft": result["draft"],
            "scores": final_scores,
            "key_changes_made": "Quality gate rewrite: targeted weak dimensions",
            "score_delta": delta,
        }

        final_gate = check_blog_gate(final_scores, iteration=3)
        return {
            "blog_draft_3": result,
            "blog_final": result,
            "blog_evolution_log": state.get("blog_evolution_log", []) + [log_entry],
            "quality_gate_log": gate_log + [final_gate],
            "current_stage": "blog_gate",
        }
    else:
        gate_log_entry = {
            "asset": "blog",
            "gate_passed": gate_result["gate_passed"],
            "trigger_reason": gate_result["trigger_reason"],
            "final_scores": gate_result["final_scores"],
        }
        return {
            "blog_final": state.get("blog_draft_2", {}),
            "quality_gate_log": gate_log + [gate_log_entry],
            "current_stage": "blog_gate",
        }


def node_generate_short_form_draft1(state: PipelineState) -> dict:
    result = generate_short_form(
        strategy_brief=state["strategy_brief"],
        validated_signal=state["validated_signal"],
        draft_number=1,
    )
    return {
        "short_form_draft_1": result,
        "current_stage": "short_form_draft_1",
    }


def node_critique_short_form_1(state: PipelineState) -> dict:
    draft = state["short_form_draft_1"]
    critique = critique_short_form(
        linkedin_draft=draft.get("linkedin", ""),
        twitter_tweets=draft.get("twitter_tweets", []),
        draft_number=1,
    )
    li_entry = {
        "draft_number": 1,
        "draft": draft.get("linkedin", ""),
        "scores": critique["linkedin_scores"],
        "key_changes_made": "Initial draft",
        "score_delta": None,
    }
    tw_entry = {
        "draft_number": 1,
        "draft": "\n".join(draft.get("twitter_tweets", [])),
        "scores": critique["twitter_scores"],
        "key_changes_made": "Initial draft",
        "score_delta": None,
    }
    return {
        "short_form_critique_1": critique,
        "linkedin_evolution_log": [li_entry],
        "twitter_evolution_log": [tw_entry],
        "current_stage": "short_form_critique_1",
    }


def node_generate_short_form_draft2(state: PipelineState) -> dict:
    critique = state["short_form_critique_1"]
    result = generate_short_form(
        strategy_brief=state["strategy_brief"],
        validated_signal=state["validated_signal"],
        draft_number=2,
        linkedin_critique=critique.get("linkedin_rewrite_instructions", ""),
        twitter_critique=critique.get("twitter_rewrite_instructions", ""),
    )
    return {
        "short_form_draft_2": result,
        "current_stage": "short_form_draft_2",
    }


def _avg_sf_scores(s) -> float:
    return (s.hook_density + s.platform_native_feel +
            s.engagement_trigger_strength + s.shareability + s.brand_fit) / 5


def node_critique_short_form_2(state: PipelineState) -> dict:
    draft = state["short_form_draft_2"]
    critique = critique_short_form(
        linkedin_draft=draft.get("linkedin", ""),
        twitter_tweets=draft.get("twitter_tweets", []),
        draft_number=2,
    )
    critique_1 = state["short_form_critique_1"]
    li_delta = round(_avg_sf_scores(critique["linkedin_scores"]) - _avg_sf_scores(critique_1["linkedin_scores"]), 2)
    tw_delta = round(_avg_sf_scores(critique["twitter_scores"]) - _avg_sf_scores(critique_1["twitter_scores"]), 2)

    li_entry = {
        "draft_number": 2,
        "draft": draft.get("linkedin", ""),
        "scores": critique["linkedin_scores"],
        "key_changes_made": "Applied critique: " + critique.get("linkedin_rewrite_instructions", "")[:150],
        "score_delta": li_delta,
    }
    tw_entry = {
        "draft_number": 2,
        "draft": "\n".join(draft.get("twitter_tweets", [])),
        "scores": critique["twitter_scores"],
        "key_changes_made": "Applied critique: " + critique.get("twitter_rewrite_instructions", "")[:150],
        "score_delta": tw_delta,
    }
    return {
        "short_form_critique_2": critique,
        "linkedin_evolution_log": state.get("linkedin_evolution_log", []) + [li_entry],
        "twitter_evolution_log": state.get("twitter_evolution_log", []) + [tw_entry],
        "current_stage": "short_form_critique_2",
    }


def node_short_form_quality_gate(state: PipelineState) -> dict:
    critique_2 = state.get("short_form_critique_2", {})
    li_scores = critique_2.get("linkedin_scores")
    tw_scores = critique_2.get("twitter_scores")
    gate_log = state.get("quality_gate_log", [])

    draft2 = state.get("short_form_draft_2", state.get("short_form_draft_1", {}))
    li_final = draft2.get("linkedin", "")
    tw_final = draft2.get("twitter_tweets", [])

    new_gates = []

    if li_scores:
        li_gate = check_short_form_gate("linkedin", li_scores, iteration=2)
        if li_gate["needs_rewrite"]:
            # One more pass for LinkedIn
            result = generate_short_form(
                strategy_brief=state["strategy_brief"],
                validated_signal=state["validated_signal"],
                draft_number=3,
                linkedin_critique=critique_2.get("linkedin_rewrite_instructions", ""),
                twitter_critique="",
            )
            li_final = result.get("linkedin", li_final)
            final_critique = critique_short_form(li_final, tw_final, draft_number=3)
            final_gate = check_short_form_gate("linkedin", final_critique["linkedin_scores"], iteration=3)
            new_gates.append(final_gate)

            li_entry = {
                "draft_number": 3,
                "draft": li_final,
                "scores": final_critique["linkedin_scores"],
                "key_changes_made": "Quality gate rewrite",
                "score_delta": round(_avg_sf_scores(final_critique["linkedin_scores"]) - _avg_sf_scores(li_scores), 2),
            }
            li_log = state.get("linkedin_evolution_log", []) + [li_entry]
        else:
            new_gates.append({
                "asset": "linkedin",
                "gate_passed": li_gate["gate_passed"],
                "trigger_reason": li_gate["trigger_reason"],
                "final_scores": li_gate["final_scores"],
            })
            li_log = state.get("linkedin_evolution_log", [])
    else:
        li_log = state.get("linkedin_evolution_log", [])

    if tw_scores:
        tw_gate = check_short_form_gate("twitter", tw_scores, iteration=2)
        if tw_gate["needs_rewrite"]:
            result = generate_short_form(
                strategy_brief=state["strategy_brief"],
                validated_signal=state["validated_signal"],
                draft_number=3,
                linkedin_critique="",
                twitter_critique=critique_2.get("twitter_rewrite_instructions", ""),
            )
            tw_final = result.get("twitter_tweets", tw_final)
            final_critique = critique_short_form(li_final, tw_final, draft_number=3)
            final_gate = check_short_form_gate("twitter", final_critique["twitter_scores"], iteration=3)
            new_gates.append(final_gate)

            tw_entry = {
                "draft_number": 3,
                "draft": "\n".join(tw_final),
                "scores": final_critique["twitter_scores"],
                "key_changes_made": "Quality gate rewrite",
                "score_delta": round(_avg_sf_scores(final_critique["twitter_scores"]) - _avg_sf_scores(tw_scores), 2),
            }
            tw_log = state.get("twitter_evolution_log", []) + [tw_entry]
        else:
            new_gates.append({
                "asset": "twitter",
                "gate_passed": tw_gate["gate_passed"],
                "trigger_reason": tw_gate["trigger_reason"],
                "final_scores": tw_gate["final_scores"],
            })
            tw_log = state.get("twitter_evolution_log", [])
    else:
        tw_log = state.get("twitter_evolution_log", [])

    return {
        "linkedin_final": li_final,
        "twitter_final": tw_final,
        "linkedin_evolution_log": li_log,
        "twitter_evolution_log": tw_log,
        "quality_gate_log": gate_log + new_gates,
        "current_stage": "short_form_gate",
    }


def node_assemble_output(state: PipelineState) -> dict:
    start_time = state.get("start_time", time.time())
    output = assemble_output(state, start_time)
    return {
        "pipeline_output": output,
        "current_stage": "complete",
    }


# ─── Build Graph ──────────────────────────────────────────────────────────────

def build_pipeline() -> StateGraph:
    graph = StateGraph(PipelineState)

    # Add all nodes
    graph.add_node("discover_signals", node_discover_signals)
    graph.add_node("score_signals", node_score_signals)
    graph.add_node("validate_signal", node_validate_signal)
    graph.add_node("scan_serp", node_scan_serp)
    graph.add_node("strategy_brief", node_strategy_brief)
    graph.add_node("generate_blog_draft1", node_generate_blog_draft1)
    graph.add_node("critique_blog_1", node_critique_blog_1)
    graph.add_node("generate_blog_draft2", node_generate_blog_draft2)
    graph.add_node("critique_blog_2", node_critique_blog_2)
    graph.add_node("blog_quality_gate", node_blog_quality_gate)
    graph.add_node("generate_short_form_draft1", node_generate_short_form_draft1)
    graph.add_node("critique_short_form_1", node_critique_short_form_1)
    graph.add_node("generate_short_form_draft2", node_generate_short_form_draft2)
    graph.add_node("critique_short_form_2", node_critique_short_form_2)
    graph.add_node("short_form_quality_gate", node_short_form_quality_gate)
    graph.add_node("assemble_output", node_assemble_output)

    # Wire edges
    graph.set_entry_point("discover_signals")
    graph.add_edge("discover_signals", "score_signals")
    graph.add_edge("score_signals", "validate_signal")
    graph.add_edge("validate_signal", "scan_serp")
    graph.add_edge("scan_serp", "strategy_brief")
    graph.add_edge("strategy_brief", "generate_blog_draft1")
    graph.add_edge("generate_blog_draft1", "critique_blog_1")
    graph.add_edge("critique_blog_1", "generate_blog_draft2")
    graph.add_edge("generate_blog_draft2", "critique_blog_2")
    graph.add_edge("critique_blog_2", "blog_quality_gate")
    graph.add_edge("blog_quality_gate", "generate_short_form_draft1")
    graph.add_edge("generate_short_form_draft1", "critique_short_form_1")
    graph.add_edge("critique_short_form_1", "generate_short_form_draft2")
    graph.add_edge("generate_short_form_draft2", "critique_short_form_2")
    graph.add_edge("critique_short_form_2", "short_form_quality_gate")
    graph.add_edge("short_form_quality_gate", "assemble_output")
    graph.add_edge("assemble_output", END)

    return graph.compile()


# Singleton compiled pipeline
compiled_pipeline = None


def get_pipeline():
    global compiled_pipeline
    if compiled_pipeline is None:
        compiled_pipeline = build_pipeline()
    return compiled_pipeline
