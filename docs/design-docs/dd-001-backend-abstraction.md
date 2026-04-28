# DD-001: Backend Abstraction

**Status:** Accepted
**Date:** 2026-04-27
**Author:** Telegrapher AI

## Context

The v0.1 launch requires `compress()` and `expand()` to run locally against a 9B SLM whose final architecture is still being decided during fine-tuning:

- The model may be **one bidirectional** SLM that produces TE from NL and NL from TE.
- Or it may be **two unidirectional** SLMs — one compressor (NL → TE), one expander (TE → NL).

The decision will not be locked before v0.1 ships, so the package must accept either configuration without breaking callers when the choice flips. The user-facing API is already defined in [`plans/telegrapher-package-launch.md`](../plans/telegrapher-package-launch.md):

```python
Telegrapher()                                    # default
Telegrapher(model="org/te-bidi")                 # one bidi model
Telegrapher(model_in="org/te-c", model_out="org/te-e")  # two unidirectional models
```

Beyond model topology, two execution targets matter for v0.1:

- **GPU hosts** (developers, RAG startups, research) — `vllm` is the fastest, most capable runner. Linux + CUDA.
- **CPU / Mac hosts** (laptops, air-gapped servers, Windows dev boxes) — `llama-cpp-python` (GGUF) handles these. No CUDA dependency.

The architecture must let us pick the runner at construction time, share weights across `compress` and `expand` calls when only one model is loaded, and stay testable without downloading multi-gigabyte weights.

## Options Considered

### Option A: `Backend` ABC + concrete `LocalBackend` that owns one or two `Runner`s

Two layers: `Backend` defines the public verb-level interface (`compress`, `expand`, `stream_compress`); `LocalBackend` is a concrete `Backend` that holds two `Runner` handles (`_compressor`, `_expander`) which may point to the same physical model. `Runner` is a thin protocol (`generate(prompt) -> str`, `stream(prompt) -> Iterator[str]`) with `VLLMRunner` and `LlamaCppRunner` implementations.

- **Pros:**
  - Matches the user-facing API exactly: `Backend` cares about *direction*, `Runner` cares about *execution*.
  - Sharing one model across both directions is a one-liner: `_compressor is _expander`.
  - Tests can substitute a `MockRunner` that returns canned strings — no weights needed.
  - Easy to add `OpenAIBackend` (no runner) later without touching `LocalBackend`.
- **Cons:**
  - Two layers when one might do. Mild ceremony.

### Option B: `Backend` ABC with one concrete subclass per execution target

`VLLMBackend`, `LlamaCppBackend`, etc. — each implements `compress`/`expand` end-to-end.

- **Pros:**
  - Flat, easy to understand.
- **Cons:**
  - Direction handling (one model vs two) duplicates across every backend.
  - The model-sharing logic — "if `model_in == model_out`, load once" — has to be re-implemented in every subclass. High odds of bugs.
  - Adding a third runner means re-implementing direction handling a third time.

### Option C: Single `LocalBackend` class that handles vLLM and llama.cpp internally via if/else

One class, no subclassing, branches on `which_runner` flags.

- **Pros:**
  - Smallest surface.
- **Cons:**
  - All runner concerns leak into one class. Adding a runner is invasive.
  - Mocking for tests requires monkey-patching internals.

## Decision

**Option A.** Two layers — `Backend` ABC for direction, `Runner` protocol for execution.

```
src/telegrapher/core/backends/
├── __init__.py        # public factory: get_backend(model, model_in, model_out, ...) -> Backend
├── base.py            # Backend ABC + Runner protocol
├── local.py           # LocalBackend — uses one or two Runner instances
├── runners/
│   ├── __init__.py
│   ├── vllm.py        # VLLMRunner   (extras = [gpu])
│   ├── llama_cpp.py   # LlamaCppRunner (extras = [cpu])
│   └── mock.py        # MockRunner — testing only, no extras dependency
└── openai.py          # (future, v0.3 extras=[openai]) — no Runner; calls API
```

### Backend ABC

```python
class Backend(ABC):
    @abstractmethod
    def compress(self, text: str, *, level: str) -> str: ...

    @abstractmethod
    def expand(self, te: str) -> str: ...

    @abstractmethod
    def stream_compress(self, text: str, *, level: str) -> Iterator[str]: ...
```

### Runner protocol

```python
class Runner(Protocol):
    def generate(self, prompt: str, *, max_tokens: int) -> str: ...
    def stream(self, prompt: str, *, max_tokens: int) -> Iterator[str]: ...
    def close(self) -> None: ...
```

### LocalBackend semantics

`LocalBackend.__init__` resolves the model arguments into two `Runner` handles:

| Constructor arguments | `_compressor` | `_expander` |
|---|---|---|
| `model="org/X"` | `Runner(load("org/X"))` | same instance as `_compressor` |
| `model_in="org/A", model_out="org/B"` (different) | `Runner(load("org/A"))` | `Runner(load("org/B"))` |
| `model_in="org/A", model_out="org/A"` (same string) | `Runner(load("org/A"))` | same instance as `_compressor` |
| (none) | `Runner(load(DEFAULT_MODEL))` | same instance |

Method routing:
- `compress()` always calls `self._compressor.generate(...)`
- `expand()` always calls `self._expander.generate(...)`

If `_compressor is _expander`, callers don't pay double memory and don't load the model twice.

### Runner selection

`get_backend()` picks the runner based on (a) installed extras, (b) the host environment:

```
if torch.cuda.is_available() and vllm is importable:  use VLLMRunner
elif llama_cpp is importable:                         use LlamaCppRunner
else:                                                 raise InstallError(...)
```

Users can override with `Telegrapher(runner="vllm" | "llama-cpp" | "mock")`.

### Default model

`telegrapher.core.config.DEFAULT_MODEL = "telegrapher-ai/te-bidi-9b"` — a stub HF Hub identifier. It is replaced before the first PyPI release with the real fine-tuned model name. Tests must never depend on this string resolving to real weights — they use `MockRunner`.

## Consequences

**Positive:**

- The two-vs-one-model decision can flip mid-fine-tuning without API changes. Switching `Telegrapher(model=...)` ↔ `Telegrapher(model_in=..., model_out=...)` is a config change at the call site, no library refactor.
- New runners (e.g., a future `OllamaRunner`) plug in by writing one file under `runners/`.
- Tests are fast and weight-free: `MockRunner` is a regular Python class with no dependencies.
- `OpenAIBackend` lives alongside `LocalBackend` without inheriting any of its model-loading machinery — it's just a different `Backend` implementation.

**Trade-offs:**

- Two abstraction layers instead of one. Worth it because the model-direction logic and the runner-execution logic genuinely change for different reasons.
- The `Runner` protocol is intentionally minimal (`generate`, `stream`, `close`). If we later need batching, it gets added there — but only if a real use case demands it. No speculative method additions.

**Boundaries enforced:**

- `Backend` never knows what runner it has — only that it can call `generate(...)`.
- `Runner` never knows about TE levels or directions — only prompt-in, text-out.
- The TE-level → prompt-template translation lives in `LocalBackend.compress()` / `expand()`, not inside the runners.

## Validation

- Unit tests use `MockRunner` to verify direction routing (compress always hits `_compressor`, expand always hits `_expander`).
- A test confirms the same-string optimization: `Telegrapher(model_in="X", model_out="X")` loads exactly once.
- Integration tests (gated `-m integration`) load a small open model via `LlamaCppRunner` and round-trip a fixture. These do not run in CI by default.

## See also

- [`plans/telegrapher-package-launch.md`](../plans/telegrapher-package-launch.md) — design source of truth
- [PS-001 Memory wedge](../product-specs/ps-001-memory-wedge.md) — depends on this DD
