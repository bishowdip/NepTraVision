"""Model zoo: the declarative registry of detectors in the benchmark."""

from .registry import REGISTRY, ModelSpec, get_model_spec, list_models

__all__ = ["REGISTRY", "ModelSpec", "get_model_spec", "list_models"]
