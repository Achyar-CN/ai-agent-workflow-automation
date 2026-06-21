"""Shared state passed between agents, plus a safe progress emitter.

Each node reads what it needs and returns a partial dict that LangGraph merges
back. ``total=False`` means every field is optional until a node produces it.
"""

from __future__ import annotations

from typing import TypedDict

from ..schemas import (
    ICP,
    CompanyProfile,
    EmailDraft,
    KeyPerson,
    Qualification,
    Stage,
    StageEvent,
    StageStatus,
)


class LeadResearchState(TypedDict, total=False):
    # Inputs
    company_name: str
    icp: ICP
    # Produced by the agents, in order
    raw_sources: list[str]
    company_profile: CompanyProfile
    key_people: list[KeyPerson]
    qualification: Qualification
    email_draft: EmailDraft


def emit(stage: Stage, status: StageStatus, data: dict | None = None, message: str = "") -> None:
    """Stream a progress event to the SSE layer, if one is listening.

    Uses LangGraph's custom stream writer. Outside a streaming run (e.g. unit
    tests calling a node directly) this is a silent no-op."""
    try:
        from langgraph.config import get_stream_writer

        writer = get_stream_writer()
    except Exception:  # noqa: BLE001 — no active stream context
        return
    if writer is None:
        return
    writer(StageEvent(stage=stage, status=status, data=data, message=message).model_dump())
