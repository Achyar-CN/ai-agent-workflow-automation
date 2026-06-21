"""Seed dataset — reproducible demo data.

Why this exists: live web extraction is noisy and depends on the network, and we
deliberately do NOT scrape LinkedIn (ToS). The seed set guarantees the demo always
works (offline too) and gives deterministic fixtures for tests. Lookups are
case-insensitive on the company name; unknown companies fall through to live search.
"""

from __future__ import annotations

from ..schemas import CompanyProfile, KeyPerson

# name (lowercased) -> (profile, key_people)
_SEED: dict[str, tuple[CompanyProfile, list[KeyPerson]]] = {
    "acme corp": (
        CompanyProfile(
            name="Acme Corp",
            industry="B2B SaaS — logistics automation",
            size="201-500",
            location="Austin, TX, USA",
            description=(
                "Acme Corp builds a logistics automation platform that helps mid-market "
                "retailers optimize warehouse routing and last-mile delivery."
            ),
            products=["Routing Engine", "Warehouse OS", "Delivery Analytics"],
            recent_signals=[
                "Raised a $25M Series B in Q1 to expand into the EU market",
                "Hiring 12 engineers and a VP of Revenue Operations",
            ],
            website="https://acme.example.com",
            sources=["https://acme.example.com/about", "https://acme.example.com/press"],
        ),
        [
            KeyPerson(
                name="Dana Whitfield",
                title="VP of Revenue Operations",
                relevance="Owns the RevOps tooling budget — direct fit for a sales-automation pitch.",
                source_url="https://acme.example.com/team",
            ),
            KeyPerson(
                name="Marco Reyes",
                title="Head of Sales",
                relevance="Feels the pain of manual lead research firsthand.",
                source_url="https://acme.example.com/team",
            ),
        ],
    ),
    "globex industries": (
        CompanyProfile(
            name="Globex Industries",
            industry="Industrial manufacturing",
            size="5000+",
            location="Osaka, Japan",
            description=(
                "Globex Industries is a legacy heavy-machinery manufacturer with limited "
                "digital sales operations and no public RevOps function."
            ),
            products=["CNC Machines", "Industrial Robotics"],
            recent_signals=["Announced a cost-cutting program and hiring freeze"],
            website="https://globex.example.com",
            sources=["https://globex.example.com/company"],
        ),
        [
            KeyPerson(
                name="Hiro Tanaka",
                title="Plant Operations Director",
                relevance="Operations-focused, not a software buyer — weak fit.",
                source_url="https://globex.example.com/leadership",
            ),
        ],
    ),
}


def lookup(company_name: str) -> tuple[CompanyProfile, list[KeyPerson]] | None:
    """Return seeded ``(profile, key_people)`` for a known company, else ``None``."""
    return _SEED.get(company_name.strip().lower())


def known_companies() -> list[str]:
    return [p.name for p, _ in _SEED.values()]
