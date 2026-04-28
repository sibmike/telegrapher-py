# Product Specs Index

> Catalog of product requirements and feature specifications.
> Each spec defines what a feature does from the user's perspective, what's implemented, and what gaps remain.

**When to update this file:** After adding a new product spec, completing implementation, or changing a spec's status.

---

## Catalog

### v0.1 — Memory Wedge (planned)

| ID | Feature | Status | Phase | Spec File |
|----|---------|--------|-------|-----------|
| — | Core compress / expand primitive | Planned | v0.1 | (PS-001 — to be written) |
| — | LocalBackend (vLLM + llama.cpp) | Planned | v0.1 | (PS-002 — to be written) |
| — | ConversationCompactor + LangChain memory adapter | Planned | v0.1 | (PS-003 — to be written) |
| — | `tg eval` + eval module | Planned | v0.1 | (PS-004 — to be written) |
| — | `tg compress / expand / download-model` CLI | Planned | v0.1 | (PS-005 — to be written) |

### v0.2 — RAG Wedge (deferred)

| ID | Feature | Status | Phase | Spec File |
|----|---------|--------|-------|-----------|
| — | TE-aware semantic chunker | Deferred | v0.2 | — |
| — | compress-then-embed adapters | Deferred | v0.2 | — |
| — | PineconeStore | Deferred | v0.2 | — |
| — | Hybrid retriever (BM25 + dense over TE) | Deferred | v0.2 | — |
| — | RAGPipeline turnkey API | Deferred | v0.2 | — |

### v0.3 — Middleware Wedge (deferred)

| ID | Feature | Status | Phase | Spec File |
|----|---------|--------|-------|-----------|
| — | preprocess() + with_te(client) middleware | Deferred | v0.3 | — |
| — | tg serve (FastAPI) | Deferred | v0.3 | — |
| — | Additional vector stores (Qdrant, Weaviate, Chroma, pgvector) | Deferred | v0.3 | — |
| — | LiteLLM / LlamaIndex / Haystack integrations | Deferred | v0.3 | — |

---

## Cross-References

- **Functionality audit:** [docs/functionality-audit.md](../functionality-audit.md) — detailed implementation status, gaps, suggestions
- **Feature proposals:** [docs/feature-proposals.md](../feature-proposals.md) — larger feature ideas under evaluation
- **Tech debt:** [docs/exec-plans/tech-debt-tracker.md](../exec-plans/tech-debt-tracker.md) — known technical debt items
- **Design docs:** [docs/design-docs/index.md](../design-docs/index.md) — architectural decisions
- **Launch plan:** [docs/plans/telegrapher-package-launch.md](../plans/telegrapher-package-launch.md) — design source-of-truth for v0.1+

---

## Phases Overview

| Phase | Scope | Status |
|-------|-------|--------|
| **Phase 0** | Inherited docs cleanup (this hygiene pass) | **In Progress** |
| **v0.1** | Memory wedge: core compress/expand, ConversationCompactor, eval | **Planned** |
| **v0.2** | RAG wedge: chunk, embed, store, retrieve, RAGPipeline | **Deferred** |
| **v0.3** | Middleware wedge: preprocess, with_te, server, more stores | **Deferred** |

---

*PS files are written before implementation begins, per the major change process in [`harness-guidelines.md`](../harness-guidelines.md) Section 3.*
