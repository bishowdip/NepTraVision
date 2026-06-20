"""Real-time prototype dashboard — deployment *context*, not a paper claim.

A FastAPI + WebSocket app that streams detections (vehicle counts, helmet-compliance
alerts, sign events) from a trained model — or a mock detector for development.
Kept deliberately thin: all the science lives in the other packages; this is the demo
that shows the benchmark's winner running. Requires the ``serve`` extra.
"""
