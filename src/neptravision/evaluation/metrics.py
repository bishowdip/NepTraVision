"""Accuracy metrics (E1) — mAP, precision/recall/F1, per-class AP, confusion matrix.

For YOLO models we delegate the heavy lifting to Ultralytics' validated mAP
implementation (re-implementing COCO mAP correctly is a trap), then normalise its
output into our own small, framework-independent :class:`AccuracyMetrics` so the rest
of the pipeline — tables, Pareto plots, aggregation over seeds — never depends on
Ultralytics' object shapes.

Requires the ``train`` extra (Ultralytics) for the YOLO path.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

from ..logging_utils import get_logger

log = get_logger(__name__)


@dataclass
class AccuracyMetrics:
    model: str
    map50: float = 0.0
    map50_95: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0
    per_class_ap: dict[str, float] = field(default_factory=dict)

    def as_row(self) -> dict:
        row = asdict(self)
        row.pop("per_class_ap")
        return row


def f1_from_pr(precision: float, recall: float) -> float:
    """Harmonic mean of precision and recall (0 if both are 0)."""
    denom = precision + recall
    return 2 * precision * recall / denom if denom > 0 else 0.0


def evaluate_ultralytics(
    weights: Path,
    data_yaml: Path,
    *,
    model_name: str,
    split: str = "test",
    imgsz: int = 640,
) -> AccuracyMetrics:
    """Run Ultralytics validation on a split and normalise into AccuracyMetrics."""
    try:
        from ultralytics import YOLO
    except ImportError as exc:  # pragma: no cover - optional extra
        raise RuntimeError('ultralytics not installed. pip install -e ".[train]"') from exc

    model = YOLO(str(weights))
    res = model.val(data=str(data_yaml), split=split, imgsz=imgsz, verbose=False)

    box = res.box
    precision = float(box.mp)   # mean precision
    recall = float(box.mr)      # mean recall
    per_class = {
        res.names[i]: float(ap)
        for i, ap in zip(getattr(box, "ap_class_index", []), getattr(box, "ap50", []), strict=False)
    }
    metrics = AccuracyMetrics(
        model=model_name,
        map50=float(box.map50),
        map50_95=float(box.map),
        precision=precision,
        recall=recall,
        f1=f1_from_pr(precision, recall),
        per_class_ap=per_class,
    )
    log.info(
        "[%s] mAP50=%.3f mAP50-95=%.3f P=%.3f R=%.3f F1=%.3f",
        model_name, metrics.map50, metrics.map50_95,
        metrics.precision, metrics.recall, metrics.f1,
    )
    return metrics


def aggregate_over_seeds(runs: list[AccuracyMetrics]) -> dict[str, tuple[float, float]]:
    """Mean ± std of headline metrics across seeds (the benchmark reporting unit)."""
    import statistics

    fields = ["map50", "map50_95", "precision", "recall", "f1"]
    out: dict[str, tuple[float, float]] = {}
    for f in fields:
        values = [getattr(r, f) for r in runs]
        mean = statistics.fmean(values)
        std = statistics.pstdev(values) if len(values) > 1 else 0.0
        out[f] = (round(mean, 4), round(std, 4))
    return out
