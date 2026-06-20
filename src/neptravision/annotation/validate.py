"""Validate YOLO label files before they ever reach training.

Catches the silent corruptions: out-of-range coordinates, class ids outside the
frozen taxonomy, malformed lines, labels without images, and images without labels.
A clean ``validate`` run is a precondition for a trustworthy benchmark.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ..config import ClassProfile
from ..logging_utils import get_logger

log = get_logger(__name__)

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp"}


@dataclass
class ValidationReport:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    n_label_files: int = 0
    n_boxes: int = 0

    @property
    def ok(self) -> bool:
        return not self.errors

    def summary(self) -> str:
        status = "OK" if self.ok else "FAILED"
        return (
            f"[{status}] {self.n_label_files} label files, {self.n_boxes} boxes, "
            f"{len(self.errors)} errors, {len(self.warnings)} warnings"
        )


def validate_labels(
    labels_dir: Path,
    profile: ClassProfile,
    images_dir: Path | None = None,
) -> ValidationReport:
    """Validate every ``.txt`` under ``labels_dir`` against the taxonomy ``profile``.

    If ``images_dir`` is given, also cross-checks image↔label correspondence.
    """
    report = ValidationReport()
    valid_ids = set(profile.names)

    label_files = sorted(labels_dir.rglob("*.txt"))
    report.n_label_files = len(label_files)

    for lf in label_files:
        for lineno, raw in enumerate(lf.read_text(encoding="utf-8").splitlines(), 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            loc = f"{lf}:{lineno}"
            if len(parts) != 5:
                report.errors.append(f"{loc}: expected 5 fields, got {len(parts)}")
                continue
            try:
                cls = int(parts[0])
                cx, cy, w, h = (float(x) for x in parts[1:])
            except ValueError:
                report.errors.append(f"{loc}: non-numeric field in {line!r}")
                continue

            report.n_boxes += 1
            if cls not in valid_ids:
                report.errors.append(
                    f"{loc}: class id {cls} not in profile (valid: {sorted(valid_ids)})"
                )
            for label, value in (("cx", cx), ("cy", cy), ("w", w), ("h", h)):
                if not 0.0 <= value <= 1.0:
                    report.errors.append(f"{loc}: {label}={value} out of range [0,1]")
            if w <= 0 or h <= 0:
                report.errors.append(f"{loc}: non-positive box size w={w} h={h}")

    if images_dir is not None:
        _check_correspondence(labels_dir, images_dir, report)

    log.info(report.summary())
    return report


def _check_correspondence(
    labels_dir: Path, images_dir: Path, report: ValidationReport
) -> None:
    image_stems = {
        p.stem for p in images_dir.rglob("*") if p.suffix.lower() in IMAGE_SUFFIXES
    }
    label_stems = {p.stem for p in labels_dir.rglob("*.txt")}

    for orphan in sorted(label_stems - image_stems):
        report.warnings.append(f"label without image: {orphan}.txt")
    for unlabeled in sorted(image_stems - label_stems):
        report.warnings.append(f"image without label file: {unlabeled}")
