"""Data types for `validate()` results and the Markdown report writer."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class DocumentReport:
    """Per-document evaluation result."""

    name: str
    original_tokens: int
    te_tokens: int
    ratio: float
    expanded_tokens: int | None = None
    expanded_ratio: float | None = None  # original_tokens / expanded_tokens


@dataclass
class EvalReport:
    """Aggregate evaluation result for a corpus.

    Carries per-document metrics plus a corpus-level summary. v0.1 reports
    compression-ratio and round-trip token-level recovery only — full QA
    fidelity belongs to a later phase that pulls in an external evaluator
    LLM.
    """

    documents: list[DocumentReport] = field(default_factory=list)
    level: str = "L3"
    model_revision: str = ""

    @property
    def aggregate_ratio(self) -> float:
        if not self.documents:
            return 1.0
        total_original = sum(d.original_tokens for d in self.documents)
        total_te = sum(d.te_tokens for d in self.documents)
        if total_te == 0:
            return 1.0
        return total_original / total_te

    @property
    def aggregate_expanded_ratio(self) -> float | None:
        eligible = [d for d in self.documents if d.expanded_tokens is not None]
        if not eligible:
            return None
        total_original = sum(d.original_tokens for d in eligible)
        total_expanded = sum(d.expanded_tokens or 0 for d in eligible)
        if total_expanded == 0:
            return None
        return total_original / total_expanded

    def write_markdown(self, path: Path) -> None:
        """Render a Markdown report and write it to `path`."""
        lines: list[str] = []
        lines.append("# Telegrapher Evaluation Report")
        lines.append("")
        lines.append(f"_Generated_: {datetime.now(tz=timezone.utc).isoformat(timespec='seconds')}")
        lines.append(f"_Level_: `{self.level}`")
        if self.model_revision:
            lines.append(f"_Model_: `{self.model_revision}`")
        lines.append("")
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **Documents**: {len(self.documents)}")
        lines.append(f"- **Aggregate compression ratio**: {self.aggregate_ratio:.2f}×")
        if self.aggregate_expanded_ratio is not None:
            lines.append(
                f"- **Aggregate expand → original ratio**: "
                f"{self.aggregate_expanded_ratio:.2f}× (≈1.0 means expand recovers original token count)"
            )
        lines.append("")
        lines.append("## Per-document")
        lines.append("")
        lines.append(
            "| Document | Original (tokens) | TE (tokens) | Ratio | Expanded (tokens) | Expanded ratio |"
        )
        lines.append("|---|---:|---:|---:|---:|---:|")
        for d in self.documents:
            expanded = "—" if d.expanded_tokens is None else str(d.expanded_tokens)
            expanded_ratio = (
                "—" if d.expanded_ratio is None else f"{d.expanded_ratio:.2f}×"
            )
            lines.append(
                f"| `{d.name}` | {d.original_tokens} | {d.te_tokens} | "
                f"{d.ratio:.2f}× | {expanded} | {expanded_ratio} |"
            )
        lines.append("")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines), encoding="utf-8")
