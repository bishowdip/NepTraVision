# Nepal Traffic-CV Landscape & Gap Dossier

> A Nepal-first survey of what already exists — datasets, models, prior works,
> infrastructure, and law — so the project builds on reality and the gaps it claims are
> *precise and defensible*. Compiled 2026-06-21 from web research (sources linked
> inline). Companion: [`10_feasibility_study.md`](10_feasibility_study.md). Reading-list
> framing is in [`08_literature_review.md`](08_literature_review.md).
>
> **Verify-before-cite rule still applies.** Inline links are the evidence; confirm any
> figure at its source before it enters the manuscript, and **re-run the Nepal searches
> right before submission** — this is a fast-moving local space.

---

## 1. Why this matters (the Nepal motivation, with numbers)

Nepal's road-safety burden is severe and **two-wheeler-dominated**, which is exactly
what makes a Nepal-specific detection benchmark worth building:

- **~2,368 road deaths in FY 2023/24**; ~**75 accidents/day**, ~**7 deaths/day**
  (Nepal Police). Over five years (2019/20–2023/24): **12,542 killed, 29,729 seriously
  injured**. [(Kathmandu Post)](https://kathmandupost.com/national/2025/01/26/nepal-sees-at-least-75-road-accidents-on-average-daily-report-shows)
- **Motorcycles ≈ 79–84% of registered vehicles** and are involved in **~two-thirds of
  fatal crashes**; in one month ~70% of crashed vehicles were motorcycles.
  [(Kathmandu Post, 2023)](https://kathmandupost.com/national/2023/06/27/over-two-thirds-of-road-accident-deaths-in-nepal-involve-motorcycles-report-says)
- **Helmet use is low**, especially pillion and female riders — a directly
  CV-observable, policy-relevant compliance problem. [(Asian Transport Observatory — Nepal Road Safety Profile 2025)](https://asiantransportobservatory.org/analytical-outputs/roadsafetyprofiles/nepal-road-safety-profile-2025/)
- **3M+ registered vehicles**; motorcycles **83.7% of new registrations in 2023**
  (DoTM via [CEIC](https://www.ceicdata.com/en/nepal/motor-vehicles-registration/number-of-motor-vehicles-registered-motorcycles)).

**Implication for the project:** the *motorcycle_scooter* + *helmet/no_helmet* tasks are
not arbitrary — they target the single largest contributor to Nepal's road deaths. This
is the motivation paragraph of the paper, and it is data-backed.

## 2. Existing Nepali datasets (the inventory)

Machine-readable version: [`nepal_assets_inventory.csv`](nepal_assets_inventory.csv).

| Asset | What it is | Size / classes | Format | Gap it leaves |
|---|---|---|---|---|
| **vehicles-nepal-dataset** ([GitHub](https://github.com/sdevkota007/vehicles-nepal-dataset), [Kaggle](https://www.kaggle.com/datasets/sdevkota007/vehicles-nepal)) | Vehicles cropped from 30 Kathmandu street videos | 4,797 images; **2 classes** (two-/four-wheeler); 1,823 + 2,974 | **Classification only — no bounding boxes**; no license | Not detection; coarse; no helmet/sign; single city |
| Other Kaggle "Nepali vehicle" sets ([aryalrupesh](https://www.kaggle.com/datasets/aryalrupesh/nepli-vehicle-dataset), [ishworsubedii](https://www.kaggle.com/datasets/ishworsubedii/vehicles-dataset-nepal)) | Community vehicle image sets | unverified | unverified | Provenance/labels unverified; likely classification |
| **"New Nepali Dataset"** ([Roboflow, Sharad Pathak, 2022](https://universe.roboflow.com/sharad-pathak/new-nepali-dataset)) | Nepali **road signs** with Nepali text | community; object detection | YOLO (Roboflow) | Quality/size/license unknown; **only Nepali sign set found** — assess as external test/aug |
| Nepali license-plate / ANPR sets | Plate + Devanagari character data | e.g. 19,663-char set; ALPR V2 ~2,000 plates | detection + OCR | Plate-only; not the traffic stream |
| Devanagari character datasets | Handwritten/printed Devanagari (e.g. [Nepali-Datasets list](https://github.com/pemagrg1/Nepali-Datasets)) | 10k+ images | classification | Text glyphs, not traffic objects |

**Bottom line:** there is **no public, detection-grade, multi-class Nepali traffic
dataset** with vehicle + helmet + sign annotations and leakage-safe splits. The closest
asset (vehicles-nepal) is classification-only with two coarse classes. **This is the C1
gap, confirmed by direct inventory rather than assumption.**

## 3. Existing Nepali works & the local research scene

- **License-plate recognition (the bulk of Nepali traffic CV):** SVM-based Nepali plate
  recognition [(Pant, 2015)](http://ashokpant.github.io/publications/ashok_2015_automatic.pdf);
  Devanagari plate detection/recognition with CNNs
  [(Springer, 2021)](https://link.springer.com/chapter/10.1007/978-3-030-88244-0_9); and
  recent YOLOv8/v9 ANPR pipelines for the Nepali context. **All plate-reading, all needing
  high-res frontal crops.**
- **Conceptual / framework work:** *Framework for AI-Driven Traffic Management in
  Kathmandu* [(ResearchGate, 2024)](https://www.researchgate.net/publication/392543119_Framework_for_AI-Driven_Traffic_Management_in_Kathmandu) — a framework, not a dataset/benchmark.
- **Nepali CV community is active but not on traffic detection:** IOE Graduate Conference
  proceedings include Nepali Sign Language recognition (CNN+MediaPipe), medical imaging,
  landslide mapping, plant-disease classification
  [(IOEGC](https://conference.ioe.edu.np/publications/ioegc16/); [16th abstracts](https://conference.ioe.edu.np/downloads/IOEGC16-Book-of-Abstracts.pdf)).
  **Refined gap claim:** the gap is not "no CV in Nepal" — it is **no traffic-detection CV
  and no public Nepali traffic detection dataset.** State it this precisely; the broad
  version is easy for a reviewer to falsify.

## 4. Regional precedent (the ladder we're climbing)

These justify *both* that the problem is real and that a regional dataset is a publishable
contribution type:

- **India Driving Dataset (IDD)** — built because KITTI/Cityscapes/BDD100K assume
  structured Western roads and fail on South-Asian unstructured traffic
  [(Varma et al., WACV 2019)](https://arxiv.org/abs/2210.12878). **DriveIndia**
  [(arXiv 2507.19912, ITSC 2025)](https://arxiv.org/abs/2507.19912) and **UVH-26**
  (26k CCTV images, 1.8M boxes, 14 India classes) [(arXiv 2511.02563)](https://arxiv.org/abs/2511.02563) continue it.
- **Bangladesh** YOLO vehicle-detection benchmark [(arXiv 2212.09144)](https://arxiv.org/pdf/2212.09144) — a near-neighbour precedent for exactly our paper type.
- **Triple-riding / helmet violation** South-Asian datasets: **RideSafe-400 / DashCop**
  dashcam dataset for triple-riding + helmet rule violations; triple-riding detection via
  YOLOv8 and Mask R-CNN [(Springer 2025)](https://link.springer.com/article/10.1007/s44163-025-00263-3), [(T&F 2025)](https://www.tandfonline.com/doi/full/10.1080/21642583.2025.2546829).

**Takeaway:** Nepal sits one rung below India/Bangladesh on this ladder — the method is
proven, the country slot is empty. That is the sweet spot for a first paper.

## 5. Infrastructure, deployment context & a scope-changing finding

- **Intelligent Traffic System** planned for **35 Kathmandu Valley junctions**; **ANPR
  cameras deployed** at Balkumari, Mahalaxmisthan, Dhobighat on the Ring Road; a CCTV
  control room booked 4,314 violators in seven months
  [(Kathmandu Post)](https://kathmandupost.com/valley/2023/07/07/number-plate-reader-cameras-introduced-in-valley). → The deployment story is **real**, strengthening the "deployable prototype as context" angle. But this footage is **police/government-controlled → not a data source for us.**
- **⚠ Scope-changing finding — the embossed-plate rollout.** Nepal made **ANPR-readable
  high-security embossed number plates mandatory nationwide from Ashoj 1, 2082
  (Sept 17, 2025)** — standardized Latin alphanumeric layout encoding province, **vehicle
  category (A–K)**, age code, and number
  [(ITS International)](https://www.itsinternational.com/its4/news/nepal-government-implements-anpr-readable-number-plates), [(techlekh)](https://techlekh.com/embossed-number-plate-nepal/). **This partially undercuts the old "plates are unreadable Devanagari" framing.** It does *not* kill the E6 sub-study — standoff CCTV resolution still limits *any* OCR regardless of plate design — but the framing must update: *the bottleneck is now pixels-on-plate (resolution), not script*, and the plate encodes vehicle category, which is itself interesting. **Recommendation: update [`05_experiment_protocol.md`](05_experiment_protocol.md) E6 and the charter's ANPR rationale to reflect old-Devanagari vs new-embossed plates.**

## 6. The gaps (precise, enumerated)

1. **G1 — No detection dataset.** No public Nepali traffic dataset with bounding boxes,
   fine-grained vehicle classes, helmet compliance, and signs. *(C1)*
2. **G2 — No Nepali detection benchmark.** No accuracy/efficiency comparison of detectors
   on Nepali traffic; no edge/real-time numbers for this context. *(C2)*
3. **G3 — No Nepali helmet-detection resource.** Helmet datasets exist globally
   (Roboflow), none Nepal-specific despite helmet non-compliance being a top killer. *(C2)*
4. **G4 — Nepali signage under-served.** Only one community Roboflow Nepali sign set, of
   unknown quality/license; no benchmarked Devanagari+English mixed-sign detection. *(C2/C3)*
5. **G5 — No failure/condition analysis** for Nepali conditions (occlusion, night,
   monsoon, dust, dense two-wheelers) — nobody has quantified where detectors break. *(C3)*
6. **G6 — Plate-legibility threshold unmeasured** for Nepali standoff cameras (old vs new
   plates). *(C3 / E6)*

## 7. Issues & risks flagged

| # | Issue | Why it bites | Severity |
|---|---|---|---|
| I1 | **Build-from-scratch data** — no reusable detection set | Annotation is the project's critical path | High |
| I2 | **Severe class imbalance** (motorcycles 79%+) | Hurts per-class AP; minority classes starve | High |
| I3 | **Legal/privacy** — Privacy Act 2075 (consent, PII) | Faces/plates are PII; police footage off-limits | High |
| I4 | **Plate-framing shift** (embossed rollout) | Old "unreadable Devanagari" claim now weaker | Medium |
| I5 | **Single-city bias** (Kathmandu-only is easy to gather) | Weakens generalization claim; reviewers flag it | Medium |
| I6 | **Existing assets not directly reusable** (classification, unverified) | Can't shortcut the dataset; can only seed/compare | Medium |
| I7 | **Roboflow sign set** quality/license unknown | Risky to depend on without auditing | Medium |
| I8 | **Solo compute/labor** | Limits dataset size and model count | Medium |

## 8. Solutions & recommendations (issue → action)

- **I1/I6 → Build, but stand on what exists.** Build NepTraVision-Bench as a *detection*
  dataset (boxes). Use `vehicles-nepal-dataset` as a *comparison/pretraining* reference
  and a sanity check, not as training labels. Use COCO-pretrained models for
  semi-automatic pre-labelling to cut annotation time (then human-correct).
- **I2 → Design for imbalance.** Report **per-class AP** (already in E1), keep mosaic/HSV
  augmentation (already in `configs/models/_base.yaml`), and ship the **`simple` profile
  first** (two-wheeler + helmet) so the highest-impact classes are solid before breadth.
- **I3 → Privacy-by-construction.** Public-space self-recording only; **blur faces and
  plates** before release; document source/purpose/consent per the Privacy Act 2075
  (penalties up to 3 yrs / NPR 30,000) [(Pioneer Law)](https://pioneerlaw.com/individual-privacy-act-2018-2075/); release under CC BY-NC 4.0. This is already the stance in [`07_ethics_privacy.md`](07_ethics_privacy.md) — now legally grounded.
- **I4 → Reframe E6.** Measure the legibility threshold on **both** old Devanagari and new
  embossed plates; headline becomes *"usable ANPR needs ≥ N px plate height; typical
  Nepali standoff CCTV gives M < N — regardless of the new plate standard."*
- **I5 → Multi-location from day one.** Even 3 locations (e.g. Kathmandu intersection +
  Ring Road + one Terai/Pokhara road) materially strengthens the dataset card and the
  split-by-source story.
- **I7 → Audit before use.** Evaluate the Roboflow Nepali sign set's license and label
  quality; if usable, fold it in as an **external test set** (a strong generalization
  result) rather than mixing into train.
- **I8 → Stay nano + Colab.** The edge literature confirms YOLO-nano/YOLO11 fine-tune on
  free Colab in hours and run real-time on a Pi 5 at small input sizes — the plan is
  compute-feasible (see feasibility study §3).

## 9. Recommended changes to the project (carry into the repo)

1. **Update E6 + charter ANPR rationale** for the embossed-plate reality (I4). *(propose ADR-0002)*
2. **Confirm `simple`-profile-first** as the M1 default given imbalance + solo labor (I2/I8).
3. **Add `vehicles-nepal-dataset` and the Roboflow sign set** to the dataset card's
   "related datasets / external evaluation" section.
4. **Bake Privacy Act 2075** explicitly into the ethics doc and dataset card (I3).
5. **Target ≥3 locations** in the collection plan (I5).

---

*These findings sharpen — not weaken — the project: every contribution (C1–C3) now maps
to an enumerated, evidence-backed gap (G1–G6), and the biggest risks have named
mitigations. Proceed to the [feasibility study](10_feasibility_study.md) for the go/no-go.*
