"""Efficiency benchmarking (E2) — the distinctive axis of this paper.

Measures, per model per hardware tier: latency (ms/frame), throughput (FPS), model
size (MB), parameters (M), and peak RAM. The *measurement protocol* here is real and
hardware-agnostic (warmup → timed iterations → summary stats); the per-framework
inference call is injected, so the same protocol benchmarks an Ultralytics model on a
laptop CPU or a quantized model on a Raspberry Pi without changing this code.

This separation is deliberate: the protocol is what reviewers scrutinise, and it
should be identical across every model and device.
"""

from __future__ import annotations

import statistics
import time
import tracemalloc
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path

from ..logging_utils import get_logger

log = get_logger(__name__)

# An inference callable takes one preprocessed input and returns detections.
InferenceFn = Callable[[object], object]


@dataclass
class EfficiencyResult:
    model: str
    hardware_tier: str
    imgsz: int
    latency_ms_mean: float
    latency_ms_std: float
    fps: float
    params_m: float
    model_size_mb: float
    peak_ram_mb: float

    def as_row(self) -> dict:
        return asdict(self)


def model_size_mb(weights_path: Path) -> float:
    """On-disk size of a weights file in MB (0.0 if missing)."""
    return weights_path.stat().st_size / (1024 * 1024) if weights_path.is_file() else 0.0


def benchmark_latency(
    infer: InferenceFn,
    sample_input: object,
    *,
    model: str,
    hardware_tier: str,
    imgsz: int,
    params_m: float = 0.0,
    weights_path: Path | None = None,
    warmup_iters: int = 10,
    measure_iters: int = 100,
) -> EfficiencyResult:
    """Time ``infer(sample_input)`` over many iterations after warmup.

    The protocol (identical for every model/device): run ``warmup_iters`` untimed
    passes so caches/JIT settle, then time ``measure_iters`` passes individually and
    report mean ± std latency, FPS, and peak Python-side RAM during measurement.
    """
    for _ in range(warmup_iters):
        infer(sample_input)

    tracemalloc.start()
    latencies_ms: list[float] = []
    for _ in range(measure_iters):
        t0 = time.perf_counter()
        infer(sample_input)
        latencies_ms.append((time.perf_counter() - t0) * 1000.0)
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    mean = statistics.fmean(latencies_ms)
    std = statistics.pstdev(latencies_ms) if len(latencies_ms) > 1 else 0.0
    result = EfficiencyResult(
        model=model,
        hardware_tier=hardware_tier,
        imgsz=imgsz,
        latency_ms_mean=round(mean, 3),
        latency_ms_std=round(std, 3),
        fps=round(1000.0 / mean, 2) if mean > 0 else 0.0,
        params_m=params_m,
        model_size_mb=round(model_size_mb(weights_path), 2) if weights_path else 0.0,
        peak_ram_mb=round(peak_bytes / (1024 * 1024), 2),
    )
    log.info(
        "[%s @ %s, %dpx] %.2f ms/frame → %.1f FPS",
        model, hardware_tier, imgsz, result.latency_ms_mean, result.fps,
    )
    return result
