"""Run context — the reproducibility contract, in code.

Every experiment (training or evaluation) opens a :class:`RunContext`, which creates
``experiments/<timestamp>_<name>/`` and records exactly what
``docs/06_reproducibility.md`` promises: the resolved config, the git commit, the
environment, and a metrics file. If a number in the paper can't be traced back to
one of these directories, that's a bug.
"""

from __future__ import annotations

import json
import platform
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .logging_utils import get_logger
from .paths import PATHS

log = get_logger(__name__)


def _git(*args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *args], cwd=PATHS.root, stderr=subprocess.DEVNULL, text=True
        ).strip()
    except Exception:  # noqa: BLE001 — git may be absent or repo uninitialised
        return ""


def _pip_freeze() -> str:
    try:
        return subprocess.check_output(
            [sys.executable, "-m", "pip", "freeze"], text=True, stderr=subprocess.DEVNULL
        )
    except Exception:  # noqa: BLE001
        return ""


@dataclass
class RunContext:
    name: str
    dir: Path

    @classmethod
    def create(cls, name: str, config: dict[str, Any] | None = None) -> RunContext:
        """Create a timestamped run directory and write provenance files."""
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
        run_dir = PATHS.experiments / f"{ts}_{name}"
        run_dir.mkdir(parents=True, exist_ok=True)

        # git provenance
        commit = _git("rev-parse", "HEAD")
        dirty = bool(_git("status", "--porcelain"))
        (run_dir / "git.txt").write_text(
            f"commit: {commit or '(no git)'}\ndirty: {dirty}\n", encoding="utf-8"
        )

        # environment provenance
        (run_dir / "env.txt").write_text(
            f"python: {sys.version}\nplatform: {platform.platform()}\n\n{_pip_freeze()}",
            encoding="utf-8",
        )

        if config is not None:
            with (run_dir / "config.resolved.yaml").open("w", encoding="utf-8") as fh:
                yaml.safe_dump(config, fh, sort_keys=False)

        log.info("Run dir: %s", run_dir)
        return cls(name=name, dir=run_dir)

    def write_metrics(self, metrics: dict[str, Any]) -> Path:
        out = self.dir / "metrics.json"
        out.write_text(json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8")
        log.info("Metrics written → %s", out)
        return out
