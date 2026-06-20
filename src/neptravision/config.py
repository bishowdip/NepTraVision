"""Typed configuration: load YAML once, validate it, hand back plain objects.

Reviewers ask "what value did you use?" — the answer is always a file in
``configs/``, surfaced here as a validated object. We deliberately keep config
*loading* (this module) separate from config *use* (the pipeline modules).

The classes/dataset configs are validated with pydantic so a typo (e.g. a negative
threshold, or a split ratio that doesn't sum to 1) fails loudly at load time rather
than silently corrupting a run.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

from .paths import PATHS


# ─────────────────────────────────────────────────────────────────────────────
# Low-level YAML helpers
# ─────────────────────────────────────────────────────────────────────────────
def load_yaml(path: str | Path) -> dict[str, Any]:
    """Load a YAML file into a dict, with a clear error if it's missing."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Config not found: {p}")
    with p.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected a mapping at the top level of {p}, got {type(data)}")
    return data


def load_yaml_with_extends(path: str | Path) -> dict[str, Any]:
    """Load YAML, shallow-merging a parent referenced by an ``extends:`` key.

    Used by ``configs/models/*.yaml`` which extend ``_base.yaml``. Child keys win.
    Nested dicts are merged one level deep (enough for our ``train``/``augmentation``
    sections); deeper structures should be flattened rather than relying on magic.
    """
    p = Path(path)
    data = load_yaml(p)
    parent_ref = data.pop("extends", None)
    if parent_ref is None:
        return data
    parent = load_yaml_with_extends(p.parent / parent_ref)
    return _deep_merge(parent, data)


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Class taxonomy
# ─────────────────────────────────────────────────────────────────────────────
class ClassProfile(BaseModel):
    """One taxonomy profile (e.g. ``full`` 18-class or ``simple`` 3-class)."""

    description: str = ""
    names: dict[int, str]
    groups: dict[str, list[int]] = Field(default_factory=dict)

    @property
    def num_classes(self) -> int:
        return len(self.names)

    @property
    def ordered_names(self) -> list[str]:
        """Class names ordered by id — the order YOLO/Ultralytics expects."""
        return [self.names[i] for i in sorted(self.names)]

    @field_validator("names")
    @classmethod
    def _ids_contiguous_from_zero(cls, v: dict[int, str]) -> dict[int, str]:
        expected = set(range(len(v)))
        if set(v) != expected:
            raise ValueError(
                f"Class ids must be contiguous starting at 0; got {sorted(v)}"
            )
        return v


class ClassConfig(BaseModel):
    active_profile: str
    profiles: dict[str, ClassProfile]

    @model_validator(mode="after")
    def _active_exists(self) -> ClassConfig:
        if self.active_profile not in self.profiles:
            raise ValueError(
                f"active_profile '{self.active_profile}' not in {list(self.profiles)}"
            )
        return self

    @property
    def active(self) -> ClassProfile:
        return self.profiles[self.active_profile]


# ─────────────────────────────────────────────────────────────────────────────
# Dataset policy
# ─────────────────────────────────────────────────────────────────────────────
class SplitConfig(BaseModel):
    ratios: dict[str, float]
    group_by: str = "source_id"
    stratify_by: list[str] = Field(default_factory=list)
    seed: int = 42

    @model_validator(mode="after")
    def _ratios_sum_to_one(self) -> SplitConfig:
        total = sum(self.ratios.values())
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"split ratios must sum to 1.0, got {total}")
        return self


class ExtractionConfig(BaseModel):
    fps: float = 1.0
    image_format: str = "jpg"
    jpg_quality: int = 2


class DeduplicateConfig(BaseModel):
    hash: str = "phash"
    hash_size: int = 8
    threshold: int = 6


class SelectConfig(BaseModel):
    blur_min_variance: float = 100.0
    drop_empty: bool = True
    min_object_px: int = 15


class DatasetConfig(BaseModel):
    name: str = "NepTraVision-Bench"
    version: str = "0.0"
    extraction: ExtractionConfig = Field(default_factory=ExtractionConfig)
    deduplicate: DeduplicateConfig = Field(default_factory=DeduplicateConfig)
    select: SelectConfig = Field(default_factory=SelectConfig)
    split: SplitConfig
    quality_control: dict[str, Any] = Field(default_factory=dict)
    targets: dict[str, Any] = Field(default_factory=dict)


# ─────────────────────────────────────────────────────────────────────────────
# Public loaders (cached — configs don't change within a process)
# ─────────────────────────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def load_classes(path: str | Path | None = None) -> ClassConfig:
    return ClassConfig(**load_yaml(path or PATHS.classes_config))


@lru_cache(maxsize=1)
def load_dataset_config(path: str | Path | None = None) -> DatasetConfig:
    return DatasetConfig(**load_yaml(path or PATHS.dataset_config))


def load_model_config(name: str) -> dict[str, Any]:
    """Load a model config by short name (e.g. ``"yolov8n"``), resolving ``extends``."""
    return load_yaml_with_extends(PATHS.configs / "models" / f"{name}.yaml")


def load_experiment_config(name: str) -> dict[str, Any]:
    """Load an experiment config by short name (e.g. ``"e1_baselines"``)."""
    return load_yaml(PATHS.configs / "experiments" / f"{name}.yaml")
