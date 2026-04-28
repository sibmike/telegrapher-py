"""Phase 1 tests: Backend ABC, MockRunner, LocalBackend, factory."""
from __future__ import annotations

import pytest

from telegrapher.core.backends import Backend, InstallError, LocalBackend, get_backend
from telegrapher.core.backends.local import (
    _build_compress_prompt,
    _build_expand_prompt,
)
from telegrapher.core.backends.runners.mock import MockRunner

# -- Backend ABC ----------------------------------------------------------


def test_backend_abc_not_instantiable() -> None:
    with pytest.raises(TypeError):
        Backend()  # type: ignore[abstract]


# -- MockRunner -----------------------------------------------------------


def test_mock_runner_returns_canned_responses() -> None:
    runner = MockRunner({"hello": "world"}, default="???")
    assert runner.generate("hello") == "world"
    assert runner.generate("unknown") == "???"
    assert runner.calls == ["hello", "unknown"]


def test_mock_runner_streams_complete_lines() -> None:
    runner = MockRunner(default="line1\nline2\nline3")
    chunks = list(runner.stream("anything"))
    # Each chunk preserves the trailing newline where present
    assert "".join(chunks) == "line1\nline2\nline3"


# -- LocalBackend direction routing ---------------------------------------


def test_local_backend_routes_compress_to_compressor() -> None:
    compressor = MockRunner(default="TE_OUTPUT", identity="c")
    expander = MockRunner(default="NL_OUTPUT", identity="e")
    backend = LocalBackend.from_runners(compressor=compressor, expander=expander)

    assert backend.compress("hello world", level="L3") == "TE_OUTPUT"
    assert len(compressor.calls) == 1
    assert len(expander.calls) == 0
    assert _build_compress_prompt("hello world", level="L3") == compressor.calls[0]


def test_local_backend_routes_expand_to_expander() -> None:
    compressor = MockRunner(default="TE_OUTPUT", identity="c")
    expander = MockRunner(default="NL_OUTPUT", identity="e")
    backend = LocalBackend.from_runners(compressor=compressor, expander=expander)

    assert backend.expand("SOME-TE") == "NL_OUTPUT"
    assert len(compressor.calls) == 0
    assert len(expander.calls) == 1
    assert _build_expand_prompt("SOME-TE") == expander.calls[0]


def test_local_backend_bidi_shares_runner() -> None:
    bidi = MockRunner(default="OUTPUT", identity="bidi")
    backend = LocalBackend.from_runners(bidi=bidi)

    assert backend.shares_runner is True
    backend.compress("x", level="L3")
    backend.expand("y")
    assert len(bidi.calls) == 2  # both directions hit the same runner


def test_local_backend_two_runners_do_not_share() -> None:
    compressor = MockRunner(default="C")
    expander = MockRunner(default="E")
    backend = LocalBackend.from_runners(compressor=compressor, expander=expander)
    assert backend.shares_runner is False


def test_local_backend_rejects_mixed_constructor_args() -> None:
    bidi = MockRunner()
    with pytest.raises(ValueError):
        LocalBackend.from_runners(bidi=bidi, compressor=MockRunner())


def test_local_backend_rejects_partial_two_runner_args() -> None:
    with pytest.raises(ValueError):
        LocalBackend.from_runners(compressor=MockRunner())  # missing expander
    with pytest.raises(ValueError):
        LocalBackend.from_runners(expander=MockRunner())  # missing compressor


def test_local_backend_close_calls_runner_close_once_when_shared() -> None:
    closes: list[str] = []

    class TrackingRunner(MockRunner):
        def close(self) -> None:
            closes.append(self.identity)

    bidi = TrackingRunner(identity="shared")
    LocalBackend.from_runners(bidi=bidi).close()
    assert closes == ["shared"]


def test_local_backend_close_calls_both_runners_when_distinct() -> None:
    closes: list[str] = []

    class TrackingRunner(MockRunner):
        def close(self) -> None:
            closes.append(self.identity)

    c = TrackingRunner(identity="c")
    e = TrackingRunner(identity="e")
    LocalBackend.from_runners(compressor=c, expander=e).close()
    assert sorted(closes) == ["c", "e"]


# -- LocalBackend streaming -----------------------------------------------


def test_stream_compress_yields_complete_lines() -> None:
    # Runner that streams character-by-character so we can verify line buffering.
    class CharStreamRunner(MockRunner):
        def stream(self, prompt, *, max_tokens=2048):  # type: ignore[override]
            text = self.generate(prompt, max_tokens=max_tokens)
            yield from text

    runner = CharStreamRunner(default="LINE-A\nLINE-B\nLINE-C")
    backend = LocalBackend.from_runners(bidi=runner)

    chunks = list(backend.stream_compress("anything", level="L3"))
    assert chunks == ["LINE-A\n", "LINE-B\n", "LINE-C"]


# -- Factory --------------------------------------------------------------


def test_get_backend_with_mock_runner_returns_local_backend() -> None:
    backend = get_backend(model="org/te-bidi", runner="mock")
    assert isinstance(backend, LocalBackend)
    assert backend.shares_runner is True


def test_get_backend_two_models_same_string_shares() -> None:
    backend = get_backend(model_in="org/X", model_out="org/X", runner="mock")
    assert isinstance(backend, LocalBackend)
    assert backend.shares_runner is True


def test_get_backend_two_models_different_strings_do_not_share() -> None:
    backend = get_backend(model_in="org/A", model_out="org/B", runner="mock")
    assert isinstance(backend, LocalBackend)
    assert backend.shares_runner is False


def test_get_backend_default_uses_default_model() -> None:
    backend = get_backend(runner="mock")
    assert isinstance(backend, LocalBackend)
    assert backend.shares_runner is True


def test_get_backend_rejects_mixed_args() -> None:
    with pytest.raises(ValueError):
        get_backend(model="org/X", model_in="org/A", model_out="org/B", runner="mock")


def test_get_backend_rejects_partial_unidirectional_args() -> None:
    with pytest.raises(ValueError):
        get_backend(model_in="org/A", runner="mock")
    with pytest.raises(ValueError):
        get_backend(model_out="org/B", runner="mock")


def test_get_backend_unknown_runner_raises() -> None:
    with pytest.raises(ValueError):
        get_backend(runner="notarunner")


def test_get_backend_real_runners_raise_install_error() -> None:
    with pytest.raises(InstallError):
        get_backend(runner="vllm")
    with pytest.raises(InstallError):
        get_backend(runner="llama-cpp")


def test_get_backend_auto_pick_with_no_runners_raises_install_error() -> None:
    # Phase 1: neither real runner is implemented yet, so auto-pick should
    # raise a helpful InstallError.
    with pytest.raises(InstallError):
        get_backend()  # no runner override
