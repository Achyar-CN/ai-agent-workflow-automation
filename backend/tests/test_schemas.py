"""Data-contract tests — the schemas the frontend mirrors."""

import pytest
from pydantic import ValidationError

from app.schemas import ICP, EmailDraft, Qualification, ResearchRequest, StageEvent


def test_icp_defaults_are_empty_not_none():
    icp = ICP()
    assert icp.target_industries == []
    assert icp.value_proposition == ""


def test_qualification_score_must_be_within_bounds():
    Qualification(fit_score=0, verdict="NO_GO")
    Qualification(fit_score=100, verdict="GO")
    with pytest.raises(ValidationError):
        Qualification(fit_score=101, verdict="GO")
    with pytest.raises(ValidationError):
        Qualification(fit_score=-1, verdict="NO_GO")


def test_qualification_verdict_is_constrained():
    with pytest.raises(ValidationError):
        Qualification(fit_score=50, verdict="MAYBE")


def test_research_request_requires_company_name():
    with pytest.raises(ValidationError):
        ResearchRequest(company_name="")
    req = ResearchRequest(company_name="Acme Corp")
    assert isinstance(req.icp, ICP)


def test_email_draft_requires_subject_and_body():
    with pytest.raises(ValidationError):
        EmailDraft(subject="Hi")  # missing body


def test_stage_event_roundtrips():
    ev = StageEvent(stage="research", status="done", data={"name": "Acme"})
    dumped = ev.model_dump()
    assert dumped["stage"] == "research"
    assert dumped["data"]["name"] == "Acme"
