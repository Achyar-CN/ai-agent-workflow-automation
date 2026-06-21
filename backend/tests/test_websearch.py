"""Pure parser tests for the keyless web search (no network)."""

from app.tools.fetch import strip_tags
from app.tools.websearch import (
    _DDG_LINK_RE,
    _DDG_SNIPPET_RE,
    _parse,
    parse_searxng,
    unwrap,
)


def test_strip_tags_decodes_entities_and_collapses_space():
    assert strip_tags("<p>Acme  &amp;   Co</p>") == "Acme & Co"


def test_unwrap_extracts_real_url_from_ddg_redirect():
    href = "//duckduckgo.com/l/?uddg=https%3A%2F%2Facme.com%2Fabout&rut=x"
    assert unwrap(href) == "https://acme.com/about"


def test_parse_ddg_html_pairs_links_and_snippets():
    html = (
        '<a class="result__a" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Facme.com">Acme Corp</a>'
        '<a class="result__snippet">Logistics automation platform</a>'
    )
    results = _parse(html, _DDG_LINK_RE, _DDG_SNIPPET_RE, limit=5)
    assert len(results) == 1
    assert results[0].url == "https://acme.com"
    assert results[0].title == "Acme Corp"
    assert "Logistics" in results[0].snippet


def test_parse_searxng_filters_non_http():
    payload = {"results": [{"title": "A", "url": "https://a.com", "content": "x"},
                            {"title": "B", "url": "ftp://b.com"}]}
    results = parse_searxng(payload, limit=5)
    assert len(results) == 1
    assert results[0].url == "https://a.com"
