# AI Sales Lead Researcher

A multi-agent system that turns a single company name into a qualified lead and a
ready-to-send, personalized cold email — in seconds. Built to demonstrate that an
AI pipeline can absorb the hours of manual research an SDR does per account.

> **One input → four agents → a decision and a draft.**
> Type `Acme Corp`, watch the pipeline research it, find the decision-makers, score
> it against your Ideal Customer Profile, and (if it qualifies) write the email.

---

## What it does

Given a **company name** and your **Ideal Customer Profile (ICP)**, a LangGraph
pipeline runs four specialized agents and streams their progress live:

| # | Agent | Output |
|---|-------|--------|
| 1 | **Research** | Company profile (industry, size, location, products, recent signals) from public web sources |
| 2 | **Enrich** | Key decision-makers from **public pages only** — each with its source URL |
| 3 | **Qualify** | A 0–100 fit score vs. your ICP, with matched criteria, gaps, and a **GO / NO-GO** verdict |
| 4 | **Draft** | A personalized cold email — *only when the lead qualifies* |

The decision after step 3 is the point of the project: an unqualified lead
**short-circuits** and never reaches the drafting agent. That's real SDR triage,
not a linear script.

```
START → research → enrich → qualify ─┬─ (GO)──→ draft → END
                                     └─ (NO-GO)──────────→ END
```

---

## Why it's built this way

- **Hybrid stack on purpose.** The agent orchestration is **Python + LangGraph**
  (the credible, recognizable way to build multi-agent systems); the dashboard is
  **Next.js 16 + TypeScript**, sharing the design language of my
  [`local-ai-chatbot`](https://github.com) project.
- **Provider-pluggable.** One adapter, two backends: runs fully **offline on Ollama**
  (free, private) or on a frontier **Claude** model for the best output — switch with a
  single env var, no code changes.
- **Ethical by design — no LinkedIn scraping.** Scraping LinkedIn violates its ToS, is
  brittle, and gets accounts banned. This project uses **keyless public web search** plus a
  **curated seed dataset** for a reproducible demo. People are extracted only from public
  pages and always carry a source URL. *This limitation is a feature: it shows judgement,
  not a shortcut.*

---

## Architecture

```
┌─────────────────────────┐         SSE          ┌──────────────────────────────┐
│  Next.js 16 dashboard   │  ◀───────────────────│  FastAPI  (/research stream)  │
│  (streaming UI, ICP form)│   stage events       │                              │
└─────────────────────────┘                       │   LangGraph StateGraph        │
        │ proxy /api/research                      │   research→enrich→qualify→draft│
        ▼                                          │   + provider adapter          │
   one origin, no CORS                             │     Ollama  |  Claude          │
                                                   └──────────────────────────────┘
```

- **Streaming:** each agent emits `start` / `done` / `skipped` events via LangGraph's
  custom stream writer; FastAPI relays them as Server-Sent Events; the Next.js route
  proxies the stream so the browser only ever talks to one origin.
- **Structured output:** every agent returns a **Pydantic-validated** object (Ollama
  JSON-schema mode / Claude forced tool call), so the UI always receives well-formed data.

See [`docs/architecture.md`](docs/architecture.md) for the full data flow.

---

## Quickstart

### Prerequisites
- **Python 3.11+** and **Node.js 20+**
- For the default (offline) mode: **[Ollama](https://ollama.com)** running locally with a model pulled:
  ```bash
  ollama pull llama3.2:3b        # fast, CPU-friendly default
  # ollama pull qwen2.5:7b-instruct   # optional, higher quality
  ```

### 1. Backend (agents)
```bash
cd backend
python -m venv .venv
.venv/Scripts/activate          # Windows  (source .venv/bin/activate on macOS/Linux)
pip install -e ".[dev]"
cp .env.example .env            # adjust if needed
uvicorn app.main:app --reload   # → http://127.0.0.1:8000
```

### 2. Frontend (dashboard)
```bash
cd frontend
npm install
npm run dev                     # → http://localhost:3000
```

Open **http://localhost:3000**, click **“Fill demo”**, pick **Acme Corp**, and hit
**Run agents**.

---

## Switching LLM provider

Everything is driven by `backend/.env`:

```ini
# Offline, free, private (default)
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2:3b

# Frontier quality (needs an API key)
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-opus-4-8     # or claude-sonnet-4-6 for cheaper/faster
```

The agents call one interface (`app/llm/provider.py`); nothing else changes.

---

## Testing

```bash
cd backend
pytest                 # 22 tests: schemas, provider parsing, each agent node,
                       # and GO vs NO-GO graph routing — all without network or a live model
```

Deterministic logic (schema validation, web-search parsing, threshold routing) is unit
tested; LLM-dependent steps are tested by **contract** (the output validates) rather than
exact text, using the seed fixtures.

---

## Tech stack

**Backend:** Python 3.11 · LangGraph · FastAPI · Pydantic v2 · httpx · trafilatura ·
Anthropic SDK · Ollama
**Frontend:** Next.js 16 · React 19 · TypeScript (strict) · Tailwind CSS 4 · CVA · lucide-react

---

## Project layout

```
backend/    FastAPI + LangGraph multi-agent pipeline  (see backend/app/graph)
frontend/   Next.js 16 streaming dashboard
docs/       Architecture & data-ethics notes
```

## Limitations & honesty

- Live web extraction is best-effort; for unknown companies the quality depends on what's
  publicly indexed. The **seed set** (`Acme Corp`, `Globex Industries`) guarantees a clean
  demo, including offline.
- No email is *sent* — the system drafts; a human reviews and sends. That's intentional.
- `email_guess` is left empty unless an address literally appears on a public page; the
  system never fabricates contact details.
