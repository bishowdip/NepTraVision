"""Inter-annotator agreement on a double-annotated subset.

Reviewers will ask how consistent the labels are. We report two numbers on the
QC subset: (1) mean IoU over geometrically matched boxes, and (2) class-label
agreement among matched boxes. Boxes are matched greedily by IoU above a threshold
(default 0.5), the same matching used for detection metrics.

Pure geometry over YOLO boxes — no third-party deps, fully unit-tested.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..data.convert import YoloBox, parse_label_file
from ..logging_utils import get_logger

log = get_logger(__name__)


def iou_xywh_normalised(a: YoloBox, b: YoloBox) -> float:
    """IoU between two YOLO boxes (normalised centre-x/y/w/h, same image)."""
    ax1, ay1 = a.cx - a.w / 2, a.cy - a.h / 2
    ax2, ay2 = a.cx + a.w / 2, a.cy + a.h / 2
    bx1, by1 = b.cx - b.w / 2, b.cy - b.h / 2
    bx2, by2 = b.cx + b.w / 2, b.cy + b.h / 2

    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    if inter <= 0:
        return 0.0
    union = a.w * a.h + b.w * b.h - inter
    return inter / union if union > 0 else 0.0


def _greedy_match(
    boxes_a: list[YoloBox], boxes_b: list[YoloBox], iou_thr: float
) -> list[tuple[int, int, float]]:
    """Greedily match boxes by descending IoU; return (i, j, iou) for matches."""
    candidates = [
        (iou_xywh_normalised(a, b), i, j)
        for i, a in enumerate(boxes_a)
        for j, b in enumerate(boxes_b)
    ]
    candidates.sort(reverse=True)
    used_a: set[int] = set()
    used_b: set[int] = set()
    matches: list[tuple[int, int, float]] = []
    for iou, i, j in candidates:
        if iou < iou_thr:
            break
        if i in used_a or j in used_b:
            continue
        used_a.add(i)
        used_b.add(j)
        matches.append((i, j, iou))
    return matches


@dataclass
class AgreementResult:
    n_images: int = 0
    n_matched: int = 0
    n_unmatched_a: int = 0
    n_unmatched_b: int = 0
    mean_iou: float = 0.0
    class_agreement: float = 0.0

    def summary(self) -> str:
        return (
            f"{self.n_images} images | matched {self.n_matched} "
            f"(unmatched A={self.n_unmatched_a}, B={self.n_unmatched_b}) | "
            f"mean IoU={self.mean_iou:.3f} | class agreement={self.class_agreement:.3f}"
        )


def compute_agreement(
    labels_a: Path, labels_b: Path, *, iou_thr: float = 0.5
) -> AgreementResult:
    """Compare two annotators' YOLO label directories over their shared images."""
    stems_a = {p.stem for p in labels_a.glob("*.txt")}
    stems_b = {p.stem for p in labels_b.glob("*.txt")}
    shared = sorted(stems_a & stems_b)

    result = AgreementResult(n_images=len(shared))
    iou_sum = 0.0
    class_match = 0
    for stem in shared:
        boxes_a = parse_label_file(labels_a / f"{stem}.txt")
        boxes_b = parse_label_file(labels_b / f"{stem}.txt")
        matches = _greedy_match(boxes_a, boxes_b, iou_thr)
        result.n_matched += len(matches)
        result.n_unmatched_a += len(boxes_a) - len(matches)
        result.n_unmatched_b += len(boxes_b) - len(matches)
        for i, j, iou in matches:
            iou_sum += iou
            if boxes_a[i].cls == boxes_b[j].cls:
                class_match += 1

    if result.n_matched:
        result.mean_iou = iou_sum / result.n_matched
        result.class_agreement = class_match / result.n_matched

    log.info(result.summary())
    return result
