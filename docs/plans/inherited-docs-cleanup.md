# Inherited Docs Cleanup — Strip Neighbor Project, Preserve Wisdom

## Context

The `docs/` skeleton in this repo was carried over from a neighbor project (a Next.js + FastAPI + AWS Amplify "Dataroomed" app). Most files contain valuable engineering wisdom (debugging protocol, harness theory, core beliefs) mixed with the neighbor project's specific state (test counts, AWS specifics, founder/investor business model, P-numbered feature proposals, DD/PS catalogs). For this `telegrapher_py` package, we want to **keep the wisdom, scrub the project-specific content, and reset stateful catalogs to empty.**

This is a prerequisite to anything we ship in [`telegrapher-package-launch.md`](telegrapher-package-launch.md) — the v0.1 work will reference these docs.

## Goal

After this cleanup, every file in `docs/` should:

1. Be free of references to dataroom, founder, investor, Cognito, Amplify, Bedrock, App Runner, DynamoDB, Aurora, NDA, VC memo, deal pipeline, or other neighbor-project-specific concepts
2. Contain no test counts, infrastructure tables, or stateful catalogs from the prior project
3. Read coherently for *this* package (Python library, local SLM, single-package)
4. Still encode the universal wisdom (debugging discipline, harness model, agent-behavior contract, core beliefs)

## Universal wisdom to preserve (the keep list)

These principles are stack-agnostic and worth keeping verbatim or with light edits:

**Workflow / process**
- 5-phase debugging protocol (Observe → Hypothesize → Verify → Plan → Implement)
- Plan-mode-by-default for non-trivial tasks
- Subagent strategy (offload research; one task per subagent)
- Self-improvement loop (corrections feed back into docs/lints/tests)
- Verification before "done" (run tests, prove the fix)
- "When blocked, stop and re-plan"

**Engineering values (core beliefs)**
- Validate at boundaries, not in the middle
- Prefer shared utilities over hand-rolled helpers (DRY)
- Favor boring technology
- Layered architecture with strict dependency direction
- Explicit over clever (no metaprogramming, no magic)
- Engineered enough — not under, not over
- Tests are documentation; test behavior, not implementation

**Harness theory**
- Three-layer harness: Context / Constraints / Correction
- Repository as system of record
- Map, not manual (progressive disclosure)
- Mechanical enforcement over convention
- Design for agent legibility
- Iterative signal-driven improvement (agent failures = harness bugs)
- Fight entropy actively (stale docs are worse than no docs)
- Plans as first-class artifacts
- Critical files are sacred
- Encode judgment, not just rules

**Debugging anti-patterns (universal cautionary tales)**
- "Shotgun debugging" — making changes without understanding
- "Fix forward" into production
- Conflating multiple problems
- Assuming code is the problem when it's config
- Hiding real errors behind generic messages
- "Local tests prove logic, not infrastructure"
- Trusting a passing test suite as proof of production health

These survive the cleanup. The dataroom-specific *examples* used to teach them get either generalized or replaced with Python-package-relevant ones.

## Per-file decision matrix

| File | Action | Notes |
|---|---|---|
| `agent-behavior.md` | **Edit (light)** | Strip references to AWS, founder/investor, frontend/backend split, specific test counts. Keep all 12 numbered sections. Rewrite §10 "Deployment Planning" to be Python-package generic (PyPI, HF Hub) instead of AWS. Rewrite §12 session-start checklist to drop deployment-specific docs. |
| `core-beliefs.md` | **Edit (light)** | Belief #1 has a dataroom-specific example — replace with Python-package example (e.g., "Compression artifacts are NoSQL-style records; expansion cache is filesystem; backend abstraction is interface-only"). Beliefs 2–16 are generic — keep. |
| `debugging.md` | **Edit (heavy)** | Keep §1 (Core Principle), §2 (5-phase protocol), §4 (Anti-Patterns 4.1–4.7 — they're universal even with AWS examples; the lessons transcend the stack). **Delete** §3 (Deployment Debugging Checklist — entirely AWS Amplify/App Runner), §5 (Environment-Specific Knowledge — entirely Amplify/Cognito), §6 (Decision Record — neighbor project's incident history). Rewrite anti-pattern *examples* to be more abstract or add a Python-package example alongside. |
| `dev-environment.md` | **Reset to template** | 100% neighbor-project-specific (claude_code paths, conda frontend-env, 397 backend tests). Replace with a stub: project root, Python venv path, common commands (pytest, ruff/black, build). Fill in concretely once the venv is created. |
| `feature-proposals.md` | **Reset to template** | All 35 P-numbered proposals are dataroom features. Replace with: framework intro (lifecycle, numbering, priority tiers), empty proposals table, empty decision log. Keep the "competitive context" *structure* but drop the dataroom/Papermark text — fill in when telegrapher has competitors to track. |
| `functionality-audit.md` | **Reset to template** | All sections are dataroom features (28K+ tokens). Replace with: section structure (Implemented / Planned / Gaps / Suggested / Summary) and empty tables. To be filled in as v0.1 ships. |
| `harness-guidelines.md` | **Edit (light–medium)** | §1, §2 (Core Principles), §5 (Constraint Engineering), §6 (Entropy Management), §7 (Feedback Loop), §10 (Sources) are all generic — keep. **Edit** §3 to drop dataroom-specific examples (e.g., "new permissions layer", P-number references). **Strip** §4.1 doc hierarchy of project-specific filenames (architecture.md, data-model.md, deployment.md, security.md, infrastructure.md, quality-score.md, references/, generated/) — replace with telegrapher-relevant doc list. **Delete** §4.2 (Migration Status — neighbor project's history) and §9 (Migration Plan — also history). §8 (Generated Documentation) — generalize the table or delete. |
| `post-deploy-checklist.md` | **Edit (heavy) or reset** | Almost every concrete check is AWS-specific (Amplify, App Runner, DynamoDB, IAM, Cognito, SES, App Runner role, CloudFormation). The *structure* is reusable for a Python package: §1 (Verify infra exists in PyPI/HF after release), §2 (Smoke test the published package), §5 (ERRATA check), §6 (Memory check), §7 (Session reflection) generalize cleanly. Easiest path: **reset to a Python-package version** with the same skeleton: post-release version verification, install-from-PyPI smoke test, doc updates, ERRATA, MEMORY. The Local-Tests-≠-Infrastructure principle survives but means "PyPI install and `tg --help` after release" instead of "aws dynamodb list-tables". |
| `testing.md` | **Reset to template** | Test counts, file lists, MSW handlers, Bedrock fixtures — all neighbor-project specific. Replace with: testing principles (already excellent — keep §"Testing Principles"), placeholder current-counts table, stack section (pytest + tooling, no MSW since this is a Python package), placeholder coverage targets. |
| `workflows.md` | **Edit (heavy)** | Git workflow is generic (keep). Git config block has neighbor-project user/remote — replace with telegrapher's once known, or strip. Functionality-doc-maintenance, feature-proposals-doc, README maintenance sections all reference the neighbor project's specific schema (Section 1.1-1.13 tables, frontend/backend READMEs, S20/S9 suggestion IDs) — generalize or delete. Per-Commit/Per-Milestone cadence is generic — keep but strip frontend/backend references. UI Review Checklist (§) is *entirely* irrelevant for a Python package — delete. Verification Gate is generic — keep with light edits. |
| `design-docs/index.md` | **Reset catalog** | Keep the template block at the top. Clear the catalog tables (DD-1 through DD-33 are all dataroom architectural decisions). Leave the section headings as a hint of where future DDs will go (e.g., "### Core Library", "### Backend Abstraction", "### Distribution & Packaging") but empty the rows. |
| `product-specs/index.md` | **Reset catalog** | Same treatment — keep structure, empty the catalog (PS-1 through PS-26 all gone), clear the "Milestones Overview" table (M1–M8 are dataroom milestones). Replace milestones with placeholders for v0.1 / v0.2 / v0.3 from `telegrapher-package-launch.md`. |
| `exec-plans/tech-debt-tracker.md` | **Reset to empty** | All 9 active TD items are dataroom (Lambda stubs, frontend CI, App Runner, etc.). Replace with empty Active Debt and Resolved Debt tables. Keep severity guide. |
| `exec-plans/active/` (dir) | **Verify empty** | Check if any neighbor exec plans were inherited. If so, delete. v0.1 will populate it fresh. |
| `exec-plans/completed/` (dir) | **Verify empty** | Same. |
| `plans/README.md` | **Light edit** | Reference to "qa-section-revision-and-fix-pack.md" is a neighbor-project example. Replace with a generic example or with `telegrapher-package-launch.md` / `inherited-docs-cleanup.md` as the in-flight examples. |

## Files NOT in `docs/` to also check

| File | Action | Notes |
|---|---|---|
| `CLAUDE.md` (repo root) | **Verify** | Probably doesn't exist yet. If a neighbor copy got carried over, it needs the same treatment as `dev-environment.md` — reset to a telegrapher-relevant entry point. |
| `ERRATA.md` (repo root) | **Verify** | If carried over, reset to empty. ERRATA entries are project-specific incident logs. |
| `MEMORY.md` (in `~/.claude/projects/.../memory/`) | **Already correct** | We've been writing to the telegrapher path; the dataroom MEMORY.md lives at the dataroom's path. Nothing to clean here. |
| `documentation/archive/` | **Verify doesn't exist** | If the neighbor archive folder got copied, delete. |

## Execution sequence

1. **Audit pass (read-only)** — verify the file list above is complete. Check `CLAUDE.md`, `ERRATA.md`, `documentation/`, `plans/active/`, `plans/completed/` to catch anything missed.
2. **Light-edit pass** — `agent-behavior.md`, `core-beliefs.md`, `harness-guidelines.md`, `workflows.md`, `plans/README.md`. Strip neighbor-specific text, keep wisdom.
3. **Heavy-edit pass** — `debugging.md`, `post-deploy-checklist.md`. Delete project-specific sections, keep methodology.
4. **Reset-to-template pass** — `dev-environment.md`, `feature-proposals.md`, `functionality-audit.md`, `testing.md`, `design-docs/index.md`, `product-specs/index.md`, `exec-plans/tech-debt-tracker.md`. Empty tables/catalogs, keep structure.
5. **Verification pass** — grep `docs/` for any remaining occurrences of: `dataroom`, `founder`, `investor`, `Cognito`, `Amplify`, `App Runner`, `DynamoDB`, `Aurora`, `Bedrock`, `Papermark`, `VC memo`, `frontend/`, `backend/`. Each hit gets reviewed: legitimate generic mention vs. residual leak.
6. **Coherence read** — read each file end-to-end as if seeing the package fresh. Anything that doesn't make sense for a Python library gets fixed.

## Verification

```bash
# Must return zero matches in docs/ after cleanup:
grep -ri "dataroom\|founder\|investor\|cognito\|amplify\|app runner\|dynamodb\|aurora\|bedrock\|papermark\|vc memo" docs/ | grep -v "telegrapher-package-launch.md\|inherited-docs-cleanup.md"

# Should return zero or only legitimate Python-package mentions:
grep -ri "frontend\|backend" docs/ | grep -v "telegrapher-package-launch.md\|inherited-docs-cleanup.md"

# Sanity: each top-level doc still has its "When to update this file" header
for f in docs/*.md; do head -3 "$f" | grep -q "When to update" || echo "MISSING: $f"; done
```

After cleanup, a fresh reader should be able to skim `docs/` and understand:
- This is a Python package for Telegraph English compression
- The agent-behavior contract and harness model that govern work here
- The 5-phase debugging protocol
- The doc hierarchy (plans → product-specs → design-docs → exec-plans)
- That the catalogs are empty because v0.1 hasn't been built yet

## Cascade — what this enables

Once `docs/` is clean, the v0.1 work in [`telegrapher-package-launch.md`](telegrapher-package-launch.md) can populate the now-empty catalogs:

- `product-specs/ps-001-memory-wedge.md` — v0.1 product requirements
- `design-docs/dd-001-backend-abstraction.md` — Backend ABC + LocalBackend
- `design-docs/dd-002-conversation-compactor.md` — eviction strategy
- `exec-plans/active/v0.1-memory-wedge.md` — phase-by-phase implementation

Each of those will reference `telegrapher-package-launch.md` as their source-of-truth design plan.

## Out of scope for this cleanup

- Adding new docs (e.g., `docs/architecture.md` for the Python package) — done as v0.1 progresses
- Filling the catalogs — done as PS/DD/exec-plans are written
- Writing a `CLAUDE.md` for this repo — separate task, after the docs are clean
- Setting up CI / linters / pre-commit hooks — implementation work, not docs cleanup
