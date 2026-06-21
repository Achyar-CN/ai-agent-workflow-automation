"""Data contract for the lead-research pipeline.

These Pydantic models are the single source of truth. The frontend mirrors them
in ``frontend/lib/types.ts`` — keep the two in sync.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Verdict = Literal["GO", "NO_GO"]


class ICP(BaseModel):
    """Ideal Customer Profile — the client's qualification criteria."""

    target_industries: list[str] = Field(default_factory=list)
    company_sizes: list[str] = Field(default_factory=list, description="e.g. '1-50', '51-200', '500+'")
    regions: list[str] = Field(default_factory=list)
    buying_signals: list[str] = Field(
        default_factory=list,
        description="Signals that indicate a good time to reach out (hiring, funding, new product).",
    )
    value_proposition: str = Field("", description="What the sender offers, in one or two sentences.")
    sender_name: str = ""
    sender_company: str = ""
    sender_role: str = ""


class CompanyProfile(BaseModel):
    """Output of the research agent."""

    name: str
    industry: str = ""
    size: str = ""
    location: str = ""
    description: str = ""
    products: list[str] = Field(default_factory=list)
    recent_signals: list[str] = Field(default_factory=list, description="Recent news / hiring / funding.")
    website: str = ""
    sources: list[str] = Field(default_factory=list, description="URLs the profile was built from.")


class KeyPerson(BaseModel):
    """A decision-maker discovered from public sources only."""

    name: str
    title: str = ""
    relevance: str = Field("", description="Why this person matters for the outreach.")
    source_url: str = Field("", description="Public page this person was found on (transparency).")
    email_guess: str = Field("", description="Heuristic guess, never scraped. May be empty.")


class Qualification(BaseModel):
    """Output of the qualification agent — does this lead fit the ICP?"""

    fit_score: int = Field(ge=0, le=100)
    verdict: Verdict
    reasoning: str = ""
    matched_criteria: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)


class EmailDraft(BaseModel):
    """Output of the drafting agent — a personalized cold email."""

    recipient: str = ""
    subject: str
    body: str
    personalization_hooks: list[str] = Field(
        default_factory=list,
        description="The specific facts that make this email feel hand-written.",
    )


# ── API I/O ─────────────────────────────────────────────────────────────────


class ResearchRequest(BaseModel):
    company_name: str = Field(min_length=1)
    icp: ICP = Field(default_factory=ICP)


# Pipeline stages, in order. The frontend renders one progress row per stage.
Stage = Literal["research", "enrich", "qualify", "draft"]

# Per-stage lifecycle as streamed over SSE.
StageStatus = Literal["start", "done", "skipped", "error"]


class StageEvent(BaseModel):
    """One SSE message: a stage changed state, optionally carrying its result."""

    stage: Stage
    status: StageStatus
    data: dict | None = None
    message: str = ""
