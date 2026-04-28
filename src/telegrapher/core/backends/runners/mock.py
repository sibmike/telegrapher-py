"""Deterministic test runner.

`MockRunner` returns canned responses keyed by an exact-match prompt mapping,
or falls back to a stable default. It records every call so tests can assert
direction routing, cache hits, and same-model sharing.
"""
from __future__ import annotations

from collections.abc import Iterator


class MockRunner:
    """In-memory runner for tests. Implements the `Runner` protocol structurally."""

    def __init__(
        self,
        responses: dict[str, str] | None = None,
        *,
        default: str = "",
        identity: str = "mock",
    ) -> None:
        """
        Args:
            responses: Exact prompt → reply mapping. Keys must match the prompt
                emitted by `LocalBackend` for the test to be deterministic.
            default: Returned when no exact match is found.
            identity: Marker stored on the instance — useful for asserting
                "same instance" in same-model-sharing tests.
        """
        self._responses = dict(responses or {})
        self._default = default
        self.identity = identity
        self.calls: list[str] = []

    def generate(self, prompt: str, *, max_tokens: int = 2048) -> str:
        self.calls.append(prompt)
        return self._responses.get(prompt, self._default)

    def stream(self, prompt: str, *, max_tokens: int = 2048) -> Iterator[str]:
        # Simulate streaming by yielding one line at a time.
        text = self.generate(prompt, max_tokens=max_tokens)
        yield from text.splitlines(keepends=True)

    def close(self) -> None:
        return None
