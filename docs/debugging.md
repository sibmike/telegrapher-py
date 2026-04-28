# Debugging Protocol

> Systematic methodology for diagnosing and fixing bugs. Debugging is feature engineering — it requires the same rigor as building new features: research, hypothesize, verify, then act.

**When to update this file:** After a debugging session reveals a new anti-pattern, after a misdiagnosis causes a regression, or when a new environment (e.g., new release target) is added.

---

## 1. Core Principle

**Debugging is NOT trial-and-error.** It is a systematic process of narrowing the problem space until the root cause is identified with certainty, then applying the minimum change to fix it.

**The cardinal sin:** Making changes to a working system without understanding the system. Every "quick fix" that isn't grounded in verified understanding risks creating a new, worse problem.

---

## 2. The Protocol (follow in order)

### Phase 1: Observe — Gather Evidence (NO code changes)

1. **Reproduce the exact error.** Get the exact error message, stack trace, exit status, or unexpected output.
2. **Identify the boundary.** Where does the error originate? Public API surface? Backend logic? I/O? Network? Model load?
3. **Read the logs.** All of them. stdout, stderr, log files, model server logs, dependency logs.
4. **Check what changed.** `git log` — what was the last working commit? What changed since then?
5. **Verify the environment.** Are env vars set? Are the right Python version and dependencies installed? Is the model file present? Is the cache populated correctly?

**Output of Phase 1:** A written statement: "The error is [X], occurring at [layer], caused by [evidence suggests Y]."

### Phase 2: Hypothesize — Form a Theory (NO code changes)

1. **List all possible causes.** Don't stop at the first plausible explanation.
2. **Rank by likelihood.** Use evidence from Phase 1 to rank, not gut feeling.
3. **Identify what would confirm or refute each hypothesis.** What log line, env var value, or function output would prove it?
4. **Design a verification test for the top hypothesis.** A read-only check — NOT a code change.

**Output of Phase 2:** "My top hypothesis is [X]. I can verify it by checking [Y]. If confirmed, the fix is [Z]."

### Phase 3: Verify — Confirm the Hypothesis (NO code changes)

1. **Run the verification test.** Check the env var, read the log, inspect the value, query the system.
2. **If confirmed:** Proceed to Phase 4.
3. **If refuted:** Return to Phase 2 with the next hypothesis. Do NOT start making changes.

**Output of Phase 3:** "Hypothesis confirmed/refuted. Evidence: [specific data point]."

### Phase 4: Plan the Fix (NO code changes yet)

1. **Identify the minimum change** that fixes the root cause.
2. **Assess blast radius.** What else does this change affect? Other entry points? Other features? Public API?
3. **Check for side effects.** Will this fix break something else? Read the code that depends on what you're changing.
4. **Decide: code change vs. config change vs. dependency change.** Don't change code when the problem is config.
5. **If the fix touches packaging or the release pipeline:** Verify the fix in a non-production context first if at all possible.

**Output of Phase 4:** "The fix is [specific change] to [specific file/config]. Blast radius: [what else is affected]. Verification: [how to confirm it worked]."

### Phase 5: Implement and Verify

1. **Make the single, planned change.** Nothing extra. No "while I'm here" improvements.
2. **Run tests locally.** All of them.
3. **Verify the fix addresses the original error.** Not "it compiles" — the original reproduction case must pass.
4. **Commit with a clear message** explaining the root cause and why this change fixes it.

---

## 3. Anti-Patterns (mistakes to never repeat)

### 3.1 "Shotgun Debugging" — Making changes without understanding

**The pattern:** Adding a setting, flag, or workaround based on a general assumption about what a platform "requires," without verifying it actually does. Often happens when reading partial documentation and pattern-matching to a half-remembered example.

**Rule:** NEVER change working code based on assumptions about what a platform "requires." If the code was working before, the platform config was fine. The problem is elsewhere.

### 3.2 "Fix Forward" into Production

**The pattern:** Each "fix" gets pushed directly to the release/deploy target with no way to verify the change worked before it goes out. Multiple broken releases follow.

**Rule:** Verify fixes before publishing. If the change is config/packaging, exercise it in a fresh venv first. If the change is code, run the test suite AND reason about whether the change affects the release pipeline.

### 3.3 Conflating Multiple Problems

**The pattern:** Two separate issues exist: (1) something is broken, (2) something else is fine. The agent treats them as one problem and makes a change that breaks the working part while trying to fix the non-working part.

**Rule:** Isolate problems. Fix one thing at a time. Verify each fix independently. Never make a change that could affect a working system while debugging an unrelated issue.

### 3.4 Assuming Code Is the Problem When It's Config

**The pattern:** Code works locally, fails after release. Agent makes code changes (adding guards, changing fallbacks, modifying error messages) instead of solving the real config/packaging issue.

**Rule:** If the code works locally but not after install/release, the problem is almost certainly configuration or packaging, not code. Diagnose the config issue first. Code changes should be the last resort, not the first.

### 3.5 Hiding Real Errors Behind Generic Messages

**The pattern:** A broad `except` block or string-match condition maps the real error to a generic user-facing message — making the bug appear to be one thing when it's actually another.

**Rule:** Always log the real error. Display specific error messages to the developer/console. Generic user-facing messages are fine, but NEVER suppress the actual error in logs.

### 3.6 Treating Surface Errors as Root Cause

**The pattern:** An error at one layer is actually a symptom of a deeper failure. The visible symptom (e.g., a timeout, a CORS error, a "module not found", a malformed response) gets debugged for hours while the underlying cause (e.g., the backend crashed before sending headers, the model never loaded, a dependency was excluded by the wheel build) goes unexamined.

**Rule:** When the visible error doesn't quite make sense, look one layer deeper. Read the lower-level logs. The visible message is often what happens *after* the real failure.

### 3.7 Trusting Local Tests to Prove Release Health

**The pattern:** All tests pass locally. The released wheel doesn't work because of packaging metadata, missing data files, dependency pins, or platform-specific build issues — invisible to in-tree tests.

**Rule:** Local tests prove **code logic**, not **release health**. After publishing a wheel or pushing a model, install it from scratch in a clean venv and exercise the public API. See [post-deploy-checklist.md](./post-deploy-checklist.md) for the full procedure.
