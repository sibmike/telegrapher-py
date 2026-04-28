"""Phase 2 tests: real Telegrapher class behavior — caching, level validation,
direction routing through the backend, streaming."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from telegrapher import Telegrapher
from telegrapher.core.backends.local import LocalBackend
from telegrapher.core.backends.runners.mock import MockRunner


def _make_tg(
    tmp_path: Path,
    *,
    compressor: MockRunner | None = None,
    expander: MockRunner | None = None,
    bidi: MockRunner | None = None,
) -> tuple[Telegrapher, MockRunner, MockRunner]:
    """Build a Telegrapher with explicit MockRunners and a temp cache dir.

    Returns (telegrapher, compressor_runner, expander_runner). When `bidi` is
    given both runners point at the same instance.
    """
    if bidi is not None:
        c = e = bidi
    else:
        c = compressor or MockRunner(default="TE_OUT", identity="c")
        e = expander or MockRunner(default="NL_OUT", identity="e")

    tg = Telegrapher.__new__(Telegrapher)
    tg._backend = LocalBackend.from_runners(compressor=c, expander=e)
    from telegrapher.core.cache import DiskCache

    tg._cache_compress = DiskCache(
        root=tmp_path, namespace="compress", model_revision="test"
    )
    tg._cache_expand = DiskCache(
        root=tmp_path, namespace="expand", model_revision="test"
    )
    return tg, c, e


def test_compress_returns_backend_output(tmp_path: Path) -> None:
    tg, c, _ = _make_tg(tmp_path, compressor=MockRunner(default="TE_RESULT"))
    assert tg.compress("hello world", level="L3") == "TE_RESULT"
    assert len(c.calls) == 1


def test_expand_returns_backend_output(tmp_path: Path) -> None:
    tg, _, e = _make_tg(tmp_path, expander=MockRunner(default="NL_RESULT"))
    assert tg.expand("SOME-TE") == "NL_RESULT"
    assert len(e.calls) == 1


def test_compress_caches_result(tmp_path: Path) -> None:
    """Second call with same (text, level) hits cache — backend not called twice."""
    tg, c, _ = _make_tg(tmp_path, compressor=MockRunner(default="X"))
    tg.compress("same input", level="L3")
    tg.compress("same input", level="L3")
    assert len(c.calls) == 1  # cached on second call


def test_compress_different_level_misses_cache(tmp_path: Path) -> None:
    tg, c, _ = _make_tg(tmp_path, compressor=MockRunner(default="X"))
    tg.compress("input", level="L1")
    tg.compress("input", level="L3")
    assert len(c.calls) == 2  # different level → different cache key


def test_expand_caches_result(tmp_path: Path) -> None:
    tg, _, e = _make_tg(tmp_path, expander=MockRunner(default="NL"))
    tg.expand("TE")
    tg.expand("TE")
    assert len(e.calls) == 1


def test_compress_invalid_level_raises(tmp_path: Path) -> None:
    tg, _, _ = _make_tg(tmp_path)
    with pytest.raises(ValueError):
        tg.compress("anything", level="L99")


def test_compress_stream_invalid_level_raises(tmp_path: Path) -> None:
    tg, _, _ = _make_tg(tmp_path)
    with pytest.raises(ValueError):
        list(tg.compress_stream("x", level="bogus"))


def test_compress_stream_yields_complete_lines(tmp_path: Path) -> None:
    class CharStreamRunner(MockRunner):
        def stream(self, prompt, *, max_tokens=2048):  # type: ignore[override]
            text = self.generate(prompt, max_tokens=max_tokens)
            yield from text

    runner = CharStreamRunner(default="A\nB\nC")
    tg, _, _ = _make_tg(tmp_path, compressor=runner, expander=runner)
    chunks = list(tg.compress_stream("anything", level="L3"))
    assert chunks == ["A\n", "B\n", "C"]


def test_compress_stream_does_not_populate_cache(tmp_path: Path) -> None:
    """Streaming bypasses cache by design — see Telegrapher.compress_stream docstring."""
    tg, c, _ = _make_tg(tmp_path, compressor=MockRunner(default="STREAMED"))
    list(tg.compress_stream("input", level="L3"))
    # A subsequent non-streaming compress must still hit the backend.
    tg.compress("input", level="L3")
    assert len(c.calls) == 2


def test_ratio_uses_tiktoken(tmp_path: Path) -> None:
    """`Telegrapher.ratio` is a thin wrapper around `core.metrics.ratio`."""
    tg, _, _ = _make_tg(tmp_path)
    # tiktoken cl100k_base: a long sentence vs. its compressed tag count
    long_nl = (
        "According to research by Johnson and colleagues (2023), the application "
        "of machine learning techniques to medical diagnostics resulted in a "
        "27.5% increase in early detection rates."
    )
    short_te = "ML→MEDICAL: EARLY-DETECTION+27.5% [JOHNSON:2023]"
    r = tg.ratio(long_nl, short_te)
    assert r > 1.0  # original is longer than TE in tokens


def test_telegrapher_close_calls_backend_close(tmp_path: Path) -> None:
    tg, c, e = _make_tg(tmp_path)
    closes: list[str] = []
    with (
        patch.object(c, "close", lambda: closes.append("c")),
        patch.object(e, "close", lambda: closes.append("e")),
    ):
        tg.close()
    assert sorted(closes) == ["c", "e"]


# -- End-to-end via real Telegrapher constructor (uses runner="mock") -------


def test_telegrapher_end_to_end_with_mock_runner_default(tmp_path: Path) -> None:
    """Construct via the public API and exercise both directions."""
    tg = Telegrapher(runner="mock", cache_dir=tmp_path)
    assert tg.compress("hello", level="L3") == ""  # MockRunner's default default is ""
    assert tg.expand("SOME-TE") == ""


def test_telegrapher_two_models_same_string_share_backend(tmp_path: Path) -> None:
    """Per DD-001: model_in == model_out must share one Runner instance."""
    tg = Telegrapher(model_in="org/X", model_out="org/X", runner="mock", cache_dir=tmp_path)
    assert isinstance(tg._backend, LocalBackend)
    assert tg._backend.shares_runner is True


def test_telegrapher_two_distinct_models_do_not_share_backend(tmp_path: Path) -> None:
    tg = Telegrapher(model_in="org/A", model_out="org/B", runner="mock", cache_dir=tmp_path)
    assert isinstance(tg._backend, LocalBackend)
    assert tg._backend.shares_runner is False
