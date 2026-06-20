"""Stage 6 — leakage-safe train/val/test splitting. **The most important 100 lines
in the repo for benchmark validity.**

The cardinal rule (docs/02_dataset_guide.md §6): frames from the *same source*
(video / location / session) must never appear in more than one split. Random
per-frame splitting silently inflates scores because adjacent frames are
near-duplicates. We therefore split **whole groups**, never individual images.

Algorithm (deterministic given a seed):

1. Group images by the ``group_by`` column (default ``source_id``).
2. Bucket groups by a *stratum* signature derived from ``stratify_by`` conditions,
   so each split ends up with a similar mix of day/night, weather, etc.
3. Within each stratum, shuffle groups (seeded) and greedily assign each whole group
   to whichever split is currently furthest *below* its target image quota.

This is pure Python over plain dicts — no pandas, no I/O — so it is fully unit-tested
in ``tests/test_splits.py``.
"""

from __future__ import annotations

import json
import random
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from ..logging_utils import get_logger

log = get_logger(__name__)


@dataclass
class SplitAssignment:
    """Result of splitting: which split each group and image belongs to."""

    group_to_split: dict[str, str]
    images_by_split: dict[str, list[str]] = field(default_factory=dict)

    def counts(self) -> dict[str, int]:
        return {split: len(imgs) for split, imgs in self.images_by_split.items()}


def _stratum_key(group_rows: list[dict[str, str]], stratify_by: list[str]) -> tuple:
    """A hashable signature of a group's conditions = its most common value per field.

    A single source usually has one weather/time, but if it's mixed we use the modal
    value so the group still lands in a sensible stratum.
    """
    key = []
    for field_name in stratify_by:
        values = [r.get(field_name, "") for r in group_rows]
        # modal value (ties broken by first occurrence for determinism)
        modal = max(set(values), key=values.count) if values else ""
        key.append(modal)
    return tuple(key)


def assign_splits(
    records: list[dict[str, str]],
    *,
    ratios: dict[str, float],
    group_by: str = "source_id",
    stratify_by: list[str] | None = None,
    seed: int = 42,
) -> SplitAssignment:
    """Assign whole groups to splits, approximating ``ratios`` by image count.

    ``records`` is a list of manifest rows; each must contain ``filename`` and the
    ``group_by`` column. Returns a :class:`SplitAssignment`.
    """
    stratify_by = stratify_by or []
    split_names = list(ratios)

    # 1. group images
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in records:
        gid = row.get(group_by)
        if not gid:
            raise ValueError(f"Row is missing group key '{group_by}': {row}")
        groups[gid].append(row)

    # 2. bucket groups by stratum
    strata: dict[tuple, list[str]] = defaultdict(list)
    for gid, rows in groups.items():
        strata[_stratum_key(rows, stratify_by)].append(gid)

    # running image counts per split, and the targets we're aiming for
    total_images = len(records)
    targets = {s: ratios[s] * total_images for s in split_names}
    counts = dict.fromkeys(split_names, 0)
    group_to_split: dict[str, str] = {}

    rng = random.Random(seed)

    # 3. greedy, stratum by stratum (sorted for determinism)
    for stratum in sorted(strata):
        gids = sorted(strata[stratum])
        rng.shuffle(gids)
        # assign larger groups first so big sources don't overshoot a near-full split
        gids.sort(key=lambda g: len(groups[g]), reverse=True)
        for gid in gids:
            size = len(groups[gid])
            # pick the split with the largest remaining room relative to its target
            chosen = max(split_names, key=lambda s: targets[s] - counts[s])
            group_to_split[gid] = chosen
            counts[chosen] += size

    # materialise per-split image lists
    images_by_split: dict[str, list[str]] = {s: [] for s in split_names}
    for gid, rows in groups.items():
        split = group_to_split[gid]
        images_by_split[split].extend(sorted(r["filename"] for r in rows))
    for s in split_names:
        images_by_split[s].sort()

    assignment = SplitAssignment(group_to_split, images_by_split)
    _log_summary(assignment, ratios, total_images)
    return assignment


def _log_summary(a: SplitAssignment, ratios: dict[str, float], total: int) -> None:
    log.info("Split summary (%d images, %d groups):", total, len(a.group_to_split))
    for split, n in a.counts().items():
        pct = 100 * n / total if total else 0
        log.info("  %-5s %6d images (%.1f%%, target %.1f%%)", split, n, pct, 100 * ratios[split])


def write_split_definition(assignment: SplitAssignment, out_dir: Path) -> Path:
    """Persist the split as committable JSON so the exact partition is reproducible.

    We store the *group → split* map (small, human-auditable) rather than full image
    lists; the image lists are recoverable from the manifest + this map.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "split_by_source.json"
    payload = {
        "policy": "split_by_source_group",
        "group_to_split": assignment.group_to_split,
        "counts": assignment.counts(),
    }
    out_file.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    log.info("Split definition written to %s", out_file)
    return out_file
