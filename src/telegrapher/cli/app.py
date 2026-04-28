"""Typer CLI: `tg compress | expand | download-model | eval`.

Exit code policy (per PS-001):
    0  Success
    1  User error (missing file, invalid level, missing extras)
    2  Unexpected internal error
"""
from __future__ import annotations

import sys
from pathlib import Path

import typer

from telegrapher._version import __version__
from telegrapher.core.backends import InstallError
from telegrapher.core.config import DEFAULT_MODEL
from telegrapher.core.config import cache_dir as resolve_cache_dir

app = typer.Typer(
    name="tg",
    help="Telegrapher CLI — compress, expand, and evaluate Telegraph English.",
    invoke_without_command=True,
)

# Shared option type aliases — keep the per-command signatures readable.
LevelOpt = typer.Option("L3", "--level", "-l", help="Compression level: L1 / L3 / L5.")
OutputOpt = typer.Option(None, "--output", "-o", help="Output file path (default: stdout).")
RunnerOpt = typer.Option(
    None,
    "--runner",
    help="Override runner: 'vllm' | 'llama-cpp' | 'mock'. Auto-picks if omitted.",
    hidden=False,
)


@app.callback()
def _main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False, "--version", help="Print version and exit.", is_eager=True
    ),
) -> None:
    if version:
        typer.echo(__version__)
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


def _build_telegrapher(*, runner: str | None):  # type: ignore[no-untyped-def]
    """Instantiate Telegrapher, mapping `InstallError` to a clean exit-1.

    Importing `Telegrapher` lazily keeps `tg --version` and `tg --help`
    fast — no model layer touched unless an actual command runs.
    """
    from telegrapher import Telegrapher

    try:
        return Telegrapher(runner=runner)
    except InstallError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc


def _read_input(path: Path) -> str:
    if not path.exists():
        typer.echo(f"Error: input file not found: {path}", err=True)
        raise typer.Exit(code=1)
    return path.read_text(encoding="utf-8")


def _write_output(text: str, output: Path | None) -> None:
    if output is None:
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")


@app.command()
def compress(
    path: Path = typer.Argument(..., help="Path to a text file to compress."),
    level: str = LevelOpt,
    output: Path | None = OutputOpt,
    runner: str | None = RunnerOpt,
) -> None:
    """Compress a natural-language text file into Telegraph English."""
    text = _read_input(path)
    tg = _build_telegrapher(runner=runner)
    try:
        te = tg.compress(text, level=level)
    except ValueError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    _write_output(te, output)


@app.command()
def expand(
    path: Path = typer.Argument(..., help="Path to a Telegraph English file."),
    output: Path | None = OutputOpt,
    runner: str | None = RunnerOpt,
) -> None:
    """Expand Telegraph English back into natural language."""
    te = _read_input(path)
    tg = _build_telegrapher(runner=runner)
    nl = tg.expand(te)
    _write_output(nl, output)


@app.command(name="download-model")
def download_model(
    repo_id: str = typer.Option(
        DEFAULT_MODEL,
        "--repo-id",
        help="Hugging Face Hub repo id. Defaults to the package's default model.",
    ),
    to: Path | None = typer.Option(
        None,
        "--to",
        help="Override download directory. Defaults to the package cache.",
    ),
) -> None:
    """Download model weights from Hugging Face Hub into the local cache."""
    target = to if to is not None else resolve_cache_dir() / "models"
    target.mkdir(parents=True, exist_ok=True)
    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:  # pragma: no cover — declared in core deps
        typer.echo(
            "Error: huggingface_hub is required for `tg download-model`.",
            err=True,
        )
        raise typer.Exit(code=1) from exc

    try:
        path = snapshot_download(repo_id=repo_id, local_dir=str(target))
    except Exception as exc:  # noqa: BLE001 — surface any HF failure cleanly
        typer.echo(f"Error: failed to download {repo_id}: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"Model downloaded to: {path}")


@app.command(name="eval")
def eval_cmd(  # name="eval" but function is `eval_cmd` to avoid shadowing builtin
    corpus: Path = typer.Argument(..., help="Path to a corpus directory or file."),
    report: Path = typer.Option(Path("report.md"), "--report", help="Output report path."),
    level: str = LevelOpt,
    runner: str | None = RunnerOpt,
    no_expand: bool = typer.Option(
        False,
        "--no-expand",
        help="Skip the expand-back-to-NL check (faster, omits expanded ratio).",
    ),
) -> None:
    """Validate compression fidelity and ratio on a user-supplied corpus."""
    if not corpus.exists():
        typer.echo(f"Error: corpus path not found: {corpus}", err=True)
        raise typer.Exit(code=1)

    tg = _build_telegrapher(runner=runner)

    from telegrapher.eval import validate

    eval_report = validate(
        corpus,
        level=level,
        telegrapher=tg,
        expand_check=not no_expand,
        report=report,
    )

    typer.echo(
        f"Evaluated {len(eval_report.documents)} document(s) at {level}; "
        f"aggregate ratio {eval_report.aggregate_ratio:.2f}×. "
        f"Report written to {report}."
    )
