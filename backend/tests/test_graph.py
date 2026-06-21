"""End-to-end graph routing: the GO path drafts, the NO_GO path short-circuits."""

import pytest
from langgraph.graph import END

from app.graph.graph import _should_draft, graph
from app.graph.nodes import draft as draft_mod
from app.graph.nodes import qualify as qualify_mod
from app.schemas import ICP, EmailDraft, Qualification


@pytest.fixture
def icp() -> ICP:
    return ICP(target_industries=["B2B SaaS"], value_proposition="We automate lead research.",
               sender_name="Sam", sender_company="LeadBot", sender_role="Founder")


def test_should_draft_routes_on_verdict():
    assert _should_draft({"qualification": Qualification(fit_score=80, verdict="GO")}) == "draft"
    assert _should_draft({"qualification": Qualification(fit_score=10, verdict="NO_GO")}) == END
    assert _should_draft({}) == END


async def test_full_pipeline_go_path_produces_email(monkeypatch, icp):
    async def good_qual(system, user, schema):
        return Qualification(fit_score=90, verdict="GO", reasoning="great fit")

    async def good_draft(system, user, schema):
        return EmailDraft(subject="Quick idea", body="Hi Dana…")

    monkeypatch.setattr(qualify_mod, "generate_structured", good_qual)
    monkeypatch.setattr(draft_mod, "generate_structured", good_draft)

    final = await graph.ainvoke({"company_name": "Acme Corp", "icp": icp})
    assert final["qualification"].verdict == "GO"
    assert final["email_draft"].subject == "Quick idea"
    assert final["key_people"]  # enrichment ran


async def test_full_pipeline_no_go_path_skips_draft(monkeypatch, icp):
    async def bad_qual(system, user, schema):
        return Qualification(fit_score=15, verdict="NO_GO", reasoning="poor fit")

    def must_not_run(*a, **k):  # pragma: no cover
        raise AssertionError("draft must not run on NO_GO")

    monkeypatch.setattr(qualify_mod, "generate_structured", bad_qual)
    monkeypatch.setattr(draft_mod, "generate_structured", must_not_run)

    final = await graph.ainvoke({"company_name": "Globex Industries", "icp": icp})
    assert final["qualification"].verdict == "NO_GO"
    assert "email_draft" not in final
