# `results/` — committed tables and figures for the paper

Unlike `experiments/` (raw, gitignored run outputs), this directory holds the
**curated, paper-ready** artifacts — and these *are* committed, because they're small
and they're what the manuscript cites.

```text
results/
├── tables/    ← table1_accuracy.csv, table2_efficiency.csv, table3_resolution.csv, …
└── figures/   ← pareto_<tier>.png, condition_breakdown.png, plate_legibility.png, …
```

Regenerate everything from raw runs with the analysis commands (see
`docs/06_reproducibility.md`). The mapping table → source experiment is documented in
`docs/05_experiment_protocol.md`.
