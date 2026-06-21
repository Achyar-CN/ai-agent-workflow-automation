"""LLM provider adapter.

One async entry point — :func:`generate_structured` — that returns a validated
Pydantic model regardless of backend. Switch backends with ``LLM_PROVIDER`` and
nothing else in the codebase changes. This pluggability is the project's
selling point: it runs fully offline on Ollama, or on a frontier Claude model.
"""

from __future__ import annotations

import json
from functools import lru_cache
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from ..config import config

T = TypeVar("T", bound=BaseModel)


class LLMError(RuntimeError):
    """Raised when the provider call or parsing fails. Nodes treat this as a
    signal to fall back to seed data rather than crashing the pipeline."""


# ── Clients (lazy, cached) ───────────────────────────────────────────────────


@lru_cache(maxsize=1)
def _ollama_client():
    from ollama import AsyncClient

    # Generous ceiling for CPU inference, but bounded so a missing/loading model
    # degrades to a fallback instead of hanging the pipeline forever.
    return AsyncClient(host=config.ollama_base_url, timeout=180)


@lru_cache(maxsize=1)
def _anthropic_client():
    from anthropic import AsyncAnthropic

    if not config.anthropic_api_key:
        raise LLMError("LLM_PROVIDER=claude but ANTHROPIC_API_KEY is empty.")
    return AsyncAnthropic(api_key=config.anthropic_api_key)


# ── Backends ─────────────────────────────────────────────────────────────────


async def _ollama_structured(system: str, user: str, schema: type[T]) -> T:
    """Ollama structured output: pass the JSON schema as ``format`` so the model
    is constrained to valid JSON."""
    resp = await _ollama_client().chat(
        model=config.ollama_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        format=schema.model_json_schema(),
        options={"temperature": 0.4},
    )
    content = resp["message"]["content"]
    return _parse(content, schema)


async def _claude_structured(system: str, user: str, schema: type[T]) -> T:
    """Claude structured output via a single forced tool call whose input schema
    is the Pydantic JSON schema."""
    tool_name = schema.__name__.lower()
    resp = await _anthropic_client().messages.create(
        model=config.claude_model,
        max_tokens=2048,
        system=system,
        messages=[{"role": "user", "content": user}],
        tools=[
            {
                "name": tool_name,
                "description": f"Return a well-formed {schema.__name__}.",
                "input_schema": schema.model_json_schema(),
            }
        ],
        tool_choice={"type": "tool", "name": tool_name},
    )
    for block in resp.content:
        if block.type == "tool_use":
            return _validate(block.input, schema)
    raise LLMError("Claude returned no tool_use block.")


# ── Public API ───────────────────────────────────────────────────────────────


async def generate_structured(system: str, user: str, schema: type[T]) -> T:
    """Produce a validated ``schema`` instance from the configured provider."""
    try:
        if config.provider == "claude":
            return await _claude_structured(system, user, schema)
        return await _ollama_structured(system, user, schema)
    except LLMError:
        raise
    except Exception as exc:  # noqa: BLE001 — normalize every backend failure
        raise LLMError(f"{config.provider} call failed: {exc}") from exc


# ── Parsing helpers ──────────────────────────────────────────────────────────


def _parse(content: str | dict, schema: type[T]) -> T:
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except json.JSONDecodeError as exc:
            raise LLMError(f"Model did not return valid JSON: {exc}") from exc
    return _validate(content, schema)


def _validate(payload: dict, schema: type[T]) -> T:
    try:
        return schema.model_validate(payload)
    except ValidationError as exc:
        raise LLMError(f"Output failed {schema.__name__} validation: {exc}") from exc
