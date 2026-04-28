# Functionality Audit

> Living audit of what's implemented, what's planned, what's broken (gaps), and small tactical suggestions. Updated after every commit that changes functionality.

**When to update this file:** See [workflows.md](./workflows.md) → "Functionality Doc Maintenance" for triggers, rules, and what NOT to do.

---

## Section 1 — Implemented

| Feature | Module | Tests |
|---------|--------|-------|
| (Nothing implemented yet — v0.1 in progress.) | — | — |

---

## Section 2 — Planned (current phase)

Planned items in scope for the active release phase. See [`plans/telegrapher-package-launch.md`](plans/telegrapher-package-launch.md) for the current phase plan.

| Feature | Phase | Spec | Notes |
|---------|-------|------|-------|
| Core compress / expand primitive | v0.1 | TBD (PS-001) | `Telegrapher().compress() / .expand()` |
| LocalBackend (vLLM + llama.cpp) | v0.1 | TBD (DD-001) | Loads model from HF Hub stub path |
| ConversationCompactor | v0.1 | TBD | Drop-in for LangChain memory |
| LangChain memory adapter | v0.1 | TBD | `TelegrapherSummaryMemory` |
| `tg eval` CLI + eval module | v0.1 | TBD | Trust artifact for prospects |
| `tg compress / expand / download-model` CLI | v0.1 | TBD | Typer entry points |

---

## Section 3 — Gaps

Sequential numbering `#1, #2, ...` — never reuse deleted numbers. Each gap has a description, spec reference, impact, and severity (High/Medium/Low).

| # | Gap | Spec Ref | Impact | Severity |
|---|-----|----------|--------|----------|
| — | (No gaps tracked yet.) | — | — | — |

---

## Section 4 — Suggested

Small tactical suggestions prefixed `S1, S2, ...` — never reused. Larger feature ideas go in [`feature-proposals.md`](feature-proposals.md) instead.

| # | Suggestion | Notes |
|---|------------|-------|
| — | (No suggestions yet.) | — |

---

## Section 5 — Summary

### By Severity

| Severity | Count |
|----------|-------|
| High | 0 |
| Medium | 0 |
| Low | 0 |
| **Total Gaps** | **0** |

### Release Blockers

High-severity items that must be resolved before the next release. Re-evaluate on every update.

| # | Gap | Severity | Status |
|---|-----|----------|--------|
| — | (No release blockers.) | — | — |

### Counts

| Layer | Count |
|-------|-------|
| Implemented (Section 1) | 0 |
| Planned (Section 2) | 6 |
| Gaps (Section 3) | 0 |
| Suggestions (Section 4) | 0 |
