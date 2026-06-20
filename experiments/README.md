# `experiments/` — run outputs (gitignored)

Every training/evaluation run creates a timestamped, provenance-stamped directory
here via `neptravision.run.RunContext`. Contents are **not** committed (they're large
and reproducible); only this README is tracked.

```text
experiments/2026-08-15T091200Z_yolov8n_imgsz640_seed0/
├── config.resolved.yaml   ← exact config after merges/overrides
├── git.txt                ← commit hash + dirty flag
├── env.txt                ← python + pip freeze
├── metrics.json           ← the numbers this run produced
├── train/                 ← Ultralytics run dir (weights/, curves, args)
└── ...
```

See `docs/06_reproducibility.md` for the run-metadata contract. Trained weights are
uploaded with the dataset/model release, not stored in git.
