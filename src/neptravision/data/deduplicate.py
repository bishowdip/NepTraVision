"""Stage 2 — remove near-duplicate frames with perceptual hashing.

Adjacent frames from one video are visually near-identical. Keeping them bloats
annotation effort and, worse, leaks information between splits. We compute a
perceptual hash (pHash by default) per image and greedily drop any image whose hash
is within ``threshold`` Hamming distance of an already-kept image *from the same
source* (we never dedupe across sources — different videos are meant to differ).

This is O(n²) within a source group, which is fine for the few-thousand-frame scale
we operate at; if a source ever explodes past ~50k frames, switch to a BK-tree.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from ..logging_utils import get_logger

log = get_logger(__name__)

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp"}


@dataclass
class DedupResult:
    kept: list[Path]
    dropped: list[Path]

    @property
    def n_kept(self) -> int:
        return len(self.kept)

    @property
    def n_dropped(self) -> int:
        return len(self.dropped)


def _source_id(image: Path) -> str:
    """Recover the source-video id from a frame filename (``<source>_000123.jpg``)."""
    stem = image.stem
    return stem.rsplit("_", 1)[0] if "_" in stem else stem


def _hash_fn(method: str, hash_size: int):
    import imagehash  # lazy: heavy + only needed here

    funcs = {
        "phash": imagehash.phash,
        "dhash": imagehash.dhash,
        "ahash": imagehash.average_hash,
        "whash": imagehash.whash,
    }
    if method not in funcs:
        raise ValueError(f"Unknown hash method '{method}'; choose from {list(funcs)}")
    return lambda img: funcs[method](img, hash_size=hash_size)


def find_duplicates(
    images: list[Path],
    *,
    method: str = "phash",
    hash_size: int = 8,
    threshold: int = 6,
) -> DedupResult:
    """Partition ``images`` into kept vs dropped near-duplicates.

    Deduplication is performed independently within each source group so that two
    genuinely different videos are never collapsed into one.
    """
    from PIL import Image  # lazy

    hasher = _hash_fn(method, hash_size)

    by_source: dict[str, list[Path]] = defaultdict(list)
    for img in images:
        by_source[_source_id(img)].append(img)

    kept: list[Path] = []
    dropped: list[Path] = []

    for source, group in by_source.items():
        seen_hashes: list = []
        group_kept = 0
        for img in sorted(group):
            try:
                with Image.open(img) as im:
                    h = hasher(im.convert("RGB"))
            except Exception as exc:  # noqa: BLE001 — a corrupt frame shouldn't kill the run
                log.warning("Could not hash %s (%s); dropping it.", img.name, exc)
                dropped.append(img)
                continue

            if any((h - prev) <= threshold for prev in seen_hashes):
                dropped.append(img)
            else:
                seen_hashes.append(h)
                kept.append(img)
                group_kept += 1
        log.info("  %s: kept %d / %d", source, group_kept, len(group))

    log.info("Dedup: kept %d, dropped %d (threshold=%d).", len(kept), len(dropped), threshold)
    return DedupResult(kept=kept, dropped=dropped)


def list_images(directory: Path) -> list[Path]:
    """All images directly inside ``directory`` (non-recursive), sorted."""
    return sorted(p for p in directory.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES)
