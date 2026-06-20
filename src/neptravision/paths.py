"""Canonical project paths.

Nothing in the codebase should hardcode ``"../data"`` or similar. Everything that
needs a location asks this module, so the layout can move (e.g. data onto an
external drive via ``NEPTRAVISION_DATA_ROOT``) without touching logic.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _find_project_root(start: Path | None = None) -> Path:
    """Walk upward from ``start`` until a directory containing ``pyproject.toml``.

    Falls back to two levels above this file (``src/neptravision/paths.py`` →
    project root) so things still work when the package is imported from an
    installed location during development with ``pip install -e .``.
    """
    here = (start or Path(__file__)).resolve()
    for parent in [here, *here.parents]:
        if (parent / "pyproject.toml").is_file():
            return parent
    return Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ProjectPaths:
    """Resolved, absolute paths for every well-known location in the repo."""

    root: Path

    # ── configuration ──
    @property
    def configs(self) -> Path:
        return self.root / "configs"

    @property
    def classes_config(self) -> Path:
        return self.configs / "classes.yaml"

    @property
    def dataset_config(self) -> Path:
        return self.configs / "dataset.yaml"

    # ── data (heavy; overridable via env) ──
    @property
    def data(self) -> Path:
        override = os.environ.get("NEPTRAVISION_DATA_ROOT")
        return Path(override).expanduser().resolve() if override else self.root / "data"

    @property
    def raw_videos(self) -> Path:
        return self.data / "raw_videos"

    @property
    def raw_frames(self) -> Path:
        return self.data / "raw_frames"

    @property
    def selected(self) -> Path:
        return self.data / "selected"

    @property
    def interim(self) -> Path:
        return self.data / "interim"

    @property
    def dataset(self) -> Path:
        return self.data / "dataset"

    @property
    def dataset_images(self) -> Path:
        return self.dataset / "images"

    @property
    def dataset_labels(self) -> Path:
        return self.dataset / "labels"

    @property
    def dataset_splits(self) -> Path:
        return self.dataset / "splits"

    @property
    def metadata_csv(self) -> Path:
        return self.dataset / "metadata.csv"

    # ── outputs ──
    @property
    def experiments(self) -> Path:
        override = os.environ.get("NEPTRAVISION_EXPERIMENTS_ROOT")
        return (
            Path(override).expanduser().resolve()
            if override
            else self.root / "experiments"
        )

    @property
    def results(self) -> Path:
        return self.root / "results"

    @property
    def results_tables(self) -> Path:
        return self.results / "tables"

    @property
    def results_figures(self) -> Path:
        return self.results / "figures"

    def ensure(self, *paths: Path) -> None:
        """Create the given directories if missing (used by pipeline commands)."""
        for p in paths:
            p.mkdir(parents=True, exist_ok=True)


# A single shared instance is the normal way to use this module.
PATHS = ProjectPaths(root=_find_project_root())
