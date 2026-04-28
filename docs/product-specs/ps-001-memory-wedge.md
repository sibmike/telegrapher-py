# PS-001: v0.1 Memory Wedge

**Status:** Approved
**Date:** 2026-04-27
**Phase:** v0.1
**Author:** Telegrapher AI

## Context

The v0.1 release is the first public PyPI cut of `telegrapher`. It leads with a single dominant wedge — *local memory compression for chatbots and agents* — to keep the launch story sharp. RAG and middleware wedges ship later (v0.2 and v0.3 respectively). See [`plans/telegrapher-package-launch.md`](../plans/telegrapher-package-launch.md) for the full positioning.

**Headline:** *Compress your LLM memory locally. Keep twice as much conversation context without losing facts.*

## User stories

### US-1 — Indie dev wires up persistent memory in a chatbot

> *As a Python developer building a customer support chatbot, I want a memory store that doesn't garble phone numbers and order IDs across long sessions, without forcing me to summarise turns away.*

```python
from telegrapher.memory import ConversationCompactor
memory = ConversationCompactor(level="L3", max_tokens=4000)
```

The dev should not need to think about model loading, weight downloads, GPU vs CPU, cache directories, or TE grammar. `ConversationCompactor` exposes the standard memory verbs (`add_user_message`, `add_ai_message`, `messages`, `clear`); wrapping it in a framework-specific protocol (LangChain `BaseMemory`, LangGraph checkpointer, etc.) is one short adapter the user owns or pulls from a future v0.2 extras package.

### US-2 — ML engineer compresses raw text from the CLI

> *As an ML engineer evaluating compression methods, I want to compress a file from the command line without writing Python.*

```bash
tg compress passage.txt --level L3 -o passage.te
tg expand passage.te -o passage.back.txt
```

Round-trip output must be coherent natural language; key facts must be preserved.

### US-3 — Skeptical adopter validates fidelity on their corpus

> *As a senior engineer evaluating telegrapher for production use, I want to point a CLI command at my corpus and get a fidelity report I can share internally.*

```bash
tg eval ./our-internal-docs --report report.md
```

Output: per-document compression ratio, QA fidelity (auto-generated QA pairs), aggregate summary.

### US-4 — Power user wants the Python primitive

> *As a developer building something custom, I want the lowest-level `compress`/`expand` calls without LangChain or CLI overhead.*

```python
from telegrapher import Telegrapher
tg = Telegrapher()
te = tg.compress(text, level="L3")
nl = tg.expand(te)
```

## Public API surface

### `telegrapher` (top-level)

```python
class Telegrapher:
    def __init__(
        self,
        *,
        model: str | None = None,
        model_in: str | None = None,
        model_out: str | None = None,
        runner: str | None = None,         # "vllm" | "llama-cpp" | "mock" — auto if None
        cache_dir: str | None = None,      # default: ~/.cache/telegrapher
    ): ...

    def compress(self, text: str, *, level: str = "L3") -> str: ...
    def expand(self, te: str) -> str: ...
    def ratio(self, original: str, te: str) -> float: ...
    def compress_stream(self, text: str, *, level: str = "L3") -> Iterator[str]: ...
```

`level` accepts `"L1" | "L3" | "L5"`. Invalid levels raise `ValueError`.

### `telegrapher.memory`

```python
class ConversationCompactor:
    def __init__(
        self,
        *,
        level: str = "L3",
        max_tokens: int = 4000,
        expand_on_load: bool = False,
        telegrapher: Telegrapher | None = None,    # default: shared singleton
    ): ...

    def add_user_message(self, content: str) -> None: ...
    def add_ai_message(self, content: str) -> None: ...
    def messages(self) -> list[Message]: ...        # returns NL or TE based on expand_on_load
    def token_count(self) -> int: ...
    def compression_ratio(self) -> float: ...
    def clear(self) -> None: ...
```

### Framework integrations

**Not in v0.1.** Originally PS-001 included a `TelegrapherSummaryMemory(BaseMemory)` LangChain adapter, but `langchain_core 1.x` removed `BaseMemory` and migrated to LangGraph's checkpointer pattern. Shipping a v0.1 adapter against the deprecated 0.x API would be dead-on-arrival.

The decision (2026-04-27) is to ship **`ConversationCompactor` as a generic primitive** and let users wrap it in their framework's memory protocol. Two extra lines of glue at the call site replace the framework lock-in. Framework adapters (LangChain checkpointer, LlamaIndex, Haystack) become opt-in v0.2 integrations once we have signal on which one matters most.

### `telegrapher.eval`

```python
def validate(
    documents: Iterable[str | Path],
    *,
    qa_pairs: list[tuple[str, str]] | None = None,
    level: str = "L3",
    report: Path | None = None,
) -> EvalReport: ...
```

`EvalReport` carries: aggregate compression ratio, per-document ratio, QA fidelity %, per-domain breakdown if categorical metadata is present. When `report` is provided, the report is also written as Markdown.

### `tg` CLI (Typer-based)

| Command | Purpose |
|---------|---------|
| `tg compress <path> [--level L3] [-o out]` | Compress a text file |
| `tg expand <path> [-o out]` | Expand a TE file back to NL |
| `tg eval <corpus> [--report report.md] [--level L3]` | Validate on a corpus |
| `tg download-model [--to dir]` | Pre-download default weights |
| `tg --version` | Print version |

Exit codes: 0 = success, 1 = user error (missing file, invalid level), 2 = unexpected error.

## Behavior contracts

### Round-trip fidelity

- `expand(compress(x))` is **not** byte-identical to `x` and the package never claims it is.
- It **is** semantically equivalent on key facts, measured by QA accuracy on a held-out fixture set: ≥ 95% on key facts at L3 across the v0.1 fixture corpus.
- Dates, numbers, currencies, named entities, and percentages are preserved verbatim. Stylistic phrasing is not preserved.

### Compression ratio

- L1: ~2× reduction
- L3: ~5× reduction (default)
- L5: ≥ 10× reduction
- Actual ratios are document-adaptive; values above are typical, not guaranteed.

### Caching

- Both `compress` and `expand` results are content-addressed-cached on disk in `~/.cache/telegrapher/` (overridable).
- Cache key: `(input_text_sha256, level, model_revision)`. Model upgrades never serve stale entries.
- The cache is always-on. There is no `disable_cache` flag in v0.1 (KISS — add only if asked).

### Streaming

- `compress_stream(...)` yields TE atomic lines as the model emits them.
- Lines are guaranteed to be complete (the iterator does not yield half-lines).

### Memory eviction

- New turns added to `ConversationCompactor` stay as NL while the buffer is under `max_tokens`.
- On overflow: oldest turns compress to TE at the configured level. If the buffer is still over, older compressed turns get re-compressed at the next-higher level (L1 → L3 → L5).
- `messages()` returns the merged buffer — TE entries are expanded back to NL on the way out if `expand_on_load=True` (default `False`).

## Acceptance criteria

For v0.1 to ship:

1. ✅ Package installs cleanly via `pip install telegrapher` in a fresh venv on Python 3.10, 3.11, 3.12.
2. ✅ All public API methods listed above exist with the documented signatures.
3. ✅ `tg --help` lists `compress`, `expand`, `download-model`, `eval` with one-line descriptions.
4. ✅ Smoke test: `Telegrapher().compress(s).expand(...)` round-trip on a fixture corpus achieves ≥ 95% QA fidelity on key facts at L3.
5. ✅ Smoke test: `ConversationCompactor` with a 2k token budget compresses ≥ 2× when buffer overflows.
6. ✅ Smoke test: `tg eval` on a 5-document fixture corpus runs to completion and writes a non-empty report.
7. ✅ Test suite: ≥ 80% line coverage across `core`, `memory`, `eval`. 100% on direction-routing logic in `LocalBackend`.
8. ✅ `ruff check` and `mypy --strict` both clean.
9. ✅ Round-trip fidelity tests use `MockRunner` with hand-curated NL ↔ TE pairs — no real model downloads in CI.
10. ✅ Integration tests (`-m integration`) load real weights and round-trip; gated, not run in CI.
11. ✅ No framework integrations (LangChain, LlamaIndex, etc.) ship in v0.1 — `ConversationCompactor` is the generic primitive.

## Out of scope for v0.1

- RAG: chunking, embedding, vector stores, retrieval — all v0.2.
- Middleware: `with_te(client)` / `tg serve` — v0.3.
- Multiple vector store integrations.
- Async I/O on the public API. (Internal async is fine; the public surface is sync in v0.1 to match LangChain memory ergonomics.)
- Quantization toggles exposed to users. The runner picks 4-bit by default; advanced override is a v0.2+ concern.
- Confidence-driven memory eviction (`CONF=` tagging). Possible v0.2 enhancement.

## See also

- [DD-001 Backend Abstraction](../design-docs/dd-001-backend-abstraction.md)
- [`plans/telegrapher-package-launch.md`](../plans/telegrapher-package-launch.md)
- [Exec plan: v0.1 memory wedge](../exec-plans/active/v0.1-memory-wedge.md)
