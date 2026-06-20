"""Rolling analytics over the detection stream for the dashboard.

Deliberately simple: maintains running totals (frames, vehicles, helmet/no-helmet)
and derives the helmet-compliance rate. This is *not* multi-object tracking — true
line-crossing vehicle counts are future work; for the prototype, per-frame counts and
compliance rate are enough to demonstrate the system.
"""

from __future__ import annotations

from dataclasses import dataclass

from .schemas import CountsSummary, FrameResult


@dataclass
class StreamAccumulator:
    total_frames: int = 0
    total_vehicles: int = 0
    total_helmets: int = 0
    total_no_helmets: int = 0

    def update(self, frame: FrameResult) -> None:
        self.total_frames += 1
        self.total_vehicles += frame.vehicle_count
        self.total_helmets += frame.helmet_count
        self.total_no_helmets += frame.no_helmet_count

    def summary(self) -> CountsSummary:
        heads = self.total_helmets + self.total_no_helmets
        rate = self.total_helmets / heads if heads else 0.0
        return CountsSummary(
            total_frames=self.total_frames,
            total_vehicles=self.total_vehicles,
            helmet_compliance_rate=round(rate, 4),
        )
