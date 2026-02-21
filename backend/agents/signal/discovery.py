"""External signal discovery: hybrid (live + static cache), confidence score, abort if below threshold."""
import json
from pathlib import Path

from config import settings
from utils.schemas import ExternalSignal, SignalResult
from utils.logging import get_logger

logger = get_logger(__name__)

# Default cache path relative to backend
DEFAULT_CACHE_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "signal_cache.json"


def _load_signal_cache() -> dict:
    """Load static signal cache from JSON."""
    path = Path(settings.signal_cache_path)
    if not path.exists():
        path = DEFAULT_CACHE_PATH
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning("signal_cache_load_failed", path=str(path), error=str(e))
        return {}


def _cache_entry_to_signal(keyword: str, entry: dict) -> ExternalSignal:
    """Convert cache entry to ExternalSignal."""
    return ExternalSignal(
        title=entry.get("title", ""),
        source=entry.get("source", ""),
        source_type=entry.get("source_type", "blog"),
        summary=entry.get("summary", ""),
        url=entry.get("url"),
        citation_count=entry.get("citation_count"),
        year=entry.get("year"),
        raw_snippet=entry.get("raw_snippet"),
    )


def _compute_confidence_from_cache(entry: dict, keyword: str) -> tuple[float, dict]:
    """Compute confidence score from cache entry scores (authority, recency, relevance)."""
    authority = float(entry.get("authority_score", 0.6))
    recency = float(entry.get("recency_score", 0.7))
    relevance = float(entry.get("relevance_score", 0.8))
    # Optional: slight penalty for cache vs live
    breakdown = {
        "source_authority": authority,
        "recency": recency,
        "keyword_relevance": relevance,
    }
    score = (authority * 0.3 + recency * 0.2 + relevance * 0.5)
    return round(min(1.0, score), 3), breakdown


def _try_live_signal_search(keyword: str) -> SignalResult | None:
    """
    Try to get a signal from live web search.
    Uses LLM + optional search API. For hackathon without Tavily, we return None and fall back to cache.
    """
    if not settings.use_live_signal_search:
        return None
    # Optional: integrate Tavily or SerpAPI here. For now we rely on cache.
    # If you add TAVILY_API_KEY, we could call Tavily and then use LLM to extract one signal + scores.
    return None


def run_signal_discovery(keyword: str) -> SignalResult:
    """
    Run hybrid signal discovery: try live first, then static cache.
    Always compute and attach confidence score. Caller should abort if below threshold.
    """
    keyword_lower = keyword.strip().lower()
    if not keyword_lower:
        return SignalResult(
            signal=ExternalSignal(title="", source="", source_type="", summary=""),
            confidence_score=0.0,
            confidence_breakdown={},
            abort_reason="Keyword is empty.",
        )

    # 1) Try live
    live_result = _try_live_signal_search(keyword_lower)
    if live_result is not None:
        return live_result

    # 2) Fallback: static cache
    cache = _load_signal_cache()
    # Try exact key first, then any key that contains the keyword
    entry = cache.get(keyword_lower)
    if entry is None:
        for k, v in cache.items():
            if keyword_lower in k or k in keyword_lower:
                entry = v
                break
    if entry is None:
        # No signal found: return a low-confidence placeholder so orchestrator can abort with clear message
        return SignalResult(
            signal=ExternalSignal(
                title="No signal found",
                source="N/A",
                source_type="other",
                summary="No curated or live signal found for this keyword.",
            ),
            confidence_score=0.0,
            confidence_breakdown={},
            abort_reason="No external signal found for this keyword. Add a curated signal to the cache or enable live search.",
        )

    signal = _cache_entry_to_signal(keyword_lower, entry)
    score, breakdown = _compute_confidence_from_cache(entry, keyword_lower)
    return SignalResult(
        signal=signal,
        confidence_score=score,
        confidence_breakdown=breakdown,
        from_cache=True,
    )
