# Agent Behavior

> Working rules that govern how the AI agent operates in this repository. These are behavioral contracts — not suggestions.

**When to update this file:** After any correction from the user that reveals a missing behavioral rule, after discovering a recurring agent mistake, or when a new workflow pattern is established.

---

## 1. Workflow Orchestration

1. **Plan mode is the default.** Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions). If something goes sideways mid-implementation, STOP and re-plan immediately — don't keep pushing.
2. **Use plan mode for verification too**, not just building. Plans should include verification steps.
3. **Write detailed specs upfront** to reduce ambiguity. Vague requirements produce vague implementations.
4. **When blocked, stop and re-plan.** If a fix feels like it's getting hacky or the approach isn't working, step back: "Knowing everything I know now, what's the right approach?"

## 2. Subagent Strategy

1. **Use subagents liberally** to keep the main context window clean.
2. **Offload research, exploration, and parallel analysis** to subagents. Don't pollute main context with search results.
3. **One task per subagent** for focused execution. Don't combine unrelated searches.
4. **For complex problems**, throw more compute at it via subagents rather than guessing.

## 3. Self-Improvement Loop

1. **After ANY correction from the user:** immediately update behavior docs or ERRATA with the pattern.
2. **Write rules for yourself** that prevent the same mistake from recurring.
3. **Ruthlessly iterate** on these rules until the mistake rate drops to zero.
4. **Review lessons at session start** — read ERRATA.md and auto-memory MEMORY.md before working.
5. **After completing any exec plan:** reflect on the session and determine if behavior docs or ERRATA need surgical updates.

## 4. Verification Before Done

1. **Never mark a task complete without proving it works.** Run tests, check logs, demonstrate correctness.
2. **Diff behavior** between main and your changes when relevant.
3. **Ask yourself:** "Would a staff engineer approve this?"
4. **Run the actual test suite** before updating test counts in docs. Counts drift between sessions.
5. **For features:** acceptance criteria from the exec plan must be met. User must verify. All docs must be updated. Only THEN is it done.

## 5. Demand Elegance (Balanced)

1. **For non-trivial changes:** pause and ask "is there a more elegant way?"
2. **If a fix feels hacky:** "Knowing everything I know now, implement the elegant solution."
3. **Skip this for simple, obvious fixes** — don't over-engineer a typo fix.
4. **Challenge your own work** before presenting it to the user.

## 6. Autonomous Bug Fixing

1. **When given a bug report: just fix it.** Don't ask for hand-holding.
2. **Point at logs, errors, failing tests** — then resolve them.
3. **Zero context switching required from the user.** Go fix failing tests without being told how.
4. **Follow the debugging protocol** in [docs/debugging.md](./debugging.md) — Observe, Hypothesize, Verify, Plan, Implement. No shotgun debugging.

## 7. Task Management

1. **Plan first:** Write plan with checkable items before coding.
2. **Verify plan:** Check in with the user before starting implementation.
3. **Track progress:** Mark items complete as you go. Use TodoWrite for multi-step tasks.
4. **Explain changes:** Provide a high-level summary at each step.
5. **Document results:** Add review section when work is complete.
6. **Capture lessons:** Update behavior docs after corrections.

## 8. Core Working Principles

1. **Simplicity first.** Make every change as simple as possible. Impact minimal code.
2. **No laziness.** Find root causes. No temporary fixes. Senior developer standards.
3. **Minimal impact.** Changes should only touch what's necessary. Avoid introducing bugs.
4. **Don't add what wasn't asked for.** A bug fix doesn't need surrounding code cleaned up. A simple feature doesn't need extra configurability.

## 9. Feature Development Lifecycle

The full phase sequence lives in [harness-guidelines.md](./harness-guidelines.md) Section 3. Summary:

```
product_spec (docs/product-specs/)
  → design_doc (docs/design-docs/)
    → exec_plan in active/ (docs/exec-plans/active/)
      → [DEVELOPMENT]
        → User verifies completion + tests pass
          → UPDATE product_spec, design_doc, exec_plan to align with developed version
            → UPDATE all other docs as needed (workflows, testing, functionality-audit, etc.)
              → ONLY THEN move exec_plan to completed/ (docs/exec-plans/completed/)
```

**Critical:** The documentation update happens BEFORE the exec plan moves to completed. The exec plan is not done until docs reflect reality.

## 10. Release Planning

1. **Recursively check dependencies.** When planning a release, check what downstream artifacts are needed (PyPI metadata, HF Hub model card, extras matrix, build wheels) and sub-dependencies of those, all the way down.
2. **Always use up-to-date docs.** Check current PyPI / Hugging Face / library documentation. NEVER rely on stale knowledge for release tooling — APIs change, defaults change, behavior changes.
3. **Config problems need config fixes.** If code works locally but fails after release (install, import, model load), the problem is almost certainly packaging or environment configuration, not code. Do NOT change working code based on assumptions about what a platform "requires."

## 11. Post-Release / End-of-Session Checklist

**MANDATORY:** After EVERY release to PyPI, model push to HF Hub, or debugging session, run the [post-deploy checklist](./post-deploy-checklist.md). Key checks:

1. **Verify the release is consumable** — local tests use installed source; they DON'T prove a freshly `pip install`ed wheel works. Run `pip install telegrapher==<version>` in a clean venv and exercise the public API.
2. **Run a smoke test** — `tg compress` / `tg expand` / `tg eval` on a fixture corpus; confirm round-trip fidelity meets ship criteria.
3. **Update all affected documentation** — see checklist for the full list per change type.
4. **Add ERRATA entry** if severe mistakes were made (3+ failed fix iterations, misdiagnosis, broken release).
5. **Update auto-memory** if machine-specific pitfalls were discovered.
6. **Reflect** — was the debugging protocol followed? Were behavioral rules obeyed?

## 12. Session Start Checklist

Before doing any work in a new session, read these in order:

1. **CLAUDE.md** *(when present)* — entry point, build status, milestones, doc map
2. **docs/agent-behavior.md** — this file (working rules)
3. **docs/harness-guidelines.md** — major change process, doc architecture
4. **docs/workflows.md** — git workflow, doc maintenance
5. **docs/core-beliefs.md** — engineering values and judgment heuristics
6. **ERRATA.md** *(when present)* — mistakes to never repeat
7. **Auto-memory MEMORY.md** — machine-specific pitfalls
8. **If resuming work:** read active exec plans (`docs/exec-plans/active/`) and any in-flight design plan (`docs/plans/`)
