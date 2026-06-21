"""The dataset manifest — ``metadata.csv``, one row per image.

This file is the backbone of reproducibility and of leakage-safe splitting: it
records, per image, which *source* it came from and the conditions it was captured
under. The split stage groups by ``source_id`` from here; the condition breakdown
(E5) slices by ``time_of_day`` / ``weather`` / ``density`` from here.

We use the stdlib ``csv`` module (not pandas) so this module stays dependency-light
and the split logic that consumes it remains trivially testable.
"""

from __future__ import annotations

import csv
from pathlib import Path

from ..logging_utils import get_logger

log = get_logger(__name__)

# The schema every manifest row carries. Condition columns start blank and are
# filled in by the annotator/collector — they are what E5 slices on.
MANIFEST_FIELDS = [
    "filename",      # image file name (no directory)
    "source_id",     # source video/session id — the leakage-safe grouping key
    "location",      # e.g. "kathmandu_ringroad_kalanki"
    "time_of_day",   # day | evening | night
    "weather",       # clear | rain | dust | fog
    "density",       # low | medium | high
    "resolution",    # e.g. "1920x1080"
    "license",       # source license / permission note
    "notes",
]


def source_id_from_filename(filename: str) -> str:
    """Recover ``source_id`` from a frame filename (``<source>_000123.jpg``)."""
    stem = Path(filename).stem
    return stem.rsplit("_", 1)[0] if "_" in stem else stem


def build_template(
    images: list[Path],
    out_csv: Path,
    source_conditions: dict[str, dict[str, str]] | None = None,
) -> Path:
    """Write a manifest skeleton for ``images`` with ``source_id`` pre-filled.

    Condition columns are left blank for the collector to complete — unless
    ``source_conditions`` is supplied (a ``source_id → {column: value}`` map, e.g. from
    the per-video capture log), in which case each frame inherits its source's conditions
    automatically. Existing rows in ``out_csv`` are preserved; manually-entered values are
    never overwritten by the propagated defaults.
    """
    source_conditions = source_conditions or {}
    existing: dict[str, dict[str, str]] = {}
    if out_csv.is_file():
        existing = {r["filename"]: r for r in read(out_csv)}

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    n_new = 0
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=MANIFEST_FIELDS)
        writer.writeheader()
        for img in sorted(images):
            row = existing.get(img.name)
            if row is None:
                src = source_id_from_filename(img.name)
                row = {f: "" for f in MANIFEST_FIELDS}
                row["filename"] = img.name
                row["source_id"] = src
                # inherit source-level conditions where we have them
                for field_name, value in source_conditions.get(src, {}).items():
                    if field_name in row and value:
                        row[field_name] = value
                n_new += 1
            writer.writerow({f: row.get(f, "") for f in MANIFEST_FIELDS})

    log.info("Manifest written to %s (%d new rows).", out_csv, n_new)
    return out_csv


def read(csv_path: Path) -> list[dict[str, str]]:
    """Read a manifest CSV into a list of row dicts."""
    if not csv_path.is_file():
        raise FileNotFoundError(f"Manifest not found: {csv_path}")
    with csv_path.open("r", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))
