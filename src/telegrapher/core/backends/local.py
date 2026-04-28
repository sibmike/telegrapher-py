"""LocalBackend — the v0.1 default backend.

Owns one or two `Runner` handles and routes `compress`/`expand` to the
correct one. Same-string `model_in == model_out` shares a single Runner
instance so callers don't pay double memory.

The TE-level → prompt-template translation lives here, not inside runners.
Runners stay direction-agnostic (per DD-001).
"""
from __future__ import annotations

from collections.abc import Iterator

from telegrapher.core.backends.base import Backend, Runner


def _build_compress_prompt(text: str, *, level: str) -> str:
    """Build the prompt the model sees for natural language → TE.

    Phase 1: a placeholder template. Will be replaced in Phase 6 with the
    fine-tuned model's expected prompt format. Stable string so MockRunner
    response keys are predictable in tests.
    """
    return f"<TE_COMPRESS level={level}>\n{text}\n</TE_COMPRESS>"


def _build_expand_prompt(te: str) -> str:
    """Build the prompt the model sees for TE → natural language."""
    return f"<TE_EXPAND>\n{te}\n</TE_EXPAND>"


class LocalBackend(Backend):
    """Backend that runs compression locally via one or two Runners.

    The two runner handles `_compressor` and `_expander` may be the same
    instance (one bidirectional model) or two different instances (two
    unidirectional models). All direction routing is done here so that
    higher layers never check which mode is active.
    """

    def __init__(self, *, compressor: Runner, expander: Runner) -> None:
        self._compressor = compressor
        self._expander = expander

    @classmethod
    def from_runners(
        cls,
        *,
        bidi: Runner | None = None,
        compressor: Runner | None = None,
        expander: Runner | None = None,
    ) -> LocalBackend:
        """Construct a LocalBackend from runner instances.

        Either `bidi` (one runner used both ways) or both `compressor` and
        `expander` must be provided. Mutually exclusive.
        """
        if bidi is not None and (compressor is not None or expander is not None):
            raise ValueError(
                "`bidi` and `compressor`/`expander` are mutually exclusive."
            )
        if bidi is not None:
            return cls(compressor=bidi, expander=bidi)
        if compressor is None or expander is None:
            raise ValueError(
                "When using two runners, both `compressor` and `expander` are required."
            )
        return cls(compressor=compressor, expander=expander)

    @property
    def shares_runner(self) -> bool:
        """True iff one runner instance serves both directions."""
        return self._compressor is self._expander

    def compress(self, text: str, *, level: str) -> str:
        prompt = _build_compress_prompt(text, level=level)
        return self._compressor.generate(prompt)

    def expand(self, te: str) -> str:
        prompt = _build_expand_prompt(te)
        return self._expander.generate(prompt)

    def stream_compress(self, text: str, *, level: str) -> Iterator[str]:
        prompt = _build_compress_prompt(text, level=level)
        # Buffer until we hit a newline so callers always see complete lines.
        buffer = ""
        for chunk in self._compressor.stream(prompt):
            buffer += chunk
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                yield line + "\n"
        if buffer:
            yield buffer

    def close(self) -> None:
        self._compressor.close()
        if not self.shares_runner:
            self._expander.close()
