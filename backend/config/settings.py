"""Application settings from environment."""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Google Gemini
    google_api_key: str = ""
    llm_strategy: str = "gemini-2.5-pro"  # strategy, critique, positioning
    llm_content: str = "gemini-2.5-flash"  # blog, LinkedIn, X

    # RAG / Chroma
    chroma_persist_dir: str = "./data/chroma"
    datavex_corpus_dir: str = "./data/datavex_corpus"
    signal_cache_path: str = "./data/signal_cache.json"

    # DataVex website — official site and URLs to fetch for RAG context
    datavex_website_url: str = "https://datavex.ai"
    datavex_fetch_urls: str = "https://datavex.ai"  # comma-separated; fetched and indexed at Chroma init

    # LinkedIn posts for RAG context (all DataVex LinkedIn posts)
    linkedin_posts_path: str = "./data/linkedin_posts.json"  # JSON array of { "content": "...", "date": "...", "url": "..." }

    # Thresholds
    signal_confidence_threshold: float = 0.5  # abort if below

    # External signal (hybrid)
    use_live_signal_search: bool = True
    signal_search_max_results: int = 5

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # CORS (for Vercel frontend)
    cors_origins: list[str] = ["http://localhost:3000", "https://*.vercel.app"]

    def chroma_path(self) -> Path:
        return Path(self.chroma_persist_dir)

    def datavex_path(self) -> Path:
        return Path(self.datavex_corpus_dir)


def require_google_api_key() -> str:
    """Return the Google API key, or raise a clear error if not set (avoids ADC fallback)."""
    key = (settings.google_api_key or "").strip()
    if not key:
        raise ValueError(
            "GOOGLE_API_KEY is required. Set it in backend/.env or as an environment variable. See backend/.env.example."
        )
    return key


settings = Settings()
