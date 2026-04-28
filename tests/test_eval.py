"""Phase 5 tests: validate() + EvalReport + Markdown report writer."""
from __future__ import annotations

from pathlib import Path

import pytest

from telegrapher import Telegrapher
from telegrapher.eval import DocumentReport, EvalReport, validate


@pytest.fixture
def tg(tmp_path: Path) -> Telegrapher:
    """Real Telegrapher backed by a MockRunner that always shrinks input by ~half."""
    from telegrapher.core.backends.local import LocalBackend
    from telegrapher.core.backends.runners.mock import MockRunner
    from telegrapher.core.cache import DiskCache

    class HalvingRunner(MockRunner):
        """Compress halves the input length; expand returns it (close to) original."""

        def generate(self, prompt: str, *, max_tokens: int = 2048) -> str:
            self.calls.append(prompt)
            if prompt.startswith("<TE_COMPRESS"):
                body = prompt.split("\n", 1)[1].rsplit("</TE_COMPRESS>", 1)[0].strip()
                return body[: max(1, len(body) // 2)]
            if prompt.startswith("<TE_EXPAND"):
                body = prompt.split("\n", 1)[1].rsplit("</TE_EXPAND>", 1)[0].strip()
                return body + " " + body  # double the TE back out
            return ""

    runner = HalvingRunner()
    t = Telegrapher.__new__(Telegrapher)
    t._backend = LocalBackend.from_runners(bidi=runner)
    t._cache_compress = DiskCache(root=tmp_path, namespace="compress", model_revision="t")
    t._cache_expand = DiskCache(root=tmp_path, namespace="expand", model_revision="t")
    return t


@pytest.fixture
def corpus(tmp_path: Path) -> Path:
    """Build a 3-document corpus with mixed extensions and one empty file."""
    d = tmp_path / "corpus"
    d.mkdir()
    (d / "a.txt").write_text("alpha " * 200, encoding="utf-8")
    (d / "b.md").write_text("beta " * 100, encoding="utf-8")
    (d / "c.markdown").write_text("gamma " * 50, encoding="utf-8")
    (d / "empty.txt").write_text("", encoding="utf-8")
    (d / "ignore.json").write_text('{"unrelated": true}', encoding="utf-8")
    return d


# -- validate ----------------------------------------------------------------


def test_validate_directory_processes_text_files(tg: Telegrapher, corpus: Path) -> None:
    report = validate(corpus, level="L3", telegrapher=tg)
    names = {d.name for d in report.documents}
    assert names == {"a.txt", "b.md", "c.markdown"}  # empty file skipped, json ignored


def test_validate_aggregate_ratio_above_one(tg: Telegrapher, corpus: Path) -> None:
    report = validate(corpus, level="L3", telegrapher=tg)
    assert report.aggregate_ratio > 1.0


def test_validate_per_document_metrics_populated(tg: Telegrapher, corpus: Path) -> None:
    report = validate(corpus, level="L3", telegrapher=tg)
    for doc in report.documents:
        assert doc.original_tokens > 0
        assert doc.te_tokens > 0
        assert doc.ratio > 1.0
        assert doc.expanded_tokens is not None
        assert doc.expanded_ratio is not None


def test_validate_no_expand_skips_expansion(tg: Telegrapher, corpus: Path) -> None:
    report = validate(corpus, level="L3", telegrapher=tg, expand_check=False)
    for doc in report.documents:
        assert doc.expanded_tokens is None
        assert doc.expanded_ratio is None
    assert report.aggregate_expanded_ratio is None


def test_validate_single_file(tg: Telegrapher, corpus: Path) -> None:
    report = validate(corpus / "a.txt", level="L3", telegrapher=tg)
    assert len(report.documents) == 1
    assert report.documents[0].name == "a.txt"


def test_validate_iterable_of_paths(tg: Telegrapher, corpus: Path) -> None:
    report = validate(
        [corpus / "a.txt", corpus / "b.md"], level="L3", telegrapher=tg
    )
    assert {d.name for d in report.documents} == {"a.txt", "b.md"}


def test_validate_missing_path_raises(tg: Telegrapher, tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        validate(tmp_path / "nothing", level="L3", telegrapher=tg)


def test_validate_requires_telegrapher(corpus: Path) -> None:
    with pytest.raises(ValueError):
        validate(corpus, level="L3")  # no telegrapher=


def test_validate_invalid_level_raises(tg: Telegrapher, corpus: Path) -> None:
    with pytest.raises(ValueError):
        validate(corpus, level="L99", telegrapher=tg)


def test_validate_writes_markdown_report(
    tg: Telegrapher, corpus: Path, tmp_path: Path
) -> None:
    report_path = tmp_path / "report.md"
    validate(corpus, level="L3", telegrapher=tg, report=report_path)
    assert report_path.exists()
    text = report_path.read_text(encoding="utf-8")
    assert "Telegrapher Evaluation Report" in text
    assert "Aggregate compression ratio" in text
    assert "a.txt" in text


# -- EvalReport --------------------------------------------------------------


def test_eval_report_aggregate_ratio_one_when_empty() -> None:
    assert EvalReport().aggregate_ratio == 1.0


def test_eval_report_aggregate_expanded_ratio_none_when_no_expansion() -> None:
    docs = [
        DocumentReport(name="x", original_tokens=10, te_tokens=5, ratio=2.0)
    ]
    assert EvalReport(documents=docs).aggregate_expanded_ratio is None


def test_eval_report_aggregate_expanded_ratio_computed() -> None:
    docs = [
        DocumentReport(
            name="x",
            original_tokens=20,
            te_tokens=5,
            ratio=4.0,
            expanded_tokens=10,
            expanded_ratio=2.0,
        ),
        DocumentReport(
            name="y",
            original_tokens=10,
            te_tokens=2,
            ratio=5.0,
            expanded_tokens=5,
            expanded_ratio=2.0,
        ),
    ]
    r = EvalReport(documents=docs)
    assert r.aggregate_expanded_ratio == pytest.approx((20 + 10) / (10 + 5))


def test_write_markdown_handles_no_expand(tmp_path: Path) -> None:
    report_path = tmp_path / "r.md"
    EvalReport(
        documents=[DocumentReport(name="x", original_tokens=10, te_tokens=5, ratio=2.0)],
        level="L3",
    ).write_markdown(report_path)
    text = report_path.read_text(encoding="utf-8")
    assert "—" in text  # placeholder for missing expand columns
