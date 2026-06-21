<div align="center">

# 🛺 NepTraVision

**A Nepal-Specific Traffic Computer-Vision Benchmark and Lightweight Detection System**
*for Vehicle Counting, Helmet Compliance, and Traffic-Sign Recognition*

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Code License: MIT](https://img.shields.io/badge/code-MIT-green.svg)](LICENSE)
[![Dataset License: CC BY-NC 4.0](https://img.shields.io/badge/dataset-CC%20BY--NC%204.0-lightgrey.svg)](docs/dataset_card.md)
[![Status: Foundation](https://img.shields.io/badge/status-foundation-orange.svg)](#-project-status-living)

</div>

---

## 📌 What this is, in one paragraph

Nepalese roads are *their own computer-vision problem*: motorcycle-dominated mixed
traffic, local vehicle types (tempo, microbus, e-rickshaw), dense occlusion,
undisciplined lanes, monsoon/low-light conditions, and low-resolution CCTV.
Detectors trained on Western datasets degrade here and **nobody has measured by how
much**. NepTraVision contributes three things a system alone cannot: a **curated,
annotated Nepali traffic dataset**, a **controlled accuracy–efficiency benchmark**
across detectors and hardware tiers, and an **honest failure & resolution
analysis** (including the resolution threshold at which licence-plate OCR even
becomes feasible). A FastAPI/WebSocket prototype demonstrates deployment — but the
*paper's claim is the dataset + benchmark + analysis*, not the dashboard.

> **This is a first research paper, and it is meant to be done well.** Every line of
> code here is written to be read by a human reviewer, every decision is documented,
> and the whole pipeline is reproducible end-to-end.

---

## 🎯 The three contributions (what the paper claims)

| # | Contribution | Artifact |
|---|--------------|----------|
| **C1** | **NepTraVision-Bench dataset** — first public annotated dataset for vehicle / helmet / sign detection in Nepali mixed traffic, spanning multiple conditions. | `data/dataset/`, [dataset card](docs/dataset_card.md) |
| **C2** | **Edge-efficiency benchmark** — leakage-safe comparison of real-time detectors across hardware tiers (GPU / CPU / Raspberry Pi); the accuracy–efficiency Pareto frontier for this context. | `src/neptravision/evaluation/`, `results/` |
| **C3** | **Failure & resolution analysis** — detection errors by condition + a quantified plate-legibility resolution threshold (the ANPR blocker, turned into evidence). | `src/neptravision/analysis/`, `results/` |

We are **not** claiming a new detector architecture. The novelty is in *data +
measurement* for an underrepresented setting — a legitimate, reviewable,
first-author contribution. See [`docs/decisions/0001-scope-and-framing.md`](docs/decisions/0001-scope-and-framing.md)
for why we framed it this way.

---

## 🗺️ Repository map

```text
NepTraVision/
├── README.md                  ← you are here (vision + living status)
├── pyproject.toml             ← package, deps (core / train / serve / analysis / dev)
├── Makefile                   ← make help
├── configs/                   ← single source of truth for everything tunable
│   ├── classes.yaml           ← the canonical class taxonomy (18 classes)
│   ├── dataset.yaml           ← collection / split / quality-control policy
│   ├── models/                ← per-model training configs (yolov8n, yolov8s, …)
│   └── experiments/           ← E1–E6 experiment definitions
├── src/neptravision/          ← the Python package (src-layout, importable)
│   ├── cli.py                 ← `neptravision …` command-line entry point
│   ├── config.py paths.py logging_utils.py
│   ├── data/                  ← collect → extract → dedup → select → split → convert
│   ├── annotation/            ← agreement metrics + label validation
│   ├── models/                ← model registry / zoo
│   ├── training/              ← fine-tuning runner
│   ├── evaluation/            ← accuracy, efficiency, condition breakdown, plate study
│   ├── analysis/              ← Pareto plots, error analysis
│   └── prototype/             ← FastAPI + WebSocket demo dashboard
├── data/                      ← heavy artifacts (gitignored; structure tracked)
├── experiments/               ← run outputs: weights, logs, curves (gitignored)
├── results/                   ← committed tables + figures for the paper
├── paper/                     ← the manuscript itself
├── docs/                      ← charter, architecture, guides, ADRs, dataset card
├── scripts/ notebooks/ tests/
```

Full rationale for the layout: [`docs/01_architecture.md`](docs/01_architecture.md).

---

## 🚀 Quickstart

```bash
# 1. Create an environment (any of conda / venv works; example with venv)
python -m venv .venv && source .venv/bin/activate

# 2. Install the core data pipeline + CLI (laptop, no GPU needed)
make install            # == pip install -e .

# 3. See what the CLI can do
neptravision --help

# 4. The data pipeline, end to end (once you have footage in data/raw_videos/)
neptravision data extract-frames   --fps 1
neptravision data deduplicate      --threshold 6
neptravision data make-splits      --by source
neptravision data stats

# Training (on a GPU box) and serving the dashboard use the optional extras:
pip install -e ".[train]"   # ultralytics + torch
pip install -e ".[serve]"   # fastapi + uvicorn
```

> 📍 The data folders ship empty (only `.gitkeep`). Drop your footage into
> `data/raw_videos/` to start. See [`data/README.md`](data/README.md).

---

## 🧭 The pipeline (mental model)

```text
        COLLECT            BUILD DATASET                 BENCHMARK                 ANALYSE & SHIP
   ┌──────────────┐   ┌────────────────────┐   ┌──────────────────────┐   ┌────────────────────┐
   │ raw_videos/  │   │ extract → dedup →   │   │ fine-tune model zoo  │   │ Pareto frontier    │
   │ (+ metadata, │──▶│ select → annotate → │──▶│ × seeds × hardware × │──▶│ condition errors   │
   │  privacy)    │   │ QC → leakage-safe   │   │ resolutions; metrics │   │ plate-px threshold │
   │              │   │ splits → card       │   │ + efficiency + INT8  │   │ → tables, figures  │
   └──────────────┘   └────────────────────┘   └──────────────────────┘   └─────────┬──────────┘
                                                                                     │
                                                                  ┌──────────────────▼─────────────┐
                                                                  │ prototype: FastAPI + WebSocket │
                                                                  │ dashboard (deployment context) │
                                                                  └────────────────────────────────┘
```

---

## 📈 Project status (living)

> **Convention:** this section is updated every working session. `✅ done ·
> 🚧 in progress · ⬜ not started`. The week numbering follows
> [`docs/roadmap.md`](docs/roadmap.md).

### Milestones

| Phase | Goal | Status |
|------|------|:------:|
| **M0 — Foundation** | Repo, architecture, docs, configs, runnable data pipeline skeleton | 🚧 |
| **M1 — Dataset v0** | ≥1,500 annotated images, QC'd, leakage-safe splits, dataset card | ⬜ |
| **M2 — Baselines** | Fine-tune model zoo; accuracy table (3 seeds, mean±std) | ⬜ |
| **M3 — Efficiency** | CPU / Pi / GPU sweep; resolution sweep; INT8 quantization | ⬜ |
| **M4 — Analysis** | Pareto frontier, condition breakdown, plate-resolution sub-study | ⬜ |
| **M5 — Prototype** | Trained model wired into FastAPI + WebSocket dashboard | ⬜ |
| **M6 — Paper** | Manuscript, figures, references, supervisor review, submission | ⬜ |

### What's done so far (M0)

- ✅ **Nepal landscape & feasibility study:** Nepal-first inventory of existing datasets,
  models, and works; six enumerated, evidence-backed gaps (G1–G6); a risk register with
  mitigations; and a GO feasibility verdict. Surfaced the embossed-plate rollout →
  [ADR-0002](docs/decisions/0002-anpr-reframing-embossed-plates.md) reframes the ANPR
  story. See [`docs/09_nepal_landscape.md`](docs/09_nepal_landscape.md) and
  [`docs/10_feasibility_study.md`](docs/10_feasibility_study.md).
- ✅ **Literature review (Week 2):** thematic synthesis across detectors, edge
  benchmarking, regional-traffic datasets, helmet & sign recognition, and the Nepali
  context; an evidenced 5-link gap argument; a verified seed bibliography
  ([`paper/references.bib`](paper/references.bib)) and a living reading matrix.
- ✅ Project structure, packaging (`pyproject.toml`), `Makefile`, license, ignore rules.
- ✅ Documentation set: charter, architecture, dataset guide, annotation guidelines,
  class definitions, experiment protocol, reproducibility, ethics. ADR-0001 records
  the scope/framing decision.
- ✅ Canonical configs: `classes.yaml`, `dataset.yaml`, per-model and per-experiment configs.
- ✅ Package core: typed `config`, `paths`, `logging_utils`, and a `typer` CLI.
- ✅ Data pipeline (runnable now): frame extraction, perceptual-hash dedup,
  image selection, **leakage-safe split-by-source**, YOLO/COCO conversion, dataset stats.
- ✅ Annotation tooling: inter-annotator agreement + label validators.
- ✅ Scaffolding with clear interfaces for training / evaluation / analysis / prototype.
- ✅ Test suite for the data-pipeline core.

### What's left (next up)

- 🚧 **Literature review polish:** read Tier-1 papers closely; find the Tier-3 "to find"
  sources (helmet survey, BanglaTS/PTSD, an INT8 edge study, recent Nepali ANPR); re-run
  the Nepal search before submission to keep the "no prior work" claim honest.
- ⬜ **Collect footage** across ≥3 locations × ≥2 times of day × ≥2 weather conditions.
- ⬜ Implement the training runner against Ultralytics (`training/train.py`).
- ⬜ Implement efficiency + plate-resolution measurement bodies (`evaluation/`).
- ⬜ Wire the prototype inference + dashboard (`prototype/`).
- ⬜ Fill the paper outline in `paper/`.

A detailed, dated changelog lives in [`docs/CHANGELOG.md`](docs/CHANGELOG.md).

---

## 📚 Where to read more

| If you want to… | Read |
|---|---|
| Understand the *why* and the contract of this project | [`docs/00_project_charter.md`](docs/00_project_charter.md) |
| Understand the code architecture & module boundaries | [`docs/01_architecture.md`](docs/01_architecture.md) |
| See the literature landscape & the evidenced gap argument | [`docs/08_literature_review.md`](docs/08_literature_review.md), [`docs/literature_matrix.csv`](docs/literature_matrix.csv) |
| Know what Nepali datasets/works exist & the precise gaps | [`docs/09_nepal_landscape.md`](docs/09_nepal_landscape.md), [`docs/nepal_assets_inventory.csv`](docs/nepal_assets_inventory.csv) |
| Judge whether the project is doable (data/compute/legal/time) | [`docs/10_feasibility_study.md`](docs/10_feasibility_study.md) |
| Collect & annotate data correctly | [`docs/02_dataset_guide.md`](docs/02_dataset_guide.md), [`docs/03_annotation_guidelines.md`](docs/03_annotation_guidelines.md) |
| Know exactly what each class means | [`docs/04_class_definitions.md`](docs/04_class_definitions.md) |
| Run the experiments / reproduce results | [`docs/05_experiment_protocol.md`](docs/05_experiment_protocol.md), [`docs/06_reproducibility.md`](docs/06_reproducibility.md) |
| Check the ethics & privacy stance | [`docs/07_ethics_privacy.md`](docs/07_ethics_privacy.md) |
| See the week-by-week plan | [`docs/roadmap.md`](docs/roadmap.md) |

---

## ⚖️ Ethics & privacy (non-negotiable)

Traffic footage contains PII. Before *any* image is released: faces blurred,
readable plates blurred, public-space collection only, every source documented,
dataset under CC BY-NC 4.0 with a data statement. This is built into the pipeline,
not bolted on. See [`docs/07_ethics_privacy.md`](docs/07_ethics_privacy.md).

---

## 🙏 Acknowledgements

Builds on the author's existing *Nepal Traffic AI* system (YOLOv8 + FastAPI + edge
deployment). Research framing developed for an undergraduate first-author paper
targeting the IOE Graduate Conference / regional venues. Author: **Bishow Thapa**.
