# Feasibility Study

> Can this project actually be done — solo, compute-light, in the available window, and
> legally — to a publishable standard? Assessed 2026-06-21 against the
> [Nepal landscape dossier](09_nepal_landscape.md). Verdict first, evidence after.

## 0. Verdict at a glance

| Task | Feasibility | Why |
|---|:---:|---|
| **Vehicle detection + counting** | 🟢 **High** | Mature detectors; data self-collectable; the core, lowest-risk deliverable. |
| **Helmet / no-helmet** | 🟢 **High** | Small heads are hard, but it's the highest-impact task and well-precedented; report hard slices honestly. |
| **Traffic-sign detection** | 🟡 **Medium** | Signs are sparse → slow to collect enough; a community Roboflow Nepali sign set may help. Shippable as v1.1 if data is thin. |
| **Plate OCR (E6 sub-study only)** | 🟡 **Medium** | As a *measured-threshold* study, yes. As a working ANPR claim, no — keep it future work. |
| **Edge-efficiency benchmark** | 🟢 **High** | Compute-light by design; literature confirms nano models on Colab/Pi. |
| **Real-time prototype** | 🟢 **High** | Already built (mock); swap in trained weights. Context, not a claim. |

**Overall: 🟢 GO.** Scope the paper as **dataset + edge benchmark + failure/resolution
analysis**, lead with **vehicle + helmet** (the `simple`→`full` path), treat signs as
stretch and plate-OCR as a sub-study. This matches both the gaps (G1–G6) and the
constraints below.

## 1. Data feasibility

- **Sourcing:** self-recorded smartphone/dashcam footage from public vantage points is
  legal and fully under your control — the primary source. Public CC footage is a
  secondary, license-checked source. **Police/ANPR/CCTV footage is off-limits**
  (government-controlled; Privacy Act). This is sufficient: IDD (10k imgs) and the
  Nepali vehicles set (4,797) were both built this way.
- **Volume target:** 1,500 (min) → 3,000 (good) annotated images is a realistic solo
  target and a legitimate first regional dataset (cf. IDD ~10k with a team).
- **The real cost is annotation, not collection.** Mitigations: COCO-pretrained
  pre-labelling + human correction; Roboflow free tier; `simple` 3-class profile first;
  double-annotate only a 300–500 QC subset. See [`02_dataset_guide.md`](02_dataset_guide.md).
- **Risk:** single-city bias → mitigate with ≥3 locations (landscape §8, I5).

## 2. Legal & ethical feasibility

- Governed by the **Individual Privacy Act 2075 (2018)**: collecting personal data needs
  consent/purpose disclosure; misuse carries up to **3 years / NPR 30,000**
  [(Pioneer Law)](https://pioneerlaw.com/individual-privacy-act-2018-2075/),
  [(Act PDF)](https://hmis.gov.np/media/22/03_The-Privacy-Act-2075-2018.pdf).
- **Feasible because:** wide public-space shots where individuals aren't identifiable,
  **blurring faces and plates before release**, documenting every source, and releasing
  under CC BY-NC 4.0 keep us clearly on the right side. This is already the
  [ethics stance](07_ethics_privacy.md) — now legally anchored. **No human-subjects
  approval barrier for anonymised public-scene traffic imagery**, but check whether your
  institution (IOE/TU) requires an ethics sign-off for dataset release.

## 3. Compute feasibility

- **Confirmed by the edge literature** [(Alqahtani et al., 2024)](https://arxiv.org/abs/2409.16808),
  [(YOLO11-on-Pi)](https://learnopencv.com/yolo11-on-raspberry-pi/): YOLO-nano / YOLO11n
  fine-tune on a free Colab/Kaggle T4 in hours and run **real-time on a Raspberry Pi 5**
  at small input sizes (with NCNN/INT8), while large models are impractical on Pi CPU.
- **Plan fits the hardware you have:** Colab/Kaggle T4 = server reference; laptop CPU =
  commodity tier; Pi 5 if accessible = edge tier (else report CPU+GPU and state the
  limitation). No GPU farm needed — and "ML under real resource constraints" is the
  project's distinctive identity, not a weakness.

## 4. Skills & solo feasibility

- The hard engineering (pipeline, training, eval, prototype) is **already built and
  tested** (M0). What remains is data work + running configured experiments + writing.
- Solo-doable because the **novelty is in data + measurement, not architecture** — no
  need to invent or implement a new model.

## 5. Timeline feasibility

Maps onto [`roadmap.md`](roadmap.md). M0 (foundation + lit review) is **done early**.
The binding constraint is **M1 (annotation)** — protect it; don't rush it to hit a week
number. Signs/plate sub-study are explicitly deferrable without endangering the paper.

## 6. Novelty & publication feasibility

- **Defensible novelty:** first Nepali traffic *detection* dataset (G1), first Nepali
  edge-efficiency benchmark (G2), first Nepali condition/resolution failure analysis
  (G5/G6). All evidenced in the [landscape dossier](09_nepal_landscape.md).
- **Venues:** IOE Graduate Conference (CV work is accepted there — sign-language,
  medical — but no traffic CV, so you fit *and* fill a gap); regional IEEE conferences;
  a low-resource/developing-context CV or applied-ML workshop; arXiv preprint + a
  **Zenodo DOI** for the dataset to make it citable.
- **Two-paper option** remains open (dataset paper A; benchmark paper B) — decide at M4.

## 7. Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|:---:|:---:|---|
| Annotation overruns the schedule | High | High | `simple` profile first; pre-label+correct; cap classes; defer signs |
| Class imbalance tanks minority-class AP | High | Med | per-class AP reporting; augmentation; imbalance-aware discussion |
| Single-city → weak generalization | Med | Med | ≥3 locations; hold a location out as test |
| Privacy/legal misstep | Low | High | public-space only; blur faces+plates; document; CC BY-NC |
| Embossed-plate rollout dates the ANPR framing | Med | Low | reframe E6 (resolution, not script); ADR-0002 |
| No Pi available for edge tier | Med | Low | report CPU+GPU; frame edge as motivation; state limitation |
| Roboflow Nepali sign set unusable (license/quality) | Med | Low | audit first; use as external test only, or drop signs to v1.1 |
| Scope creep back to "dashboard = paper" | Med | High | charter + ADR-0001 guardrail; prototype stays context |

## 8. Recommendation

**Proceed (GO).** Lock scope to **dataset + benchmark + analysis**, lead with
**vehicle + helmet** detection on a **≥3-location, condition-diverse, ≥1,500-image**
dataset, run the configured E1–E6 experiments on **nano models across CPU/Pi/GPU**, and
keep signs (stretch) and plate-OCR (E6 sub-study/future work) appropriately scoped.
Adopt the five repo changes in [landscape §9](09_nepal_landscape.md#9-recommended-changes-to-the-project-carry-into-the-repo);
the most urgent is **ADR-0002** to reframe the ANPR/E6 story for the embossed-plate era.
