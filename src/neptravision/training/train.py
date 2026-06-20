"""Fine-tune one model (one seed) on NepTraVision-Bench.

The runner dispatches on the model's ``framework``. The Ultralytics path is fully
wired; the non-YOLO path raises a clear ``NotImplementedError`` until that backend is
added (it needs its own training harness, out of scope for the first models). Every
run is wrapped in a :class:`~neptravision.run.RunContext` so weights, curves, and
metrics land in a reproducible, provenance-stamped directory.

Requires the ``train`` extra:  pip install -e ".[train]"
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..logging_utils import get_logger
from ..models.registry import ModelSpec, get_model_spec
from ..run import RunContext

log = get_logger(__name__)


def train_one(
    model_name: str,
    data_yaml: Path,
    *,
    seed: int = 0,
    imgsz: int | None = None,
    extra_overrides: dict[str, Any] | None = None,
) -> RunContext:
    """Fine-tune ``model_name`` from its COCO-pretrained weights on ``data_yaml``.

    Returns the :class:`RunContext`; trained weights live under ``<run.dir>/weights``.
    """
    spec = get_model_spec(model_name)
    run_name = f"{model_name}_imgsz{imgsz or spec.train_cfg.get('imgsz')}_seed{seed}"

    resolved = {
        "model": spec.name,
        "framework": spec.framework,
        "weights": spec.weights,
        "data_yaml": str(data_yaml),
        "seed": seed,
        "train": spec.train_cfg,
        "augmentation": spec.augmentation_cfg,
        **(extra_overrides or {}),
    }
    run = RunContext.create(run_name, config=resolved)

    if spec.framework == "ultralytics":
        metrics = _train_ultralytics(spec, data_yaml, run, seed=seed, imgsz=imgsz,
                                     extra_overrides=extra_overrides)
    else:
        raise NotImplementedError(
            f"Training backend '{spec.framework}' for model '{model_name}' is not wired "
            "yet. The YOLO family runs via Ultralytics; add the non-YOLO harness here."
        )

    run.write_metrics(metrics)
    return run


def _train_ultralytics(
    spec: ModelSpec,
    data_yaml: Path,
    run: RunContext,
    *,
    seed: int,
    imgsz: int | None,
    extra_overrides: dict[str, Any] | None,
) -> dict[str, Any]:
    """Ultralytics fine-tuning. Lazily imports ultralytics so the core stays light."""
    try:
        from ultralytics import YOLO
    except ImportError as exc:  # pragma: no cover - depends on optional extra
        raise RuntimeError(
            "ultralytics is not installed. Run:  pip install -e \".[train]\""
        ) from exc

    train_cfg = dict(spec.train_cfg)
    aug_cfg = dict(spec.augmentation_cfg)
    if imgsz is not None:
        train_cfg["imgsz"] = imgsz
    train_cfg["seed"] = seed

    model = YOLO(spec.weights)
    results = model.train(
        data=str(data_yaml),
        project=str(run.dir),
        name="train",
        exist_ok=True,
        **train_cfg,
        **aug_cfg,
        **(extra_overrides or {}),
    )

    # Surface the headline numbers into metrics.json (full curves stay in run.dir).
    metrics = dict(results.results_dict) if hasattr(results, "results_dict") else {}
    log.info("Training complete for %s (seed %d).", spec.name, seed)
    return {"model": spec.name, "seed": seed, "results": metrics}
