"""Best-effort page-text extraction. Pulls the readable main content of a URL,
falling back to crude tag-stripping. Never raises — returns ``""`` on failure."""

from __future__ import annotations

import re

import httpx

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

_TAG_RE = re.compile(r"<[^>]+>")
_DROP_RE = re.compile(r"<(script|style|nav|footer)[\s\S]*?</\1>", re.IGNORECASE)
_WS_RE = re.compile(r"\s+")

_ENTITIES = {
    "&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"',
    "&#x27;": "'", "&#39;": "'", "&nbsp;": " ",
}


def strip_tags(html: str) -> str:
    text = _TAG_RE.sub("", html)
    for ent, ch in _ENTITIES.items():
        text = text.replace(ent, ch)
    return _WS_RE.sub(" ", text).strip()


async def fetch_page_text(url: str, limit: int = 2400, timeout: float = 6.0) -> str:
    """Return up to ``limit`` chars of readable text from ``url``."""
    try:
        async with httpx.AsyncClient(
            timeout=timeout, follow_redirects=True, headers={"User-Agent": UA}
        ) as client:
            res = await client.get(url)
        ctype = res.headers.get("content-type", "")
        if res.status_code != 200 or "text/html" not in ctype:
            return ""
        html = res.text
    except Exception:  # noqa: BLE001 — network is best-effort
        return ""

    # Prefer a proper readability extractor when available.
    try:
        import trafilatura

        extracted = trafilatura.extract(html, include_comments=False, include_tables=False)
        if extracted:
            return extracted.strip()[:limit]
    except Exception:  # noqa: BLE001 — fall through to crude strip
        pass

    body = _DROP_RE.sub(" ", html)
    return strip_tags(body)[:limit]
