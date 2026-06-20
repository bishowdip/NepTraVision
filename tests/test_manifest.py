"""Tests for manifest round-tripping and source-id recovery."""

from __future__ import annotations

from pathlib import Path

from neptravision.data.manifest import (
    MANIFEST_FIELDS,
    build_template,
    read,
    source_id_from_filename,
)


def test_source_id_recovery():
    assert source_id_from_filename("ringroad_kalanki_000123.jpg") == "ringroad_kalanki"
    assert source_id_from_filename("noindexname.jpg") == "noindexname"


def test_build_and_read_roundtrip(tmp_path: Path):
    imgs = []
    for name in ("vidA_000001.jpg", "vidA_000002.jpg", "vidB_000001.jpg"):
        p = tmp_path / name
        p.write_bytes(b"")  # content irrelevant; manifest only reads names
        imgs.append(p)

    out = tmp_path / "metadata.csv"
    build_template(imgs, out)
    rows = read(out)

    assert len(rows) == 3
    assert set(rows[0].keys()) == set(MANIFEST_FIELDS)
    assert {r["source_id"] for r in rows} == {"vidA", "vidB"}
