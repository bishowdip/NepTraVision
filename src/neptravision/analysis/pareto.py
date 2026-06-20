"""The headline figure: the accuracy-vs-FPS Pareto frontier per hardware tier.

*"The best detector you can actually run at a Nepali checkpoint."* A model is on the
frontier if no other model is both faster **and** more accurate. The frontier
computation is pure and unit-tested; plotting is a thin, lazy matplotlib wrapper
(``analysis`` extra) that writes a PNG into ``results/figures/``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..logging_utils import get_logger

log = get_logger(__name__)


@dataclass(frozen=True)
class Point:
    """One model on the accuracy/speed plane."""

    label: str
    fps: float        # x-axis: higher is better (faster)
    accuracy: float   # y-axis: higher is better (e.g. mAP@0.5)


def pareto_frontier(points: list[Point]) -> list[Point]:
    """Return the Pareto-optimal points (maximise both fps and accuracy).

    A point is dominated if another point is ≥ on both axes and strictly greater on
    at least one. The frontier is returned sorted by ascending FPS for easy plotting.
    """
    frontier: list[Point] = []
    for p in points:
        dominated = any(
            (q.fps >= p.fps and q.accuracy >= p.accuracy)
            and (q.fps > p.fps or q.accuracy > p.accuracy)
            for q in points
            if q is not p
        )
        if not dominated:
            frontier.append(p)
    return sorted(frontier, key=lambda pt: pt.fps)


def plot_pareto(
    points: list[Point],
    out_path: Path,
    *,
    title: str = "Accuracy vs. FPS",
    xlabel: str = "FPS",
    ylabel: str = "mAP@0.5",
) -> Path:
    """Scatter all models, highlight + connect the frontier, and save a PNG."""
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover - optional extra
        raise RuntimeError('matplotlib not installed. pip install -e ".[analysis]"') from exc

    frontier = pareto_frontier(points)
    frontier_set = set(frontier)

    fig, ax = plt.subplots(figsize=(7, 5))
    for p in points:
        on_front = p in frontier_set
        ax.scatter(p.fps, p.accuracy, s=70, zorder=3,
                   color="#d62728" if on_front else "#7f7f7f")
        ax.annotate(p.label, (p.fps, p.accuracy),
                    textcoords="offset points", xytext=(6, 4), fontsize=9)
    if len(frontier) > 1:
        ax.plot([p.fps for p in frontier], [p.accuracy for p in frontier],
                "--", color="#d62728", zorder=2, label="Pareto frontier")
        ax.legend()

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
    log.info("Pareto figure → %s", out_path)
    return out_path
