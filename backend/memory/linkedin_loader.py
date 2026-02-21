"""Load DataVex LinkedIn posts for RAG context. All posts in the configured JSON are indexed."""
import json
from pathlib import Path

from langchain_core.documents import Document

from config import settings
from utils.logging import get_logger

logger = get_logger(__name__)


def _linkedin_posts_path() -> Path:
    """Resolve path to LinkedIn posts JSON (config or default under backend/data)."""
    p = Path(settings.linkedin_posts_path)
    if p.is_absolute():
        return p
    if p.exists():
        return p
    # Default relative to backend
    default = Path(__file__).resolve().parent.parent / "data" / "linkedin_posts.json"
    return default if default.exists() else p


def load_linkedin_posts() -> list[Document]:
    """
    Load all LinkedIn posts from the configured JSON file.
    Expected format: array of objects with "content" (required), optional "date", "url", "title".
    Returns empty list if file missing or invalid.
    """
    path = _linkedin_posts_path()
    if not path.exists():
        logger.debug("linkedin_posts_file_missing", path=str(path))
        return []
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except Exception as e:
        logger.warning("linkedin_posts_load_failed", path=str(path), error=str(e))
        return []
    if not isinstance(data, list):
        logger.warning("linkedin_posts_not_array", path=str(path))
        return []
    docs: list[Document] = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            continue
        content = item.get("content") or item.get("text") or item.get("body") or ""
        if not content or not str(content).strip():
            continue
        content = str(content).strip()
        meta = {
            "source": f"linkedin_post_{i}",
            "origin": "linkedin",
        }
        if item.get("date"):
            meta["date"] = str(item["date"])
        if item.get("url"):
            meta["url"] = str(item["url"])
        if item.get("title"):
            meta["title"] = str(item["title"])
        docs.append(Document(page_content=content, metadata=meta))
    if docs:
        logger.info("linkedin_posts_loaded", path=str(path), count=len(docs))
    return docs
