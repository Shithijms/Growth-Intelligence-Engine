"""Fetch DataVex website and other configured URLs for RAG context. All DataVex AI posts/pages are searched and indexed."""
import re
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from langchain_core.documents import Document

from config import settings
from utils.logging import get_logger

logger = get_logger(__name__)

# Timeout and headers for polite fetching
FETCH_TIMEOUT = 15.0
HEADERS = {
    "User-Agent": "DataVexGrowthEngine/1.0 (context indexing; datavex.ai)",
    "Accept": "text/html,application/xhtml+xml",
}


def _urls_to_fetch() -> list[str]:
    """Normalize and deduplicate URLs from settings."""
    raw = (settings.datavex_fetch_urls or "").strip()
    if not raw:
        return [settings.datavex_website_url]
    urls = [u.strip() for u in raw.split(",") if u.strip()]
    if not urls:
        return [settings.datavex_website_url]
    return list(dict.fromkeys(urls))


def _html_to_text(html: str, url: str) -> str:
    """Extract readable text from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    # Drop script/style
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    # Collapse multiple newlines and trim
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() or ""


def fetch_url(url: str) -> str | None:
    """Fetch one URL and return response text, or None on failure."""
    try:
        with httpx.Client(timeout=FETCH_TIMEOUT, follow_redirects=True, headers=HEADERS) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.text
    except Exception as e:
        logger.warning("datavex_fetch_failed", url=url, error=str(e))
        return None


def fetch_datavex_web_documents() -> list[Document]:
    """
    Fetch all configured DataVex URLs (e.g. datavex.ai and any blog/posts paths),
    extract text, and return LangChain Documents for RAG indexing.
    """
    docs: list[Document] = []
    for url in _urls_to_fetch():
        html = fetch_url(url)
        if not html:
            continue
        text = _html_to_text(html, url)
        if not text or len(text) < 100:
            continue
        name = urlparse(url).path or urlparse(url).netloc or "datavex"
        if name == "/" or not name.strip("/"):
            name = "datavex_homepage"
        else:
            name = name.strip("/").replace("/", "_") or "datavex_page"
        docs.append(
            Document(
                page_content=text,
                metadata={
                    "source": f"datavex_web_{name}",
                    "url": url,
                    "origin": "datavex.ai",
                },
            )
        )
        logger.info("datavex_web_indexed", url=url, content_length=len(text))
    return docs
