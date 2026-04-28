"""Typer CLI entry point.

Implementation arrives in Phase 3 of the v0.1 exec plan. This stub registers
the `tg` command so `pip install -e .` works and `tg --help` returns
something useful.
"""
from __future__ import annotations

import typer

from telegrapher._version import __version__

app = typer.Typer(
    name="tg",
    help="Telegrapher CLI — compress, expand, and evaluate Telegraph English.",
    no_args_is_help=True,
)


@app.callback()
def _main(
    version: bool = typer.Option(
        False, "--version", help="Print version and exit.", is_eager=True
    ),
) -> None:
    if version:
        typer.echo(__version__)
        raise typer.Exit()


@app.command()
def compress(
    path: str = typer.Argument(..., help="Path to a text file to compress."),
    level: str = typer.Option("L3", "--level", "-l", help="Compression level: L1/L3/L5."),
    output: str | None = typer.Option(None, "--output", "-o", help="Output path."),
) -> None:
    """Compress a text file into Telegraph English."""
    raise typer.Exit(code=2)  # NotImplementedError surfaced as a clean exit


@app.command()
def expand(
    path: str = typer.Argument(..., help="Path to a Telegraph English file."),
    output: str | None = typer.Option(None, "--output", "-o", help="Output path."),
) -> None:
    """Expand Telegraph English back into natural language."""
    raise typer.Exit(code=2)


@app.command()
def eval(
    corpus: str = typer.Argument(..., help="Path to a corpus directory."),
    report: str = typer.Option("report.md", "--report", help="Output report path."),
    level: str = typer.Option("L3", "--level", "-l"),
) -> None:
    """Validate compression fidelity and ratio on a user-supplied corpus."""
    raise typer.Exit(code=2)


@app.command(name="download-model")
def download_model(
    to: str | None = typer.Option(None, "--to", help="Override download directory."),
) -> None:
    """Download the default model weights from Hugging Face Hub to the local cache."""
    raise typer.Exit(code=2)
