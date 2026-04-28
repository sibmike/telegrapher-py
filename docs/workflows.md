# Workflows

> Development workflows, CI/CD, git branching, documentation maintenance, and release processes.

**When to update this file:** After changing git workflow, adding CI/CD steps, or modifying documentation maintenance procedures.

---

## Git Workflow

- **`main`** branch is production
- **`dev`** branch for active development
- Feature branches: `feature/<short-description>`
- Bug fix branches: `fix/<short-description>`
- Commit messages: imperative mood, concise summary line

### Git Config (repo-local)

- User: TBD (set when repo is initialized)
- Remote: `origin` → TBD

### Merge Procedure (dev → main)

All commits go to `dev` first. Dev is always ahead of or equal to main. Never commit directly to main. Even hotfixes go through dev first.

```bash
# 1. Work on dev
git checkout dev
# ... make changes, commit, push ...
git push origin dev

# 2. When ready for production
git checkout main
git merge dev
git push origin main

# 3. After merge, dev and main should be at the same commit
```

---

## Functionality Doc Maintenance

**File:** `docs/functionality-audit.md`

Living audit of implemented vs. missing vs. suggested functionality. Updated after every commit that changes functionality.

### When to Update

| Trigger | Action |
|---------|--------|
| New module / public API surface | Add row to Section 1 (Implemented) |
| Stub → real implementation | Move from Section 2 (Planned) to Section 1 |
| Gap resolved | Remove from Section 3, add to Section 1, update Section 5 counts |
| New gap discovered | Add numbered row to Section 3, assign severity, update Section 5 |
| Suggested feature implemented | Remove from Section 4, add to Section 1 |
| Test count changes | Update Tests column in Section 1 + Section 5 summary |

### Precise Rules

1. **Section 1 (Implemented):** Each row has columns: Feature | Module | Tests. Fill every column — use `--` for N/A, specific file/function references for implemented. Always include the test file name if tests exist.
2. **Section 2 (Planned):** Only items in scope for the current phase (v0.1 / v0.2 / v0.3). When work starts, items move to Section 1 as completed.
3. **Section 3 (Gaps):** Sequential numbering `#1, #2, ...` — never reuse deleted numbers. Each gap has: `#`, Gap description (bold), Spec Reference, Impact, Severity (High/Medium/Low).
4. **Section 4 (Suggested):** Prefixed `S1, S2, ...` — never reuse.
5. **Section 5 (Summary):** Recount after any Section 1-4 change. Update by-severity and release-blockers tables.
6. **Severity assignment:** High = broken feature or security/correctness risk. Medium = degraded UX or incomplete feature. Low = nice-to-have or future concern.
7. **Release-Blockers list:** Only High-severity items that must be resolved before the next release. Re-evaluate on every update.
8. **Gap numbers are permanent.** Never change or reuse.

### What NOT to Do

- Do not rewrite entire sections — edit individual rows in place.
- Do not remove gaps without verifying the fix is committed and tests pass.
- Do not add speculative features to Section 1 — only committed, tested code.
- Do not change gap numbers — downstream references may rely on them.

---

## Feature Proposals Doc

**File:** `docs/feature-proposals.md`

Candidates for future features. Not committed work.

- Tracks larger feature ideas under evaluation
- When approved → create a phase entry, track implementation in `functionality-audit.md`
- When rejected → leave the row with a rationale in the Decision Log (never delete)
- Proposals numbered `P1, P2, ...` — sequential, never reused
- Small tactical suggestions belong in `functionality-audit.md` Section 4 (`S1, S2, ...`); larger feature ideas go here
- Do not move proposals to "Implemented" until code is committed and tested
- Record every approve/defer/reject decision in the Decision Log at the bottom of this file

---

## Documentation Maintenance Cadence

### Per-Commit

- Update `docs/functionality-audit.md` if functionality changed
- Update test counts in CLAUDE.md build status table (when CLAUDE.md exists)

### Per-Release

- Run full audit loop (see [harness-guidelines.md](./harness-guidelines.md) Section 6.3)
- Update `docs/exec-plans/tech-debt-tracker.md`
- Review and update `docs/core-beliefs.md` if engineering philosophy evolved
- Move completed exec plans from `active/` to `completed/`
- Update README — see README rules below
- Archive any documentation that has become stale

### Per-Session (Agent)

- Check MEMORY.md pitfalls before running commands
- After discovering a new pitfall → add to MEMORY.md
- After any recurring agent mistake → apply feedback loop protocol (see [harness-guidelines.md](./harness-guidelines.md) Section 7)

---

## README Maintenance

**File:** `README.md` (root)

Human-facing onboarding doc for PyPI visitors, GitHub viewers, and new collaborators. Must stay factually accurate but doesn't need the same depth as `docs/`.

### When to Update

| Trigger | What to check |
|---------|---------------|
| Release | Version, milestone checklist, test counts, feature list |
| New module added | Project structure tree, feature list |
| New extra added to `pyproject.toml` | Install matrix in README |
| Test count changes | Test count lines |

### What the README Contains

- One-paragraph package overview (what it does, who it's for)
- Install commands (`pip install telegrapher` + extras)
- Quickstart code snippet (the v0.1 minimum demo)
- Tech stack bullets (Python version, key dependencies, model source)
- Project structure tree (top-level only)
- Test command + count + coverage
- Phase / version status
- Link to `docs/` for deeper detail

### Precise Rules

1. **Counts must match:** Test counts, version, dependency lists in the README must match `docs/testing.md`, `pyproject.toml`, and CLAUDE.md (when present). When in doubt, run the test suite.
2. **No duplication of detailed docs:** The README summarizes — it doesn't replace `docs/`. Keep descriptions to one line per item.
3. **Quick start must work:** The setup commands should be valid for a fresh clone. Don't include machine-specific paths (those live in `docs/dev-environment.md`).
4. **Feature lists reflect reality:** Only list features that are implemented and tested. Don't list planned features as if they exist.

---

## Debugging Protocol

**MANDATORY:** Follow the [debugging protocol](./debugging.md) before making ANY code changes when something breaks. Full 5-phase protocol (Observe → Hypothesize → Verify → Plan → Implement) and key rules live in that doc.

---

## Post-Release Checklist

**MANDATORY:** Run the [post-deploy checklist](./post-deploy-checklist.md) after EVERY release to PyPI / model push to HF Hub / debugging session. The checklist covers:

1. **Release verification** — `pip install <version>` in a fresh venv and exercise the public API (local tests DON'T prove a published wheel works)
2. **Smoke test** — `tg compress` / `tg expand` / `tg eval` end-to-end on a fixture corpus
3. **Documentation updates** — exec plans, product specs, design docs, functionality audit, testing, CLAUDE.md, README
4. **ERRATA check** — add entry if severe mistakes were made
5. **Memory check** — add machine-specific pitfalls to MEMORY.md
6. **Session reflection** — verify debugging protocol was followed, behavioral rules obeyed

---

## Verification Gate — Before Marking Work Complete

Before moving an exec plan from `active/` to `completed/`, ALL of the following must be true:

1. All exec plan acceptance criteria are met
2. All tests passing
3. Docs updated per the maintenance cadence above
4. Product spec, design doc, and exec plan updated to align with the developed version
5. User has verified the feature works
6. All other affected docs updated as needed (functionality-audit, testing, README, etc.)

Only THEN: move the exec plan to `completed/` and reflect on whether behavior docs ([agent-behavior.md](./agent-behavior.md)) or `ERRATA.md` need updates based on session experience.
