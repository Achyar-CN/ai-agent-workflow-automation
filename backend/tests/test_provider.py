"""Provider parsing/validation — the deterministic core of the LLM adapter."""

import pytest

from app.llm.provider import LLMError, _parse, _validate
from app.schemas import Qualification


def test_parse_accepts_json_string():
    qual = _parse('{"fit_score": 80, "verdict": "GO"}', Qualification)
    assert qual.fit_score == 80


def test_parse_accepts_dict():
    qual = _parse({"fit_score": 30, "verdict": "NO_GO"}, Qualification)
    assert qual.verdict == "NO_GO"


def test_parse_rejects_malformed_json():
    with pytest.raises(LLMError):
        _parse("{not json", Qualification)


def test_validate_rejects_schema_violation():
    with pytest.raises(LLMError):
        _validate({"fit_score": 999, "verdict": "GO"}, Qualification)
