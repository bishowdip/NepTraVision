# Changelog

All notable changes to NepTraVision are recorded here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/). Dates are absolute.

## [Unreleased] — 2026-06-21 — Literature review (Week 2, M0)

### Added
- `docs/08_literature_review.md`: thematic synthesis across the five review areas
  (detectors, edge benchmarking, regional-traffic datasets & geographic bias, helmet
  detection, traffic-sign recognition) plus the Nepali context and the IOEGC gap.
  Includes a reproducible search strategy, an evidenced 5-link gap argument (the
  Introduction's spine), a reference→section map, and a tiered reading priority.
- `paper/references.bib`: seed bibliography. Canonical detector/dataset works verified;
  regional/recent entries flagged `VERIFY` for author/venue confirmation before
  submission; Tier-3 "to find" sources listed.
- `docs/literature_matrix.csv`: living per-paper reading matrix, pre-populated with
  the works surfaced during the review.

### Notes
- Key gap evidence: Nepali traffic CV exists only for *license plates* (Pant 2015;
  Devanagari ANPR), while regional precedent (IDD, DriveIndia, UVH-26) shows Western
  benchmarks fail on South-Asian unstructured traffic — and no public Nepali traffic
  *detection* dataset/benchmark exists. This underwrites contributions C1–C3.

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
