# Literature Review (Week 2)

> The working document behind the paper's **Introduction**, **Related Work**, and the
> **research-gap** argument. It is a *living* file: the synthesis below is a defensible
> first map of the field, but every claim you carry into the manuscript must be checked
> against the actual paper you cite. Track your reading in
> [`literature_matrix.csv`](literature_matrix.csv); citations live in
> [`paper/references.bib`](../paper/references.bib).
>
> **Scholarly-integrity rule for this project:** never cite a paper you have not at
> least skimmed, and never trust a bibliographic detail you have not verified at the
> source. Entries marked `VERIFY` in `references.bib` are sourced from search/abstract
> metadata and must be confirmed before final submission.

---

## 0. How to use this document

1. Read theme by theme (§3). Each theme ends with **"What this means for NepTraVision"** —
   that paragraph is raw material for your Related Work section.
2. As you read a paper, add a row to `literature_matrix.csv` and flip its `read_status`.
3. §4 is the **gap argument** — the spine of your Introduction. Strengthen it with
   every paper you read; it should get *harder to argue against*, not longer.
4. §5 maps references → paper sections so writing Week 11 is assembly, not panic.

## 1. Search strategy (reproducible)

**Databases / sources:** Google Scholar, arXiv, IEEE Xplore, SpringerLink, MDPI,
Semantic Scholar; plus the [IOE Graduate Conference proceedings](https://conference.ioe.edu.np/publications/ioegc16/)
for the local gap.

**Query families used (extend as needed):**
- *Detection backbones:* `YOLOv8|YOLOv10|YOLO11 real-time object detection`,
  `Faster R-CNN / SSD / EfficientDet / RT-DETR comparison`.
- *Edge efficiency:* `object detection edge devices benchmark Raspberry Pi Jetson`,
  `INT8 quantization detector latency FPS`.
- *Mixed / unstructured traffic:* `unstructured traffic detection dataset India`,
  `mixed traffic motorcycle dominated detection`.
- *Helmet compliance:* `motorcycle helmet detection YOLO`, `helmet violation detection`.
- *Traffic-sign recognition:* `traffic sign recognition benchmark`,
  `traffic sign dataset developing country / non-Latin script`.
- *Nepal-specific:* `Nepal vehicle / license plate / Devanagari recognition`,
  `Nepali traffic computer vision`.

**Inclusion criteria:** peer-reviewed or well-cited preprints; relevance to detection,
edge deployment, mixed traffic, helmet/sign tasks, or the South-Asian / Nepali context.
**Exclusion:** pure traffic-*engineering* flow studies (cited only to establish the CV
gap), and blog posts (used for orientation, not as citations).

## 2. The five review areas (from the roadmap)

1. Object-detection backbones & the YOLO family.
2. Edge / efficient detection and benchmarking (our distinctive axis).
3. Traffic-detection datasets and their geographic bias (mixed/unstructured traffic).
4. Helmet-compliance detection.
5. Traffic-sign recognition (incl. non-Latin / regional signage).
6. *(+ local context)* Nepali traffic CV and the IOEGC gap.

---

## 3. Thematic synthesis

### 3.1 Object detection & the YOLO family

Modern detection split into two-stage (region-proposal) detectors such as **Faster
R-CNN** [`ren2015faster`] — accurate but heavier — and single-stage detectors such as
**SSD** [`liu2016ssd`] and the **YOLO** line [`redmon2016yolo`], which trade a little
accuracy for the real-time speed that matters at a roadside. The YOLO family is now the
de-facto choice for applied, real-time traffic work: **YOLOv8** [`jocher2023yolov8`] is
the widely used Ultralytics baseline; **YOLOv10** [`wang2024yolov10`] removes the NMS
post-processing step (consistent dual assignments → NMS-free, lower latency); and
**YOLO11** [`jocher2024yolo11`] reduces model complexity (~37% fewer params than
YOLOv8 at comparable mAP) — directly relevant to edge budgets. Transformer detectors
like **RT-DETR** [`zhao2024rtdetr`] and anchor-free efficient nets like **EfficientDet**
[`tan2020efficientdet`] are useful non-YOLO contrast points. All are pretrained on
**COCO** [`lin2014coco`], a Western-centric object distribution.

**What this means for NepTraVision:** the architectures are mature and commoditised —
so a new architecture is *not* a credible contribution. The open question is empirical:
*which of these, fine-tuned, gives usable accuracy at real-time speed on Nepali mixed
traffic and edge hardware?* That is a benchmark question, not a modelling one.

### 3.2 Edge / efficient detection & benchmarking *(our distinctive axis)*

A growing literature measures detectors not by accuracy alone but by accuracy **per
unit of compute** on real hardware. Alqahtani et al. [`alqahtani2024edge`] evaluate
YOLOv8, EfficientDet-Lite and SSD across Raspberry Pi 3/4/5 (± Coral TPU) and Jetson
Orin Nano on inference time, energy, and mAP — the template for our E2/E4 protocol.
Vendor and community studies confirm the operating envelope: YOLO11/YOLOv8-nano with
NCNN/INT8 reach ~real-time on a Pi 5 at small input sizes, while larger models are
multi-second-per-frame on Pi CPUs (impractical) [`learnopencv_yolo11_rpi`]. Energy and
thermal behaviour of larger YOLO vs RT-DETR on edge is itself a studied axis
[`nature2026_yolo_rtdetr_energy`].

**What this means for NepTraVision:** the *accuracy–efficiency Pareto frontier per
hardware tier* (our headline figure) is an established, valued contribution type —
and it is exactly aligned with Nepal's deployment reality (commodity/edge, not GPU
farms). We adopt the warmup→timed-iterations protocol and report latency/FPS/params/
FLOPs/size/RAM, with INT8 as the edge sweetener.

### 3.3 Traffic-detection datasets & their geographic bias

The most-used driving/traffic benchmarks — KITTI, Cityscapes, BDD100K — assume
*structured, lane-disciplined, rule-compliant* roads typical of the West. The
**India Driving Dataset (IDD)** [`varma2019idd`] was created precisely because those
benchmarks "fall short of representing the unstructured, heterogeneous, often chaotic"
traffic of South Asia. The line continues with **DriveIndia** [`kumar2025driveindia`]
and large CCTV-sourced sets like **UVH-26** [`uvh2025`] (Bengaluru, 26k images, 1.8M
boxes, 14 India-specific vehicle classes incl. auto-rickshaws). These establish both
the phenomenon (Western models degrade on South-Asian roads) and the accepted remedy
(build a regional dataset).

**What this means for NepTraVision:** there is strong precedent that a *regional traffic
dataset* is a legitimate, publishable contribution — and a clear ladder (India is
covered; Nepal is not). Our split-by-source, condition-stratified design and dataset
card follow this lineage while targeting the unaddressed Nepali setting.

### 3.4 Helmet-compliance detection

Helmet detection is an active applied niche, almost entirely YOLO-based (v2→v8) on
*custom* datasets, because public helmet datasets are scarce. Representative works:
real-time improved-YOLOv5 helmet detection in urban traffic [`jia2021helmet`]; YOLOv8 +
DCGAN augmentation to fight class imbalance [`mdpi2024helmet`]; and city-scale rider
helmet-violation + vehicle-ID pipelines for Indian smart cities [`frontiers2025helmet`].
Reported mAP is often high (>0.9) but on small, clean, single-context datasets — and the
hard cases (small/occluded heads, night, pillion passengers) are exactly where numbers
drop.

**What this means for NepTraVision:** helmet compliance is well-motivated and tractable,
but (a) it needs *our own* annotated data (no Nepali helmet set exists) and (b) honest
evaluation must report the hard slices, which our condition breakdown (E5) is built for.
This justifies treating helmet as a first-class but *difficult* task in the benchmark.

### 3.5 Traffic-sign recognition (incl. non-Latin / regional signage)

The canonical benchmark is **GTSRB** [`stallkamp2012gtsrb`] (43 German classes), with
LISA (US), BelgiumTS, TT100K (China) and others. Surveys note that signs outside the
Western canon — different glyphs, bilingual/non-Latin text — are under-served, and
recent regional sets (**BanglaTS**, **PTSD** for Pakistan) "highlight language- and
culture-specific patterns but remain insufficient in scale and coverage" [`signs_survey`].
Sign recognition is also a hard *small-object* detection problem under faded/occluded
real-world conditions [`challenging_signs2019`].

**What this means for NepTraVision:** Nepali signage (English + Devanagari + mixed)
sits squarely in the under-served category. Even a modest, well-defined Nepali sign
subset is novel, and the small-object/faded-sign failure modes feed directly into our
RQ4 error analysis.

### 3.6 Nepali traffic CV & the IOEGC gap *(the local case)*

Nepal-specific computer-vision traffic work that exists is concentrated on **license
plates**: SVM-based Nepali plate recognition [`pant2015nepali`], Devanagari
plate detection/recognition with CNNs [`devanagari_lp2021`], and recent YOLOv8/v9 ANPR
pipelines for the Nepali context. Crucially, this work is about *reading plates*, not
*detecting and classifying the mixed traffic stream*, and it depends on high-resolution
frontal plate crops. Meanwhile, the IOE Graduate Conference corpus
[`ioegc16`] — the main local research venue — contains traffic studies that are
classical traffic *engineering* (gap acceptance, VISSIM, flow), with **no traffic
computer-vision detection work and no public Nepali traffic detection dataset.**

**What this means for NepTraVision:** the gap is specific and defensible — Nepali plate
OCR has been attempted, but the *upstream, resolution-tolerant* tasks (vehicle/helmet/
sign detection) and a *benchmark dataset* are absent. This also motivates our ANPR
reframing: instead of competing on plate OCR (resolution-limited), we **measure** the
resolution threshold at which it becomes feasible (E6).

---

## 4. The gap argument (spine of the Introduction)

Assemble the Introduction from this chain — each link is now backed by §3:

1. **Detection is a solved-enough tool.** Real-time detectors (YOLO family, RT-DETR,
   EfficientDet) are mature and commoditised [`redmon2016yolo`, `wang2024yolov10`,
   `zhao2024rtdetr`]. Contribution must come from *data + measurement*, not architecture.
2. **But they are trained for the wrong world.** Mainstream benchmarks assume
   structured Western roads; South-Asian unstructured traffic breaks them, which is why
   regional datasets (IDD, DriveIndia, UVH-26) had to be built [`varma2019idd`,
   `kumar2025driveindia`, `uvh2025`].
3. **Deployment reality is the edge, not the GPU.** Usable systems must run on
   commodity/edge hardware; the accuracy–efficiency frontier on such devices is an
   active, valued research axis [`alqahtani2024edge`].
4. **Nepal is a blank spot on this map.** Nepali CV work exists only for license plates
   [`pant2015nepali`, `devanagari_lp2021`]; the IOEGC corpus has no traffic-CV detection
   work and no public Nepali traffic dataset [`ioegc16`].
5. **Therefore:** NepTraVision contributes (C1) the first Nepali traffic detection
   dataset, (C2) an edge-efficiency benchmark for this context, and (C3) a failure +
   resolution analysis incl. the plate-legibility threshold — converting the ANPR
   blocker into a measured finding.

This is the **honest-novelty** statement from [`05_experiment_protocol.md`](05_experiment_protocol.md§8),
now evidenced.

## 5. Reference → paper-section map

| Paper section | Lean on |
|---|---|
| Intro / gap | `varma2019idd`, `kumar2025driveindia`, `alqahtani2024edge`, `pant2015nepali`, `ioegc16` |
| Related work — detectors | `redmon2016yolo`, `ren2015faster`, `liu2016ssd`, `wang2024yolov10`, `jocher2023yolov8`, `zhao2024rtdetr`, `tan2020efficientdet`, `lin2014coco` |
| Related work — edge benchmark | `alqahtani2024edge`, `nature2026_yolo_rtdetr_energy`, `learnopencv_yolo11_rpi` |
| Related work — datasets/bias | `varma2019idd`, `kumar2025driveindia`, `uvh2025` |
| Related work — helmet | `jia2021helmet`, `mdpi2024helmet`, `frontiers2025helmet` |
| Related work — signs | `stallkamp2012gtsrb`, `signs_survey`, `challenging_signs2019` |
| Related work — Nepal | `pant2015nepali`, `devanagari_lp2021`, `ioegc16` |

## 6. Reading priority (do these first)

**Tier 1 — read closely (shape the paper):**
`varma2019idd` (the gap template), `alqahtani2024edge` (the benchmark template),
`wang2024yolov10` (the modern detector), `pant2015nepali` (the local precedent),
`stallkamp2012gtsrb` (the sign benchmark).

**Tier 2 — skim for framing & numbers:**
`kumar2025driveindia`, `uvh2025`, `frontiers2025helmet`, `zhao2024rtdetr`,
`tan2020efficientdet`.

**Tier 3 — to find & add (gaps in our coverage):**
- A proper **survey** of helmet-detection methods (for one citation that covers the niche).
- **BanglaTS / PTSD** primary papers (regional sign datasets) — find exact citations.
- One **edge-quantization** paper (INT8/TFLite/TensorRT accuracy-vs-speed) for E4.
- Recent **Nepali ANPR (YOLOv8/v9)** paper — find the exact citation for §3.6.
- Verify whether *any* 2024–2026 Nepali traffic-CV detection paper now exists
  (re-run the Nepal search before final submission so the "no prior work" claim holds).

---

*Next milestone: M1 — data collection & annotation. This review's class/condition
findings (mixed types, Devanagari signs, hard helmet cases) should inform the final
freeze of `configs/classes.yaml` and the condition matrix in the dataset card.*
