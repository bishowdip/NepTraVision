# Dataset Construction Guide — NepTraVision-Bench

> This is the make-or-break artifact. **The dataset *is* the contribution** — spend
> your care here. Consolidated from the two source guides. The class taxonomy is
> defined separately in [`04_class_definitions.md`](04_class_definitions.md); the
> per-box rules in [`03_annotation_guidelines.md`](03_annotation_guidelines.md).

## 1. Design goal

Capture the **real-world difficulty** that makes Nepali traffic distinct and that
off-the-shelf models fail on: motorcycle/scooter-dominated mixed traffic; local
vehicle types (tempo/auto, microbus, e-rickshaw, tractor); dense occlusion and
undisciplined lanes; day/night, clear/monsoon, urban/highway; and realistic camera
quality (CCTV/standoff, not only clean dashcam).

> A *diverse, honestly-hard* 2–4k-image set beats a large, easy, single-location one.

## 2. Sourcing (legal & ethical, in priority order)

1. **Your own recordings** — phone/camera from public vantage (intersections,
   overpasses). Most control over conditions and metadata.
2. **Publicly available Nepali traffic footage** (YouTube dashcam/CCTV channels) —
   check licence/ToS; prefer Creative Commons or get permission; document each source.
3. **Existing CCTV** only with explicit operator permission.

**Avoid:** private feeds; sensitive locations; anything whose provenance you can't
document; footage gathered by dangerous roadside behaviour.

**Log per source** (this becomes `data/dataset/metadata.csv`): location, date/time,
weather, resolution, fps, licence/permission. See [`manifest`](../src/neptravision/data/manifest.py).

## 3. Pipeline steps (each is a `neptravision data …` command)

| Step | Command | What it does | Source rule |
|---|---|---|---|
| 1. Extract | `data extract-frames --fps 1` | Video → frames at a controlled rate. | 1 FPS, or 1 frame / 2 s for dense traffic, to avoid duplicate frames. |
| 2. Deduplicate | `data deduplicate --threshold 6` | Drop near-duplicate frames via perceptual hash. | Adjacent frames are near-identical and **inflate scores massively** if split across train/test. |
| 3. Select | `data select` | Drop blurry / empty / too-tiny-object frames; keep diverse ones. | Keep multi-vehicle, two-wheeler, sign, occlusion, day/night/rain frames. |
| 4. Annotate | *(external tool — see below)* | Draw boxes in YOLO format. | Follow [`03_annotation_guidelines.md`](03_annotation_guidelines.md) exactly. |
| 5. Validate | `data validate-labels` | Reject malformed/out-of-range labels. | Catch class-id and coordinate errors before training. |
| 6. Split | `data make-splits --by source` | Leakage-safe train/val/test. | **Split by source-group, never randomly.** |
| 7. Convert | `data to-coco` / data.yaml | YOLO ⇄ COCO; Ultralytics `data.yaml`. | — |
| 8. Stats | `data stats` | Class distribution, condition matrix, counts. | Feeds the dataset card. |

## 4. Annotation tooling

YOLO format is canonical: one `.txt` per image, lines of `class cx cy w h`
(normalised). Recommended tools:

- **Roboflow** (free tier, fastest for solo; YOLO export + augmentation) — recommended.
- **CVAT** / **Label Studio** / **labelImg** (offline; fits a no-cloud preference).

Export to YOLO and drop labels next to images; the pipeline takes it from there.

## 5. Quality control (reviewers will ask)

- **Double-annotate** a 300–500 image subset with 1–2 classmates.
- Report **inter-annotator agreement** (mean IoU on matched boxes + class-label
  agreement) — `neptravision annotation agreement`.
- Spot-check 10% of all labels; fix systematic errors.
- Three passes per image where possible: first annotator → second reviewer →
  final correction.

**Common mistakes:** boxes too loose; wrong vehicle class; missing small
motorcycles; confusing helmet with hair/cap; mis-annotating overlapping signs.

## 6. Splits — avoid leakage (critical)

**Never** put frames from the *same video / location / session* in both train and
test. Split **by source/location/time**: hold out entire locations/sessions for the
test set. Default policy: **70 / 15 / 15 by source-group**, stratified across
conditions. Report the policy in the paper. This is enforced in code by
[`splits.py`](../src/neptravision/data/splits.py).

## 7. Metadata & dataset card

Ship a [dataset card](dataset_card.md): size, class distribution, condition-coverage
matrix (location × time × weather), resolution distribution, sources/licences,
annotation process, agreement numbers, known limitations, and the privacy statement.

## 8. Privacy (build in from day one)

Blur faces; blur/pixelate readable plates in released images; prefer wide shots
where individuals aren't identifiable; release under CC BY-NC 4.0 with a data
statement. Details in [`07_ethics_privacy.md`](07_ethics_privacy.md).

## 9. Realistic size target

| Tier | Images | Use |
|---|---|---|
| Minimum viable | ~1,500 | first dataset + baselines |
| Good | ~3,000 | solid condition coverage |
| Stretch | ~5,000 | if annotation is fast / you get help |

Spread across **≥3 locations, ≥2 times of day, ≥2 weather conditions.** Targets:
≥5,000 boxes (min) to 20,000+ (strong).

## 10. Release

Release on **Zenodo** (DOI → citable) and/or **Hugging Face Datasets**, with the
dataset card, `metadata.csv`, the split definition, annotation guidelines, and LICENSE.
