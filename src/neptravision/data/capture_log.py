"""Per-video capture log — auto-extract what the camera embeds, prompt for the rest.

A phone (e.g. iPhone) does **not** overlay time/temperature on the footage, but it *does*
embed rich metadata inside the file: capture timestamp, GPS location, resolution, frame
rate, and device model. This module reads that with ``ffprobe`` and pre-fills a per-video
log, leaving only the things no camera can know — **weather** and **traffic density** —
for the person who filmed to enter by hand.

The log is keyed by ``source_id`` (the video stem), which is the same grouping key the
leakage-safe split uses, so conditions logged once per video propagate to every frame
extracted from it (see :func:`neptravision.data.manifest.build_template`).
"""

from __future__ import annotations

import contextlib
import csv
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from ..logging_utils import get_logger
from .frame_extraction import VIDEO_SUFFIXES, _stem_prefix

log = get_logger(__name__)

# One row per source video. Auto-filled columns come from ffprobe; the rest are manual.
CAPTURE_FIELDS = [
    "filename",          # the video file name
    "source_id",         # video stem == leakage-safe grouping key
    # ── auto-filled from embedded metadata ──
    "capture_datetime",  # ISO timestamp from the file (UTC as stored)
    "time_of_day",       # derived bucket: day | evening | night
    "gps_lat",
    "gps_lon",
    "resolution",        # e.g. 3840x2160
    "fps",
    "duration_s",
    "device",            # e.g. "iPhone 14 Pro Max"
    # ── you fill these by hand (no camera records them) ──
    "location",          # human place name, e.g. "kathmandu_ringroad_kalanki"
    "weather",           # clear | rain | dust | fog
    "density",           # low | medium | high
    "license",           # "self-recorded, public space" etc.
    "notes",
]

# Columns the collector owns — never overwritten by a re-probe.
_MANUAL_FIELDS = {"location", "weather", "density", "license", "notes"}

# Subset propagated to each frame's manifest row.
_CONDITION_FIELDS = ["location", "time_of_day", "weather", "density", "resolution", "license"]


@dataclass
class VideoMeta:
    capture_datetime: str = ""
    time_of_day: str = ""
    gps_lat: str = ""
    gps_lon: str = ""
    resolution: str = ""
    fps: str = ""
    duration_s: str = ""
    device: str = ""


def time_of_day_from_hour(hour: int) -> str:
    """Bucket an hour-of-day into day / evening / night (override by hand if wrong)."""
    if 6 <= hour < 17:
        return "day"
    if 17 <= hour < 20:
        return "evening"
    return "night"


def parse_iso6709(value: str) -> tuple[str, str]:
    """Parse a QuickTime ISO-6709 location string → (lat, lon) as strings.

    Example: ``+27.7172+085.3240+1300.000/`` → ("27.7172", "085.3240"). Returns
    empty strings if it can't be parsed (e.g. Location was off when filming).
    """
    if not value:
        return "", ""
    body = value.strip().rstrip("/")
    # Find the split between latitude and longitude: the second sign character.
    signs = [i for i, c in enumerate(body) if c in "+-"]
    if len(signs) < 2:
        return "", ""
    lat = body[signs[0]:signs[1]]
    lon = body[signs[1]:signs[2]] if len(signs) >= 3 else body[signs[1]:]
    return lat.lstrip("+"), lon.lstrip("+")


def _fps_from_rate(rate: str) -> str:
    """Convert ffprobe's ``avg_frame_rate`` like '30000/1001' to a rounded fps string."""
    try:
        num, den = rate.split("/")
        den_f = float(den)
        return str(round(float(num) / den_f, 2)) if den_f else ""
    except (ValueError, ZeroDivisionError):
        return ""


def probe_video(path: Path) -> VideoMeta:
    """Read embedded metadata from one video via ffprobe. Best-effort; never raises."""
    try:
        out = subprocess.check_output(
            [
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_format", "-show_streams", str(path),
            ],
            text=True,
        )
        data = json.loads(out)
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError) as exc:
        log.warning("ffprobe failed on %s (%s).", path.name, exc)
        return VideoMeta()

    fmt = data.get("format", {})
    fmt_tags = {k.lower(): v for k, v in fmt.get("tags", {}).items()}
    streams = data.get("streams", [])
    video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})

    meta = VideoMeta()

    # timestamp (QuickTime/MP4 'creation_time', ISO 8601)
    created = fmt_tags.get("creation_time") or video_stream.get("tags", {}).get("creation_time", "")
    meta.capture_datetime = created
    if created and "T" in created:
        with contextlib.suppress(ValueError, IndexError):
            meta.time_of_day = time_of_day_from_hour(int(created.split("T")[1][:2]))

    # GPS (Apple stores ISO-6709 under com.apple.quicktime.location.ISO6709)
    loc = fmt_tags.get("com.apple.quicktime.location.iso6709") or fmt_tags.get("location", "")
    meta.gps_lat, meta.gps_lon = parse_iso6709(loc)

    # device model
    meta.device = fmt_tags.get("com.apple.quicktime.model") or fmt_tags.get("model", "")

    # resolution / fps / duration
    w, h = video_stream.get("width"), video_stream.get("height")
    if w and h:
        meta.resolution = f"{w}x{h}"
    meta.fps = _fps_from_rate(video_stream.get("avg_frame_rate", "")) or ""
    dur = fmt.get("duration") or video_stream.get("duration", "")
    if dur:
        with contextlib.suppress(ValueError):
            meta.duration_s = str(round(float(dur), 1))

    return meta


def build_capture_log(videos_dir: Path, out_csv: Path) -> Path:
    """Probe every video in ``videos_dir`` and write/update the capture log.

    Manual columns (weather, density, location, license, notes) you've already filled in
    are **preserved** across re-runs; only the auto-extracted columns are refreshed.
    """
    existing: dict[str, dict[str, str]] = {}
    if out_csv.is_file():
        existing = {r["filename"]: r for r in read(out_csv)}

    videos = sorted(p for p in videos_dir.iterdir() if p.suffix.lower() in VIDEO_SUFFIXES)
    if not videos:
        log.warning("No videos found in %s", videos_dir)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CAPTURE_FIELDS)
        writer.writeheader()
        for video in videos:
            meta = probe_video(video)
            prior = existing.get(video.name, {})
            row = {f: "" for f in CAPTURE_FIELDS}
            row["filename"] = video.name
            row["source_id"] = _stem_prefix(video)
            # auto fields from probe
            for f in ("capture_datetime", "time_of_day", "gps_lat", "gps_lon",
                      "resolution", "fps", "duration_s", "device"):
                row[f] = getattr(meta, f)
            # keep manual fields the collector already entered
            for f in _MANUAL_FIELDS:
                row[f] = prior.get(f, "")
            writer.writerow(row)

    log.info("Capture log written → %s (%d videos).", out_csv, len(videos))
    return out_csv


def read(csv_path: Path) -> list[dict[str, str]]:
    if not csv_path.is_file():
        raise FileNotFoundError(f"Capture log not found: {csv_path}")
    with csv_path.open("r", newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def as_source_conditions(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    """Map source_id → its condition columns, for propagation into the frame manifest."""
    return {
        row["source_id"]: {f: row.get(f, "") for f in _CONDITION_FIELDS}
        for row in rows
        if row.get("source_id")
    }
