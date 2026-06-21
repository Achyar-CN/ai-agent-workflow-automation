"""Agent 2 — Key-people enrichment.

Extracts named decision-makers from PUBLIC pages only (team / leadership / about /
press). Never scrapes LinkedIn. Each person keeps the source URL they came from so
the result is auditable. Seeded companies return their curated contacts."""

from __future__ import annotations

from pydantic import BaseModel

from ...config import config
from ...data.seed import lookup
from ...llm.prompts import ENRICH_SYSTEM
from ...llm.provider import LLMError, generate_structured
from ...schemas import KeyPerson
from ...tools.websearch import web_search
from ..state import LeadResearchState, emit


class _KeyPeople(BaseModel):
    """Wrapper so the model returns a list under a named field."""

    people: list[KeyPerson]


async def enrich_node(state: LeadResearchState) -> dict:
    name = state["company_name"]
    emit("enrich", "start", message="Finding key people…")

    seeded = lookup(name)
    if seeded is not None:
        people = seeded[1]
        emit("enrich", "done", data={"people": [p.model_dump() for p in people]})
        return {"key_people": people}

    people: list[KeyPerson] = []
    if config.web_search_enabled:
        results = await web_search(f"{name} leadership team management", limit=config.max_sources)
        corpus = "\n\n".join(f"{r.url}\n{r.text}" for r in results)[:6000]
        if corpus:
            user = (
                f"Company: {name}\n\nPublic page text:\n{corpus}\n\n"
                "Extract the named key people with their roles and source URLs."
            )
            try:
                people = (await generate_structured(ENRICH_SYSTEM, user, _KeyPeople)).people
            except LLMError:
                people = []

    emit("enrich", "done", data={"people": [p.model_dump() for p in people]})
    return {"key_people": people}
