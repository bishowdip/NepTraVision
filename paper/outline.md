# NepTraVision — Paper Outline

> Drafting skeleton. Each section lists what it must contain. Fill as milestones
> complete; the numbers come from `results/`. Headline framing: *data + measurement
> for an underrepresented setting* (not a new architecture).

## Title
**NepTraVision: A Nepal-Specific Traffic Computer-Vision Benchmark and Lightweight
Detection System for Vehicle Counting, Helmet Compliance, and Traffic-Sign
Recognition.**

## Abstract
The gap (no Nepali traffic CV dataset/benchmark) → the dataset → the benchmark →
**one headline number** (e.g. "best edge detector achieves X mAP@0.5 at Y FPS on a
Raspberry Pi 5"). 150–250 words.

## Keywords
Computer Vision; YOLO; Traffic Monitoring; Nepal; Vehicle Detection; Helmet
Detection; Traffic-Sign Recognition; Edge AI; Benchmark Dataset; Intelligent
Transportation Systems.

## 1. Introduction
- Nepali mixed-traffic reality and why COCO-trained detectors degrade.
- The confirmed local gap (≈200 IOEGC papers, all classical traffic *engineering*).
- Edge-deployment reality (checkpoints run on commodity/edge hardware).
- Contributions C1–C3 (dataset, edge-efficiency benchmark, failure/resolution
  analysis incl. plate-px threshold).

## 2. Related Work
- Traffic-detection datasets and their Western bias.
- Efficient / edge object detectors (YOLO family, NanoDet, SSD-Mobile, EfficientDet).
- Low-resource / developing-context CV.
- Nepali traffic *engineering* literature — to establish the CV gap.

## 3. The NepTraVision Dataset (C1)
Collection (sources, conditions, legality); taxonomy (18-class / simple);
annotation process + guidelines; inter-annotator agreement; **leakage-safe splits by
source-group**; privacy handling. Pull numbers from the dataset card + `data stats`.

## 4. Benchmark Setup
Model set (4–6 detectors); hardware tiers (GPU/CPU/Pi); training protocol (COCO
pretrain → fine-tune, 3 seeds, identical augmentation); metrics (accuracy +
efficiency).

## 5. Results
- Accuracy (Table 1, mean±std).
- Efficiency Pareto frontier per tier (headline figure).
- Resolution sweep (Table 3).
- Quantization (INT8 trade-off).
- Condition breakdown (E5).

## 6. Analysis & Discussion
Failure modes (small two-wheelers, occlusion, night/monsoon, class confusions);
**the plate-legibility threshold** (E6) — "ANPR needs ≥ N px; typical Nepali CCTV
gives M < N"; what to deploy at a Nepali checkpoint.

## 7. Limitations & Ethics
Dataset size/coverage; annotation error; underrepresented night/rain; privacy
handling; not for legal enforcement.

## 8. Conclusion & Future Work
Scale the dataset; violation/anomaly detection; full ANPR + DoTM integration as
deployment future work; public dataset release.

## References
(Seed list in `references.bib`: Ultralytics YOLO docs/metrics; COCO; CVAT; IOEGC
proceedings; helmet-detection and traffic-sign-recognition prior work — fill during
the literature review.)
