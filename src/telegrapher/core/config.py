"""Package-level configuration: defaults, cache directory, model identifiers.

Runtime settings (compression level, override paths) live on call signatures,
not here. This module only contains values that are truly process-wide.
"""
from __future__ import annotations

import os
from pathlib import Path

import platformdirs

# Stub HF Hub identifier — replaced with the production model name before the
# first PyPI release. Tests must never depend on this string resolving to real
# weights; they use `MockRunner` instead.
DEFAULT_MODEL: str = "telegrapher-ai/te-bidi-9b"

# Directional model stubs (when the user wants two unidirectional models without
# specifying explicit names). These are equally placeholder.
DEFAULT_MODEL_IN: str = "telegrapher-ai/te-compressor-9b"
DEFAULT_MODEL_OUT: str = "telegrapher-ai/te-expander-9b"


def cache_dir(override: str | os.PathLike[str] | None = None) -> Path:
    """Return the directory where telegrapher stores caches and downloaded weights.

    Resolution order:
    1. Explicit `override` argument (used by tests and CLI flags).
    2. `TELEGRAPHER_CACHE_DIR` environment variable.
    3. `platformdirs` user cache (`~/.cache/telegrapher` on Linux,
       `~/Library/Caches/telegrapher` on macOS, `%LOCALAPPDATA%\\telegrapher\\Cache`
       on Windows).
    """
    if override is not None:
        return Path(override).expanduser().resolve()
    env = os.environ.get("TELEGRAPHER_CACHE_DIR")
    if env:
        return Path(env).expanduser().resolve()
    return Path(platformdirs.user_cache_dir(appname="telegrapher", appauthor=False))


VALID_LEVELS: frozenset[str] = frozenset({"L1", "L3", "L5"})


def validate_level(level: str) -> str:
    """Raise `ValueError` if `level` is not one of the documented values."""
    if level not in VALID_LEVELS:
        raise ValueError(
            f"Invalid compression level {level!r}. Use one of {sorted(VALID_LEVELS)}."
        )
    return level
