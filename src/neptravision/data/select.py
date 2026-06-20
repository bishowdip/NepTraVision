"""Stage 3 — curate frames: drop unusable images, keep diverse useful ones.

Right now this implements the *automatable* curation rules from the dataset guide:
reject blurry frames (low variance of the Laplacian). The human-judgement rules
("keep multi-vehicle / two-wheeler / sign / occlusion / day-night-rain diversity")
are left to the annotator's eye — this stage just removes frames that are not worth
their time, and flags the rest for review.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..logging_utils import get_logger

log = get_logger(__name__)


@dataclass
class SelectionResult:
    kept: list[Path]
    rejected_blurry: list[Path]

    @property
    def n_kept(self) -> int:
        return len(self.kept)


def blur_score(image_path: Path) -> float:
    """Variance of the Laplacian — a standard, cheap sharpness proxy.

    Higher = sharper. Blurry frames score low. Returns 0.0 for unreadable images.
    """
    import cv2  # lazy

    img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        return 0.0
    return float(cv2.Laplacian(img, cv2.CV_64F).var())


def select_images(
    images: list[Path],
    *,
    blur_min_variance: float = 100.0,
) -> SelectionResult:
    """Keep images sharper than ``blur_min_variance``; reject the rest as blurry."""
    kept: list[Path] = []
    rejected: list[Path] = []
    for img in images:
        if blur_score(img) >= blur_min_variance:
            kept.append(img)
        else:
            rejected.append(img)
    log.info(
        "Selection: kept %d, rejected %d blurry (min_var=%.1f).",
        len(kept), len(rejected), blur_min_variance,
    )
    return SelectionResult(kept=kept, rejected_blurry=rejected)
