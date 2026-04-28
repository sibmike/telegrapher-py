# Design Docs Index

> Catalog of architectural decisions and design rationale.
> Each design doc captures the context, options considered, and decision made for a significant architectural choice.

**When to update this file:** After adding a new design doc or changing the verification status of an existing one.

---

## Design Doc Template

When creating a new design doc, use this structure:

```markdown
# DD-{number}: {Title}

**Status:** Draft | Accepted | Superseded
**Date:** YYYY-MM-DD
**Author:** {name}

## Context
What problem are we solving? What constraints exist?

## Options Considered
### Option A: {name}
- Pros: ...
- Cons: ...

### Option B: {name}
- Pros: ...
- Cons: ...

## Decision
Which option was chosen and why.

## Consequences
What changes as a result. What trade-offs are we accepting.
```

---

## Catalog

### Core Library

| ID | Title | File | Status | Date | Summary |
|----|-------|------|--------|------|---------|
| — | (No design docs yet — first DDs land with v0.1.) | — | — | — | — |

### Backend Abstraction

| ID | Title | File | Status | Date | Summary |
|----|-------|------|--------|------|---------|
| — | (Planned: DD-001 Backend ABC + LocalBackend) | — | — | — | — |

### Memory Wedge

| ID | Title | File | Status | Date | Summary |
|----|-------|------|--------|------|---------|
| — | (Planned: DD-002 Conversation Compactor — eviction + expand_on_load) | — | — | — | — |

### Distribution & Packaging

| ID | Title | File | Status | Date | Summary |
|----|-------|------|--------|------|---------|
| — | (Future: extras matrix, HF Hub model distribution, cache layout) | — | — | — | — |

---

*The first DDs will be written before v0.1 implementation begins, per the major change process in [`harness-guidelines.md`](../harness-guidelines.md) Section 3.*
