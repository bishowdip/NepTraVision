"""The benchmark orchestration layer — turns experiment configs into result tables.

This package is the bridge between *what to run* (``configs/experiments/*.yaml``) and
*the numbers the paper reports* (``results/tables/*.csv`` → ``results/figures/*``):

    configs/experiments/e1_baselines.yaml
        → runner.run_benchmark()  (models × seeds × hardware tiers)
            → benchmark/tables.py  (write/aggregate CSVs)
                → analysis/pareto.py  (the headline figure)

It supports a ``dry_run`` mode that fabricates deterministic, *clearly-labelled*
metrics derived from each model's real parameter count, so the entire pipeline —
orchestration, aggregation, table writing, and plotting — runs and is tested without
torch/Ultralytics or a dataset. Real mode swaps the synthetic calls for training +
evaluation. Simulated rows always carry ``simulated=true`` so they can never be mistaken
for measured results.
"""
