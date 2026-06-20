# Reproducibility

> "A reproducible benchmark is half the paper's value." Everything below exists so a
> stranger (or you, in six months) can regenerate every number.

## 1. What gets released

- **Dataset** (Zenodo DOI + Hugging Face): images, YOLO labels, `metadata.csv`,
  split definition, dataset card, annotation guidelines, LICENSE.
- **Code** (this repo): pipeline, training, evaluation, configs.
- **Configs**: every `configs/*.yaml` used, with no hidden defaults.
- **Trained weights**: per model × seed, with the exact training args.
- **Exact eval scripts** and the seeds used.

## 2. Determinism rules

- Global seed in `.env` (`NEPTRAVISION_SEED`); per-experiment seeds in the
  experiment YAML override it. Benchmark runs use **3 seeds** and report mean ± std.
- Every run writes to `experiments/<timestamp>_<name>/` containing: the **resolved**
  config (after merges), the git commit hash, the environment (`pip freeze`), and
  the metrics. Nothing is left implicit.
- Augmentation is identical across models (declared once, referenced by config).

## 3. Run-metadata contract

Each experiment directory must contain:

```text
experiments/2026-08-15_e1_yolov8n_seed0/
├── config.resolved.yaml     # the exact config after all merges/overrides
├── env.txt                  # pip freeze + python/cuda versions
├── git.txt                  # commit hash + dirty flag
├── metrics.json             # all numbers this run produced
├── weights/best.pt          # (gitignored; uploaded to release)
└── curves/                  # loss/metric curves
```

## 4. The split is frozen and shipped

The leakage-safe split (by source-group) is computed once and written to
`data/dataset/splits/` as an explicit list of which source-groups are train/val/test.
It is committed (it's small text) so the exact partition is reproducible regardless
of file ordering. Re-running `make-splits` with the same seed + manifest reproduces it.

## 5. Reproduce-from-scratch checklist

```bash
pip install -e ".[train,analysis,dev]"   # pinned via pyproject lower bounds
neptravision data validate-labels data/dataset/labels
neptravision data stats                  # confirms class counts match the card
neptravision train --config configs/experiments/e1_baselines.yaml   # M2+
neptravision eval  --config configs/experiments/e1_baselines.yaml
neptravision analyze pareto              # regenerates results/figures/pareto_*.png
```

## 6. Versioning

- **Code:** semantic-ish (`0.1.0` = foundation). Tag the commit used for the paper.
- **Dataset:** versioned independently (`NepTraVision-Bench v1.0`); the dataset card
  records the version, size, and date.
