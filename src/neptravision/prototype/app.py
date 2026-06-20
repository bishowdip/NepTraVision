"""FastAPI app for the prototype dashboard (deployment context demo).

Endpoints:
    GET  /health          → detector status
    GET  /analytics       → rolling counts + helmet-compliance rate
    WS   /ws/stream       → pushes a FrameResult per simulated frame
    GET  /                → the static dashboard page

Run it (mock detector, no model needed):
    pip install -e ".[serve]"
    uvicorn neptravision.prototype.app:app --reload

FastAPI/uvicorn are imported lazily inside ``create_app`` so importing this module
(e.g. in tests) does not require the ``serve`` extra.
"""

from __future__ import annotations

import asyncio
import time
from pathlib import Path

from ..logging_utils import get_logger
from .inference import Detector, MockDetector
from .tracking import StreamAccumulator

log = get_logger(__name__)

WEB_DIR = Path(__file__).parent / "web"


def create_app(detector: Detector | None = None):
    """Application factory. Pass a real detector to serve a trained model."""
    try:
        from fastapi import FastAPI, WebSocket, WebSocketDisconnect
        from fastapi.responses import FileResponse
        from fastapi.staticfiles import StaticFiles
    except ImportError as exc:  # pragma: no cover - optional extra
        raise RuntimeError('fastapi not installed. pip install -e ".[serve]"') from exc

    det: Detector = detector or MockDetector()
    accumulator = StreamAccumulator()

    app = FastAPI(title="NepTraVision Prototype", version="0.1.0")

    @app.get("/health")
    def health():
        return {"status": "ok", "detector": det.name, "model_loaded": det.name != "mock"}

    @app.get("/analytics")
    def analytics():
        return accumulator.summary().model_dump()

    @app.websocket("/ws/stream")
    async def stream(ws: WebSocket):
        """Simulated live stream: emit one inferred frame per tick.

        A real deployment would pull frames from an RTSP/video reader; here we drive
        the same pipeline with a frame counter so the dashboard works end-to-end.
        """
        await ws.accept()
        frame_id = 0
        try:
            while True:
                result = det.infer(frame=None, frame_id=frame_id, timestamp=time.time())
                accumulator.update(result)
                await ws.send_json(result.model_dump())
                frame_id += 1
                await asyncio.sleep(0.1)  # ~10 fps simulated
        except WebSocketDisconnect:
            log.info("Dashboard disconnected after %d frames.", frame_id)

    if WEB_DIR.is_dir():
        app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

        @app.get("/")
        def index():
            return FileResponse(WEB_DIR / "index.html")

    return app


# Module-level app for `uvicorn neptravision.prototype.app:app`.
# Constructed lazily-ish: only fails if uvicorn actually imports it without the extra.
try:  # pragma: no cover - exercised only when serve extra is installed
    app = create_app()
except RuntimeError:  # fastapi missing — that's fine until someone runs the server
    app = None
