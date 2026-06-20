"""The benchmark model registry.

Adding a model to the benchmark is a *declarative* act: drop a config in
``configs/models/<name>.yaml`` and it becomes available here. The ``framework`` field
tells the training/eval runners which backend to dispatch to (Ultralytics for the
YOLO family; a separate path for the non-YOLO contrast point). This keeps the runner
free of per-model ``if`` branches scattered through the code.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..config import load_model_config
from ..paths import PATHS


@dataclass(frozen=True)
class ModelSpec:
    """Everything the runners need to train/evaluate one model."""

    name: str
    framework: str          # "ultralytics" | "nanodet" | ...
    weights: str            # COCO-pretrained checkpoint to fine-tune from
    role: str               # human description of why it's in the benchmark
    approx_params_m: float
    raw: dict               # the full resolved config (train/augmentation/...)

    @property
    def train_cfg(self) -> dict:
        return self.raw.get("train", {})

    @property
    def augmentation_cfg(self) -> dict:
        return self.raw.get("augmentation", {})


def list_models() -> list[str]:
    """Names of all models declared under ``configs/models/`` (excluding ``_base``)."""
    return sorted(
        p.stem
        for p in (PATHS.configs / "models").glob("*.yaml")
        if not p.stem.startswith("_")
    )


def get_model_spec(name: str) -> ModelSpec:
    """Load and resolve one model's config into a :class:`ModelSpec`."""
    cfg = load_model_config(name)
    return ModelSpec(
        name=cfg.get("name", name),
        framework=cfg["framework"],
        weights=cfg["weights"],
        role=cfg.get("role", ""),
        approx_params_m=float(cfg.get("approx_params_m", 0.0)),
        raw=cfg,
    )


class _LazyRegistry:
    """Dict-like access to model specs, resolved on demand from config files."""

    def __getitem__(self, name: str) -> ModelSpec:
        return get_model_spec(name)

    def __iter__(self):
        return iter(list_models())

    def __contains__(self, name: str) -> bool:
        return name in list_models()


REGISTRY = _LazyRegistry()
