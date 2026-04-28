"""Public `Telegrapher` facade.

Wires user-supplied model arguments through `get_backend(...)` to a `Backend`
instance, layers the disk cache on top of `compress` / `expand`, and routes
`ratio(...)` to the metrics module.
"""
from __future__ import annotations

import os
from collections.abc import Iterator

from telegrapher.core.backends import Backend, get_backend
from telegrapher.core.cache import DiskCache
from telegrapher.core.config import (
    DEFAULT_MODEL,
    validate_level,
)
from telegrapher.core.config import (
    cache_dir as resolve_cache_dir,
)
from telegrapher.core.metrics import ratio as _ratio_metric


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
        runner: str | None = None,
        cache_dir: str | os.PathLike[str] | None = None,
    ) -> None:
        # `get_backend` validates the model-args contract. We re-invoke its
        # rules here only for the construction-time error to mention the
        # public-facing names; backend factory's checks are the source of truth.
        self._backend: Backend = get_backend(
            model=model,
            model_in=model_in,
            model_out=model_out,
            runner=runner,
        )

        revision = _model_revision(model=model, model_in=model_in, model_out=model_out)
        root = resolve_cache_dir(cache_dir)
        self._cache_compress = DiskCache(root=root, namespace="compress", model_revision=revision)
        self._cache_expand = DiskCache(root=root, namespace="expand", model_revision=revision)

    def compress(self, text: str, *, level: str = "L3") -> str:
        """Compress natural-language `text` into Telegraph English at `level`."""
        validate_level(level)
        cached = self._cache_compress.get(text=text, level=level)
        if cached is not None:
            return cached
        result = self._backend.compress(text, level=level)
        self._cache_compress.put(text=text, value=result, level=level)
        return result

    def expand(self, te: str) -> str:
        """Expand Telegraph English `te` back into natural language."""
        cached = self._cache_expand.get(text=te)
        if cached is not None:
            return cached
        result = self._backend.expand(te)
        self._cache_expand.put(text=te, value=result)
        return result

    def ratio(self, original: str, te: str) -> float:
        """Token-count ratio: tokens(original) / tokens(te)."""
        return _ratio_metric(original, te)

    def compress_stream(self, text: str, *, level: str = "L3") -> Iterator[str]:
        """Yield TE atomic lines as the model emits them.

        Streaming bypasses the cache by design — caching streamed output
        without materialising it would defeat the purpose. Users who want
        a cached round-trip should call `compress(...)` instead.
        """
        validate_level(level)
        return self._backend.stream_compress(text, level=level)

    def close(self) -> None:
        """Release backend resources (model weights, GPU memory)."""
        self._backend.close()


def _model_revision(
    *,
    model: str | None,
    model_in: str | None,
    model_out: str | None,
) -> str:
    """Build the cache-keying revision string from the user's model args.

    For v0.1 with stub HF Hub paths the revision *is* the identifier (so a
    user who flips from one model name to another sees a fresh cache). When
    real model commits are wired up in Phase 6, this should fold in the
    `huggingface_hub.snapshot_download` revision SHA so weight updates also
    invalidate the cache.
    """
    if model is not None:
        return model
    if model_in is not None and model_out is not None:
        if model_in == model_out:
            return model_in
        return f"{model_in}::{model_out}"
    return DEFAULT_MODEL
