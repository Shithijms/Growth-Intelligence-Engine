"""DataVex Growth Intelligence Engine — FastAPI entrypoint."""
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router as api_router
from config import settings
from memory import init_chroma


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize Chroma and ensure DataVex corpus is indexed."""
    init_chroma()
    yield
    # Teardown if needed


app = FastAPI(
    title="DataVex Growth Intelligence Engine",
    description="Keyword-driven growth content pipeline with signal discovery, strategy, and critique.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins + ["*"],  # allow all for hackathon demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api", tags=["api"])


@app.get("/")
def root():
    return {"service": "DataVex Growth Intelligence Engine", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok", "timestamp": time.time()}
