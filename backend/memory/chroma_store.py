"""Chroma vector store for DataVex corpus. RAG for grounding only. Includes static corpus + fetched datavex.ai pages."""
from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from config import settings
from memory.datavex_fetcher import fetch_datavex_web_documents
from memory.linkedin_loader import load_linkedin_posts
from utils.logging import get_logger

logger = get_logger(__name__)

_collection_name = "datavex_corpus"
_vector_store: Chroma | None = None


def _load_corpus_documents() -> list[Document]:
    """Load markdown/text files from DataVex corpus dir into LangChain Documents."""
    corpus_path = settings.datavex_path()
    if not corpus_path.exists():
        corpus_path = Path(__file__).resolve().parent.parent / "data" / "datavex_corpus"
    docs: list[Document] = []
    for path in sorted(corpus_path.glob("**/*.md")):
        try:
            text = path.read_text(encoding="utf-8")
            docs.append(
                Document(
                    page_content=text,
                    metadata={"source": str(path.name), "path": str(path)},
                )
            )
        except Exception as e:
            logger.warning("skip_corpus_file", path=str(path), error=str(e))
    return docs


def _all_documents() -> list[Document]:
    """Static corpus + LinkedIn posts + fetched DataVex AI web pages (datavex.ai and any configured URLs)."""
    static = _load_corpus_documents()
    try:
        linkedin_docs = load_linkedin_posts()
    except Exception as e:
        logger.warning("linkedin_posts_load_error", error=str(e))
        linkedin_docs = []
    try:
        web_docs = fetch_datavex_web_documents()
    except Exception as e:
        logger.warning("datavex_web_fetch_error", error=str(e))
        web_docs = []
    return static + linkedin_docs + web_docs


def init_chroma() -> Chroma:
    """Create or load Chroma collection with DataVex corpus (static + datavex.ai). Idempotent."""
    global _vector_store
    if _vector_store is not None:
        return _vector_store

    persist_dir = str(settings.chroma_path())
    settings.chroma_path().mkdir(parents=True, exist_ok=True)

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=settings.google_api_key or None,
    )

    docs = _all_documents()
    if not docs:
        logger.warning("no_corpus_documents", dir=str(settings.datavex_path()))

    _vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=_collection_name,
        persist_directory=persist_dir,
    )
    static_count = len(_load_corpus_documents())
    linkedin_count = len(load_linkedin_posts())
    web_count = len(docs) - static_count - linkedin_count
    logger.info(
        "chroma_initialized",
        num_docs=len(docs),
        static_docs=static_count,
        linkedin_posts=linkedin_count,
        web_docs=web_count,
        persist_dir=persist_dir,
    )
    return _vector_store


def get_datavex_retriever(k: int = 4):
    """Return a LangChain retriever over DataVex corpus. k = number of chunks."""
    if _vector_store is None:
        init_chroma()
    return _vector_store.as_retriever(search_kwargs={"k": k})
