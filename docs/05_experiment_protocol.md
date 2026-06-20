# Experiment Protocol

> The benchmark that turns the dataset into a paper. Each experiment is defined by a
> YAML in [`configs/experiments/`](../configs/experiments/) so it is reproducible and
> auditable. Headline deliverable: an **accuracy-vs-FPS Pareto plot per hardware
> tier** — *"the best detector you can actually run at a Nepali checkpoint."*

## 1. The model set (4–6 models spanning size/speed)

All COCO-pretrained, then fine-tuned on NepTraVision-Bench. Verify weight
availability before committing.

| Model | Role |
|---|---|
| YOLOv8n | existing base; fastest nano baseline |
| YOLOv8s | balanced option |
| YOLOv5n | strong nano baseline |
| YOLO11n (or YOLOv10n) | one recent nano model |
| **one non-YOLO** (NanoDet-Plus / MobileNet-SSD / EfficientDet-Lite0) | architecture contrast point |

Declared in [`models/registry.py`](../src/neptravision/models/registry.py) and
`configs/models/`.

## 2. Hardware tiers

| Tier | Device | Meaning |
|---|---|---|
| Server reference | free Colab/Kaggle GPU (T4) | upper bound |
| Commodity | laptop **CPU** | the realistic Nepali desktop |
| Edge | **Raspberry Pi 5** (Jetson Nano optional) | deployment target |

No Pi available? Report CPU + GPU, frame edge as motivation, **state the limitation
honestly.**

## 3. Training protocol

- Start from COCO-pretrained weights; fine-tune on NepTraVision-Bench.
- Resolution study uses fixed input sizes **320, 416, 640**.
- **Identical augmentation** across models (mosaic, flips, HSV).
- **3 seeds**; report **mean ± std**. Same epochs / early-stopping rule for all.
- Log everything (configs, weights, curves) for release.

## 4. Metrics

- **Accuracy:** mAP@0.5, mAP@0.5:0.95, per-class AP (watch the small two-wheeler
  class), precision, recall, F1, confusion matrix.
- **Efficiency (per tier):** latency (ms/frame), throughput (FPS), parameters (M),
  FLOPs (G), model size (MB), peak RAM; on Pi optionally power (W) and thermal
  throttling.

## 5. Core experiments

| ID | Name | What it produces |
|---|---|---|
| **E1** | Baselines | All models fine-tuned; accuracy on the held-out test set. |
| **E2** | Efficiency sweep | Each model × each hardware tier → latency / FPS / memory. |
| **E3** | Resolution sweep (320/416/640) | Accuracy ↔ speed trade-off; feeds the plate question. |
| **E4** | Quantization (edge) | INT8 (ONNX Runtime / TFLite / TensorRT) → accuracy drop vs. speedup. |
| **E5** | Condition breakdown | Accuracy by day/night, weather, density. Where does it break? |
| **E6** | Plate-resolution sub-study | Mean plate px-height vs. distance/resolution; OCR CER vs. px-height → **legibility threshold** ("ANPR needs ≥ N px; typical Nepali CCTV gives M < N"). |

## 6. Result tables (templates → `results/tables/`)

**Table 1 — Accuracy (test set, mean±std, 3 seeds)**

| Model | params (M) | mAP@.5 | mAP@.5:.95 | AP_two_wheeler |
|---|---|---|---|---|
| YOLOv8n | | | | |

**Table 2 — Efficiency by hardware (640 input)**

| Model | CPU FPS | Pi5 FPS | GPU FPS | size (MB) | peak RAM |
|---|---|---|---|---|---|

**Table 3 — Resolution sweep (best small model)**

| Input | mAP@.5 | Pi5 FPS |
|---|---|---|
| 320 / 416 / 640 | | |

## 7. Paper outline (section by section)

1. **Abstract** — gap, dataset, benchmark, one headline number.
2. **Introduction** — Nepali traffic-CV gap (cite IOEGC survey), edge-deployment
   reality, contributions.
3. **Related work** — traffic-detection datasets (and their Western bias); efficient
   detectors; low-resource/developing-context CV; Nepali traffic *engineering* (to
   establish the CV gap).
4. **The NepTraVision dataset** — collection, classes, conditions, annotation,
   agreement, splits, privacy.
5. **Benchmark setup** — models, hardware, training, metrics.
6. **Results** — accuracy; efficiency Pareto; resolution sweep; quantization;
   condition breakdown.
7. **Analysis & discussion** — failure modes; plate-legibility threshold; what to
   deploy at a Nepali checkpoint.
8. **Limitations & ethics** — dataset size/coverage, privacy, generalization.
9. **Conclusion & future work** — scaling the dataset; full ANPR + DoTM as future work.

## 8. Honest novelty statement (for your head, not the paper)

You are **not** claiming a new detector architecture. You contribute (1) the first
Nepali traffic detection **dataset**, (2) an **edge-efficiency benchmark** for this
context, and (3) a **resolution/failure analysis** including the ANPR-feasibility
threshold. A legitimate, reviewable, honest first-author contribution for an
underrepresented setting.
