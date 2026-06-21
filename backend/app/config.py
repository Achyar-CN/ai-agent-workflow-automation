"""Centralized env-driven config.

Mirrors the spirit of the Next.js repo's ``lib/config.ts``: read every env var
once, expose a single frozen object with sane defaults so the rest of the code
never touches ``os.environ`` directly.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

# Load .env (local dev). In production the real environment wins.
load_dotenv()


def _str(name: str, default: str) -> str:
    return os.environ.get(name, default).strip()


def _int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def _bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _list(name: str, default: str) -> list[str]:
    return [p.strip() for p in _str(name, default).split(",") if p.strip()]


@dataclass(frozen=True)
class Config:
    # LLM provider
    provider: str = field(default_factory=lambda: _str("LLM_PROVIDER", "ollama").lower())
    ollama_base_url: str = field(default_factory=lambda: _str("OLLAMA_BASE_URL", "http://127.0.0.1:11434"))
    ollama_model: str = field(default_factory=lambda: _str("OLLAMA_MODEL", "llama3.2:3b"))
    anthropic_api_key: str = field(default_factory=lambda: _str("ANTHROPIC_API_KEY", ""))
    claude_model: str = field(default_factory=lambda: _str("CLAUDE_MODEL", "claude-opus-4-8"))

    # Pipeline behaviour
    qualify_threshold: int = field(default_factory=lambda: _int("QUALIFY_THRESHOLD", 60))
    web_search_enabled: bool = field(default_factory=lambda: _bool("WEB_SEARCH_ENABLED", True))
    max_sources: int = field(default_factory=lambda: _int("MAX_SOURCES", 5))
    searxng_url: str = field(default_factory=lambda: _str("SEARXNG_URL", ""))

    # Server
    cors_origins: list[str] = field(default_factory=lambda: _list("CORS_ORIGINS", "http://localhost:3000"))


config = Config()
