# Harness + Context Guidelines

> Guiding principles for maintaining AI-agent-friendly project infrastructure.
> This document governs how we build and maintain all documentation, linting rules, architectural constraints, and feedback loops in this repository.

**When to update this file:** After changing any doc structure, adding a new doc category, changing constraint mechanisms, or discovering a new principle from agent interactions.

---

## 1. What Is a Harness?

A **harness** is the complete infrastructure that keeps AI coding agents productive and reliable. It is broader than "context engineering" (giving the agent the right information). A harness also **prevents** bad output, **measures** quality, and **corrects** drift over time.

| Layer | Question It Answers | Examples |
|-------|---------------------|----------|
| **Context** | What should the agent *know*? | CLAUDE.md, architecture docs, core beliefs, inline code comments, reference docs |
| **Constraints** | What should the system *prevent*? | Linters, structural tests, CI gates, dependency rules, schema validation |
| **Correction** | What should the system *fix automatically*? | Periodic audits, stale-doc detection, consistency checks, auto-formatting |

**Diagnostic rule:** Wrong output once? Likely a context problem. Slow degradation over weeks? That's a harness problem.

---

## 2. Core Principles

### 2.1 Repository as System of Record

All critical context lives **inside the repo**, not in external wikis, Notion pages, or chat history.

- Agents can only reliably access what's in the repo (or explicitly provided tools).
- If knowledge isn't in the repo, it doesn't exist for the agent.
- That Slack discussion that aligned the team on an architectural pattern? If it isn't in the repo, it's illegible -- same as being unknown to a new hire joining three months later.

### 2.2 Map, Not Manual

> "Give the agent a map, not a 1,000-page instruction manual."

- Context is a scarce resource. A giant instruction file crowds out the task, the code, and the relevant docs.
- Root-level docs (CLAUDE.md, MEMORY.md) are **indexes with pointers**, not encyclopedias.
- Each doc is **self-contained for its scope** -- an agent reading only that doc should understand its domain.
- **Progressive disclosure**: agents start with a small, stable entry point and are taught where to look next, rather than being overwhelmed up front.

### 2.3 Progressive Disclosure

Documentation is organized in layers of increasing detail:

```
Layer 0: CLAUDE.md (~130 lines)    -- env setup, current state, pointers to docs/
Layer 1: docs/ top-level files     -- domain overviews (architecture, conventions, testing)
Layer 2: docs/ subdirectories      -- detailed specs, design decisions, references
Layer 3: Inline code comments      -- implementation-specific context
```

An agent working on a typical task reads Layer 0, follows a pointer to the relevant Layer 1 doc, and dives into Layer 2 only when the task demands it. No task should require reading all of Layer 2.

### 2.4 Mechanical Enforcement Over Convention

Rules that depend on agents "remembering" to follow them will eventually be violated.

- **Encode constraints deterministically** wherever possible: linters, CI checks, schema validation, structural tests.
- Linter error messages should **teach** -- they double as context for agents.
- Reserve LLM-based enforcement only for rules that can't be expressed mechanically (e.g., "is this commit message clear?").
- When documentation falls short, **promote the rule into code** -- a lint rule that fires on every build is more reliable than a doc that might not be read.

### 2.5 Design for Agent Legibility

Code and docs should be optimized for agent comprehension, not just human readability.

- **Consistent naming patterns** reduce ambiguity (agents pattern-match harder than humans).
- **Predictable file locations** -- agents shouldn't have to search for where things "might" be.
- **Explicit over clever** -- avoid metaprogramming, dynamic imports, or magic that requires deep context to understand.
- **Favor "boring" technology** -- composable, stable APIs with broad representation in training data are easier for agents to model than exotic dependencies.
- When an external library's behavior is opaque, consider reimplementing the needed subset with full test coverage rather than fighting upstream surprises.

### 2.6 Iterative Signal-Driven Improvement

> "When the agent struggles, treat it as a signal: identify what is missing -- tools, guardrails, documentation -- and feed it back into the repository."

- Agent failures are **harness bugs**, not just model limitations.
- After every recurring issue, ask: "What doc, lint rule, or test would have prevented this?"
- Capture human judgment **once**, enforce it **continuously**.
- The agent should write the fix to the harness itself -- the human's job is to identify what's missing and direct the agent to encode it.

### 2.7 Fight Entropy Actively

Agents replicate existing patterns -- good and bad. Without active maintenance, quality drifts downward.

- Stale documentation is worse than no documentation (it actively misleads).
- Remove outdated content aggressively -- don't let dead docs accumulate.
- Encode "golden principles" directly into the repo and run periodic cleanup against them.
- Technical debt is a high-interest loan: pay it down in small continuous increments, not in painful bursts.

### 2.8 Plans as First-Class Artifacts

Plans are versioned, co-located, and independently loadable -- not buried in monolithic docs.

- Active plans live in `docs/exec-plans/active/`.
- Completed plans move to `docs/exec-plans/completed/` with a decision log.
- Each plan has its own progress state, so agents can pick up where they left off.
- Plans don't crowd out other context -- an agent working on feature X only loads plan X.

### 2.9 Critical Files Are Sacred

Critical project files — whether git-tracked or gitignored — must never be carelessly deleted. Gitignored files (.env, .claude/) contain local-only state. CLAUDE.md and ERRATA.md are now git-tracked to prevent loss.

- **NEVER delete, move, rename, or overwrite critical files** without explicit user confirmation AND a local backup.
- "Archive the original" means creating a frozen snapshot — it does NOT mean deleting the working copy.
- Before any destructive operation on a file, check whether it's gitignored (`git check-ignore <file>`). If gitignored: STOP and confirm with the user.
- See `ERRATA.md` ERR-001 for the incident that motivated this rule.

### 2.10 Encode Judgment, Not Just Rules

Some engineering wisdom can't be expressed as lint rules: "prefer boring technology," "validate at boundaries," "when in doubt, add a test." These are captured as **core beliefs** -- a small set of opinionated principles that guide agent decision-making when no specific rule applies.

- Core beliefs live in `docs/core-beliefs.md`.
- They're short, numbered, and written as directives (not explanations).
- They change rarely -- these are team values, not implementation details.

### 2.11 Debug Like an Engineer, Not a Gambler

Debugging is feature engineering -- it requires the same rigor as building new features. Trial-and-error pushed to production is not debugging; it's gambling with a working system.

- **NEVER change working code based on assumptions.** If the app was working, the code was fine. The problem is elsewhere.
- **Observe before acting.** Gather all evidence (logs, env vars, build output, network requests) before forming a hypothesis.
- **Verify before fixing.** Confirm the root cause with read-only checks before writing any code.
- **Fix one thing at a time.** Isolate problems. Never combine fixes for unrelated issues in one change.
- **Config problems need config fixes.** If code works locally but not in deployment, the problem is almost certainly configuration, not code.
- **Protect working systems.** A change that risks breaking something that currently works is not a fix -- it's a new risk that requires its own justification and verification.
- Full debugging protocol lives in `docs/debugging.md`.

---

## 3. Major Change Process

Major changes (new subsystem, new backend, cross-cutting feature) follow a structured sequence. Each phase produces a versioned artifact before the next phase begins. This prevents architecture decisions from being made in a vacuum and ensures documentation stays synchronized with design.

### 3.1 Phase Sequence

```
Phase 1: Requirements Gathering
  ├── Read existing feature proposals, functionality audit, business model docs
  ├── Identify requirements (R1, R2, ...) with source references
  ├── Flag gaps: requirements NOT covered by existing proposals
  └── Output: Requirements list (inline in conversation or working doc)

Phase 2: Scoping & Formal Proposals
  ├── User scopes each requirement (include / defer / reject)
  ├── Write formal feature proposals (P-numbered) in feature-proposals.md
  ├── Update cross-reference table, supersede old proposals if applicable
  └── Output: feature-proposals.md updated

Phase 3: Architecture Decision
  ├── Analyze options (≥2) against core beliefs, existing stack, cost, complexity
  ├── Present trade-offs with concrete numbers (cost, latency, migration effort)
  ├── User selects approach
  ├── Write design decision (DD-numbered) in design-docs/
  ├── Cascade updates to affected docs (data-model, infrastructure, architecture, etc.)
  └── Output: DD-NNN created, affected docs updated

Phase 4: Product Spec
  ├── Write product spec (PS-numbered) in product-specs/
  ├── Covers: user stories, data model, API surface, known gaps
  ├── References the DD and P-numbers from prior phases
  ├── Update product-specs/index.md
  └── Output: PS-NNN created

Phase 5: Execution Plan
  ├── Break implementation into ordered phases with dependencies
  ├── Each phase: scope, files to create/modify, tests, acceptance criteria
  ├── Place in exec-plans/active/
  ├── Reference DD and PS from prior phases
  └── Output: Exec plan in active/

Phase 6: Implementation
  ├── Read context chain BEFORE writing code (see 3.5)
  ├── Follow exec plan phase-by-phase
  ├── Update exec plan progress after each phase
  ├── Run post-commit doc update checklist (workflows.md)
  └── When complete: move exec plan to completed/
```

### 3.2 When to Use This Process

| Trigger | Use Full Process? |
|---------|-------------------|
| New database / data store | Yes — all 6 phases |
| New subsystem (e.g., new backend, retrieval layer) | Yes — all 6 phases |
| Cross-cutting feature (affects ≥3 existing services) | Yes — all 6 phases |
| Single feature in existing subsystem | Phases 2 + 4 + 6 (skip architecture decision if no new infrastructure) |
| Bug fix or small enhancement | None — just implement and update docs per workflows.md |

### 3.3 Artifact Dependency Graph

```
Requirements (Phase 1)
  └─→ Feature Proposals (Phase 2)  ← feature-proposals.md
        └─→ Design Decision (Phase 3)  ← design-docs/dd-NNN.md
              ├─→ Product Spec (Phase 4)  ← product-specs/ps-NNN.md
              └─→ Cascading doc updates (data-model, infrastructure, architecture, etc.)
                    └─→ Execution Plan (Phase 5)  ← exec-plans/active/
                          └─→ Implementation (Phase 6)
```

Each artifact references its upstream artifacts by ID (P-number, DD-number, PS-number). This creates a traceable chain from business requirement to committed code.

### 3.4 Cross-Session Continuity

Major changes often span multiple agent sessions. To maintain continuity:

- **Feature proposals** are the entry point — read `feature-proposals.md` to know what's been scoped.
- **Design decisions** capture the "why" — read the DD to understand architectural choices.
- **Exec plans** track "where we are" — read the active exec plan to resume from the last completed phase.
- Never rely on conversation history for state — all decisions must be in versioned files.

### 3.5 Pre-Implementation Reading Order

Before writing any code for a major change, read these docs in order:

1. **Exec plan** (`exec-plans/active/`) — find the current phase, read its tasks and acceptance criteria
2. **Design decision** (referenced in exec plan header) — understand the architecture, key interfaces, boundary rules
3. **Product spec** (referenced in exec plan header) — understand user stories, API surface, behavior contracts
4. **Existing code** (referenced in exec plan phase tasks) — read files you'll modify before editing them

The exec plan's header block links to all upstream artifacts. Follow those links — don't search for context independently.

---

## 4. Documentation Architecture

### 4.1 Full Document Hierarchy

```
CLAUDE.md                              # Layer 0: Agent entry point (when present)
                                       #   session-start reading list, build status, doc map
ERRATA.md                              # Severe mistakes to never repeat (when present)
README.md                              # Human-facing: package overview, quick start, install

docs/
├── agent-behavior.md                  # Agent working rules, task management, verification, feature lifecycle
├── dev-environment.md                 # Environment paths, dev commands, known pitfalls
├── harness-guidelines.md              # THIS FILE -- meta-rules for all docs
├── core-beliefs.md                    # Engineering values and judgment heuristics
├── testing.md                         # Testing strategy, coverage targets, patterns
├── workflows.md                       # Git workflow, doc maintenance, verification gate
├── debugging.md                       # MANDATORY debugging protocol (5-phase)
├── post-deploy-checklist.md           # Post-release checklist
├── functionality-audit.md             # Living audit: implemented, gaps, suggestions
├── feature-proposals.md               # Feature candidates under evaluation
│
├── plans/                             # Plan-mode design workbooks (decision traces)
│   └── *.md
│
├── design-docs/                       # Architectural decisions and design rationale (DD-NNN)
│   ├── index.md
│   └── dd-NNN-*.md
│
├── product-specs/                     # Product requirements and feature specs (PS-NNN)
│   ├── index.md
│   └── ps-NNN-*.md
│
└── exec-plans/                        # Milestone and feature execution plans
    ├── active/                        # In-progress plans
    ├── completed/                     # Finished plans (with decision log)
    └── tech-debt-tracker.md           # Known technical debt, prioritized
```

### 4.2 Document Design Rules

1. **Single responsibility**: Each doc covers one domain. No doc should need to reference another to be usable within its scope.
2. **Living documents**: Update in-place on every relevant commit. Never append changelogs -- these are snapshots, not logs.
3. **Concise by default**: If a section exceeds ~30 lines, the detail likely belongs in code comments or a sub-doc.
4. **Machine-parseable structure**: Use consistent heading levels, tables, and code blocks. Avoid prose paragraphs where a table or list works better.
5. **Cross-reference with relative links**: When one doc references another, use a relative link. Don't duplicate content across docs.
6. **Freshness markers**: Every doc starts with a "When to update" note specifying what triggers an update.
7. **Index files for subdirectories**: Every subdirectory (`design-docs/`, `product-specs/`, `exec-plans/`) has an `index.md` cataloging its contents with verification status.

### 4.3 CLAUDE.md Role

CLAUDE.md, when present, is a **lean entry point** (~100 lines). It contains:

- **Session-start reading list** (MANDATORY) — lists all behavior-defining docs that must be read on every new session
- Project overview (2-3 sentences)
- Current build status (test counts, coverage)
- Phase / version status (what's done, what's next)
- Environment pointer (→ `docs/dev-environment.md` for paths and commands)
- Documentation map table pointing to all `docs/` files with one-line descriptions

**How agents should use docs/:** CLAUDE.md is always loaded. On session start, read ALL docs listed in the session-start section. During the session, use the Documentation Map to find domain-specific docs as needed. When modifying functionality, check `docs/workflows.md` for post-commit update requirements and the verification gate.

### 4.4 README Role

The root `README.md` is a **human-facing onboarding doc** — it targets PyPI visitors, GitHub viewers, and new collaborators. It is NOT agent context (that's CLAUDE.md + docs/). It IS git-tracked and must stay accurate.

**Key rules:**
- The README mirrors a subset of `docs/` content but is written for humans skimming GitHub or PyPI, not agents deep in a task.
- **Test counts, version status, and feature lists** must match the values in `docs/` and CLAUDE.md.
- The README does NOT replace `docs/` — it is a summary with pointers. Don't duplicate detailed architecture or conventions.
- When updating `docs/` during a release, **always check the README for stale counts** (test numbers, version, feature list).

### 4.5 MEMORY.md Role

MEMORY.md lives in Claude's auto-memory directory (`~/.claude/projects/.../memory/MEMORY.md`), not the repo root. It is a cross-session operational memory file:
- Machine-specific environment paths (venv, package manager)
- Git config (user, remote, branches)
- Common pitfalls and their fixes (things that waste time if forgotten)
- Documentation structure quick-reference (where things live)
- NOT for encoding rules or conventions -- those go into `docs/`

### 4.6 Agent Behavior Doc Role

`docs/agent-behavior.md` is the **behavioral contract** — how the agent works, not what the code does. It covers:
- Workflow orchestration (plan mode, subagent strategy, self-improvement)
- Task management (plan first, verify, track, explain, capture lessons)
- Verification rules (never mark done without proving it works)
- Feature development lifecycle (product_spec → design_doc → exec_plan → develop → update docs → complete)
- Release planning
- Core working principles (simplicity, no laziness, minimal impact)

---

## 5. Constraint Engineering

### 5.1 Constraint Hierarchy

Constraints exist at three levels, in order of reliability:

| Level | Mechanism | Reliability | Examples |
|-------|-----------|-------------|----------|
| **Mechanical** | Deterministic tools (linters, CI, type checkers) | Highest | `ruff`, `mypy --strict`, CI gates |
| **Structural** | Tests that verify architecture invariants | High | Dependency direction tests, import rules, file structure checks |
| **Agent-Assisted** | LLM self-checks during workflow | Medium | Doc freshness, commit message quality, coverage checks |

Always prefer a higher-reliability mechanism. Promote agent-assisted constraints to mechanical ones when the pattern becomes clear.

### 5.2 Deterministic Constraints (Currently Active)

| Constraint | Mechanism | Purpose |
|------------|-----------|---------|
| Code formatting | `ruff format` / `black` | Eliminate style debates |
| Import ordering | `ruff` / `isort` rules | Consistent dependency structure |
| Type safety | Python type hints + `mypy` strict | Catch errors before runtime |
| Public API validation | `pydantic` models at I/O boundaries | Contract enforcement |
| Test gate | CI: tests must pass before merge | Prevent regressions |
| Secret prevention | `.gitignore` patterns | Security baseline |

### 5.3 Structural Constraints (To Build)

| Constraint | Mechanism | Purpose |
|------------|-----------|---------|
| Dependency direction | Custom lint: high-level modules can't import from concrete backends | Enforce layered architecture |
| File size limits | CI check: no file > N lines | Prevent monolithic files |
| Naming conventions | Regex lint on filenames and exports | Consistent discoverability |
| Boundary validation | Test: every public API call passes through pydantic validation | Validate at boundaries |

### 5.4 Agent-Assisted Constraints

| Constraint | When | Purpose |
|------------|------|---------|
| Doc freshness check | Before commit | Flag when changed files have no corresponding doc update |
| Commit message review | Before commit | Verify imperative mood, concise summary |
| Architectural conformance | During code review | Validate new code follows established patterns |
| Test coverage for new code | After implementation | Ensure new features have tests |

### 5.5 Constraint Design Principles

- Constraints should **fail loudly** with messages that explain **why** and **how to fix**. Error messages are agent context.
- Prefer **prevention** (pre-commit) over **detection** (post-merge). Catching errors early is cheaper.
- Every constraint must be **documented** -- an undocumented rule is invisible to agents.
- When you find yourself telling the agent the same correction twice, that's a signal to add a constraint.

---

## 6. Entropy Management ("Garbage Collection")

### 6.1 What Decays

| Thing | How It Decays | Consequence |
|-------|--------------|-------------|
| Documentation | Becomes stale as code changes | Agent builds on wrong assumptions |
| Test descriptions | Drift from what tests actually verify | False confidence in coverage |
| Naming conventions | Inconsistencies creep in across files | Agent can't find things by pattern |
| Dead code | Unused functions, orphaned files | Agent copies bad patterns |
| Dependencies | Security vulnerabilities, breaking changes | Build failures, security gaps |
| Quality scores | Grades don't reflect actual state | Wrong prioritization |

### 6.2 Countermeasures

| Decay Type | Countermeasure | Frequency |
|------------|---------------|-----------|
| Stale docs | Compare doc claims against actual code | Every release |
| Dead code | Run coverage + unused-export analysis | Monthly |
| Naming drift | Grep for convention violations | Per PR |
| Dependency rot | `pip-audit` | Weekly |
| Test drift | Review test descriptions vs. assertions | Every release |

### 6.3 The Audit Loop

After every release:
1. Agent scans all docs against current code state.
2. Agent lists discrepancies (outdated counts, missing features, wrong file paths).
3. Human reviews and approves fixes.
4. Agent applies fixes and updates freshness markers.
5. Agent opens targeted refactoring PRs for any code issues found.

### 6.4 Golden Principles

"Golden principles" are the subset of constraints that are so important they're checked on every audit run. They live in `docs/core-beliefs.md` and represent the team's strongest opinions. Examples:
- We validate data at boundaries, not in the middle.
- We prefer shared utilities over hand-rolled helpers.
- Every public API surface has a corresponding test.

---

## 7. Feedback Loop Protocol

When an agent makes a mistake or struggles with a task:

```
1. IDENTIFY  -- What went wrong? (wrong output, missed edge case, wrong file, etc.)
2. DIAGNOSE  -- Was it a context, constraint, or correction problem?
    Context:    Agent didn't know something    → update docs
    Constraint: Agent violated a rule          → add lint rule or CI check
    Correction: Issue accumulated over time    → add periodic audit
3. FIX       -- Have the agent implement the countermeasure in the repo
4. VERIFY    -- Test that the fix would have prevented the original issue
```

**Key rules:**
- Fixes go into the **repository** (docs, linters, tests), not into ephemeral session memory.
- MEMORY.md is for operational quick-start facts (env paths, common pitfalls), not for encoding rules.
- The agent should write the harness fix itself -- human's job is to identify the gap and direct the fix.
- Always ask: "Will this fix prevent the *category* of mistake, or just this *instance*?"

---

## 8. Generated Documentation

Some docs should be auto-generated from code to guarantee freshness. When the generation pipeline exists in this repo, generated docs live under `docs/generated/`.

**Rules for generated docs:**
- Always include a header: `<!-- GENERATED FILE -- DO NOT EDIT MANUALLY -->`
- Include the generation command so any agent can regenerate.
- Never mix manual content into generated files.

Candidate generated docs for this package (build as needed):
- API catalog from `src/telegrapher/` public exports + docstrings
- Extras matrix from `pyproject.toml`
- Backend ABC method table from `telegrapher.core.backends`

---

## Sources

These guidelines synthesize insights from:
- [OpenAI: Harness Engineering](https://openai.com/index/harness-engineering/) -- the original concept and lessons from building a million-line codebase with zero manually-written code.
- [Martin Fowler: Harness Engineering](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html) -- analysis of the three-layer harness model (context, constraints, correction).
- [mtrajan: Harness Engineering Is Not Context Engineering](https://mtrajan.substack.com/p/harness-engineering-is-not-context) -- the critical distinction between giving agents information vs. building systems that prevent, measure, and correct.
- [Can.ac: The Harness Problem](https://blog.can.ac/2026/02/12/the-harness-problem/) -- how the interface layer between LLM output and code changes is the highest-leverage place to invest.
