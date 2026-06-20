"""Tests for config loading, the frozen taxonomy, and label validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from neptravision.annotation.validate import validate_labels
from neptravision.config import ClassProfile, load_classes


def test_active_profile_loads_and_is_contiguous():
    classes = load_classes()
    profile = classes.active
    assert profile.num_classes >= 3
    # ids 0..n-1 present and ordered_names matches that order
    assert profile.ordered_names[0] == profile.names[0]


def test_profile_rejects_non_contiguous_ids():
    with pytest.raises(ValueError):
        ClassProfile(names={0: "a", 2: "b"})  # missing id 1


def test_validate_flags_bad_class_and_coords(tmp_path: Path):
    profile = ClassProfile(names={0: "two_wheeler", 1: "helmet", 2: "no_helmet"})
    labels = tmp_path / "labels"
    labels.mkdir()
    # good line, bad class id (9), out-of-range coord (1.5), malformed (3 fields)
    (labels / "img1.txt").write_text(
        "0 0.5 0.5 0.2 0.2\n9 0.5 0.5 0.1 0.1\n1 1.5 0.5 0.1 0.1\n2 0.5 0.5\n",
        encoding="utf-8",
    )
    report = validate_labels(labels, profile)
    assert not report.ok
    joined = "\n".join(report.errors)
    assert "class id 9" in joined
    assert "out of range" in joined
    assert "expected 5 fields" in joined


def test_validate_passes_clean_labels(tmp_path: Path):
    profile = ClassProfile(names={0: "two_wheeler", 1: "helmet", 2: "no_helmet"})
    labels = tmp_path / "labels"
    labels.mkdir()
    (labels / "img1.txt").write_text("0 0.5 0.5 0.2 0.2\n1 0.3 0.3 0.1 0.1\n", encoding="utf-8")
    report = validate_labels(labels, profile)
    assert report.ok
    assert report.n_boxes == 2
