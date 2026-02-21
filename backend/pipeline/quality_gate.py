"""Quality Gate — enforces 7/10 threshold, max 3 iterations."""
from models import BlogScores, ShortFormScores

THRESHOLD = 7.0
MAX_ITERATIONS = 3


def check_blog_gate(scores: BlogScores, iteration: int) -> dict:
    passed = scores.all_pass(THRESHOLD)
    low_dims = _get_low_blog_dims(scores)
    return {
        "asset": "blog",
        "gate_passed": passed,
        "iteration": iteration,
        "trigger_reason": (
            "All dimensions >= 7.0" if passed
            else f"Dimensions below threshold: {', '.join(low_dims)}"
        ),
        "final_scores": {
            "hook_strength": scores.hook_strength,
            "clarity": scores.clarity,
            "authority_tone": scores.authority_tone,
            "differentiation": scores.differentiation,
            "logical_structure": scores.logical_structure,
            "datavex_brand_fit": scores.datavex_brand_fit,
        },
        "needs_rewrite": not passed and iteration < MAX_ITERATIONS,
    }


def check_short_form_gate(asset: str, scores: ShortFormScores, iteration: int) -> dict:
    passed = scores.all_pass(THRESHOLD)
    low_dims = _get_low_short_form_dims(scores)
    return {
        "asset": asset,
        "gate_passed": passed,
        "iteration": iteration,
        "trigger_reason": (
            "All dimensions >= 7.0" if passed
            else f"Dimensions below threshold: {', '.join(low_dims)}"
        ),
        "final_scores": {
            "hook_density": scores.hook_density,
            "platform_native_feel": scores.platform_native_feel,
            "engagement_trigger_strength": scores.engagement_trigger_strength,
            "shareability": scores.shareability,
            "brand_fit": scores.brand_fit,
        },
        "needs_rewrite": not passed and iteration < MAX_ITERATIONS,
    }


def _get_low_blog_dims(scores: BlogScores) -> list[str]:
    dims = []
    if scores.hook_strength < THRESHOLD: dims.append("hook_strength")
    if scores.clarity < THRESHOLD: dims.append("clarity")
    if scores.authority_tone < THRESHOLD: dims.append("authority_tone")
    if scores.differentiation < THRESHOLD: dims.append("differentiation")
    if scores.logical_structure < THRESHOLD: dims.append("logical_structure")
    if scores.datavex_brand_fit < THRESHOLD: dims.append("datavex_brand_fit")
    return dims


def _get_low_short_form_dims(scores: ShortFormScores) -> list[str]:
    dims = []
    if scores.hook_density < THRESHOLD: dims.append("hook_density")
    if scores.platform_native_feel < THRESHOLD: dims.append("platform_native_feel")
    if scores.engagement_trigger_strength < THRESHOLD: dims.append("engagement_trigger_strength")
    if scores.shareability < THRESHOLD: dims.append("shareability")
    if scores.brand_fit < THRESHOLD: dims.append("brand_fit")
    return dims
