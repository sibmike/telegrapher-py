"""Smoke tests: package imports cleanly and exposes its declared public API."""
from __future__ import annotations

import pytest


def test_package_imports() -> None:
    import telegrapher

    assert telegrapher.__version__
    assert hasattr(telegrapher, "Telegrapher")


def test_telegrapher_constructor_accepts_default() -> None:
    from telegrapher import Telegrapher

    Telegrapher()  # default constructor must succeed without arguments


def test_telegrapher_rejects_mixed_model_args() -> None:
    from telegrapher import Telegrapher

    with pytest.raises(ValueError):
        Telegrapher(model="org/te-bidi", model_in="org/te-compress", model_out="org/te-expand")


def test_telegrapher_rejects_partial_unidirectional_args() -> None:
    from telegrapher import Telegrapher

    with pytest.raises(ValueError):
        Telegrapher(model_in="org/te-compress")  # missing model_out
    with pytest.raises(ValueError):
        Telegrapher(model_out="org/te-expand")  # missing model_in


def test_compress_not_yet_implemented() -> None:
    from telegrapher import Telegrapher

    tg = Telegrapher()
    with pytest.raises(NotImplementedError):
        tg.compress("hello")


def test_cli_entrypoint_registered() -> None:
    from telegrapher.cli import app

    assert app is not None
    assert callable(app)
