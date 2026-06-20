"""Pydantic models for the prototype API — the contract between backend and dashboard.

Defined with pydantic (a core dependency) so they are importable and testable without
FastAPI installed.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Detection(BaseModel):
    """One detected object in a frame."""

    cls_id: int
    cls_name: str
    confidence: float = Field(ge=0.0, le=1.0)
    # Pixel-space box: [x1, y1, x2, y2]
    box: tuple[float, float, float, float]


class FrameResult(BaseModel):
    """Everything inferred from a single frame, ready to push over the WebSocket."""

    frame_id: int
    timestamp: float
    detections: list[Detection] = Field(default_factory=list)
    vehicle_count: int = 0
    helmet_count: int = 0
    no_helmet_count: int = 0
    sign_events: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str = "ok"
    detector: str
    model_loaded: bool


class CountsSummary(BaseModel):
    """Rolling totals surfaced by the REST analytics endpoint."""

    total_frames: int = 0
    total_vehicles: int = 0
    helmet_compliance_rate: float = 0.0  # helmets / (helmets + no_helmets)
