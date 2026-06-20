"""Stage 8 — dataset statistics that populate the dataset card and sanity-check QC.

Everything here reads YOLO labels + the manifest and emits plain dictionaries, so
the same numbers can be printed to the console, written to the dataset card, or
asserted in a reproducibility check.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from ..config import ClassProfile
from .convert import parse_label_file

LABEL_SUFFIX = ".txt"


@dataclass
class DatasetStats:
    n_images: int = 0
    n_boxes: int = 0
    class_counts: dict[str, int] = field(default_factory=dict)
    images_with_labels: int = 0
    empty_images: int = 0

    def as_dict(self) -> dict:
        return {
            "n_images": self.n_images,
            "n_boxes": self.n_boxes,
            "images_with_labels": self.images_with_labels,
            "empty_images": self.empty_images,
            "class_counts": self.class_counts,
        }


def compute_label_stats(labels_dir: Path, profile: ClassProfile) -> DatasetStats:
    """Class distribution and box/image counts across all label files in a dir tree."""
    counter: Counter[int] = Counter()
    stats = DatasetStats()

    label_files = sorted(labels_dir.rglob(f"*{LABEL_SUFFIX}"))
    for lf in label_files:
        boxes = parse_label_file(lf)
        stats.n_images += 1
        if boxes:
            stats.images_with_labels += 1
        else:
            stats.empty_images += 1
        for b in boxes:
            counter[b.cls] += 1

    stats.n_boxes = sum(counter.values())
    # name the classes, preserving id order; unknown ids surface as "id:<n>"
    stats.class_counts = {
        profile.names.get(cid, f"id:{cid}"): counter.get(cid, 0)
        for cid in sorted(set(profile.names) | set(counter))
    }
    return stats


def condition_coverage(records: list[dict[str, str]]) -> dict[str, dict[str, int]]:
    """Coverage counts per condition column (time_of_day / weather / density / location)."""
    coverage: dict[str, Counter] = {
        col: Counter() for col in ("location", "time_of_day", "weather", "density")
    }
    for row in records:
        for col, counter in coverage.items():
            value = (row.get(col) or "").strip() or "(blank)"
            counter[value] += 1
    return {col: dict(sorted(counter.items())) for col, counter in coverage.items()}
