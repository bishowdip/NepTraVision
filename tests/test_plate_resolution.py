"""Tests for the plate-legibility core: CER and threshold search (E6)."""

from __future__ import annotations

from neptravision.evaluation.plate_resolution import (
    character_error_rate,
    find_legibility_threshold,
)


def test_cer_perfect_match():
    assert character_error_rate("BA12PA3456", "BA12PA3456") == 0.0


def test_cer_one_substitution():
    # one wrong char out of 4
    assert character_error_rate("CARS", "CART") == 0.25


def test_cer_empty_ground_truth():
    assert character_error_rate("", "") == 0.0
    assert character_error_rate("X", "") == 1.0


def test_threshold_picks_smallest_usable_height():
    cer = {
        8: [0.9, 0.8],
        16: [0.5, 0.6],
        24: [0.1, 0.15],   # first to drop below 0.20
        32: [0.05, 0.05],
    }
    curve = find_legibility_threshold(cer, usable_threshold=0.20)
    assert curve.threshold_px == 24


def test_threshold_none_when_never_usable():
    cer = {8: [0.9], 16: [0.8], 24: [0.7]}
    curve = find_legibility_threshold(cer, usable_threshold=0.20)
    assert curve.threshold_px is None
