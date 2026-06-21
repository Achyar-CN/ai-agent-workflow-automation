"""Keyless web search, ported from the reference repo's ``lib/websearch.ts``.

Tries backends in order until one returns results:
  1. SearXNG JSON  (if SEARXNG_URL set — most reliable, e.g. self-hosted)
  2. DuckDuckGo Lite HTML
  3. DuckDuckGo HTML
No API key, nothing logged, nothing persisted.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import unquote

import httpx

from ..config import config
from .fetch import UA, fetch_page_text, strip_tags


@dataclass
class WebResult:
    title: str
    url: str
    snippet: str
    text: str = ""


_DDG_LINK_RE = re.compile(r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>([\s\S]*?)</a>')
_DDG_SNIPPET_RE = re.compile(r'<a[^>]*class="result__snippet"[^>]*>([\s\S]*?)</a>')
_LITE_LINK_RE = re.compile(r'<a[^>]*class="result-link"[^>]*href="([^"]+)"[^>]*>([\s\S]*?)</a>')
_LITE_SNIPPET_RE = re.compile(r'<td[^>]*class="result-snippet"[^>]*>([\s\S]*?)</td>')
_UDDG_RE = re.compile(r"[?&]uddg=([^&]+)")


def unwrap(href: str) -> str:
    """DuckDuckGo wraps result URLs in a redirect; pull the real one out."""
    m = _UDDG_RE.search(href)
    if m:
        return unquote(m.group(1))
    return f"https:{href}" if href.startswith("//") else href


def _parse(html: str, link_re: re.Pattern, snippet_re: re.Pattern, limit: int) -> list[WebResult]:
    snippets = [strip_tags(s) for s in snippet_re.findall(html)]
    out: list[WebResult] = []
    for i, (href, title) in enumerate(link_re.findall(html)):
        if len(out) >= limit:
            break
        url = unwrap(href)
        if re.match(r"^https?://", url):
            snippet = snippets[i] if i < len(snippets) else ""
            out.append(WebResult(title=strip_tags(title) or url, url=url, snippet=snippet))
    return out


def parse_searxng(payload: dict, limit: int) -> list[WebResult]:
    results = payload.get("results") if isinstance(payload, dict) else None
    if not isinstance(results, list):
        return []
    out: list[WebResult] = []
    for r in results:
        url = (r or {}).get("url", "")
        if url and re.match(r"^https?://", url):
            out.append(WebResult(title=r.get("title") or url, url=url, snippet=r.get("content", "")))
        if len(out) >= limit:
            break
    return out


async def _via_searxng(client: httpx.AsyncClient, query: str, limit: int) -> list[WebResult]:
    if not config.searxng_url:
        return []
    base = config.searxng_url.rstrip("/")
    res = await client.get(
        f"{base}/search", params={"q": query, "format": "json", "safesearch": 1},
        headers={"Accept": "application/json"},
    )
    return parse_searxng(res.json(), limit) if res.status_code == 200 else []


async def _via_ddg_lite(client: httpx.AsyncClient, query: str, limit: int) -> list[WebResult]:
    res = await client.post("https://lite.duckduckgo.com/lite/", data={"q": query})
    return _parse(res.text, _LITE_LINK_RE, _LITE_SNIPPET_RE, limit) if res.status_code == 200 else []


async def _via_ddg_html(client: httpx.AsyncClient, query: str, limit: int) -> list[WebResult]:
    res = await client.get("https://html.duckduckgo.com/html/", params={"q": query})
    return _parse(res.text, _DDG_LINK_RE, _DDG_SNIPPET_RE, limit) if res.status_code == 200 else []


async def web_search(query: str, limit: int = 3, enrich: bool = True) -> list[WebResult]:
    """Return up to ``limit`` results. When ``enrich`` is set, each result's
    ``text`` is filled from the page body (best-effort)."""
    hits: list[WebResult] = []
    async with httpx.AsyncClient(timeout=8.0, follow_redirects=True, headers={"User-Agent": UA}) as client:
        for backend in (_via_searxng, _via_ddg_lite, _via_ddg_html):
            try:
                hits = await backend(client, query, limit)
                if hits:
                    break
            except Exception:  # noqa: BLE001 — try the next backend
                continue

    if not hits or not enrich:
        return hits

    for hit in hits:
        hit.text = (await fetch_page_text(hit.url)) or hit.snippet
    return hits
