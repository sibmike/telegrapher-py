# Core Beliefs

> Engineering values and judgment heuristics that guide decision-making when no specific rule applies.
> These are team principles, not implementation details. They change rarely.

**When to update this file:** Only when the team's fundamental engineering philosophy changes. Adding a new belief requires explicit discussion. Never add more than ~15 beliefs -- if the list grows too long, it stops being useful.

---

## Beliefs

### Architecture

1. **Simple, modular, purpose-fit storage.** Pick the simplest store that fits each piece of state. Compression artifacts and expansion caches are content-addressed files on disk. Memory state is the application's own data structure, not a database. Each store is used for what it does best. Do not over-engineer.

2. **Validate data at boundaries, not in the middle.** Parse and validate at the public API surface and at I/O edges (model output, file ingest, network calls). Interior code trusts validated types. No redundant validation in business logic.

3. **Prefer shared utilities over hand-rolled helpers.** Centralize invariants in one place. When you see two implementations of the same logic, extract to a shared module. DRY is a core value.

4. **Favor boring technology.** Composable, stable APIs with broad documentation are easier for both humans and agents to work with. Choose well-known libraries over exotic alternatives. When an external library's behavior is opaque, consider reimplementing the needed subset with full test coverage.

5. **Layered architecture with strict dependency direction.** Higher-level modules depend on lower-level ones, never the reverse. Concrete backends (vLLM, llama.cpp, OpenAI) sit behind a `Backend` ABC; everything else depends on the interface. Cross-cutting concerns enter through explicit providers.

### Code Quality

6. **Explicit over clever.** No metaprogramming, no dynamic imports, no magic that requires deep context to understand. If a human or agent reading the code needs to "just know" something to understand it, that's a failure.

7. **Engineered enough -- not under, not over.** No premature abstraction, no unnecessary complexity. But also no fragile hacks. Find the balance: handle the edge cases you can foresee, don't build for edge cases you're imagining.

8. **Handle more edge cases, not fewer.** Thoughtfulness over speed. When in doubt, handle the error case. An unhandled error in production is worse than a slightly longer implementation.

### Testing

9. **Well-tested code is non-negotiable.** Every public API surface has a corresponding test. Every new feature ships with tests. 80% line coverage minimum, critical paths at 100%.

10. **Tests are documentation.** Test names should describe the behavior being verified, not the implementation. A failing test should tell you what broke without reading the test code.

11. **Test at the right level.** Unit tests for business logic. Integration tests for API endpoints. E2E tests for critical user journeys. Don't test implementation details.

### Process

12. **Agent failures are harness bugs.** When the agent makes a mistake, the first question is: "What was missing from the harness?" -- not "Why is the model bad?" Fix the environment, not the symptom.

13. **Capture judgment once, enforce continuously.** Human taste and decisions should be encoded into docs, lints, or tests. Don't rely on remembering to tell the agent the same thing next session.

14. **Corrections are cheap, waiting is expensive.** Bias toward shipping and fixing over blocking and debating. But never compromise on data integrity or security -- those corrections are not cheap.

### Discipline

15. **Simplicity first.** Make every change as simple as possible. Impact minimal code. Don't add features, refactor code, or make "improvements" beyond what was asked. A bug fix doesn't need surrounding code cleaned up. A simple feature doesn't need extra configurability.

16. **Minimal blast radius.** Changes should only touch what's necessary. Avoid introducing bugs by keeping the scope tight. No temporary fixes — find root causes. Senior developer standards apply to every commit.
