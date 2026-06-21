"""Agent 3 — Qualification.

Scores the company against the client's ICP (0–100) and decides GO / NO_GO. The
final verdict is pinned to ``QUALIFY_THRESHOLD`` so the routing decision stays
consistent with the score the user sees. A NO_GO emits a ``skipped`` event for the
draft stage so the UI can show the pipeline short-circuited on purpose."""

from __future__ import annotations

from ...config import config
from ...llm.prompts import QUALIFY_SYSTEM
from ...llm.provider import LLMError, generate_structured
from ...schemas import Qualification
from ..state import LeadResearchState, emit


async def qualify_node(state: LeadResearchState) -> dict:
    emit("qualify", "start", message="Scoring fit against ICP…")

    profile = state["company_profile"]
    icp = state["icp"]
    user = (
        f"Company profile:\n{profile.model_dump_json(indent=2)}\n\n"
        f"Client Ideal Customer Profile (ICP):\n{icp.model_dump_json(indent=2)}\n\n"
        f"Score the fit 0–100 and explain the matched criteria and gaps."
    )

    try:
        qual = await generate_structured(QUALIFY_SYSTEM, user, Qualification)
    except LLMError as exc:
        qual = Qualification(
            fit_score=0, verdict="NO_GO", reasoning=f"Qualification unavailable: {exc}"
        )

    # Pin the verdict to the threshold so it matches the displayed score.
    qual.verdict = "GO" if qual.fit_score >= config.qualify_threshold else "NO_GO"

    emit("qualify", "done", data=qual.model_dump())
    if qual.verdict == "NO_GO":
        emit("draft", "skipped", message="Below fit threshold — no email drafted.")
    return {"qualification": qual}
