# Changelog

All notable changes to NepTraVision are recorded here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/). Dates are absolute.

## [Unreleased] — 2026-06-22 — Benchmark pipeline wired (M2–M4 plumbing)

### Added
- `neptravision/benchmark/`: orchestration layer — `runner.run_benchmark()` reads an
  experiment config and writes result tables (`tables.py`), with a `--dry-run` mode
  backed by deterministic, param-count-derived synthetic metrics (`synthetic.py`) so the
  whole flow runs without torch/Ultralytics or a dataset.
- CLI: `neptravision benchmark --experiment <id> [--dry-run]`, `neptravision eval`, and
  `neptravision analyze pareto` (one figure per hardware tier).
- `analysis/pareto.load_pareto_points()`: joins the accuracy + efficiency tables on model
  for a given hardware tier.
- 8 benchmark tests (synthetic determinism, tier ordering, aggregation, full dry-run,
  Pareto join + frontier, table round-trip). Suite now 36 tests.

### Notes
- Real mode (no `--dry-run`) trains + evaluates via Ultralytics and measures latency with
  the shared protocol; it needs the dataset (`data.yaml`) and the `[train]` extra.
- Verified end-to-end in dry-run: E2 → accuracy/efficiency tables → 3 Pareto figures
  (one per tier), with dominated models correctly excluded from the frontier. Simulated
  outputs are tagged `simulated=true` and are **not** committed to `results/`.

## [Unreleased] — 2026-06-21 — Capture log for phone footage (M1 prep)

### Added
- `neptravision/data/capture_log.py` + `neptravision data probe-videos`: read embedded
  video metadata (capture time → time_of_day, GPS, resolution, fps, device) from
  `data/raw_videos/` via ffprobe into a per-video `capture_log.csv`. Solves "my phone
  doesn't overlay time/location" — that data is in the file; only weather & density need
  manual entry.
- `build_template`/`data build-manifest --from-capture-log`: each frame inherits its
  source video's conditions, so conditions are logged once per video, not per frame.
- iPhone field-capture guidance in `data/README.md`; tests for the pure helpers.

## [Unreleased] — 2026-06-21 — Nepal landscape & feasibility study

### Added
- `docs/09_nepal_landscape.md`: Nepal-first dossier — road-safety motivation (with
  figures), an inventory of existing Nepali datasets/models/works, regional precedent
  (IDD/DriveIndia/UVH-26/Bangladesh/RideSafe), infrastructure context, six enumerated
  evidence-backed gaps (G1–G6), a flagged issue/risk list, and issue→solution actions.
- `docs/10_feasibility_study.md`: per-task feasibility verdict (GO), with data, legal
  (Privacy Act 2075), compute, skills, timeline, and publication assessments + a risk
  register.
- `docs/nepal_assets_inventory.csv`: machine-readable inventory of existing Nepali
  assets and their usefulness/verification status.
- `docs/decisions/0002-anpr-reframing-embossed-plates.md` (ADR-0002): reframe E6/ANPR
  around plate *resolution* rather than Devanagari *script*, given Nepal's mandatory
  ANPR-ready embossed-plate rollout (Sept 2025).
- Nepal-context citations added to `paper/references.bib`.

### Key findings
- No public detection-grade Nepali traffic dataset exists; the closest asset
  (vehicles-nepal, 4,797 imgs) is classification-only with 2 coarse classes → confirms C1.
- Nepali CV community is active (IOEGC: sign-language, medical) but absent on *traffic
  detection* → gap sharpened to "no traffic-detection CV / no Nepali traffic dataset."
- Motorcycles are ~79–84% of vehicles and ~2/3 of fatal crashes → the vehicle+helmet
  focus is the highest-impact, data-backed choice.

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
