"""Condition breakdown (E5) — where does the detector break?

Slices test-set accuracy by the metadata conditions recorded in the manifest
(time_of_day, weather, density). The mechanism: partition the test images by a
condition value, evaluate the model on each partition, and tabulate. The per-slice
evaluation reuses :mod:`neptravision.evaluation.metrics`, so this module is mostly
*bookkeeping*: building the slices and assembling the table.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from ..logging_utils import get_logger

log = get_logger(__name__)


def slice_images_by_condition(
    records: list[dict[str, str]],
    condition: str,
    test_filenames: set[str],
) -> dict[str, list[str]]:
    """Group test-set image filenames by their value of ``condition`` in the manifest.

    Only images in ``test_filenames`` are considered (we never analyse train/val
    leakage into the condition study).
    """
    slices: dict[str, list[str]] = defaultdict(list)
    for row in records:
        fn = row["filename"]
        if fn not in test_filenames:
            continue
        value = (row.get(condition) or "").strip() or "(blank)"
        slices[value].append(fn)
    counts = {k: len(v) for k, v in slices.items()}
    log.info("Condition '%s' slices: %s", condition, counts)
    return dict(slices)


def build_condition_table(
    weights: Path,
    data_yaml: Path,
    records: list[dict[str, str]],
    test_filenames: set[str],
    *,
    model_name: str,
    conditions: list[str],
    imgsz: int = 640,
) -> list[dict]:
    """Assemble the per-condition accuracy rows for E5.

    For each condition value we build a temporary single-slice dataset and evaluate.
    The slice-dataset construction (symlinking the subset + a scoped data.yaml) is
    implemented when the dataset exists; until then this raises a clear marker so the
    call site fails loudly rather than silently returning empty results.
    """
    raise NotImplementedError(
        "E5 per-slice evaluation needs an annotated test split. Implement slice-dataset "
        "construction (symlink subset + scoped data.yaml) once data/dataset/ is "
        "populated; the slicing logic in slice_images_by_condition() is ready to use."
    )
