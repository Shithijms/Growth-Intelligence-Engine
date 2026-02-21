"""FastAPI main application — /health + /run-pipeline (SSE streaming)."""
import time
import json
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse

from config import get_settings
from models import PipelineRequest
from pipeline.graph import get_pipeline
from pipeline.state import PipelineState

STAGE_LABELS = {
    "discover_signals": "🔍 Discovering signals via Tavily...",
    "score_signals": "📊 Scoring signal confidence...",
    "validate_signal": "✅ Validating selected signal...",
    "scan_serp": "🗺️ Scanning SERP for competitive gaps...",
    "strategy_brief": "🧠 Generating strategy brief...",
    "generate_blog_draft1": "✍️ Writing blog Draft 1...",
    "critique_blog_1": "🔴 Critiquing blog Draft 1...",
    "generate_blog_draft2": "✍️ Rewriting blog Draft 2...",
    "critique_blog_2": "🔴 Critiquing blog Draft 2...",
    "blog_quality_gate": "🚦 Blog quality gate check...",
    "generate_short_form_draft1": "📱 Writing LinkedIn + Twitter Draft 1...",
    "critique_short_form_1": "🔴 Critiquing short form Draft 1...",
    "generate_short_form_draft2": "📱 Rewriting short form Draft 2...",
    "critique_short_form_2": "🔴 Critiquing short form Draft 2...",
    "short_form_quality_gate": "🚦 Short form quality gate check...",
    "assemble_output": "📦 Assembling final output...",
    "complete": "✅ Pipeline complete!",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm up the pipeline graph at startup
    get_pipeline()
    yield


app = FastAPI(
    title="DataVex Growth Intelligence Engine",
    version="1.0.0",
    lifespan=lifespan,
)

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "DataVex Growth Intelligence Engine"}


@app.post("/run-pipeline")
async def run_pipeline_endpoint(request: PipelineRequest):
    """Run the full pipeline and return SSE stream of progress + final output."""

    async def event_generator():
        pipeline = get_pipeline()
        initial_state: PipelineState = {
            "keyword": request.keyword,
            "start_time": time.time(),
            "errors": [],
            "quality_gate_log": [],
        }

        try:
            # Stream events as the graph executes
            async for event in pipeline.astream(initial_state):
                # Each event is a dict of {node_name: state_updates}
                for node_name, state_update in event.items():
                    stage = state_update.get("current_stage", node_name)
                    label = STAGE_LABELS.get(stage, f"Processing {stage}...")

                    progress_event = {
                        "type": "progress",
                        "stage": stage,
                        "label": label,
                        "node": node_name,
                    }
                    yield {
                        "event": "progress",
                        "data": json.dumps(progress_event),
                    }

                    # If this is the final assembly node, emit the full result
                    if "pipeline_output" in state_update:
                        output = state_update["pipeline_output"]
                        yield {
                            "event": "result",
                            "data": json.dumps({"type": "result", "output": output}),
                        }

        except Exception as e:
            error_payload = {
                "type": "error",
                "message": str(e),
            }
            yield {
                "event": "error",
                "data": json.dumps(error_payload),
            }

    return EventSourceResponse(event_generator())


@app.post("/run-pipeline-sync")
async def run_pipeline_sync(request: PipelineRequest):
    """Synchronous version — waits for full pipeline to complete, returns JSON."""
    pipeline = get_pipeline()
    initial_state: PipelineState = {
        "keyword": request.keyword,
        "start_time": time.time(),
        "errors": [],
        "quality_gate_log": [],
    }

    try:
        final_state = await pipeline.ainvoke(initial_state)
        output = final_state.get("pipeline_output", {})
        return JSONResponse(content=output)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )
