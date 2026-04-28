# Plans

> Design workbooks from plan-mode sessions. Preserved as reference artifacts.

**When to update this file:** After establishing or refining the convention.

---

## What belongs here

A **plan** is a design workbook captured during a plan-mode session. It's not a progress tracker — it's the *decision trace* that produced the implementation. Content typically includes:

- Context and desired outcome (the why)
- Exploration summaries / ground-truth findings
- Options considered + chosen approach with rationale
- Decision records (keyed user choices)
- Post-launch fix-pack plans with explicit debugging-protocol traces (Phase 1 Observe → Phase 5 Implement)
- Cascade notes — what downstream docs need to be kept in sync

Plans are written incrementally during plan mode. Each revision is saved in-place; the final artifact represents the session's full thought process.

## What does NOT belong here

| Artifact | Where it goes |
|---|---|
| Forward-looking phase-by-phase implementation checklist | `docs/exec-plans/active/` → `completed/` |
| Product requirements and acceptance criteria | `docs/product-specs/ps-NNN-*.md` |
| Architectural decisions and rationale | `docs/design-docs/dd-NNN-*.md` |
| Severe mistakes to never repeat | `ERRATA.md` |
| Engineering values / judgment heuristics | `docs/core-beliefs.md` |

A plan often produces a PS, a DD, and an exec plan — those are the *formal* outputs. The plan itself is the raw session record.

## Distinction from exec-plans

| | `docs/exec-plans/` | `docs/plans/` |
|---|---|---|
| **Purpose** | Track implementation progress | Preserve design reasoning |
| **Format** | Phase table with checkboxes, progress column | Narrative with decision traces, exploration notes |
| **Lifecycle** | active/ → completed/ | Immutable once session ends |
| **Updated** | Each phase shipped | Only during the original plan-mode session |
| **Linked from** | CLAUDE.md, debugging.md, PS/DD | Usually referenced by the exec plan's "See also" |

If you only have 30 seconds and want to know *what's being built*: read the exec plan. If you want to know *why this shape was chosen and what alternatives were rejected*: read the plan.

## Naming

Files are named after the user-facing feature and, when relevant, the session date:

- `telegrapher-package-launch.md` — v0.1 design plan (memory wedge)
- `inherited-docs-cleanup.md` — one-time hygiene pass on neighbor-project docs
- Future: `feature-name-<YYYY-MM-DD>.md` when sessions branch or a feature is revisited

## Cross-reference conventions

When writing the formal PS/DD/exec-plan for a feature, add a "See also" line referencing the plan under this folder. Plans are not load-bearing for session continuity (that's the exec plan's job), but they're invaluable when someone asks "why did we choose Option B over Option A?" a month later.
