"""Phase 3 tests: Typer CLI commands.

Use Typer's CliRunner so tests don't spawn subprocesses. Wire the runner
through `--runner mock` everywhere — no real weights, no real downloads.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from telegrapher._version import __version__
from telegrapher.cli import app

runner = CliRunner()


# -- top-level ---------------------------------------------------------------


def test_version_flag_prints_and_exits() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_no_args_shows_help() -> None:
    result = runner.invoke(app, [])
    # Typer's no_args_is_help=True returns code 2 with help text.
    assert "compress" in result.stdout
    assert "expand" in result.stdout
    assert "eval" in result.stdout
    assert "download-model" in result.stdout


# -- compress ----------------------------------------------------------------


def test_compress_file_writes_output(tmp_path: Path) -> None:
    src = tmp_path / "input.txt"
    src.write_text("hello world", encoding="utf-8")
    out = tmp_path / "out.te"
    result = runner.invoke(
        app,
        ["compress", str(src), "--level", "L3", "-o", str(out), "--runner", "mock"],
    )
    assert result.exit_code == 0, result.stdout
    assert out.exists()
    # MockRunner default is "" — but the file should still be written.
    assert out.read_text(encoding="utf-8") == ""


def test_compress_missing_file_exits_1(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["compress", str(tmp_path / "does-not-exist.txt"), "--runner", "mock"],
    )
    assert result.exit_code == 1
    assert "not found" in result.stderr or "not found" in result.stdout


def test_compress_invalid_level_exits_1(tmp_path: Path) -> None:
    src = tmp_path / "in.txt"
    src.write_text("x", encoding="utf-8")
    result = runner.invoke(
        app,
        ["compress", str(src), "--level", "L42", "--runner", "mock"],
    )
    assert result.exit_code == 1


def test_compress_install_error_exits_1(tmp_path: Path) -> None:
    """Without --runner, auto-pick raises InstallError until Phase 6."""
    src = tmp_path / "in.txt"
    src.write_text("x", encoding="utf-8")
    result = runner.invoke(app, ["compress", str(src)])
    assert result.exit_code == 1


# -- expand ------------------------------------------------------------------


def test_expand_file_writes_output(tmp_path: Path) -> None:
    src = tmp_path / "input.te"
    src.write_text("SOME-TE", encoding="utf-8")
    out = tmp_path / "out.txt"
    result = runner.invoke(
        app, ["expand", str(src), "-o", str(out), "--runner", "mock"]
    )
    assert result.exit_code == 0
    assert out.exists()


def test_expand_stdout_when_no_output_flag(tmp_path: Path) -> None:
    src = tmp_path / "input.te"
    src.write_text("SOME-TE", encoding="utf-8")
    result = runner.invoke(app, ["expand", str(src), "--runner", "mock"])
    assert result.exit_code == 0


# -- download-model ---------------------------------------------------------


def test_download_model_invokes_huggingface_hub(tmp_path: Path) -> None:
    target = tmp_path / "weights"
    with patch("huggingface_hub.snapshot_download") as snap:
        snap.return_value = str(target)
        result = runner.invoke(
            app, ["download-model", "--repo-id", "org/te-bidi-9b", "--to", str(target)]
        )
    assert result.exit_code == 0, result.stdout
    snap.assert_called_once()
    kwargs = snap.call_args.kwargs
    assert kwargs["repo_id"] == "org/te-bidi-9b"
    assert kwargs["local_dir"] == str(target)


def test_download_model_failure_exits_1(tmp_path: Path) -> None:
    target = tmp_path / "weights"
    with patch("huggingface_hub.snapshot_download", side_effect=RuntimeError("boom")):
        result = runner.invoke(
            app, ["download-model", "--repo-id", "org/te-bidi-9b", "--to", str(target)]
        )
    assert result.exit_code == 1
    assert "boom" in result.stdout or "boom" in result.stderr


# -- eval (stub until Phase 5) ----------------------------------------------


def test_eval_command_runs_against_corpus(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "a.txt").write_text("alpha " * 100, encoding="utf-8")
    (corpus / "b.md").write_text("beta " * 50, encoding="utf-8")
    report_path = tmp_path / "report.md"

    result = runner.invoke(
        app,
        [
            "eval",
            str(corpus),
            "--report",
            str(report_path),
            "--level",
            "L3",
            "--runner",
            "mock",
        ],
    )
    assert result.exit_code == 0, result.stdout
    assert report_path.exists()
    assert "Telegrapher Evaluation Report" in report_path.read_text(encoding="utf-8")


def test_eval_command_missing_corpus_exits_1(tmp_path: Path) -> None:
    result = runner.invoke(
        app, ["eval", str(tmp_path / "missing"), "--runner", "mock"]
    )
    assert result.exit_code == 1


def test_eval_command_no_expand_flag(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "a.txt").write_text("alpha " * 50, encoding="utf-8")
    report_path = tmp_path / "report.md"
    result = runner.invoke(
        app,
        [
            "eval",
            str(corpus),
            "--report",
            str(report_path),
            "--no-expand",
            "--runner",
            "mock",
        ],
    )
    assert result.exit_code == 0, result.stdout
    text = report_path.read_text(encoding="utf-8")
    # With --no-expand, the per-doc expanded columns are placeholders.
    assert "—" in text
