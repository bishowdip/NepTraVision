# Project Charter — NepTraVision

> The one-page contract for the project. If a decision contradicts this document,
> either the decision is wrong or this document must be consciously amended (with a
> note in the changelog). Last reviewed: 2026-06-20.

## 1. One-line identity

NepTraVision is **a Nepal-specific traffic computer-vision benchmark plus a
deployable prototype** for realistic, low-resolution, mixed-traffic environments —
*not* "just a YOLO training script" and *not* "just a dashboard".

## 2. The problem

- **Local gap (confirmed):** across ~200 IOE Graduate Conference papers, every
  traffic study is classical traffic *engineering* (gap acceptance, VISSIM, flow
  diagrams). There is **no computer-vision work on Nepali traffic, and no public
  Nepali traffic detection dataset.**
- **Why Nepal is its own problem:** motorcycle-dominated mixed traffic, local
  vehicle types, dense occlusion, undisciplined lanes, monsoon/low-light, and
  low-resolution CCTV. COCO-trained detectors degrade — and the degradation is
  unquantified.
- **Deployment reality:** Nepali checkpoints run on commodity/edge hardware, not
  GPU farms. *Which detector is usable at real-time speed on a Pi-class device?* is
  unanswered.
- **ANPR reality:** at typical standoff resolution, plates are too few pixels for
  OCR. Rather than pretend otherwise, we **measure the resolution threshold** at
  which plate OCR becomes feasible.

## 3. Research questions

- **RQ1.** Can a reliable, condition-diverse vehicle / helmet / sign detection
  dataset be built for Nepali mixed traffic?
- **RQ2.** Among real-time detectors, what is the **accuracy–efficiency frontier**
  on commodity / edge hardware (mAP vs. FPS, params, memory, power)?
- **RQ3.** Where do detectors fail in Nepali conditions (small two-wheelers,
  occlusion, night/monsoon), and **at what input resolution does plate-level OCR
  become feasible at all?**

## 4. Contributions (the paper's claims)

1. **C1 — NepTraVision-Bench dataset** (the make-or-break artifact).
2. **C2 — Edge-efficiency benchmark** across detectors × hardware tiers.
3. **C3 — Failure & resolution analysis**, including the plate-legibility threshold.

We are **not** claiming a new architecture. Honest novelty = data + measurement for
an underrepresented setting.

## 5. Scope

**In:** dataset construction; lightweight detector benchmark; efficiency on
CPU/Pi/GPU; resolution & condition analysis; plate-px sub-study; a prototype
dashboard as *deployment context*.

**Out (v1):** fine-grained plate OCR as a core claim; DoTM verification; automated
enforcement; face/person identification; nationwide deployment.

**The trap to avoid:** do *not* let the full ANPR + DoTM + dashboard become the
paper. The paper is dataset + benchmark + analysis. The rest is context.

## 6. Success criteria

| Tier | Looks like |
|---|---|
| Minimum publishable | ≥1,500 QC'd images; ≥2 detectors × 3 seeds; leakage-safe splits; one Pareto plot; condition breakdown; dataset card; reproducible repo. |
| Strong | ≥3,000 images, multi-location/condition; 4–6 detectors; CPU+Pi+GPU sweep; resolution sweep; INT8; plate-px threshold finding; public Zenodo/HF release. |

## 7. Constraints & resources

- **Author:** Bishow Thapa (solo, first author). Window: Aug–Nov 2026 (flexible).
- **Compute:** free Colab/Kaggle T4 (server reference), laptop CPU (commodity),
  Raspberry Pi 5 if available (edge). No GPU farm assumed.
- **Builds on:** existing *Nepal Traffic AI* system (YOLOv8 + FastAPI + edge configs).

## 8. Definition of done

A reproducible repository (dataset card + configs + splits + seeds + eval scripts),
committed result tables/figures, a written manuscript reviewed by a supervisor, and
a citable dataset release. See [`06_reproducibility.md`](06_reproducibility.md).
