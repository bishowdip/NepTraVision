"""Tests for the Pareto-frontier computation behind the headline figure."""

from __future__ import annotations

from neptravision.analysis.pareto import Point, pareto_frontier


def test_dominated_point_excluded():
    # B is faster AND more accurate than A → A is dominated.
    a = Point("A", fps=10, accuracy=0.5)
    b = Point("B", fps=20, accuracy=0.6)
    front = pareto_frontier([a, b])
    assert front == [b]


def test_tradeoff_points_both_on_frontier():
    # Fast-but-less-accurate vs slow-but-more-accurate: neither dominates.
    fast = Point("fast", fps=30, accuracy=0.4)
    accurate = Point("accurate", fps=8, accuracy=0.7)
    front = pareto_frontier([fast, accurate])
    assert set(front) == {fast, accurate}
    # sorted by ascending fps
    assert front[0].fps <= front[1].fps


def test_frontier_with_equal_point():
    p1 = Point("p1", fps=10, accuracy=0.5)
    p2 = Point("p2", fps=10, accuracy=0.5)  # identical → neither strictly dominates
    front = pareto_frontier([p1, p2])
    assert len(front) == 2
