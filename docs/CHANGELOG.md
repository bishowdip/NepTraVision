# Changelog

All notable changes to NepTraVision are recorded here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/). Dates are absolute.

## [0.1.0] — 2026-06-20 — Foundation (M0)

### Added
- Project structure (`src`-layout package, `configs/`, `docs/`, `data/`,
  `experiments/`, `results/`, `paper/`, `tests/`).
- Packaging: `pyproject.toml` with core + `train`/`serve`/`analysis`/`dev` extras,
  `requirements.txt`, `Makefile`, `LICENSE` (MIT), `CITATION.cff`, `.gitignore`,
  `.env.example`.
- Documentation set: project charter, code architecture, dataset guide, annotation
  guidelines, frozen class definitions, experiment protocol, reproducibility guide,
  ethics & privacy, dataset card, roadmap.
- ADRs: 0000 (record decisions), 0001 (scope & framing — reconcile the two source
  proposals into one paper).
- Configs: `classes.yaml` (18-class `full` + 3-class `simple` taxonomy),
  `dataset.yaml`, per-model configs, E1–E6 experiment configs.
- Package core: `config` (pydantic settings + YAML), `paths`, `logging_utils`, and a
  `typer` CLI (`neptravision`).
- Data pipeline (runnable): frame extraction (FFmpeg), perceptual-hash dedup, image
  selection, leakage-safe split-by-source, YOLO/COCO conversion, dataset stats,
  metadata manifest.
- Annotation tooling: inter-annotator agreement + label validation.
- Scaffolding with typed interfaces for training, evaluation, analysis, prototype.
- Test suite for the data-pipeline core.

### Decisions
- Merged Track A scope (18 classes + prototype) with Track B rigor (leakage-safe
  splits, multi-seed, multi-hardware, resolution/plate analysis). Paper claims =
  dataset + benchmark + analysis; prototype is deployment context. (ADR-0001)

### Next
- Collect footage (M1); implement training runner, efficiency/plate measurement,
  prototype wiring; begin literature review.
