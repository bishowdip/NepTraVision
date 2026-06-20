"""Tests for IoU and inter-annotator matching geometry."""

from __future__ import annotations

import pytest

from neptravision.annotation.agreement import _greedy_match, iou_xywh_normalised
from neptravision.data.convert import YoloBox


def test_iou_identical_boxes_is_one():
    b = YoloBox(0, 0.5, 0.5, 0.2, 0.2)
    assert iou_xywh_normalised(b, b) == pytest.approx(1.0)


def test_iou_disjoint_boxes_is_zero():
    a = YoloBox(0, 0.1, 0.1, 0.1, 0.1)
    b = YoloBox(0, 0.9, 0.9, 0.1, 0.1)
    assert iou_xywh_normalised(a, b) == 0.0


def test_iou_half_overlap():
    # Two unit-ish boxes overlapping on exactly half their area.
    a = YoloBox(0, 0.25, 0.5, 0.5, 0.5)  # x in [0.0, 0.5]
    b = YoloBox(0, 0.50, 0.5, 0.5, 0.5)  # x in [0.25, 0.75]
    iou = iou_xywh_normalised(a, b)
    # intersection x in [0.25,0.5] (0.25 wide) × full height 0.5 = 0.125
    # union = 0.25 + 0.25 - 0.125 = 0.375 → IoU = 1/3
    assert abs(iou - (0.125 / 0.375)) < 1e-9


def test_greedy_match_pairs_closest():
    a = [YoloBox(0, 0.5, 0.5, 0.2, 0.2), YoloBox(1, 0.1, 0.1, 0.1, 0.1)]
    b = [YoloBox(0, 0.5, 0.5, 0.2, 0.2)]
    matches = _greedy_match(a, b, iou_thr=0.5)
    assert len(matches) == 1
    assert matches[0][0] == 0 and matches[0][1] == 0
