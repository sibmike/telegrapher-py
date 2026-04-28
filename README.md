# telegrapher

> *Caveman makes agents speak less. Telegrapher makes knowledge weigh less.*

**Compress your LLM memory locally. Keep twice as much conversation context without losing facts.**

`telegrapher` is a Python package for **bidirectional compression** between Natural Language and Telegraph English (TE). It runs locally — no per-token API fee — using a 9B small language model trained for fact-preserving reversible compression.

> **Status:** v0.1 in development. Public API not yet stable. Model weights are stubs until fine-tuning is finalized.

---

## Quick start

```bash
pip install telegrapher
```

```python
from telegrapher import Telegrapher

tg = Telegrapher()                              # default model from HF Hub
te = tg.compress("Some long passage…", level="L3")
nl = tg.expand(te)
```

Drop-in memory compactor for LangChain:

```python
from telegrapher.memory import ConversationCompactor

memory = ConversationCompactor(level="L3", max_tokens=4000)
```

Validate fidelity on your own corpus:

```bash
tg eval ./my_docs --report report.md
```

---

## What is Telegraph English?

Telegraph English (TE) is a structured, symbol-rich, atomic-line dialect of English designed for fact-preserving compression. It compresses ~50% of tokens at the L3 level while preserving ≥95% of key facts measurable by QA accuracy. Compression is **bidirectional** — every TE line expands back to one unambiguous natural-language sentence.

See the [paper draft](https://telegrapher.ai/paper) for the full grammar and benchmark results.

---

## Phases

| Phase | Scope | Status |
|-------|-------|--------|
| **v0.1** | Memory wedge: core `compress`/`expand`, `ConversationCompactor`, `tg eval` | In development |
| **v0.2** | RAG wedge: chunking, embeddings, vector stores, hybrid retrieval | Deferred |
| **v0.3** | Middleware wedge: `with_te(client)`, `tg serve`, more integrations | Deferred |

---

## Documentation

- [Design plan](docs/plans/telegrapher-package-launch.md) — full design + adoption brainstorm
- [Agent behavior](docs/agent-behavior.md) — working rules for AI contributors
- [Debugging](docs/debugging.md) — 5-phase debugging protocol
- [Testing](docs/testing.md) — test strategy and patterns

---

## License

MIT — see [LICENSE](LICENSE).
