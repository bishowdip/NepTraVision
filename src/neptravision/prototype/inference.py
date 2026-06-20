"""Detector abstraction for the prototype.

A small ``Detector`` protocol with two implementations:

* :class:`MockDetector` — deterministic fake detections, so the dashboard and the
  whole API can be developed and tested with **zero** model weights or GPU.
* :class:`UltralyticsDetector` — wraps a trained ``.pt`` checkpoint (lazy import).

The protocol is what the FastAPI app depends on, so swapping mock ↔ real is a
one-line change and never touches the web layer.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from ..config import load_classes
from .schemas import Detection, FrameResult


class Detector(Protocol):
    name: str

    def infer(self, frame: object, frame_id: int, timestamp: float) -> FrameResult: ...


# ─────────────────────────────────────────────────────────────────────────────
def _summarise(detections: list[Detection], frame_id: int, timestamp: float) -> FrameResult:
    """Roll raw detections up into the dashboard-facing per-frame summary."""
    classes = load_classes().active
    vehicle_ids = set(classes.groups.get("vehicle", []))
    helmet_name_to_id = {v: k for k, v in classes.names.items()}
    helmet_id = helmet_name_to_id.get("helmet")
    no_helmet_id = helmet_name_to_id.get("no_helmet")
    sign_ids = set(classes.groups.get("sign", []))

    return FrameResult(
        frame_id=frame_id,
        timestamp=timestamp,
        detections=detections,
        vehicle_count=sum(d.cls_id in vehicle_ids for d in detections),
        helmet_count=sum(d.cls_id == helmet_id for d in detections),
        no_helmet_count=sum(d.cls_id == no_helmet_id for d in detections),
        sign_events=[d.cls_name for d in detections if d.cls_id in sign_ids],
    )


# ─────────────────────────────────────────────────────────────────────────────
class MockDetector:
    """Deterministic stand-in: emits a couple of plausible boxes per frame.

    Useful for building/testing the dashboard before any model is trained.
    """

    name = "mock"

    def infer(self, frame: object, frame_id: int, timestamp: float) -> FrameResult:
        classes = load_classes().active
        names = classes.names
        # Cycle through a few classes deterministically so the UI shows variety.
        picks = [frame_id % len(names), (frame_id + 3) % len(names)]
        detections = [
            Detection(
                cls_id=cid,
                cls_name=names[cid],
                confidence=0.5 + 0.4 * ((frame_id + cid) % 5) / 5,
                box=(10.0 + cid, 10.0 + cid, 80.0 + cid, 80.0 + cid),
            )
            for cid in picks
        ]
        return _summarise(detections, frame_id, timestamp)


class UltralyticsDetector:
    """Wraps a trained YOLO checkpoint. Lazily imports ultralytics."""

    name = "ultralytics"

    def __init__(self, weights: Path, conf: float = 0.25, imgsz: int = 640) -> None:
        try:
            from ultralytics import YOLO
        except ImportError as exc:  # pragma: no cover - optional extra
            raise RuntimeError('ultralytics not installed. pip install -e ".[train]"') from exc
        self._model = YOLO(str(weights))
        self._conf = conf
        self._imgsz = imgsz

    def infer(self, frame: object, frame_id: int, timestamp: float) -> FrameResult:
        results = self._model.predict(frame, conf=self._conf, imgsz=self._imgsz, verbose=False)
        detections: list[Detection] = []
        for r in results:
            names = r.names
            for b in r.boxes:
                cid = int(b.cls)
                x1, y1, x2, y2 = (float(v) for v in b.xyxy[0])
                detections.append(
                    Detection(
                        cls_id=cid,
                        cls_name=names.get(cid, str(cid)),
                        confidence=float(b.conf),
                        box=(x1, y1, x2, y2),
                    )
                )
        return _summarise(detections, frame_id, timestamp)
