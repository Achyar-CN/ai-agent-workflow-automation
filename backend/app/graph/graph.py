"""LangGraph wiring.

    START → research → enrich → qualify ─┬─(GO)──→ draft → END
                                         └─(NO_GO)──────────→ END

The conditional edge after ``qualify`` is the multi-agent decision point: an
unqualified lead skips drafting entirely, saving tokens and reflecting real SDR
triage rather than a blind linear pipeline.
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from .nodes.draft import draft_node
from .nodes.enrich import enrich_node
from .nodes.qualify import qualify_node
from .nodes.research import research_node
from .state import LeadResearchState


def _should_draft(state: LeadResearchState) -> str:
    """Route to drafting only when the lead qualified GO."""
    qual = state.get("qualification")
    return "draft" if qual is not None and qual.verdict == "GO" else END


def build_graph():
    g = StateGraph(LeadResearchState)
    g.add_node("research", research_node)
    g.add_node("enrich", enrich_node)
    g.add_node("qualify", qualify_node)
    g.add_node("draft", draft_node)

    g.add_edge(START, "research")
    g.add_edge("research", "enrich")
    g.add_edge("enrich", "qualify")
    g.add_conditional_edges("qualify", _should_draft, {"draft": "draft", END: END})
    g.add_edge("draft", END)
    return g.compile()


# Compiled once at import — reused across requests.
graph = build_graph()
