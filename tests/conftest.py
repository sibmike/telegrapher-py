"""Shared pytest fixtures."""
from __future__ import annotations

import pytest


@pytest.fixture
def sample_nl() -> str:
    """A short natural-language passage useful as a round-trip fixture."""
    return (
        "According to research by Johnson and colleagues (2023), the application "
        "of machine learning techniques to medical diagnostics resulted in a "
        "27.5% increase in early detection rates while simultaneously reducing "
        "false positives by approximately 12% compared to traditional methods."
    )


@pytest.fixture
def sample_te() -> str:
    """The hand-curated TE form of `sample_nl` (target for compression tests)."""
    return (
        "MACHINE-LEARNING→MEDICAL-DIAGNOSTICS: EARLY-DETECTION+27.5% "
        "∧ FALSE-POSITIVE-12% [JOHNSON:2023]"
    )
