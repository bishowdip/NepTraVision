"""Qualitative + quantitative failure-mode aggregation for the discussion section.

Detection errors fall into a small set of buckets the paper discusses: missed
small two-wheelers, occlusion failures, class confusions (bus↔truck,
tempo↔car), and night/monsoon degradation. This module classifies a model's
predictions-vs-ground-truth into those buckets so the discussion is backed by counts,
not anecdote.

The matching core (greedy IoU, error categorisation) is pure and testable; loading a
model's predictions on the test set is the caller's job (it produces the lists this
module consumes).
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from ..annotation.agreement import _greedy_match
from ..data.convert import YoloBox


@dataclass
class ErrorBuckets:
    missed: Counter            # ground-truth boxes with no matching prediction, by class
    false_positive: Counter    # predictions with no matching ground truth, by class
    misclassified: Counter     # matched geometry but wrong class, by (true→pred)

    def as_dict(self) -> dict:
        return {
            "missed": dict(self.missed),
            "false_positive": dict(self.false_positive),
            "misclassified": {f"{t}->{p}": n for (t, p), n in self.misclassified.items()},
        }


def categorise_errors(
    ground_truth: list[YoloBox],
    predictions: list[YoloBox],
    class_names: dict[int, str],
    *,
    iou_thr: float = 0.5,
) -> ErrorBuckets:
    """Bucket one image's errors into missed / false-positive / misclassified.

    Geometry is matched greedily by IoU (the same routine used for annotator
    agreement, keeping "match" defined identically everywhere). A matched pair with
    differing class is a misclassification; unmatched GT is a miss; unmatched
    prediction is a false positive.
    """
    matches = _greedy_match(ground_truth, predictions, iou_thr)
    matched_gt = {i for i, _, _ in matches}
    matched_pred = {j for _, j, _ in matches}

    missed: Counter = Counter()
    false_positive: Counter = Counter()
    misclassified: Counter = Counter()

    def name(cls: int) -> str:
        return class_names.get(cls, f"id:{cls}")

    for i, gt in enumerate(ground_truth):
        if i not in matched_gt:
            missed[name(gt.cls)] += 1
    for j, pred in enumerate(predictions):
        if j not in matched_pred:
            false_positive[name(pred.cls)] += 1
    for i, j, _ in matches:
        if ground_truth[i].cls != predictions[j].cls:
            misclassified[(name(ground_truth[i].cls), name(predictions[j].cls))] += 1

    return ErrorBuckets(missed, false_positive, misclassified)
