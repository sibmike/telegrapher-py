# Telegrapher Python Package — Design + Adoption Plan

> **Positioning**
> *Caveman makes agents speak less. Telegrapher makes knowledge weigh less.*

> **v0.1 headline**
> *Compress your LLM memory locally. Keep twice as much conversation context without losing facts.*

> **Source-of-truth note**
> This plan was authored in plan-mode in the research repo (`C:\Users\mikea\SCRIPTS\telegrapher_ai`) and migrated here as the canonical design record for the `telegrapher_py` package. Module paths below use the `src/telegrapher/...` src-layout for this repo. Origin code that gets refactored lives at `..\telegrapher_ai\code\telegrapher\`.

> **Amendment 2026-04-27 — LangChain BaseMemory adapter dropped from v0.1**
> The Phase 4 LangChain `TelegrapherSummaryMemory` adapter described below was **removed** from v0.1 mid-implementation. `langchain_core 1.x` deleted `BaseMemory` in favour of LangGraph's checkpointer pattern, so any subclass adapter would be deprecated on the day it shipped. Decision: ship `ConversationCompactor` as a generic primitive in v0.1; framework adapters (LangChain checkpointer, LlamaIndex, Haystack, LiteLLM) become opt-in v0.2 integrations once we have signal on which one matters most. References to `telegrapher.integrations.langchain` and the `[langchain]` extra below are kept as the original design trace but no longer reflect what's shipping. See [PS-001](../product-specs/ps-001-memory-wedge.md) and [the active exec plan](../exec-plans/active/v0.1-memory-wedge.md) for the current surface.

## Context

You have a working Telegraph English (TE) compression pipeline (paper draft v0.8): ~50% token reduction, ~99% key-fact preservation, 85–96% fine-fact preservation across LongBench-v2. Two trained **9B bidirectional SLMs** (NL ↔ TE) with a **compression-ratio toggle** (L1/L3/L5) are the new ingredient that wasn't in the research-repo `code/telegrapher/` package — that codebase still calls `gpt-4.1` / `o4-mini` for compression.

The user wants to package this for distribution, taking inspiration from `JuliusBrussee/caveman` (LLM-based prompt-shrinker). Caveman is text-in → simpler-text-out via an external LLM API. **Telegrapher's owned model + bidirectional translation + compression knob flip the package from a "prompt shrinker" into a memory and storage format**.

### Decisions confirmed

1. **Scope (phased)**: launch with one dominant wedge — *local memory compression*. RAG and middleware ship later as documented "next" patterns, not as v0.1 promises.
2. **Model distribution**: local weights only, pulled from Hugging Face Hub (privacy-first, self-hosted, no managed service in v0.1)
3. **Packaging**: single PyPI package, optional extras

### Language discipline

Two phrases to **never use**:

- ❌ *"Lossless"* — TE is not literally reconstructive. Use **"fact-preserving reversible compression"** or **"bidirectional compression with measured round-trip fidelity"**.
- ❌ *"Free at inference"* — local inference still costs GPU/CPU/electricity. Use **"no per-token API fee; runs locally"**.

These guardrails apply to docs, README, blog posts, and conference talks.

---

## Phase plan

The package ships in three phases. Each phase is independently coherent (works alone, ships, gets feedback). Later phases extend the surface; they do not refactor it.

### Phase 0 — *Inherited docs cleanup* (prerequisite, not user-facing)

Before any v0.1 implementation starts, the `docs/` skeleton inherited from a neighbor project must be scrubbed of dataroom/AWS/founder/investor specifics while preserving the universal harness wisdom (debugging protocol, core beliefs, agent-behavior contract). This is a one-time hygiene pass — see [`inherited-docs-cleanup.md`](inherited-docs-cleanup.md) for the full per-file decision matrix and verification grep commands.

### v0.1 — *Memory wedge* (the launch)

**One headline, one demo, one CLI command.** Resist scope creep here — the launch product proves the model works end-to-end before any RAG / middleware integration risk gets bundled in.

Surface area:

```python
# (1) Core primitive
from telegrapher import Telegrapher

# Default — uses the packaged bidirectional model
tg = Telegrapher()

# Explicit single bidirectional model
tg = Telegrapher(model="telegrapher-ai/te-bidi-9b")  # HF Hub path (stub)

# Two unidirectional models — compressor + expander
tg = Telegrapher(
    model_in="telegrapher-ai/te-compressor-9b",   # NL → TE  (stub)
    model_out="telegrapher-ai/te-expander-9b",    # TE → NL  (stub)
)

te = tg.compress(text, level="L3")
nl = tg.expand(te)

# (2) The wedge — drop-in memory compactor
from telegrapher.memory import ConversationCompactor
memory = ConversationCompactor(level="L3", max_tokens=4000)

# (3) The trust artifact — eval on the user's corpus
$ tg eval ./my_docs --report report.md
```

**Model parameters**: the constructor accepts either `model=` (one bidirectional model used for both directions) or `model_in=` / `model_out=` (two unidirectional models). The two forms are mutually exclusive — passing both raises. Internally, if `model_in` and `model_out` resolve to the same string, the weights are loaded once and shared. This keeps the API simple while letting us swap between architectures during fine-tuning without breaking users.

**HF Hub paths are placeholders** until fine-tuning settles. The strings `telegrapher-ai/te-bidi-9b`, `te-compressor-9b`, `te-expander-9b` above are stubs — they will be replaced with the real HF org and model names before the first PyPI release. Until then the package can ship with `model=` defaulting to a known-good local fixture for tests, with the production default bound at release-time via `pyproject.toml` package metadata or `telegrapher.core.config.DEFAULT_MODEL`.

That is the entire v0.1 promise. Three things. Everything else is a "next" example in the docs.

**v0.1 modules**: `telegrapher.core`, `telegrapher.memory`, `telegrapher.eval`, `telegrapher.cli` (with only `compress`, `expand`, `eval`, `download-model`).

**v0.1 audience**: Ring 1 — solo devs and small teams building chatbots/agents.

**v0.1 success criteria**:
- 1k GitHub stars in 90 days
- Round-trip fidelity ≥95% on key facts at L3 across user-submitted corpora
- One LangChain integration PR merged
- `tg eval` cited in at least one third-party blog post

### v0.2 — *RAG wedge* (when memory has signal)

Adds vector store integrations and TE-aware retrieval. Triggered by user demand from v0.1, not by calendar.

Adds: `telegrapher.chunk` (semantic chunker), `telegrapher.embed`, `telegrapher.store` (Pinecone first), `telegrapher.retrieve` (hybrid BM25+dense), `telegrapher.rag` (turnkey pipeline). New CLI: `tg ingest`.

Audience expansion: Ring 2 (RAG startups).

### v0.3 — *Middleware wedge*

Adds `telegrapher.preprocess` and `with_te(client)` middleware for OpenAI/Anthropic/LiteLLM, plus `tg serve` for polyglot teams. This is the literal caveman-analogue, deferred because it's the *least* differentiated wedge (caveman already exists for prompt preprocessing — leading with this gives away the positioning).

Audience expansion: Rings 3–5 (regulated enterprises, researchers, framework maintainers).

---

## Target audience

Five concentric rings, ordered from highest fit / fastest-to-adopt outward.

### Ring 1 — Solo devs and small teams building LLM chatbots & agents *(primary)*

- **Who**: indie hackers, AI startups (1–10 engineers), internal tool builders at any company
- **Stack**: Python, OpenAI/Anthropic API, LangChain or LlamaIndex, sometimes a vector DB
- **Pain points**: context-window costs spiral on long sessions; `ConversationSummaryMemory` is lossy; their bot "forgets" customer details
- **Why TE wins for them**: drop-in LangChain memory, two-line change, ~2× more retained context per token budget, no per-token API fee (runs locally on their box)
- **How they find you**: HN, Twitter, dev.to tutorials, PRs into LangChain-community
- **Adoption friction**: needs `pip install` + ~20 GB model download. Mitigated with quantized 4-bit weights (~5 GB).

### Ring 2 — Startups running production RAG

- **Who**: product startups, Series A/B, "AI search" / "AI knowledge base" / "AI customer support" companies
- **Stack**: Pinecone / Qdrant / Weaviate, OpenAI embeddings, custom retrieval pipeline
- **Pain points**: vector DB bills scale linearly with chunk count and chunk size; embedding cost on re-ingest is brutal; retrieval quality plateaus
- **Why TE wins for them**: compress-then-embed → 50% storage, 50% write cost. TE atomic lines align with retrieval granularity. Hybrid BM25 over TE is genuinely better (entities preserved, stopwords gone).
- **How they find you**: a benchmark blog post that shows their exact stack getting cheaper without losing accuracy, comparing against LLMLingua2 (already in your benchmarks)
- **Adoption friction**: re-ingest cost + DB schema changes (need an `original_ref` column). One-shot CLI helper kills this.

### Ring 3 — Enterprises with privacy / compliance constraints

- **Who**: healthcare, legal, financial services, government contractors, regulated industries
- **Stack**: often air-gapped or private cloud; can't use OpenAI/Anthropic for sensitive payloads; sometimes running self-hosted LLMs already
- **Pain points**: data can't leave the VPC. Self-hosted LLMs are slow / expensive. Multi-agent systems compound the cost.
- **Why TE wins for them**: 100% local. Compression makes a 7B/13B local LLM punch above its weight. Auditable (every TE line maps back to one NL sentence — defensible in legal review).
- **How they find you**: case studies, conference talks, partnerships with regulated-industry consultancies
- **Adoption friction**: enterprise procurement, security review. Solved by clean MIT licensing + reproducible builds + SBOM.

### Ring 4 — Research labs and ML engineers

- **Who**: academics, applied research at FAANG-likes, AI evaluators
- **Stack**: HF Hub, vLLM, custom training pipelines, often pytorch from scratch
- **Pain points**: long-context experiments are expensive; reproducibility is hard when prompts are huge; benchmarks don't directly measure compression-fidelity tradeoffs
- **Why TE wins for them**: TE as a research artifact — your published v0.8 paper + HF model card give them a citable, reproducible compression baseline. Your `eval` module is the benchmarking tool they need anyway.
- **How they find you**: arxiv paper, HuggingFace trending models, NeurIPS/ACL workshops
- **Adoption friction**: low — researchers love a paper + weights + benchmark.

### Ring 5 — Framework / tooling maintainers

- **Who**: maintainers of LangChain, LlamaIndex, Haystack, LiteLLM, Continue, Cody, Cursor, etc.
- **Stack**: their own framework + integrations
- **Pain points**: their users complain about token costs; competitive pressure to lower latency
- **Why TE wins for them**: TE as a built-in option in their framework gives them a "we got 30% cheaper" headline
- **How they find you**: you write the integration PR. They merge it. Their docs surface you.
- **Adoption friction**: zero on their side once the PR is merged. The work is yours.

---

## Why people will adopt TE — five concrete value props

| # | Value prop | Headline | Quantified | Phase |
|---|---|---|---|---|
| **1** | **Bigger effective memory** | "Keep twice as much conversation context, don't lose facts." | ~50% token reduction at L3, ≤1pp accuracy drop on key facts | v0.1 |
| **2** | **Cheaper LLM bills** | "Halve your input tokens." | Same numbers, inverted | v0.1 |
| **3** | **Privacy-preserving compression** | "Compress your data without sending it to a third-party API." | Local 9B SLM, single GPU or quantized CPU | v0.1 |
| **4** | **Cheaper RAG storage + retrieval** | "Cut your vector DB bill in half on the next re-ingest." | 50% chunk size → 50% storage + 50% write | v0.2 |
| **5** | **Better retrieval quality** | "Hybrid BM25 + dense over TE retrieves better than over NL." | Hypothesis to validate in `eval`; paper-worthy if confirmed | v0.2 |

The launch leads with #1 alone. #2 and #3 are supporting bullets. #4 and #5 are deferred to the v0.2 announcement to keep the launch story sharp.

---

## Six usage scenarios (the demo gallery)

These are the stories your README, blog posts, and conference talks tell. Each is tagged with the phase that unlocks it.

### Scenario 1 *(v0.1)* — "My LangChain bot keeps forgetting things"

> *Persona*: indie dev building a customer support chatbot. Sessions run long. `ConversationSummaryMemory` keeps mangling phone numbers and order IDs.
>
> *Solution*: swap one import. Memory now compresses to TE instead of summarizing.

```python
# Before:
from langchain.memory import ConversationSummaryMemory
memory = ConversationSummaryMemory(llm=llm)

# After:
from telegrapher.integrations.langchain import TelegrapherSummaryMemory
memory = TelegrapherSummaryMemory(level="L3", max_tokens=4000)
```

> *Result*: ~2× more retained context per token budget, fine details (numbers, dates, names) preserved with measured round-trip fidelity ≥95% on key facts.

---

### Scenario 2 *(v0.2)* — "Our Pinecone bill is killing us"

> *Persona*: Series-A AI startup with 12M chunks indexed. $4k/mo Pinecone bill. Re-ingest costs $1.2k each time.
>
> *Solution*: re-ingest with TE compression. Same retrieval API, half the chunks-on-the-wire.

```bash
tg ingest ./corpus/ --to pinecone --index docs-v2 --level L3
```

```python
from telegrapher.store import PineconeStore
store = PineconeStore(index="docs-v2")
results = store.query("What did we ship in Q3?", top_k=5)
# results[i].te is the compressed chunk; results[i].expand() yields NL on demand
```

> *Result*: ~50% storage cost reduction, ~50% write cost reduction, comparable retrieval recall (validate via `tg eval`).

---

### Scenario 3 *(v0.1)* — "My agent loop is too slow"

> *Persona*: dev building a multi-step research agent. Each tool call replays the whole conversation. 5 hops × 8k tokens = 40k tokens per query. Cost + latency are both hurting.
>
> *Solution*: TE memory keeps the history at half the size at every hop, compounding savings.

```python
from telegrapher.memory import ConversationCompactor

memory = ConversationCompactor(level="L3", max_tokens=4000, expand_on_load=False)
agent = Agent(memory=memory, llm=llm)  # llm gets TE-formatted history; trained models read it natively
```

> *Result*: 40k → 20k tokens per query → ~2× faster and ~2× cheaper.

---

### Scenario 4 *(v0.1 + v0.3)* — "We're a healthcare startup, can't send PHI to OpenAI"

> *Persona*: HIPAA-bound team. All inference must stay in their VPC. They run a local Llama-3.1-8B but the context is too small for full patient histories.
>
> *Solution*: Telegrapher runs locally too. Compress patient notes; the local LLM now fits 2× as much.

```python
from telegrapher import Telegrapher
from telegrapher.preprocess import with_te

tg = Telegrapher()                          # local 9B SLM, no network calls
client = with_te(local_llm_client, level="L3")
response = client.chat.completions.create(messages=[
    {"role": "system", "content": "You are a clinical assistant."},
    {"role": "user", "content": full_patient_history},
])
# `with_te` compressed the user message before it hit the model
```

> *Result*: privacy preserved, effective context doubled, no API calls leave the VPC.

---

### Scenario 5 *(v0.2)* — "RAG retrieval misses fine details in long contracts"

> *Persona*: legal-tech engineer. Their RAG pipeline retrieves whole paragraphs and the LLM misses single-sentence qualifications buried in the middle.
>
> *Solution*: TE chunking is atomic-line — each claim is independently retrievable.

```python
from telegrapher.chunk import semantic_chunk
from telegrapher.store import QdrantStore

chunks = semantic_chunk(contract_text, level="L3")     # one TE atomic line per claim
store = QdrantStore(collection="contracts")
store.upsert(chunks)

results = store.query("What are the termination conditions?", top_k=5)
```

> *Result*: each retrieved unit is one factual claim. Recall@5 on fine facts goes up because granularity matches the question.

---

### Scenario 6 *(v0.1)* — "I'm skeptical — does this actually work on MY data?"

> *Persona*: senior engineer evaluating compression methods. Reads your blog, doesn't trust benchmarks on someone else's corpus.
>
> *Solution*: one CLI command runs your benchmark on their corpus and writes a report.

```bash
tg eval ./our-internal-docs/ --report report.md --baseline llmlingua2
```

> *Output*: per-document compression ratio, QA fidelity (auto-generated QA pairs), comparison against LLMLingua2-50/33, hybrid-search recall@k. They share the report internally; adoption decision becomes data-driven.

---

## How users plug it in — five integration patterns

The package supports five entry points, each chosen for a different developer "shape". Mass adoption depends on each pattern being **one import + one config line**. v0.1 ships patterns 1, 2, and the v0.1 subset of 5.

### Pattern 1 *(v0.1)* — As a Python primitive (lowest level)

```python
from telegrapher import Telegrapher
tg = Telegrapher()
te = tg.compress(text, level="L3")
nl = tg.expand(te)
```

For: scripts, notebooks, custom pipelines.

### Pattern 2 *(v0.1)* — As LangChain memory (drop-in)

```python
from telegrapher.integrations.langchain import TelegrapherSummaryMemory
memory = TelegrapherSummaryMemory(level="L3", max_tokens=4000)
```

For: anyone with an existing LangChain bot.

### Pattern 3 *(v0.3)* — As an OpenAI/Anthropic client middleware (transparent)

```python
from openai import OpenAI
from telegrapher.preprocess import with_te
client = with_te(OpenAI(), level="L3")
# every prompt is auto-compressed; outputs unchanged
```

For: existing apps that don't want to refactor — wrap the client and they're done.

### Pattern 4 *(v0.2)* — As a vector store backend (drop-in)

```python
from telegrapher.store import PineconeStore
store = PineconeStore(index="docs", level="L3")
store.upsert(documents)              # auto-chunk, auto-compress, auto-embed
results = store.query("…")
```

For: RAG builders.

### Pattern 5 — As a CLI for batch operations (no Python required)

```bash
# v0.1
tg compress doc.txt --level L3 -o doc.te
tg expand doc.te -o doc.txt
tg eval ./corpus/ --report report.md
tg download-model

# v0.2
tg ingest ./corpus/ --to pinecone --index docs --level L3

# v0.3
tg serve --port 8000   # FastAPI for non-Python clients
```

For: data engineers, polyglot teams, ops people.

**Design discipline**: every pattern hides the model loading, caching, error retries, and quantization. The user doesn't think about TE grammar, the SLM, or HF Hub. Just install + import + go.

---

## Mass adoption playbook

Mass adoption isn't a feature; it's a distribution strategy. Here's the playbook.

### 1. Frictionless install
- One `pip install telegrapher` — works without any extras for compress/expand
- Default 4-bit quantized weights (≤6 GB) auto-download on first use
- Show a progress bar; cache to `~/.cache/telegrapher/`
- Detect GPU/CPU automatically; never make the user pick

### 2. Killer first-3-minutes experience
- README opens with **Scenario 1** (LangChain memory drop-in) — a story every dev recognizes
- `tg compress sample.txt` shows the magic in one CLI command
- A `notebooks/quickstart.ipynb` that runs end-to-end on a free Colab T4

### 3. Open source, permissively licensed
- MIT for the package code
- CC-BY-SA 4.0 for the TE spec (per existing `approach_description.md` in the research repo)
- Open weights on HuggingFace Hub with a clear model card

### 4. Benchmark-first marketing
- Reuse your existing LongBench numbers in a public benchmark dashboard
- Side-by-side vs LLMLingua2 (you already have this data)
- A "TE vs no-TE" calculator on the website: paste tokens-per-month + use-case → estimated savings

### 5. Integration PRs into upstream projects
- LangChain memory PR (Ring 5 unlock) — biggest distribution lever
- LlamaIndex `Node` adapter
- LiteLLM middleware (covers all proxied LLMs in one shot)
- Continue.dev / Cursor / Cody — code editors that handle long context

### 6. Content engine
- Blog post per scenario above (six in total)
- arxiv paper companion: "Telegraph English: A Reversible Compression Format for LLM Pipelines"
- HuggingFace blog co-publication
- HN launch with the LangChain-memory scenario as the headline

### 7. Trust artifacts
- `tg eval` is the trust lever: it lets skeptics validate on their own corpus
- Public benchmark reproduction repo
- Compression-ratio leaderboard (per-domain)

### 8. Community
- GitHub Discussions for use cases
- Discord/Slack with #showcase channel
- Monthly office hours for first 6 months

### 9. Network effects
- Every TE-stored corpus is portable — same store, different LLM downstream
- Every benchmark report shared by users is an ad
- TE-aware fine-tunes (later) deepen the moat

### 10. Partnerships (later)
- Pinecone / Qdrant / Weaviate co-marketing once you have signal
- Anthropic / OpenAI dev rel for "running with smaller models" angle
- Langfuse / Helicone for observability integration

---

## Why TE > caveman, structurally

| Asset | Caveman | Telegrapher |
|---|---|---|
| Model | External LLM API | Owned 9B SLM (local, deterministic) |
| Direction | One-way (compress only) | **Bidirectional** (compress + expand) |
| Ratio control | None | L1 / L3 / L5 dial |
| Output structure | Free-form simplified text | Symbolic, atomic-line, parseable |
| Pipeline role | Prompt preprocessor | Storage + retrieval + memory format |
| Privacy | Data leaves your VPC | Stays local |

These four capabilities multiplied together unlock five distinct product wedges; caveman only has the prompt-preprocessing wedge.

---

## Proposed package: `telegrapher`

### Repo layout (src-layout)

```
telegrapher_py/
├── pyproject.toml
├── README.md
├── LICENSE                                    # MIT
├── docs/                                      (already scaffolded)
├── src/
│   └── telegrapher/
│       ├── __init__.py                        # exports Telegrapher, compress, expand
│       ├── core/                              # v0.1
│       ├── memory/                            # v0.1
│       ├── eval/                              # v0.1
│       ├── cli/                               # v0.1+
│       ├── integrations/                      # v0.1+ (langchain memory in v0.1)
│       ├── chunk/                             # v0.2
│       ├── embed/                             # v0.2
│       ├── store/                             # v0.2
│       ├── retrieve/                          # v0.2
│       ├── rag/                               # v0.2
│       ├── preprocess.py                      # v0.3
│       └── server/                            # v0.3
└── tests/
```

### Install matrix (single package + extras)

```
# v0.1
pip install telegrapher                  # core compress/expand + memory + eval + local SLM
pip install telegrapher[gpu]             # CUDA wheels, vLLM
pip install telegrapher[cpu]             # llama.cpp / GGUF for laptop inference
pip install telegrapher[langchain]       # LangChain memory adapter (TelegrapherSummaryMemory)

# v0.2
pip install telegrapher[pinecone]        # Pinecone store
pip install telegrapher[qdrant]
pip install telegrapher[weaviate]
pip install telegrapher[chroma]
pip install telegrapher[pgvector]
pip install telegrapher[llamaindex]      # LlamaIndex Node adapters

# v0.3
pip install telegrapher[openai]          # opt-in fallback to existing prompt-driven path
pip install telegrapher[server]          # FastAPI server (`tg serve`)
pip install telegrapher[all]
```

### Core API

```python
from telegrapher import Telegrapher

# Default: auto-loads the packaged bidirectional 9B from HF Hub (stub path)
tg = Telegrapher()

# Or explicitly:
tg = Telegrapher(model="telegrapher-ai/te-bidi-9b")                         # one model both ways
tg = Telegrapher(model_in="telegrapher-ai/te-compressor-9b",                # NL → TE
                 model_out="telegrapher-ai/te-expander-9b")                 # TE → NL

te = tg.compress("…", level="L3")
nl = tg.expand(te)
ratio = tg.ratio(original, te)
for line in tg.compress_stream(long_text):  # streaming TE atomic lines
    print(line)
```

`model` and `(model_in, model_out)` are mutually exclusive. When both `model_in` and `model_out` resolve to the same identifier, weights load once. HF Hub paths are stubs until fine-tuning is finalized.

### Module surface

| Module | Purpose | Phase |
|---|---|---|
| `telegrapher.core` | compress / expand / backends / cache | **v0.1** |
| `telegrapher.memory` | `ConversationCompactor` + LangChain memory adapter | **v0.1** |
| `telegrapher.eval` | corpus validation + benchmark reports | **v0.1** |
| `telegrapher.cli` | `tg compress / expand / eval / download-model` (v0.1); `tg ingest` (v0.2); `tg serve` (v0.3) | **v0.1+** |
| `telegrapher.chunk` | TE-aware chunking + semantic chunking | v0.2 |
| `telegrapher.embed` | compress-then-embed adapters | v0.2 |
| `telegrapher.store` | Pinecone first; Qdrant / Weaviate / Chroma / pgvector follow | v0.2 |
| `telegrapher.retrieve` | hybrid BM25 + dense over TE | v0.2 |
| `telegrapher.rag` | turnkey `RAGPipeline` | v0.2 |
| `telegrapher.preprocess` | `preprocess()` + `with_te()` middleware | v0.3 |
| `telegrapher.integrations` | LangChain (v0.1 memory) / LlamaIndex / Haystack / LiteLLM | v0.1+ |
| `telegrapher.server` | FastAPI for polyglot clients | v0.3 |

### Backend abstraction

```
telegrapher.core.backends
├── Backend (ABC)            # methods: compress(), expand(), stream_compress()
├── LocalBackend (default)   # holds compressor + expander handles (may be the same model)
│   ├── VLLMRunner     (CUDA)
│   └── LlamaCppRunner (CPU/Metal)
└── OpenAIBackend (opt-in)
```

All higher-level modules depend on `Backend`. Quantization, batching, KV-cache reuse live in `LocalBackend`.

**Direction handling**: `LocalBackend` carries two handles — `_compressor` and `_expander` — that may point to the same loaded model (if `model=` was used) or two different models (if `model_in=` / `model_out=` were used). `compress()` always uses `_compressor`; `expand()` always uses `_expander`. This lets us migrate from one architecture to the other (or back) without touching any caller code, and without paying double the memory when one model handles both directions.

---

## What migrates from the research repo `telegrapher_ai\code\telegrapher\`

| Origin (research repo) | New status (this repo) |
|---|---|
| `compression/sync.py` | Refactor into `src/telegrapher/core/backends/openai.py` (opt-in extra) |
| `compression/batch.py` | Stays alongside; expose as `OpenAIBackend.batch_compress()` |
| `chunking.py` | Promote to `src/telegrapher/chunk/__init__.py`; add `chunk_te` and `semantic_chunk` (v0.2) |
| `tokens.py` | Promote to `src/telegrapher/core/metrics.py` |
| `clients.py` | Replaced by `src/telegrapher/core/backends/__init__.py` factory |
| `benchmark/` | Promote to `src/telegrapher/eval/` |
| `data/longbench.py` | Inside `eval` (validator-only) |
| `cli/` | Rename to `tg`; new subcommands (Typer) at `src/telegrapher/cli/` |
| `prompts/compression_v5.txt` | Bundled package data via `importlib.resources`; only `OpenAIBackend` uses it |
| `config.py` | Split: package config (env / cache) vs. runtime config (per-call args) |

---

## Critical files to create / modify (this repo)

- `pyproject.toml` *(new)* — declare extras matrix
- `src/telegrapher/__init__.py` *(new)* — export `Telegrapher`, `compress`, `expand`
- `src/telegrapher/core/config.py` *(new)* — holds `DEFAULT_MODEL` stub HF path; updated when fine-tuning lands
- `src/telegrapher/core/{backends,local,cache,metrics}.py` *(new)*
- `src/telegrapher/memory/compactor.py` *(new)*
- `src/telegrapher/eval/__init__.py` *(new)* — wraps migrated `benchmark/qa_bench.py`
- `src/telegrapher/cli/__init__.py` *(new)* — Typer CLI (`tg`)
- `src/telegrapher/integrations/langchain.py` *(new)* — `TelegrapherSummaryMemory`
- `src/telegrapher/chunk/__init__.py` *(v0.2)*
- `src/telegrapher/embed/__init__.py` *(v0.2)*
- `src/telegrapher/store/{pinecone,qdrant,weaviate,chroma,pgvector}.py` *(v0.2)*
- `src/telegrapher/retrieve/__init__.py` *(v0.2)*
- `src/telegrapher/rag/__init__.py` *(v0.2)*
- `src/telegrapher/preprocess.py` *(v0.3)*
- `src/telegrapher/server/app.py` *(v0.3, extras=server)*

---

## Sequencing

### v0.1 (the launch — narrow on purpose)

1. **Backend abstraction + LocalBackend** — biggest unknown (model loading, quantization, streaming). Everything depends on it.
2. **Core API + caching** — `compress`, `expand`, `ratio`, content-hash disk cache.
3. **CLI subset** — `tg compress`, `tg expand`, `tg download-model`. (`tg eval` waits for step 5.)
4. **`memory.ConversationCompactor`** + `telegrapher.integrations.langchain.TelegrapherSummaryMemory` — the wedge.
5. **`eval` module** + `tg eval` — promote existing benchmark code; this is the trust artifact.

That's it for v0.1. No `chunk`, no `embed`, no `store`, no `preprocess`, no `serve`.

### v0.2 (after v0.1 has signal)

6. `chunk.semantic_chunk` (TE-aware chunker).
7. `embed` adapters (OpenAI, sentence-transformers).
8. `store.PineconeStore` (one store, not five).
9. `retrieve` (hybrid BM25 + dense over TE).
10. `rag.RAGPipeline` (turnkey).
11. CLI: `tg ingest`.

### v0.3

12. `preprocess.preprocess` + `with_te(client)` middleware.
13. Other vector stores (Qdrant, Weaviate, Chroma, pgvector) — one per follow-up release.
14. LiteLLM / LlamaIndex / Haystack integrations.
15. CLI: `tg serve` (FastAPI server, extras=server).

---

## Things worth exploring later (not v0.1)

- **TE-aware fine-tunes**: a small TE-native LLM that consumes TE directly without expansion (compounds savings)
- **Diff-aware recompression**: only recompress affected atomic lines on doc change
- **TE-native search index**: skip embeddings entirely for some workloads
- **Confidence-driven retrieval**: use `CONF=` tags to weight retrieval scoring
- **Encrypted memory**: TE is naturally less re-identifiable than NL — formalize for healthcare/legal

---

## Verification

Each v0.1 module ships with:
- Unit tests for round-trip fidelity (`expand(compress(x))` semantically ≈ `x`, measured by QA accuracy on a held-out set — *not* string equality)
- Integration tests against a fixture corpus (subset of LongBench)
- `tg eval` available for users to run on their own data

End-to-end smoke test for v0.1:

```bash
pip install -e .[langchain]
tg download-model
tg compress README.md --level L3 -o readme.te
tg expand readme.te -o readme.back.txt
# Don't expect byte-identical — expect QA fidelity on key facts:
tg eval ./texts/ --report smoke.md

python -c "
from telegrapher.memory import ConversationCompactor
m = ConversationCompactor(level='L3', max_tokens=2000)
for _ in range(20): m.add_user_message('long turn …')
print(m.token_count(), m.compression_ratio())
"
```

**Ship criteria**: round-trip fidelity ≥ 95% on key facts and compression ratio ≥ 2× at L3 across the smoke corpus.

---

## Cascade — downstream docs to keep in sync

Per the convention in [`docs/plans/README.md`](../plans/README.md), this plan is the *raw decision trace*. The formal artifacts that should be derived from it:

- `docs/product-specs/ps-001-memory-wedge.md` — v0.1 product requirements + acceptance criteria
- `docs/design-docs/dd-001-backend-abstraction.md` — Backend ABC + LocalBackend rationale (vLLM vs llama.cpp choice)
- `docs/design-docs/dd-002-conversation-compactor.md` — eviction strategy, `expand_on_load`, confidence-driven retention
- `docs/exec-plans/active/v0.1-memory-wedge.md` — phase-by-phase implementation checklist (sequencing steps 1–5)

Add "See also" lines pointing back to this plan from each derived doc.
