"""Result-table I/O and aggregation — the CSVs the paper's tables are built from.

Plain CSV over list-of-dict rows (no pandas needed), so it is trivially testable and the
files are diff-friendly in git. Accuracy is aggregated over seeds into mean ± std, the
benchmark's reporting unit.
"""

from __future__ import annotations

import csv
import statistics
from pathlib import Path

from ..evaluation.metrics import AccuracyMetrics

# Columns of the headline accuracy table (one row per model, aggregated over seeds).
ACCURACY_AGG_FIELDS = [
    "experiment", "model", "n_seeds",
    "map50_mean", "map50_std",
    "map50_95_mean", "map50_95_std",
    "precision_mean", "recall_mean", "f1_mean",
    "params_m", "simulated",
]


def write_table(rows: list[dict], path: Path, fieldnames: list[str] | None = None) -> Path:
    """Write list-of-dict ``rows`` to ``path`` as CSV. Field order from the first row
    unless ``fieldnames`` is given."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return path
    fields = fieldnames or list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def read_table(path: Path) -> list[dict]:
    """Read a CSV result table back into list-of-dict rows."""
    if not path.is_file():
        raise FileNotFoundError(f"Result table not found: {path}")
    with path.open("r", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def aggregate_accuracy(
    experiment: str,
    model: str,
    runs: list[AccuracyMetrics],
    *,
    params_m: float = 0.0,
    simulated: bool = False,
) -> dict:
    """Collapse a model's per-seed :class:`AccuracyMetrics` into one mean ± std row."""

    def mean_std(values: list[float]) -> tuple[float, float]:
        mean = statistics.fmean(values)
        std = statistics.pstdev(values) if len(values) > 1 else 0.0
        return round(mean, 4), round(std, 4)

    map50_m, map50_s = mean_std([r.map50 for r in runs])
    map95_m, map95_s = mean_std([r.map50_95 for r in runs])
    prec_m, _ = mean_std([r.precision for r in runs])
    rec_m, _ = mean_std([r.recall for r in runs])
    f1_m, _ = mean_std([r.f1 for r in runs])

    return {
        "experiment": experiment,
        "model": model,
        "n_seeds": len(runs),
        "map50_mean": map50_m,
        "map50_std": map50_s,
        "map50_95_mean": map95_m,
        "map50_95_std": map95_s,
        "precision_mean": prec_m,
        "recall_mean": rec_m,
        "f1_mean": f1_m,
        "params_m": params_m,
        "simulated": str(simulated).lower(),
    }


def accuracy_raw_row(
    experiment: str, model: str, seed: int, m: AccuracyMetrics, *, simulated: bool
) -> dict:
    """One un-aggregated (model, seed) accuracy row, for the audit trail."""
    return {
        "experiment": experiment,
        "model": model,
        "seed": seed,
        **m.as_row(),
        "simulated": str(simulated).lower(),
    }


def to_markdown(rows: list[dict], columns: list[str]) -> str:
    """Render rows as a GitHub-flavoured Markdown table (for console / paper drafts)."""
    if not rows:
        return "(no rows)"
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join("---" for _ in columns) + " |"
    body = [
        "| " + " | ".join(str(row.get(c, "")) for c in columns) + " |"
        for row in rows
    ]
    return "\n".join([header, sep, *body])
