"""Agent node behaviour with seed data + a mocked LLM (no network, no real model)."""

import pytest

from app.graph.nodes import draft as draft_mod
from app.graph.nodes import qualify as qualify_mod
from app.graph.nodes.enrich import enrich_node
from app.graph.nodes.research import research_node
from app.schemas import ICP, CompanyProfile, EmailDraft, KeyPerson, Qualification


@pytest.fixture
def icp() -> ICP:
    return ICP(
        target_industries=["B2B SaaS"],
        company_sizes=["201-500"],
        regions=["USA"],
        value_proposition="We automate sales lead research.",
        sender_name="Sam Seller",
        sender_company="LeadBot",
        sender_role="Founder",
    )


async def test_research_node_uses_seed_for_known_company():
    out = await research_node({"company_name": "Acme Corp", "icp": ICP()})
    profile = out["company_profile"]
    assert isinstance(profile, CompanyProfile)
    assert profile.name == "Acme Corp"
    assert profile.sources  # seed carries source URLs


async def test_enrich_node_returns_seeded_people_with_sources():
    out = await enrich_node({"company_name": "Acme Corp", "icp": ICP()})
    people = out["key_people"]
    assert people and all(isinstance(p, KeyPerson) for p in people)
    assert all(p.source_url for p in people)  # auditable


async def test_qualify_node_pins_verdict_to_threshold(monkeypatch, icp):
    async def fake(system, user, schema):
        # Model proposes GO, but the score is below the default threshold (60).
        return Qualification(fit_score=40, verdict="GO", reasoning="weak")

    monkeypatch.setattr(qualify_mod, "generate_structured", fake)
    out = await qualify_node_state(icp)
    assert out["qualification"].verdict == "NO_GO"  # threshold overrides the model


async def qualify_node_state(icp):
    from app.graph.nodes.qualify import qualify_node

    state = {
        "company_name": "Acme Corp",
        "icp": icp,
        "company_profile": CompanyProfile(name="Acme Corp", industry="B2B SaaS", size="201-500"),
    }
    return await qualify_node(state)


async def test_qualify_node_go_when_above_threshold(monkeypatch, icp):
    async def fake(system, user, schema):
        return Qualification(fit_score=85, verdict="NO_GO", reasoning="strong")

    monkeypatch.setattr(qualify_mod, "generate_structured", fake)
    out = await qualify_node_state(icp)
    assert out["qualification"].verdict == "GO"


async def test_draft_node_personalizes_to_top_person(monkeypatch, icp):
    captured = {}

    async def fake(system, user, schema):
        captured["user"] = user
        return EmailDraft(subject="Hi", body="Body", personalization_hooks=["Series B"])

    monkeypatch.setattr(draft_mod, "generate_structured", fake)
    state = {
        "company_name": "Acme Corp",
        "icp": icp,
        "company_profile": CompanyProfile(name="Acme Corp"),
        "key_people": [KeyPerson(name="Dana Whitfield", title="VP RevOps")],
    }
    out = await draft_mod.draft_node(state)
    assert out["email_draft"].recipient == "Dana Whitfield"
    assert "Dana Whitfield" in captured["user"]
