"""Tests for the pure capture-log helpers (time-of-day buckets, ISO-6709 GPS parse)."""

from __future__ import annotations

from neptravision.data.capture_log import (
    as_source_conditions,
    parse_iso6709,
    time_of_day_from_hour,
)


def test_time_of_day_buckets():
    assert time_of_day_from_hour(8) == "day"
    assert time_of_day_from_hour(16) == "day"
    assert time_of_day_from_hour(18) == "evening"
    assert time_of_day_from_hour(22) == "night"
    assert time_of_day_from_hour(3) == "night"


def test_parse_iso6709_apple_format():
    lat, lon = parse_iso6709("+27.7172+085.3240+1300.000/")
    assert lat == "27.7172"
    assert lon == "085.3240"


def test_parse_iso6709_negative_lon():
    lat, lon = parse_iso6709("+27.7172-085.3240/")
    assert lat == "27.7172"
    assert lon == "-085.3240"


def test_parse_iso6709_empty_or_bad():
    assert parse_iso6709("") == ("", "")
    assert parse_iso6709("garbage") == ("", "")


def test_as_source_conditions_maps_by_source():
    rows = [
        {"source_id": "vidA", "location": "kalanki", "time_of_day": "day",
         "weather": "clear", "density": "high", "resolution": "3840x2160", "license": "self"},
    ]
    cond = as_source_conditions(rows)
    assert cond["vidA"]["weather"] == "clear"
    assert cond["vidA"]["resolution"] == "3840x2160"
