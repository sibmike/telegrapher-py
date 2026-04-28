"""Token-count metrics for measuring compression ratio.

Uses tiktoken's `cl100k_base` encoding — the same encoding used in the v0.8
benchmark paper, so reported ratios stay comparable across studies. Users who
want the SLM's native tokenizer can wrap their own metric; for v0.1 we expose
only the canonical (paper-aligned) tiktoken-based ratio.
"""
from __future__ import annotations

from functools import lru_cache

import tiktoken

# Match the paper's methodology. Updating this would invalidate
# cross-version ratio comparisons, so changes need explicit decision-record
# coverage in the design docs.
_ENCODING_NAME = "cl100k_base"


@lru_cache(maxsize=1)
def _encoder() -> tiktoken.Encoding:
    """Return the cached tiktoken encoder. Loading is non-trivial; cache it."""
    return tiktoken.get_encoding(_ENCODING_NAME)


def count_tokens(text: str) -> int:
    """Return the number of tiktoken `cl100k_base` tokens in `text`."""
    return len(_encoder().encode(text))


def ratio(original: str, te: str) -> float:
    """Return the compression ratio: token-count(original) / token-count(te).

    A ratio of 2.0 means the TE form is half as many tokens as the original.
    `te` must not be empty (raises `ValueError` to surface the bug rather
    than silently returning `inf`).
    """
    te_tokens = count_tokens(te)
    if te_tokens == 0:
        raise ValueError("Cannot compute ratio: TE text is empty (zero tokens).")
    return count_tokens(original) / te_tokens
