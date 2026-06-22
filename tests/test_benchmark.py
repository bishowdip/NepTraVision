"""Tests for the benchmark orchestration: dry-run runner, tables, and Pareto join."""

from __future__ import annotations

from pathlib import Path

from neptravision.analysis.pareto import load_pareto_points, pareto_frontier
from neptravision.benchmark import synthetic, tables
from neptravision.benchmark.runner import run_benchmark
from neptravision.benchmark.tables import aggregate_accuracy, read_table


# ── synthetic metrics ──
def test_synth_accuracy_is_deterministic():
    a = synthetic.synth_accuracy("yolov8n", 0)
    b = synthetic.synth_accuracy("yolov8n", 0)
    assert a == b
    assert 0.0 <= a.map50 <= 0.95


def test_synth_efficiency_tier_ordering():
    # GPU should be faster than CPU, which should be faster than a Raspberry Pi.
    gpu = synthetic.synth_efficiency("yolov8n", "gpu_t4")
    cpu = synthetic.synth_efficiency("yolov8n", "cpu_laptop")
    pi = synthetic.synth_efficiency("yolov8n", "rpi5")
    assert gpu.fps > cpu.fps > pi.fps


def test_bigger_model_slower_than_nano():
    nano = synthetic.synth_efficiency("yolov8n", "cpu_laptop")
    small = synthetic.synth_efficiency("yolov8s", "cpu_laptop")
    assert nano.fps > small.fps  # 3.2M vs 11.2M params


# ── aggregation ──
def test_aggregate_accuracy_mean_std():
    runs = [synthetic.synth_accuracy("yolov8n", s) for s in (0, 1, 2)]
    row = aggregate_accuracy("e1", "yolov8n", runs, params_m=3.2, simulated=True)
    assert row["model"] == "yolov8n"
    assert row["n_seeds"] == 3
    assert 0.0 <= row["map50_mean"] <= 1.0
    assert row["simulated"] == "true"


# ── full dry-run runner ──
def test_run_benchmark_dryrun_efficiency(tmp_path: Path):
    res = run_benchmark("e2_efficiency", dry_run=True, out_dir=tmp_path)
    assert res.dry_run
    assert res.accuracy_table.is_file()
    assert res.efficiency_table.is_file()

    acc = read_table(res.accuracy_table)
    assert {r["model"] for r in acc} == set(res.models)
    assert all(r["simulated"] == "true" for r in acc)

    eff = read_table(res.efficiency_table)
    # one row per (model × tier); e2 declares 3 tiers
    assert len(eff) == len(res.models) * 3


def test_run_benchmark_dryrun_accuracy_only(tmp_path: Path):
    # e1_baselines has seeds but no hardware tiers → no efficiency table
    res = run_benchmark("e1_baselines", dry_run=True, out_dir=tmp_path)
    assert res.efficiency_table is None
    raw = read_table(res.accuracy_raw_table)
    # 5 models × 3 seeds
    assert len(raw) == 15


# ── Pareto join ──
def test_pareto_join_and_frontier(tmp_path: Path):
    res = run_benchmark("e2_efficiency", dry_run=True, out_dir=tmp_path)
    points = load_pareto_points(res.accuracy_table, res.efficiency_table, "cpu_laptop")
    assert len(points) == len(res.models)
    frontier = pareto_frontier(points)
    assert 1 <= len(frontier) <= len(points)
    # frontier sorted by ascending fps
    assert frontier == sorted(frontier, key=lambda p: p.fps)


def test_write_and_read_table_roundtrip(tmp_path: Path):
    rows = [{"a": 1, "b": "x"}, {"a": 2, "b": "y"}]
    path = tables.write_table(rows, tmp_path / "t.csv")
    back = read_table(path)
    assert back[0]["a"] == "1" and back[1]["b"] == "y"
