"""Plate-resolution sub-study (E6) — the ANPR blocker, converted into evidence.

The headline finding this produces: *"ANPR needs ≥ N px plate height; typical Nepali
CCTV gives M < N."* The method:

1. Take a set of plate crops (or whole vehicles with plate boxes).
2. Resample each plate to a sweep of target pixel heights (8, 12, …, 64).
3. Run an OCR engine at each height and measure character error rate (CER).
4. The **legibility threshold** is the smallest pixel height at which mean CER drops
   below a usable bar (default 0.20).

The pure, testable core here is the CER and the threshold search. The OCR call and
image resampling are injected/lazy so this module imports without EasyOCR/PaddleOCR.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from ..logging_utils import get_logger

log = get_logger(__name__)

# An OCR callable takes an image (resized plate crop) and returns the decoded string.
OcrFn = Callable[[object], str]


def character_error_rate(prediction: str, ground_truth: str) -> float:
    """CER = Levenshtein(pred, gt) / len(gt). 0.0 is perfect; >=1.0 is hopeless.

    Uses a standard dynamic-programming edit distance. Pure stdlib so it is unit-tested.
    """
    gt = ground_truth.strip()
    pred = prediction.strip()
    if not gt:
        return 0.0 if not pred else 1.0

    # Levenshtein distance (Wagner–Fischer), O(len(gt) * len(pred)) time, O(len(gt)) space.
    prev = list(range(len(gt) + 1))
    for i, pc in enumerate(pred, 1):
        cur = [i]
        for j, gc in enumerate(gt, 1):
            cost = 0 if pc == gc else 1
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost))
        prev = cur
    return prev[-1] / len(gt)


@dataclass
class LegibilityCurve:
    px_heights: list[int]
    mean_cer: list[float]
    threshold_px: int | None  # smallest px height with mean CER < usable bar
    usable_threshold: float

    def as_dict(self) -> dict:
        return {
            "px_heights": self.px_heights,
            "mean_cer": self.mean_cer,
            "legibility_threshold_px": self.threshold_px,
            "cer_usable_threshold": self.usable_threshold,
        }


def find_legibility_threshold(
    cer_by_height: dict[int, list[float]],
    *,
    usable_threshold: float = 0.20,
) -> LegibilityCurve:
    """Given per-height CER samples, compute the mean curve and the threshold px.

    ``cer_by_height`` maps a target pixel height to the list of CERs measured across
    plate crops at that height. The threshold is the smallest height whose *mean* CER
    falls below ``usable_threshold``.
    """
    import statistics

    heights = sorted(cer_by_height)
    means = [round(statistics.fmean(cer_by_height[h]), 4) if cer_by_height[h] else 1.0
             for h in heights]

    threshold_px: int | None = None
    for h, m in zip(heights, means, strict=False):
        if m < usable_threshold:
            threshold_px = h
            break

    curve = LegibilityCurve(heights, means, threshold_px, usable_threshold)
    if threshold_px is not None:
        log.info("Legibility threshold: %d px (mean CER < %.2f).", threshold_px, usable_threshold)
    else:
        log.info("No tested height reached CER < %.2f — ANPR infeasible in this range.",
                 usable_threshold)
    return curve
