# Post-Release & End-of-Session Checklist

> Mandatory checklist to run after ANY release to PyPI, model push to Hugging Face Hub, merge to main, or debugging session. Every item must be checked — no shortcuts.
>
> **When to update this file:** After a post-release failure reveals a missing check, after a new release pipeline is introduced, or when a new distribution target is added.

---

## When to Use This Checklist

| Trigger | Which sections |
|---------|---------------|
| Release to PyPI | **All sections** (1–6) |
| Model push to HF Hub | Sections 1, 2, 3, 5, 6 |
| Hotfix / patch release | Sections 1, 2, 3, 5, 6 |
| Debugging session (no release) | Sections 4, 5, 6 only |

---

## 1. Release Verification

**Purpose:** Catch broken wheels, missing data files, or dependency issues BEFORE users hit them. In-tree tests run against editable installs and source — they NEVER prove that a built wheel works.

### 1.1 Install from the published artifact

Run this in a **fresh, empty virtualenv** — not the dev venv.

```bash
# Create a clean throwaway venv
python -m venv /tmp/te-verify && source /tmp/te-verify/bin/activate

# Install from PyPI (or test PyPI for pre-release)
pip install telegrapher==<version>

# Verify the public API imports
python -c "from telegrapher import Telegrapher; print(Telegrapher.__module__)"

# Verify CLI is on PATH
tg --version

# If extras shipped: install one and exercise it
pip install telegrapher[langchain]==<version>
python -c "from telegrapher.integrations.langchain import TelegrapherSummaryMemory"
```

### 1.2 Verify the model card / weights (HF Hub releases)

When a new model version is pushed to HF Hub:

1. **Pull from a fresh cache** — delete `~/.cache/telegrapher/` and `~/.cache/huggingface/` for the relevant entry, then run `tg download-model` to confirm the published artifact is reachable.
2. **Run a smoke compress + expand** — round-trip a fixture and confirm fidelity meets the ship criteria.
3. **Check the model card** — version field, license, intended use, evaluation metrics all match the source-of-truth in `docs/`.

### 1.3 Why local tests don't catch this

> **CRITICAL:** Local tests run against the source tree (`pip install -e .`) or in-tree imports. They do NOT validate:
> - That `pyproject.toml` declared all required dependencies
> - That data files (prompts, model cards, fixtures) made it into the wheel
> - That extras correctly gate optional imports
> - That the entry-point CLI got registered
> - That the wheel is platform-compatible (manylinux, macOS arm64, Windows)
>
> The single most common source of "works locally, broken on PyPI" bugs is packaging. Always install the published wheel and exercise the public API before declaring a release done.

---

## 2. Smoke Test

**Purpose:** Verify the package actually works end-to-end with the published artifact — not the source tree.

### 2.1 Manual smoke test (minimum)

After installing from PyPI in a clean venv:

```bash
# Round-trip a known fixture
echo "Some long passage about machine learning and medical diagnostics." > /tmp/sample.txt
tg compress /tmp/sample.txt --level L3 -o /tmp/sample.te
tg expand /tmp/sample.te -o /tmp/sample.back.txt

# Run eval against a small corpus
tg eval ./tests/fixtures/corpus/ --report /tmp/smoke.md

# Memory wedge sanity check
python -c "
from telegrapher.memory import ConversationCompactor
m = ConversationCompactor(level='L3', max_tokens=2000)
for _ in range(20): m.add_user_message('long turn …')
print(m.token_count(), m.compression_ratio())
"
```

### 2.2 Ship criteria (must pass for release)

- Round-trip QA fidelity ≥ 95% on key facts at L3
- Compression ratio ≥ 2× at L3 across the smoke corpus
- All CLI commands return exit code 0 on the fixture inputs
- All public API imports succeed in the clean venv

---

## 3. Documentation Updates — Feature Releases

For every feature that reaches a release, update ALL of these:

### 3.1 Exec Plan

| If... | Then... |
|-------|---------|
| Feature is fully complete and verified | Move exec plan from `docs/exec-plans/active/` to `docs/exec-plans/completed/` |
| Feature is partially shipped (phased) | Update exec plan in `active/` with completed phases and remaining work |
| Bug fix with no exec plan | No action |

**Before moving to completed:** Ensure the exec plan reflects the ACTUAL implementation (not the original plan). Update any sections that diverged during development.

### 3.2 Product Spec & Design Doc

Update to align with what was ACTUALLY built:

- `docs/product-specs/ps-NNN-*.md` — Update acceptance criteria, public API contracts, behavior to match reality
- `docs/design-docs/dd-NNN-*.md` — Update architecture diagrams, data flow, decision records

### 3.3 Functionality Audit

**File:** `docs/functionality-audit.md`

- Add new features to Section 1 (Implemented) with Module/Tests columns filled
- Move items from Section 2 (Planned) to Section 1 as completed
- Resolve gaps in Section 3 that this release fixes
- Update Section 5 summary counts

### 3.4 Testing Doc

**File:** `docs/testing.md`

- Update test counts (run the actual suite — don't guess)
- Add new test patterns or fixtures introduced
- Update coverage numbers if available

### 3.5 CLAUDE.md Build Status

**File:** `CLAUDE.md` (when present)

- Update the Build Status table (file counts, test counts, coverage, status)
- Update phase / version section if a phase was completed
- Update any doc references that changed

### 3.6 README

**File:** `README.md`

- Update version
- Update test counts
- Update feature lists
- Update install/extras matrix
- Verify quick-start commands still work against the published wheel

---

## 4. Documentation Updates — Bug Fixes / Patch Releases

Lighter weight than feature releases:

1. **CLAUDE.md** (when present): update build status table test counts if they changed
2. **Functionality audit:** if the bug was a gap in Section 3, mark it resolved

---

## 5. ERRATA Check

**File:** `ERRATA.md` (when present)

Ask yourself: **Did I make a severe mistake during this session?**

Criteria for adding an ERRATA entry:
- Data loss or broken release state
- Multiple failed fix attempts (3+ iterations on the same bug)
- Misdiagnosis that led to the wrong fix being released
- Violation of a behavioral rule (e.g., skipping documentation trail, "fix forward" without verification)
- Security-sensitive mistake (exposed secret, broken auth in a server build)

If yes: add an `ERR-NNN` entry with Date, Severity, What happened, Impact, Root cause, and Rules to Prevent Recurrence.

**Be honest.** ERRATA entries exist to prevent recurrence, not to assign blame.

---

## 6. Memory Check & Session Reflection

### Memory Check

Did I discover a new machine-specific pitfall or operational fact?

Things that belong in `~/.claude/projects/.../memory/MEMORY.md`:
- New shell command quirks on this machine
- New environment path discoveries
- Release pipeline gotchas specific to this account / token / build host
- Session workflow lessons (things that save time next session)

Things that DON'T belong in MEMORY.md (they go in `docs/` instead):
- Code conventions → `docs/core-beliefs.md` (or a future `docs/conventions.md`)
- Debugging patterns → `docs/debugging.md`
- Release steps → `docs/workflows.md` / `docs/post-deploy-checklist.md`
- Behavioral rules → `docs/agent-behavior.md`

### Session Reflection

Before ending the session, answer these questions:

1. **Did the debugging protocol (Observe → Hypothesize → Verify → Plan → Implement) get followed?** If not, what was skipped and why?
2. **Were there any "shotgun debugging" moments?** (Making changes without verified understanding)
3. **Did any behavioral rule get violated?** If so, does `docs/agent-behavior.md` need a new rule?
4. **Is there a pattern here that will recur?** If so, write a rule to prevent it.
5. **Are all active exec plans in `docs/exec-plans/active/` still accurate?** Update or archive stale ones.

---

## Quick Reference: What to Update When

| Changed | Update these docs |
|---------|------------------|
| New module / public API | `functionality-audit.md`, `README.md` (feature list) |
| New extra in `pyproject.toml` | `README.md` install matrix, `docs/testing.md` if relevant |
| New test file | `testing.md` (counts), CLAUDE.md (build status), `README.md` (test count) |
| New backend (vLLM/llama.cpp/etc.) | `design-docs/` (DD), functionality audit, README features |
| Bug fix | `debugging.md` (decision record, if you keep one), `ERRATA.md` (if severe) |
| Release shipped | CLAUDE.md (version), `README.md` (version + features), move exec plan to `completed/` |
| New env var | `dev-environment.md`, `pyproject.toml` if relevant |

---

## Debugging-Specific Addendum

### Local Tests ≠ Released Wheel ≠ End-User Environment

**This cannot be overstated:**

| What local tests prove | What local tests DO NOT prove |
|------------------------|-------------------------------|
| Code logic is correct | The wheel installs cleanly |
| Public API contracts work in-tree | Data files made it into the wheel |
| Tests pass against the source tree | Extras correctly gate optional imports |
| Imports resolve in the dev venv | The CLI entry-point got registered |
| Mocked backends behave correctly | Real backend (vLLM, llama.cpp, HF Hub) work end-to-end |

**Local tests use:**
- Editable installs (`pip install -e .`) — bypasses wheel building
- Possibly mocked model backends — no real inference cost
- The dev venv's already-present dependencies — no clean-install verification

**The gap between "tests pass" and "users can install and use it" is packaging + distribution.** After every release that introduces new modules, extras, data files, or model dependencies, you MUST install the published artifact in a clean venv and exercise the public API.

---

## Appendix: Release Timing

| Artifact | Trigger | Typical time | How to check |
|----------|---------|-------------|--------------|
| PyPI wheel | `twine upload dist/*` (manual) or release CI | Seconds–minutes | `pip index versions telegrapher` |
| HF Hub model | `huggingface-cli upload` or model push | Minutes (depends on weight size) | HF Hub model page version field |
| GitHub release | Push tag → release CI | Minutes | GitHub Releases page |

**Important:** PyPI does not allow re-uploading the same version. If a release is broken, bump the patch version and re-release. Yanking the bad version is OK to prevent further installs but does not let you rewrite it.
