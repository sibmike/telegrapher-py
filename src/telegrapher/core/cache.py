"""Content-addressed disk cache for compress/expand results.

Cache keys are sha256 hashes of `(model_revision, namespace, level, input)`.
Switching models invalidates everything; switching levels invalidates the
relevant subset; identical inputs round-trip from disk on the second call.

Storage layout (under the configured cache root):

    compress/<sha256>.txt
    expand/<sha256>.txt

Files are plain UTF-8 text. No metadata sidecars in v0.1 — the hash
captures all the keying we need.
"""
from __future__ import annotations

import hashlib
from pathlib import Path


class DiskCache:
    """Per-namespace disk-backed cache (compress and expand share the API)."""

    def __init__(
        self,
        *,
        root: Path,
        namespace: str,
        model_revision: str,
    ) -> None:
        """
        Args:
            root: Cache root directory (already resolved by `config.cache_dir`).
            namespace: "compress" or "expand". Each gets its own subdirectory.
            model_revision: Identifier that changes when the underlying model
                changes. For v0.1 with stub HF Hub paths this is the model
                identifier itself; once real revisions land it should be the
                model's commit SHA.
        """
        self._namespace = namespace
        self._model_revision = model_revision
        self._dir = root / namespace
        self._dir.mkdir(parents=True, exist_ok=True)

    def _key(self, *, text: str, level: str | None) -> str:
        h = hashlib.sha256()
        h.update(self._model_revision.encode("utf-8"))
        h.update(b"\x1f")
        h.update(self._namespace.encode("utf-8"))
        h.update(b"\x1f")
        h.update((level or "").encode("utf-8"))
        h.update(b"\x1f")
        h.update(text.encode("utf-8"))
        return h.hexdigest()

    def _path(self, key: str) -> Path:
        return self._dir / f"{key}.txt"

    def get(self, *, text: str, level: str | None = None) -> str | None:
        """Return the cached value or `None` if absent."""
        path = self._path(self._key(text=text, level=level))
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    def put(self, *, text: str, value: str, level: str | None = None) -> None:
        """Write `value` to the cache. Overwrites any prior entry."""
        path = self._path(self._key(text=text, level=level))
        # Atomic-ish write: stage to .tmp then rename.
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(value, encoding="utf-8")
        tmp.replace(path)
