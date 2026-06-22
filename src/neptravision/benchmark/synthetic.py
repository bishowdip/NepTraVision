"""Deterministic synthetic metrics for ``--dry-run`` benchmark runs.

These let the *whole* pipeline (orchestrate → aggregate → tabulate → plot) run and be
tested without torch, Ultralytics, or a dataset. The numbers are **fabricated** but
*plausible*: they are derived from each model's real parameter count (from
``configs/models/*.yaml``) so larger models look slightly more accurate but slower —
producing a realistic accuracy/speed trade-off and a meaningful Pareto frontier for
demos. Every row produced this way is tagged ``simulated=true`` upstream so it can never
be confused with a measured result.
"""

from __future__ import annotations

import random

from ..evaluation.efficiency import EfficiencyResult
from ..evaluation.metrics import AccuracyMetrics, f1_from_pr
from ..models.registry import get_model_spec

# Relative speed of each hardware tier vs the laptop-CPU baseline (rough, for demo only).
_TIER_SPEED = {
    "gpu_t4": 8.0,
    "cpu_laptop": 1.0,
    "rpi5": 0.35,
    "jetson_nano": 1.6,
}


def _rng(*parts: object) -> random.Random:
    """A deterministic RNG seeded by the given parts (so dry-runs are reproducible)."""
    return random.Random(hash(parts) & 0xFFFFFFFF)


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def synth_accuracy(model_name: str, seed: int) -> AccuracyMetrics:
    """Fabricate a plausible per-seed accuracy result for ``model_name``."""
    spec = get_model_spec(model_name)
    params = max(spec.approx_params_m, 0.5)
    rng = _rng("acc", model_name, seed)

    # Larger models: modestly higher mAP, with small per-seed jitter.
    map50 = _clamp(0.42 + 0.045 * (params ** 0.5), 0.40, 0.86) + rng.uniform(-0.012, 0.012)
    map50 = _clamp(map50, 0.0, 0.95)
    map50_95 = map50 * (0.62 + rng.uniform(-0.02, 0.02))
    precision = _clamp(map50 + rng.uniform(-0.02, 0.05), 0.0, 0.97)
    recall = _clamp(map50 + rng.uniform(-0.05, 0.02), 0.0, 0.97)

    return AccuracyMetrics(
        model=model_name,
        map50=round(map50, 4),
        map50_95=round(map50_95, 4),
        precision=round(precision, 4),
        recall=round(recall, 4),
        f1=round(f1_from_pr(precision, recall), 4),
        per_class_ap={},
    )


def synth_efficiency(model_name: str, hardware_tier: str, imgsz: int = 640) -> EfficiencyResult:
    """Fabricate a plausible efficiency result for ``model_name`` on ``hardware_tier``."""
    spec = get_model_spec(model_name)
    params = max(spec.approx_params_m, 0.5)
    rng = _rng("eff", model_name, hardware_tier, imgsz)

    tier_speed = _TIER_SPEED.get(hardware_tier, 1.0)
    # Laptop-CPU FPS falls off as params grow; scale by tier and input resolution.
    cpu_fps = 90.0 / (params + 2.0)
    res_scale = (640.0 / imgsz) ** 2
    fps = cpu_fps * tier_speed * res_scale * (1 + rng.uniform(-0.05, 0.05))
    latency = 1000.0 / fps if fps > 0 else 0.0

    return EfficiencyResult(
        model=model_name,
        hardware_tier=hardware_tier,
        imgsz=imgsz,
        latency_ms_mean=round(latency, 3),
        latency_ms_std=round(latency * rng.uniform(0.03, 0.08), 3),
        fps=round(fps, 2),
        params_m=round(params, 2),
        model_size_mb=round(params * 2.0, 2),
        peak_ram_mb=round(180 + params * 28, 1),
    )
