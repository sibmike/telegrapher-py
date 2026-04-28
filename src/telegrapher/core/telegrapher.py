"""Public `Telegrapher` facade.

Implementation arrives in Phase 2 of the v0.1 exec plan. This stub exists so
the package imports cleanly and downstream modules can reference the type.
"""
from __future__ import annotations

from collections.abc import Iterator


class Telegrapher:
    """Bidirectional Natural Language ↔ Telegraph English compression.

    The constructor is mutually-exclusive between two model configurations:

    - `model="hf-org/te-bidi"`: one bidirectional model used for both directions.
    - `model_in=..., model_out=...`: two unidirectional models, one per direction.

    Passing both forms together raises `ValueError`. Passing neither uses the
    package default (also a stub HF Hub path until fine-tuning is finalized).

    All HF Hub paths in this version are placeholders — they will be replaced
    with the production identifiers before the first PyPI release.
    """

    def __init__(
        self,
        *,
        model: str | None = None,
        model_in: str | None = None,
        model_out: str | None = None,
    ) -> None:
        if model is not None and (model_in is not None or model_out is not None):
            raise ValueError(
                "`model` and `model_in`/`model_out` are mutually exclusive. "
                "Pass either one bidirectional model or two unidirectional models."
            )
        if (model_in is None) != (model_out is None):
            raise ValueError(
                "When using two unidirectional models, both `model_in` and "
                "`model_out` must be provided."
            )
        self._model = model
        self._model_in = model_in
        self._model_out = model_out

    def compress(self, text: str, *, level: str = "L3") -> str:
        """Compress natural-language `text` into Telegraph English at `level`."""
        raise NotImplementedError("Phase 2 — core compress/expand")

    def expand(self, te: str) -> str:
        """Expand Telegraph English `te` back into natural language."""
        raise NotImplementedError("Phase 2 — core compress/expand")

    def ratio(self, original: str, te: str) -> float:
        """Return the token-count compression ratio (original / te)."""
        raise NotImplementedError("Phase 2 — core compress/expand")

    def compress_stream(
        self, text: str, *, level: str = "L3"
    ) -> Iterator[str]:
        """Yield TE atomic lines as the model emits them."""
        raise NotImplementedError("Phase 2 — core compress/expand")
