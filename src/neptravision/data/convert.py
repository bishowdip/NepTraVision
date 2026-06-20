"""Stage 7 — format conversion: YOLO labels ⇄ COCO, and the Ultralytics data.yaml.

YOLO is our canonical on-disk format (one ``.txt`` per image, ``class cx cy w h``
normalised). This module produces the two derived artifacts training/eval need:
the Ultralytics ``data.yaml`` pointer file, and a COCO JSON for tools/metrics that
expect it.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import yaml

from ..config import ClassProfile
from ..logging_utils import get_logger

log = get_logger(__name__)


@dataclass
class YoloBox:
    cls: int
    cx: float
    cy: float
    w: float
    h: float


def parse_label_file(path: Path) -> list[YoloBox]:
    """Parse a YOLO ``.txt`` label file into boxes. Blank/comment lines are ignored."""
    boxes: list[YoloBox] = []
    if not path.is_file():
        return boxes
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) != 5:
            raise ValueError(f"{path}:{lineno}: expected 5 fields, got {len(parts)}: {line!r}")
        cls, cx, cy, w, h = parts
        boxes.append(YoloBox(int(cls), float(cx), float(cy), float(w), float(h)))
    return boxes


def write_ultralytics_data_yaml(
    profile: ClassProfile,
    dataset_root: Path,
    out_path: Path,
) -> Path:
    """Write the ``data.yaml`` that Ultralytics training/val reads.

    Paths point at the ``images/{train,val,test}`` directories relative to
    ``dataset_root``; class names come from the active taxonomy profile.
    """
    data = {
        "path": str(dataset_root),
        "train": "images/train",
        "val": "images/val",
        "test": "images/test",
        "nc": profile.num_classes,
        "names": profile.ordered_names,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh, sort_keys=False)
    log.info("Wrote Ultralytics data.yaml → %s (%d classes)", out_path, profile.num_classes)
    return out_path


def yolo_to_coco(
    images_dir: Path,
    labels_dir: Path,
    profile: ClassProfile,
    out_json: Path,
) -> Path:
    """Convert a YOLO split (images + labels) into a single COCO-format JSON file.

    Needs image dimensions to denormalise boxes, so it opens each image (lazily via
    PIL). Categories use the active taxonomy profile, with COCO's 1-based ids.
    """
    from PIL import Image  # lazy

    images_json: list[dict] = []
    annotations_json: list[dict] = []
    ann_id = 1

    image_files = sorted(
        p for p in images_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}
    )
    for img_id, img_path in enumerate(image_files, 1):
        with Image.open(img_path) as im:
            width, height = im.size
        images_json.append(
            {"id": img_id, "file_name": img_path.name, "width": width, "height": height}
        )
        for box in parse_label_file(labels_dir / f"{img_path.stem}.txt"):
            bw, bh = box.w * width, box.h * height
            x = (box.cx * width) - bw / 2
            y = (box.cy * height) - bh / 2
            annotations_json.append(
                {
                    "id": ann_id,
                    "image_id": img_id,
                    "category_id": box.cls + 1,  # COCO categories are 1-based
                    "bbox": [round(x, 2), round(y, 2), round(bw, 2), round(bh, 2)],
                    "area": round(bw * bh, 2),
                    "iscrowd": 0,
                }
            )
            ann_id += 1

    categories = [
        {"id": cid + 1, "name": name}
        for cid, name in sorted(profile.names.items())
    ]
    coco = {"images": images_json, "annotations": annotations_json, "categories": categories}

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(coco, indent=2), encoding="utf-8")
    log.info(
        "COCO written → %s (%d images, %d annotations).",
        out_json, len(images_json), len(annotations_json),
    )
    return out_json
