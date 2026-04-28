"""Smoke tests: package imports cleanly and exposes its declared public API."""
from __future__ import annotations

import pytest


def test_package_imports() -> None:
    import telegrapher

    assert telegrapher.__version__
    assert hasattr(telegrapher, "Telegrapher")


def test_telegrapher_constructs_with_mock_runner() -> None:
    from telegrapher import Telegrapher

    Telegrapher(runner="mock")  # mock runner is bundled with core; always works


def test_telegrapher_default_runner_raises_until_real_runners_implemented() -> None:
    """Phase 1 contract: without an extras-provided runner installed,
    constructing without `runner="mock"` raises a helpful InstallError."""
    from telegrapher import Telegrapher
    from telegrapher.core.backends import InstallError

    with pytest.raises(InstallError):
        Telegrapher()  # auto-pick fails until vLLM / llama-cpp are wired in Phase 6


def test_telegrapher_rejects_mixed_model_args() -> None:
    from telegrapher import Telegrapher

    with pytest.raises(ValueError):
        Telegrapher(
            model="org/te-bidi",
            model_in="org/te-compress",
            model_out="org/te-expand",
            runner="mock",
        )


def test_telegrapher_rejects_partial_unidirectional_args() -> None:
    from telegrapher import Telegrapher

    with pytest.raises(ValueError):
        Telegrapher(model_in="org/te-compress", runner="mock")  # missing model_out
    with pytest.raises(ValueError):
        Telegrapher(model_out="org/te-expand", runner="mock")  # missing model_in


def test_cli_entrypoint_registered() -> None:
    from telegrapher.cli import app

    assert app is not None
    assert callable(app)
