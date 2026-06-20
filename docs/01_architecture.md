# Code Architecture

> How the repository is organised and *why*, so that adding code never means
> guessing where it goes. Read alongside [`00_project_charter.md`](00_project_charter.md).

## 1. Guiding principles

1. **The dataset is the contribution.** Code exists to produce, validate, and
   measure a dataset and models — not the other way round. The `data/` pipeline gets
   the most engineering care.
2. **`src`-layout, installable package.** Everything importable lives under
   `src/neptravision/`. No `sys.path` hacks, no scripts importing siblings by
   relative path. Install with `pip install -e .` and `import neptravision`.
3. **Config over code.** Anything a reviewer might ask "what value did you use?" is
   a YAML file in `configs/`, not a magic number in a function. Configs are the
   reproducibility surface.
4. **Pure core, thin shell.** Library functions are pure and testable; the CLI
   (`cli.py`) and the FastAPI app are thin shells that call them. This keeps the
   science unit-testable without a server or a GPU.
5. **Light core, heavy extras.** Core deps (data pipeline + CLI) run on any laptop.
   `torch`/`ultralytics` (`[train]`), `fastapi` (`[serve]`), and plotting
   (`[analysis]`) are *optional* groups, imported lazily so the data tooling never
   pulls a GPU stack.
6. **Reproducible by construction.** Seeds, configs, and run metadata are logged
   with every experiment. See [`06_reproducibility.md`](06_reproducibility.md).

## 2. Module map and responsibilities

```text
src/neptravision/
├── config.py          Typed settings (pydantic) + YAML loading. Single entry to all config.
├── paths.py           Canonical project paths. Nothing hardcodes "../data".
├── logging_utils.py   Rich-backed logger; one configuration point.
├── cli.py             `neptravision` Typer app. Thin: parses args → calls library.
│
├── data/              ── THE PIPELINE ──  (raw footage → release-ready dataset)
│   ├── frame_extraction.py   FFmpeg wrapper: video → frames at controlled FPS.
│   ├── deduplicate.py        Perceptual-hash near-duplicate removal.
│   ├── select.py             Keep/drop heuristics (blur, emptiness) for curation.
│   ├── manifest.py           metadata.csv: per-image source/location/time/weather/res.
│   ├── splits.py             LEAKAGE-SAFE split by source-group (critical).
│   ├── convert.py            YOLO ⇄ COCO label conversion; build Ultralytics data.yaml.
│   └── stats.py              Class distribution, condition coverage, image counts.
│
├── annotation/        ── DATASET QUALITY ──
│   ├── agreement.py          Inter-annotator IoU + label agreement on a QC subset.
│   └── validate.py           Sanity checks: out-of-range boxes, bad class ids, orphans.
│
├── models/            ── MODEL ZOO ──
│   └── registry.py           Declarative registry of benchmark models + metadata.
│
├── training/          ── FINE-TUNING ──
│   └── train.py              Runner: COCO-pretrained → fine-tune on NepTraVision.
│
├── evaluation/        ── MEASUREMENT ──
│   ├── metrics.py            Accuracy: mAP@.5, mAP@.5:.95, P/R/F1, per-class AP, CM.
│   ├── efficiency.py         Latency/FPS/params/FLOPs/size/RAM per hardware tier.
│   ├── condition_breakdown.py  Accuracy sliced by day/night, weather, density.
│   └── plate_resolution.py   E6: plate px-height vs. OCR legibility threshold.
│
├── analysis/          ── INSIGHT ──
│   ├── pareto.py             Accuracy-vs-FPS Pareto frontier plots per hardware tier.
│   └── error_analysis.py     Qualitative + quantitative failure-mode aggregation.
│
└── prototype/         ── DEPLOYMENT CONTEXT (not a paper claim) ──
    ├── app.py                FastAPI: REST + WebSocket endpoints.
    ├── inference.py          Detector wrapper (mock-able) for the live demo.
    ├── tracking.py           Simple counting/tracking over the stream.
    ├── schemas.py            Pydantic request/response/event models.
    └── web/                  Static dashboard assets.
```

## 3. Data flow

```text
configs/  ─────────────────────────────────────────────────────────────┐
   (classes.yaml, dataset.yaml, models/*, experiments/*)                │ read by everything
                                                                        ▼
raw_videos/ ──extract──▶ raw_frames/ ──dedup+select──▶ selected/ ──annotate(external tool)──▶
   labels ──validate+agreement──▶ convert(YOLO) ──make-splits(by source)──▶ data/dataset/{images,labels}/{train,val,test}
                                                                        │
                                              training/ ◀── data.yaml ──┘
                                                  │ fine-tune × seeds × models
                                                  ▼
                                            experiments/<run>/weights, curves, args
                                                  │
                       evaluation/ ──▶ results/tables/*.csv ──▶ analysis/ ──▶ results/figures/*.png ──▶ paper/
```

The dashed boundary between **library code** (pure, tested) and **CLI / server
shells** (thin) is the most important architectural line in the repo: it is what
lets the science be tested without a GPU or a browser.

## 4. Where does new code go? (decision shortcuts)

| You are adding… | Put it in… |
|---|---|
| A new data-cleaning step | `data/`, expose as a `neptravision data …` subcommand |
| A new metric | `evaluation/metrics.py` |
| A new model to benchmark | a row in `models/registry.py` + a config in `configs/models/` |
| A new experiment | a YAML in `configs/experiments/` + a runner that reads it |
| A plot for the paper | `analysis/`, write output to `results/figures/` |
| A tunable number | a key in the relevant `configs/*.yaml` — never a literal in code |

## 5. Conventions

- **Style:** `ruff` (lint + format), `mypy` (types). `make lint fmt typecheck`.
- **Type hints everywhere** in `src/`. Public functions get docstrings explaining
  *why*, not *what*.
- **No notebooks in the import path.** Notebooks in `notebooks/` are for exploration
  and call into `neptravision`; they never define reusable logic.
- **Outputs are addressable.** Every run writes to `experiments/<timestamp>_<name>/`
  with the resolved config saved alongside.
