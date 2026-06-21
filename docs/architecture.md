# Architecture

## Pipeline

The system is a [LangGraph](https://langchain-ai.github.io/langgraph/) `StateGraph`
with four agent nodes and one conditional edge.

```
START → research → enrich → qualify ─┬─ should_draft == "draft" ──→ draft → END
                                     └─ should_draft == END ───────────────→ END
```

- **research** — `app/graph/nodes/research.py`. Seeded companies use curated fixtures;
  unknown companies trigger keyless web search + LLM summarization into a `CompanyProfile`.
- **enrich** — `app/graph/nodes/enrich.py`. Extracts `KeyPerson[]` from public pages only;
  each person keeps a `source_url`. Never scrapes LinkedIn.
- **qualify** — `app/graph/nodes/qualify.py`. Scores fit 0–100 vs. the ICP. The final
  `verdict` is **pinned to `QUALIFY_THRESHOLD`** so the routing decision always matches the
  score the user sees.
- **draft** — `app/graph/nodes/draft.py`. Runs only on `GO`. Personalizes to the top key
  person using true facts from the profile.

The routing function `_should_draft` (`app/graph/graph.py`) is the multi-agent decision
point: a `NO_GO` lead skips drafting, saving tokens and reflecting real triage.

## Shared state

`LeadResearchState` (`app/graph/state.py`) is a `TypedDict` that each node reads from and
returns a partial update to. Fields fill in order: `company_profile` → `key_people` →
`qualification` → `email_draft`.

## Streaming

Nodes call `emit(stage, status, data)` (`app/graph/state.py`), which writes to LangGraph's
custom stream writer. The server consumes the graph with
`graph.astream(state, stream_mode="custom")` and relays each event as **Server-Sent
Events** (`app/main.py`). Outside a streaming run (e.g. unit tests) `emit` is a silent
no-op, so nodes stay directly testable.

The Next.js route `frontend/app/api/research/route.ts` proxies the SSE stream so the
browser talks to a single origin (no CORS). `frontend/lib/api.ts` parses the stream and
dispatches typed `StageEvent`s to the dashboard.

## LLM provider adapter

`app/llm/provider.py` exposes one async function, `generate_structured(system, user,
schema)`, returning a validated Pydantic model:

- **Ollama** — `format=<json schema>` constrains the local model to valid JSON.
- **Claude** — a single forced tool call whose `input_schema` is the Pydantic JSON schema.

Selecting a provider is a one-line env change (`LLM_PROVIDER`); the agent code is identical
for both. Failures normalize to `LLMError`, which nodes catch to degrade gracefully
(fallback profile, neutral qualification) instead of crashing the pipeline.

## Data contract

`backend/app/schemas.py` (Pydantic) is the single source of truth and is mirrored in
`frontend/lib/types.ts` (TypeScript). The SSE `data` payloads are `model_dump()`s of these
models, so the frontend can cast them directly.

## Data ethics

- **No LinkedIn scraping.** It violates LinkedIn's Terms of Service, is technically brittle,
  and risks account bans. People are sourced only from public team/leadership/press pages.
- **Provenance.** Every `KeyPerson` and `CompanyProfile` carries the `source_url`(s) it was
  built from.
- **No fabricated contacts.** `email_guess` stays empty unless an address literally appears
  in public text.
- **Reproducible demo.** The seed dataset (`app/data/seed.py`) makes the demo deterministic
  and lets it run fully offline.
