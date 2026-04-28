"""Phase 2 tests: DiskCache content-hash keying and model-revision invalidation."""
from __future__ import annotations

from pathlib import Path

from telegrapher.core.cache import DiskCache


def test_cache_round_trip(tmp_path: Path) -> None:
    cache = DiskCache(root=tmp_path, namespace="compress", model_revision="v1")
    assert cache.get(text="hello", level="L3") is None
    cache.put(text="hello", value="WORLD", level="L3")
    assert cache.get(text="hello", level="L3") == "WORLD"


def test_cache_keys_isolate_levels(tmp_path: Path) -> None:
    cache = DiskCache(root=tmp_path, namespace="compress", model_revision="v1")
    cache.put(text="text", value="L1_OUT", level="L1")
    cache.put(text="text", value="L3_OUT", level="L3")
    assert cache.get(text="text", level="L1") == "L1_OUT"
    assert cache.get(text="text", level="L3") == "L3_OUT"


def test_cache_keys_isolate_namespaces(tmp_path: Path) -> None:
    compress = DiskCache(root=tmp_path, namespace="compress", model_revision="v1")
    expand = DiskCache(root=tmp_path, namespace="expand", model_revision="v1")
    compress.put(text="x", value="C")
    expand.put(text="x", value="E")
    assert compress.get(text="x") == "C"
    assert expand.get(text="x") == "E"


def test_cache_invalidates_on_model_revision_change(tmp_path: Path) -> None:
    """A model upgrade must not serve stale entries."""
    old = DiskCache(root=tmp_path, namespace="compress", model_revision="v1")
    new = DiskCache(root=tmp_path, namespace="compress", model_revision="v2")
    old.put(text="hello", value="OLD_OUTPUT", level="L3")
    # New revision must miss — its key hash differs.
    assert new.get(text="hello", level="L3") is None


def test_cache_overwrite(tmp_path: Path) -> None:
    cache = DiskCache(root=tmp_path, namespace="compress", model_revision="v1")
    cache.put(text="x", value="first", level="L3")
    cache.put(text="x", value="second", level="L3")
    assert cache.get(text="x", level="L3") == "second"


def test_cache_handles_unicode(tmp_path: Path) -> None:
    cache = DiskCache(root=tmp_path, namespace="compress", model_revision="v1")
    cache.put(text="café — naïve", value="L=7\nW=4 → AREA=28 m²", level="L3")
    assert cache.get(text="café — naïve", level="L3") == "L=7\nW=4 → AREA=28 m²"


def test_cache_creates_namespace_dir(tmp_path: Path) -> None:
    DiskCache(root=tmp_path, namespace="compress", model_revision="v1")
    assert (tmp_path / "compress").is_dir()
