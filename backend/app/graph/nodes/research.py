"""Agent 1 — Company research.

Builds a factual ``CompanyProfile`` from public web pages. For curated demo
companies it uses the seed fixtures (those are fictional, so live search can't
find them); for any other name it does live keyless search + LLM summarization,
and degrades gracefully if neither the web nor the LLM is available."""

from __future__ import annotations

from ...config import config
from ...data.seed import lookup
from ...llm.prompts import RESEARCH_SYSTEM
from ...llm.provider import LLMError, generate_structured
from ...schemas import CompanyProfile
from ...tools.websearch import web_search
from ..state import LeadResearchState, emit


async def research_node(state: LeadResearchState) -> dict:
    name = state["company_name"]
    emit("research", "start", message=f"Researching {name}…")

    seeded = lookup(name)
    if seeded is not None:
        profile = seeded[0]
        emit("research", "done", data=profile.model_dump())
        return {"company_profile": profile, "raw_sources": profile.sources}

    sources: list[str] = []
    corpus = ""
    if config.web_search_enabled:
        results = await web_search(f"{name} company overview about products", limit=config.max_sources)
        sources = [r.url for r in results]
        corpus = "\n\n".join(f"# {r.title}\n{r.url}\n{r.text}" for r in results)[:6000]

    if corpus:
        user = (
            f"Company name: {name}\n\n"
            f"Raw text from public web pages:\n{corpus}\n\n"
            "Build the company profile from these sources only."
        )
        try:
            profile = await generate_structured(RESEARCH_SYSTEM, user, CompanyProfile)
            profile.name = profile.name or name
            profile.sources = profile.sources or sources
        except LLMError as exc:
            profile = _fallback(name, sources, str(exc))
    else:
        profile = _fallback(name, sources, "No public web results found.")

    emit("research", "done", data=profile.model_dump())
    return {"company_profile": profile, "raw_sources": sources}


def _fallback(name: str, sources: list[str], reason: str) -> CompanyProfile:
    return CompanyProfile(
        name=name,
        description=f"Limited public information available. ({reason})",
        sources=sources,
    )
