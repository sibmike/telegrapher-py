# Testing

> Testing strategy, coverage targets, infrastructure, and patterns.

**When to update this file:** After adding/removing test files, changing test counts, modifying test infrastructure, or updating coverage targets.

---

## Current Counts

| Layer | Tests | Coverage | Files |
|-------|-------|----------|-------|
| Unit | TBD | TBD | TBD |
| Integration | TBD | TBD | TBD |
| End-to-end | TBD | TBD | TBD |

(Counts populate as v0.1 ships. Run the actual suite — never guess.)

---

## Coverage Targets

- **80% line coverage minimum** (CI-enforced once CI exists)
- **100% on critical paths:** `compress()` / `expand()` round-trip; cache hit/miss; backend swap; `ConversationCompactor` eviction; CLI exit codes

---

## Stack

- **pytest** — test runner, async support via `pytest-asyncio` if/when async paths are introduced
- **pytest-cov** — coverage reporting
- **HF Hub fixtures or local model stubs** — for tests that touch the model, prefer a small fixture or a fully mocked Backend rather than downloading the full 9B in CI
- **No frontend / no MSW** — this is a pure Python package

---

## Test Layout

```
tests/
├── conftest.py                # Shared fixtures: sample TE strings, mock Backend, temp cache dir
├── fixtures/
│   ├── corpus/                # Small sample documents for smoke + eval tests
│   └── te_samples/            # Hand-curated NL ↔ TE pairs for round-trip assertions
├── test_core_compress.py      # compress() / expand() / ratio() / streaming
├── test_backend_local.py      # LocalBackend: model load, quantization, GPU/CPU pick
├── test_cache.py              # Content-hash cache hit/miss, model-revision keying
├── test_memory.py             # ConversationCompactor eviction, expand_on_load, CONF tagging
├── test_eval.py               # validate(); QA fidelity calculation
├── test_cli.py                # tg compress / expand / eval / download-model exit codes + outputs
└── test_integrations_langchain.py   # TelegrapherSummaryMemory drop-in compatibility
```

This layout is a target — files appear as the corresponding modules ship.

---

## Round-Trip Fidelity Tests (the most important class)

The package's whole value proposition rests on `expand(compress(x)) ≈ x`. Tests must not check string equality — they must check **fact preservation** measured by QA accuracy on a held-out set:

```python
def test_round_trip_key_facts(qa_pairs, tg):
    for nl, qa in qa_pairs:
        te = tg.compress(nl, level="L3")
        nl_back = tg.expand(te)
        for question, expected in qa:
            assert answer_from_text(nl_back, question) == expected
```

The test corpus is bundled as fixtures; large-scale eval lives in `tg eval`, not unit tests.

---

## Testing Principles

- **Test behavior, not implementation.** Assert what callers see, not internal state.
- **One assertion concept per test.** Tests should fail for exactly one reason.
- **Tests are documentation.** Test names describe the behavior being verified.
- **Test at the right level.** Unit for logic, integration for backends, end-to-end for CLI + memory wedge.
- **Every new feature ships with tests.** No exceptions.
- **Mock model calls in unit tests.** Real model loads belong in a small set of integration tests (gated, slow).
