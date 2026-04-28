"""Corpus-level fidelity validation.

`validate()` walks a list of documents (or a directory), compresses each at
the configured level, optionally expands back to NL for a round-trip token
check, and aggregates the result into an `EvalReport`.

QA-fidelity (asking the model the same question against original vs. TE
forms and comparing answers) is intentionally out of scope for v0.1 — it
requires a separate evaluator LLM beyond the compressor/expander.
"""
from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from telegrapher import Telegrapher
from telegrapher.core.metrics import count_tokens
from telegrapher.eval.report import DocumentReport, EvalReport

# File extensions treated as text corpus members when a directory is passed.
_CORPUS_EXTENSIONS = frozenset({".txt", ".md", ".markdown"})


def _resolve_documents(source: Iterable[str | Path] | str | Path) -> list[Path]:
    """Expand a directory or iterable of paths into a flat list of file paths."""
    if isinstance(source, (str, Path)):
        path = Path(source)
        if path.is_dir():
            return sorted(
                p
                for p in path.iterdir()
                if p.is_file() and p.suffix.lower() in _CORPUS_EXTENSIONS
            )
        if path.is_file():
            return [path]
        raise FileNotFoundError(f"No such corpus path: {path}")
    return [Path(p) for p in source]


def validate(
    source: Iterable[str | Path] | str | Path,
    *,
    level: str = "L3",
    telegrapher: Telegrapher | None = None,
    expand_check: bool = True,
    report: Path | None = None,
) -> EvalReport:
    """Evaluate compression on a corpus and return an `EvalReport`.

    Args:
        source: A directory of `.txt` / `.md` files, a single file, or an
            iterable of paths.
        level: Compression level (`L1` / `L3` / `L5`).
        telegrapher: A `Telegrapher` instance. Required because v0.1 has no
            real default model — auto-pick raises `InstallError` until
            Phase 6.
        expand_check: When True (default), each compressed document is also
            expanded back to NL and the recovered token count is recorded.
            Set False to skip expansion (faster).
        report: If provided, also write a Markdown report to this path.
    """
    if telegrapher is None:
        # The caller would otherwise hit `InstallError` deep in the stack.
        # Surface the requirement up front with a clearer message.
        raise ValueError(
            "validate() needs an explicit `telegrapher=Telegrapher(...)` instance "
            "in v0.1. Auto-pick of a default Telegrapher requires real model "
            "weights, which arrive in Phase 6."
        )

    paths = _resolve_documents(source)
    documents: list[DocumentReport] = []

    for path in paths:
        original = path.read_text(encoding="utf-8")
        if not original.strip():
            continue  # skip empty files
        te = telegrapher.compress(original, level=level)
        original_tokens = count_tokens(original)
        te_tokens = count_tokens(te)
        ratio = original_tokens / te_tokens if te_tokens else 1.0

        expanded_tokens: int | None = None
        expanded_ratio: float | None = None
        if expand_check:
            expanded = telegrapher.expand(te)
            expanded_tokens = count_tokens(expanded)
            if expanded_tokens:
                expanded_ratio = original_tokens / expanded_tokens

        documents.append(
            DocumentReport(
                name=path.name,
                original_tokens=original_tokens,
                te_tokens=te_tokens,
                ratio=ratio,
                expanded_tokens=expanded_tokens,
                expanded_ratio=expanded_ratio,
            )
        )

    eval_report = EvalReport(documents=documents, level=level)

    if report is not None:
        eval_report.write_markdown(report)

    return eval_report
