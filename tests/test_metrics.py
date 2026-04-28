"""Phase 2 tests: tiktoken-based token counting and ratio."""
from __future__ import annotations

import pytest

from telegrapher.core.metrics import count_tokens, ratio


def test_count_tokens_nonempty() -> None:
    assert count_tokens("hello world") > 0


def test_count_tokens_empty_is_zero() -> None:
    assert count_tokens("") == 0


def test_ratio_greater_than_one_when_te_is_shorter() -> None:
    long_nl = (
        "According to research by Johnson and colleagues (2023), the application "
        "of machine learning techniques to medical diagnostics resulted in a "
        "27.5% increase in early detection rates."
    )
    short_te = "ML→MEDICAL: EARLY-DETECTION+27.5% [JOHNSON:2023]"
    assert ratio(long_nl, short_te) > 1.0


def test_ratio_equals_one_when_inputs_match() -> None:
    s = "identical text"
    assert ratio(s, s) == pytest.approx(1.0)


def test_ratio_raises_on_empty_te() -> None:
    with pytest.raises(ValueError):
        ratio("nonempty", "")


def test_count_tokens_matches_known_values() -> None:
    """Sanity-check against tiktoken's documented behavior for cl100k_base."""
    # "hello world" in cl100k_base is 2 tokens. If this changes, our paper
    # comparison numbers shift — flag loudly.
    assert count_tokens("hello world") == 2
