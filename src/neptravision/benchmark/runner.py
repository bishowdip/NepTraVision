"""Benchmark orchestration: run an experiment config end to end into result tables.

Reads a ``configs/experiments/*.yaml``, iterates over models × seeds (accuracy / E1) and
models × hardware tiers (efficiency / E2), and writes:

    results/tables/<exp>_accuracy_raw.csv   one row per (model, seed)
    results/tables/<exp>_accuracy.csv       one row per model, mean ± std
    results/tables/<exp>_efficiency.csv     one row per (model, hardware tier)

``dry_run=True`` fills metrics from :mod:`~neptravision.benchmark.synthetic` (no torch /
data needed) — the path exercised by tests and demos. ``dry_run=False`` trains and
evaluates for real (requires the ``train`` extra + an annotated dataset).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ..config import load_experiment_config
from ..evaluation.metrics import AccuracyMetrics
from ..logging_utils import get_logger
from ..models.registry import get_model_spec
from ..paths import PATHS
from . import synthetic, tables

log = get_logger(__name__)


@dataclass
class BenchmarkResult:
    experiment: str
    dry_run: bool
    accuracy_table: Path | None = None
    accuracy_raw_table: Path | None = None
    efficiency_table: Path | None = None
    models: list[str] = field(default_factory=list)

    def summary(self) -> str:
        mode = "DRY-RUN (simulated)" if self.dry_run else "real"
        return f"[{self.experiment}] {mode} — {len(self.models)} models → {self.accuracy_table}"


def run_benchmark(
    experiment: str,
    *,
    dry_run: bool = False,
    out_dir: Path | None = None,
    data_yaml: Path | None = None,
) -> BenchmarkResult:
    """Run one experiment config and write its result tables. Returns paths produced."""
    cfg = load_experiment_config(experiment)
    out_dir = out_dir or PATHS.results_tables
    out_dir.mkdir(parents=True, exist_ok=True)

    exp_id = cfg.get("id", experiment)
    models = cfg.get("models") or ([cfg["model"]] if "model" in cfg else [])
    seeds = cfg.get("seeds", [0])
    imgsz = int(cfg.get("imgsz", 640))
    tiers = cfg.get("hardware_tiers", [])

    if not models:
        raise ValueError(f"Experiment '{experiment}' lists no models.")

    log.info(
        "Running %s (%s): %d models, %d seeds%s",
        exp_id, "dry-run" if dry_run else "real", len(models), len(seeds),
        f", tiers={tiers}" if tiers else "",
    )

    result = BenchmarkResult(experiment=exp_id, dry_run=dry_run, models=list(models))

    # ── Accuracy (E1) ──
    raw_rows: list[dict] = []
    agg_rows: list[dict] = []
    for model in models:
        spec = get_model_spec(model)
        per_seed: list[AccuracyMetrics] = []
        for seed in seeds:
            metrics = (
                synthetic.synth_accuracy(model, seed)
                if dry_run
                else _real_accuracy(model, data_yaml, seed, imgsz)
            )
            per_seed.append(metrics)
            raw_rows.append(
                tables.accuracy_raw_row(exp_id, model, seed, metrics, simulated=dry_run)
            )
        agg_rows.append(
            tables.aggregate_accuracy(
                exp_id, model, per_seed, params_m=spec.approx_params_m, simulated=dry_run
            )
        )

    result.accuracy_raw_table = tables.write_table(raw_rows, out_dir / f"{exp_id}_accuracy_raw.csv")
    result.accuracy_table = tables.write_table(
        agg_rows, out_dir / f"{exp_id}_accuracy.csv", fieldnames=tables.ACCURACY_AGG_FIELDS
    )

    # ── Efficiency (E2) — only if the experiment declares hardware tiers ──
    if tiers:
        eff_rows = []
        for model in models:
            for tier in tiers:
                eff = (
                    synthetic.synth_efficiency(model, tier, imgsz)
                    if dry_run
                    else _real_efficiency(model, tier, imgsz)
                )
                row = eff.as_row()
                row["simulated"] = str(dry_run).lower()
                eff_rows.append(row)
        result.efficiency_table = tables.write_table(eff_rows, out_dir / f"{exp_id}_efficiency.csv")

    log.info(result.summary())
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Real-mode helpers (require the [train] extra + a dataset). Lazy + guarded.
# ─────────────────────────────────────────────────────────────────────────────
def _real_accuracy(model: str, data_yaml: Path | None, seed: int, imgsz: int) -> AccuracyMetrics:
    if data_yaml is None or not Path(data_yaml).is_file():
        raise FileNotFoundError(
            "Real benchmark needs a dataset data.yaml. Run 'neptravision data write-data-yaml' "
            "after building the dataset, or use --dry-run to validate the pipeline."
        )
    from ..evaluation.metrics import evaluate_ultralytics
    from ..training.train import train_one

    run = train_one(model, Path(data_yaml), seed=seed, imgsz=imgsz)
    weights = run.dir / "train" / "weights" / "best.pt"
    return evaluate_ultralytics(
        weights, Path(data_yaml), model_name=model, split="test", imgsz=imgsz
    )


def _real_efficiency(model: str, tier: str, imgsz: int):
    """Measure real latency with the shared protocol. Uses a blank image as input."""
    import numpy as np

    from ..evaluation.efficiency import benchmark_latency
    from ..prototype.inference import UltralyticsDetector

    spec = get_model_spec(model)
    detector = UltralyticsDetector(Path(spec.weights), imgsz=imgsz)
    sample = np.zeros((imgsz, imgsz, 3), dtype="uint8")
    return benchmark_latency(
        lambda x: detector.infer(x, 0, 0.0),
        sample,
        model=model, hardware_tier=tier, imgsz=imgsz, params_m=spec.approx_params_m,
    )
