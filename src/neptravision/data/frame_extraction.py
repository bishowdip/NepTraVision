"""Stage 1 — extract frames from raw videos with FFmpeg at a controlled rate.

We shell out to FFmpeg (rather than decode in Python) because it is fast, ubiquitous,
and the exact command is easy to cite in the methodology. Extracting at a low,
controlled FPS is deliberate: dense traffic video at native frame rate produces
near-identical frames that, if split across train/test, inflate scores massively
(see docs/02_dataset_guide.md §6).
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from ..logging_utils import get_logger

log = get_logger(__name__)

VIDEO_SUFFIXES = {".mp4", ".mov", ".avi", ".mkv", ".m4v", ".webm"}


@dataclass
class ExtractionResult:
    video: Path
    frames_written: int
    output_dir: Path


def ffmpeg_available() -> bool:
    """True if an ``ffmpeg`` binary is on PATH."""
    return shutil.which("ffmpeg") is not None


def _stem_prefix(video: Path) -> str:
    """A filesystem-safe, source-traceable prefix derived from the video name.

    The prefix doubles as the ``source_id`` used by leakage-safe splitting, so all
    frames of one video share a group. Keep it stable.
    """
    return video.stem.replace(" ", "_")


def extract_one(
    video: Path,
    output_dir: Path,
    *,
    fps: float = 1.0,
    image_format: str = "jpg",
    jpg_quality: int = 2,
    overwrite: bool = False,
) -> ExtractionResult:
    """Extract frames from a single video into ``output_dir``.

    Frames are named ``<video_stem>_%06d.<ext>`` so the source video is recoverable
    from any frame filename. Returns how many frames were written.
    """
    if not ffmpeg_available():
        raise RuntimeError("ffmpeg not found on PATH; install it to extract frames.")

    output_dir.mkdir(parents=True, exist_ok=True)
    prefix = _stem_prefix(video)
    pattern = str(output_dir / f"{prefix}_%06d.{image_format}")

    existing = sorted(output_dir.glob(f"{prefix}_*.{image_format}"))
    if existing and not overwrite:
        log.info("Skipping %s — %d frames already extracted.", video.name, len(existing))
        return ExtractionResult(video, len(existing), output_dir)

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-y" if overwrite else "-n",
        "-i", str(video),
        "-vf", f"fps={fps}",
        "-q:v", str(jpg_quality),
        pattern,
    ]
    log.info("Extracting %s at %s fps", video.name, fps)
    subprocess.run(cmd, check=True)

    written = sorted(output_dir.glob(f"{prefix}_*.{image_format}"))
    log.info("  → %d frames", len(written))
    return ExtractionResult(video, len(written), output_dir)


def extract_all(
    videos_dir: Path,
    output_dir: Path,
    *,
    fps: float = 1.0,
    image_format: str = "jpg",
    jpg_quality: int = 2,
    overwrite: bool = False,
) -> list[ExtractionResult]:
    """Extract frames from every video in ``videos_dir`` (non-recursive)."""
    videos = sorted(
        p for p in videos_dir.iterdir() if p.suffix.lower() in VIDEO_SUFFIXES
    )
    if not videos:
        log.warning("No videos found in %s (looked for %s)", videos_dir, sorted(VIDEO_SUFFIXES))
        return []

    results = [
        extract_one(
            v, output_dir,
            fps=fps, image_format=image_format,
            jpg_quality=jpg_quality, overwrite=overwrite,
        )
        for v in videos
    ]
    total = sum(r.frames_written for r in results)
    log.info("Extracted %d frames from %d videos.", total, len(results))
    return results
