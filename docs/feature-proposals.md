# Feature Proposals

> Tracking features we might want to build. Not committed — candidates for evaluation and prioritization.

**When to update this file:** When a new feature idea is proposed, when a proposal status changes (PROPOSED / EVALUATING / APPROVED / DEFERRED / REJECTED), or after a proposal is implemented and moves to `functionality-audit.md`.

**Update rules:** See [workflows.md](./workflows.md) → "Feature Proposals Doc" for lifecycle and numbering rules.

---

## Context

`telegrapher` is a Python package wrapping bidirectional Natural Language ↔ Telegraph English compression. v0.1 leads with the local memory-compression wedge ([`plans/telegrapher-package-launch.md`](plans/telegrapher-package-launch.md)). Proposals here either extend that wedge or open new wedges.

**Strategic principle:** add features that compound the value of the core compress/expand primitive. Don't chase generic "LLM utility belt" features that aren't differentiated by Telegraph English's properties (bidirectionality, ratio control, symbolic structure, locality).

---

## How This Document Works

- **functionality-audit.md** tracks what IS built, what's broken (gaps), and small tactical suggestions (S-numbered).
- **This document** tracks larger feature ideas we MIGHT build. Research-stage proposals, not commitments.
- Proposals stay here until a decision is made. When approved → create a phase entry, track implementation in `functionality-audit.md`.
- Proposals can be rejected → add a one-line rationale in the Decision Log and leave the row (audit trail).

### Proposal Lifecycle

```
PROPOSED  →  EVALUATING  →  APPROVED (moves to phase plan)
                          →  DEFERRED (keep, revisit later)
                          →  REJECTED (keep with rationale)
```

### Numbering

Proposals are numbered `P1, P2, ...` — sequential, never reused, never renumbered.

### Priority Tiers

- **Critical** — Competitive table stakes. The package is incomplete without this.
- **High** — Strong adoption driver. Needed within first 6 months post-launch.
- **Medium** — Meaningful improvement. Plan for when resources allow.
- **Low** — Nice-to-have or speculative. Build only if effort is trivial.

---

## Competitive Context

To be filled in as competitors emerge. Closest reference points today:

- **JuliusBrussee/caveman** — LLM-backed prompt simplifier ("caveman speak"). One-way, API-bound.
- **LLMLingua / LLMLingua2 (Microsoft)** — Token-deletion classifier. Fixed-ratio, input-only.
- **Generic prompt compression tooling** — various.

Telegrapher's distinctive ground: **owned local model**, **bidirectional**, **adjustable ratio**, **symbolic/parseable output**, **memory + storage role** (not just preprocessing).

---

## Proposals

| # | Proposal | Priority | Status | Rationale | Effort | Notes |
|---|----------|----------|--------|-----------|--------|-------|
| — | (No proposals yet — add as the design surface evolves.) | — | — | — | — | — |

---

## Cross-Reference to functionality-audit.md

Some proposals overlap with existing gaps or suggestions in `functionality-audit.md`. When a proposal is approved, consolidate.

| Proposal | Overlaps With | Action on Approval |
|----------|--------------|-------------------|
| — | — | — |

---

## Decision Log

Record decisions here as proposals are evaluated. One line per decision.

| Date | Proposal | Decision | Rationale |
|------|----------|----------|-----------|
| — | — | — | — |
