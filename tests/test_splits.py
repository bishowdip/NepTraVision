"""Tests for leakage-safe splitting — the property that protects benchmark validity."""

from __future__ import annotations

from neptravision.data.splits import assign_splits


def _records(n_sources: int, frames_per_source: int, **conditions: str):
    """Build synthetic manifest rows: source_<i> with N frames each."""
    rows = []
    for s in range(n_sources):
        for f in range(frames_per_source):
            rows.append(
                {
                    "filename": f"source_{s}_{f:06d}.jpg",
                    "source_id": f"source_{s}",
                    **conditions,
                }
            )
    return rows


def test_no_source_appears_in_two_splits():
    """THE invariant: every source lands in exactly one split."""
    records = _records(20, 10)
    a = assign_splits(records, ratios={"train": 0.7, "val": 0.15, "test": 0.15}, seed=1)

    # Build source -> set(splits) and assert each set has size 1.
    from collections import defaultdict

    source_splits = defaultdict(set)
    for split, files in a.images_by_split.items():
        for fn in files:
            source_splits[fn.rsplit("_", 1)[0]].add(split)
    assert all(len(splits) == 1 for splits in source_splits.values())


def test_all_images_assigned_exactly_once():
    records = _records(15, 8)
    a = assign_splits(records, ratios={"train": 0.7, "val": 0.15, "test": 0.15}, seed=3)
    total = sum(len(v) for v in a.images_by_split.values())
    assert total == len(records)
    # no duplicates across splits
    seen = [fn for files in a.images_by_split.values() for fn in files]
    assert len(seen) == len(set(seen))


def test_ratios_are_approximately_respected():
    records = _records(30, 10)  # 300 images, uniform group sizes → close to target
    a = assign_splits(records, ratios={"train": 0.7, "val": 0.15, "test": 0.15}, seed=0)
    counts = a.counts()
    assert abs(counts["train"] / 300 - 0.70) < 0.12
    assert abs(counts["val"] / 300 - 0.15) < 0.12
    assert abs(counts["test"] / 300 - 0.15) < 0.12


def test_deterministic_given_seed():
    records = _records(12, 7)
    a = assign_splits(records, ratios={"train": 0.7, "val": 0.15, "test": 0.15}, seed=42)
    b = assign_splits(records, ratios={"train": 0.7, "val": 0.15, "test": 0.15}, seed=42)
    assert a.group_to_split == b.group_to_split


def test_missing_group_key_raises():
    import pytest

    bad = [{"filename": "x.jpg"}]  # no source_id
    with pytest.raises(ValueError):
        assign_splits(bad, ratios={"train": 0.8, "test": 0.2})
