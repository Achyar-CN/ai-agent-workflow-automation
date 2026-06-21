"""FastAPI app exposing the pipeline as a Server-Sent Events stream.

``POST /research`` runs the LangGraph pipeline and streams one JSON event per
stage transition (start / done / skipped / error). The Next.js frontend proxies
and renders these events live.
"""

from __future__ import annotations

import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .config import config
from .data.seed import known_companies
from .graph.graph import graph
from .schemas import ResearchRequest

app = FastAPI(title="AI Sales Lead Researcher", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


@app.get("/health")
async def health() -> dict:
    model = config.claude_model if config.provider == "claude" else config.ollama_model
    return {"status": "ok", "provider": config.provider, "model": model}


@app.get("/seed-companies")
async def seed_companies() -> dict:
    """Companies guaranteed to produce a full demo (offline included)."""
    return {"companies": known_companies()}


@app.post("/research")
async def research(req: ResearchRequest) -> StreamingResponse:
    async def event_stream():
        state = {"company_name": req.company_name, "icp": req.icp}
        try:
            async for event in graph.astream(state, stream_mode="custom"):
                yield _sse(event)
        except Exception as exc:  # noqa: BLE001 — surface failures to the client
            yield _sse({"stage": "research", "status": "error", "message": str(exc)})
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # disable proxy buffering
        },
    )
