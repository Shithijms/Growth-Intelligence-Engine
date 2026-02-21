"""API routes: run pipeline, health."""
import asyncio
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agents.orchestration import run_pipeline
from utils.schemas import PipelineState

router = APIRouter()


class RunRequest(BaseModel):
    keyword: str


class RunResponse(BaseModel):
    success: bool
    aborted: bool
    abort_reason: str | None
    total_latency_seconds: float
    stage_timings_seconds: dict[str, float]
    result: dict[str, Any] | None  # full PipelineState as dict for flexibility


@router.post("/run", response_model=RunResponse)
async def run_growth_pipeline(body: RunRequest):
    """
    Run the Growth Intelligence pipeline for the given keyword.
    Returns full state: signal, strategy brief, rejected angles, content assets, critique trace, latency.
    """
    keyword = (body.keyword or "").strip()
    if not keyword:
        raise HTTPException(status_code=400, detail="keyword is required")

    # Run CPU/IO-heavy pipeline in thread so we don't block the event loop
    state: PipelineState = await asyncio.to_thread(run_pipeline, keyword)

    return RunResponse(
        success=not state.aborted,
        aborted=state.aborted,
        abort_reason=state.abort_reason,
        total_latency_seconds=state.total_latency_seconds,
        stage_timings_seconds=state.stage_timings_seconds,
        result=state.model_dump() if state else None,
    )


@router.get("/health")
def api_health():
    return {"status": "ok"}
