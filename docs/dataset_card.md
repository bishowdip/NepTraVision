# Dataset Card — NepTraVision-Bench

> Template to be filled as data is collected and annotated. Numbers marked `TBD` are
> populated by `neptravision data stats`. Keep this honest — it is the first thing
> reviewers read.

## Overview

| Field | Value |
|---|---|
| Dataset name | NepTraVision-Bench |
| Version | v0.0 (pre-release) |
| Author | Bishow Thapa |
| Release date | TBD |
| Code license | MIT |
| Dataset license | CC BY-NC 4.0 (research, non-commercial) |
| Citation | see `CITATION.cff` |
| DOI | TBD (Zenodo) |

## Collection

| Field | Value |
|---|---|
| Collection period | TBD |
| Locations | TBD (target: ≥3 — e.g. Kathmandu intersections, Ring Road, Pokhara, Terai highway) |
| Road types | urban intersection / ring-road / highway / hilly / bus-stop / school-zone |
| Sources | self-recorded smartphone / dashcam / public CC footage (documented per source) |
| Camera types | TBD |

## Coverage matrix (location × time × weather)

| | Day | Evening/Night | Rain/Monsoon | Dust |
|---|---|---|---|---|
| Location A | TBD | TBD | TBD | TBD |
| Location B | TBD | TBD | TBD | TBD |
| Location C | TBD | TBD | TBD | TBD |

Target: **≥3 locations, ≥2 times of day, ≥2 weather conditions.**

## Size

| Field | Value |
|---|---|
| Images | TBD (min 1,500 / good 3,000 / stretch 5,000) |
| Object instances (boxes) | TBD (min 5,000 / strong 20,000+) |
| Classes | 18 (`full`) or 3 (`simple`) — see `04_class_definitions.md` |
| Resolution distribution | TBD |

## Class distribution

| id | class | instances | % |
|---|---|---|---|
| … | … | TBD | TBD |

## Annotation

| Field | Value |
|---|---|
| Format | YOLO (`class cx cy w h`, normalised) |
| Tool | Roboflow / CVAT / labelImg |
| Guidelines | `docs/03_annotation_guidelines.md` (frozen) |
| QC process | first annotator → reviewer → correction; 10% spot-check |
| Inter-annotator agreement | TBD (mean IoU + label agreement on 300–500 subset) |

## Splits

| Split | % | Policy |
|---|---|---|
| train | 70 | by source-group |
| val | 15 | by source-group |
| test | 15 | by source-group, held-out locations/sessions |

**No frames from the same video/location/session appear in more than one split.**

## Privacy

Faces and readable plates blurred; public-space collection; raw footage stored
securely and deleted after annotation. See `docs/07_ethics_privacy.md`.

## Known limitations

- Size and geographic coverage limited (solo, single-season collection).
- Night/rain likely underrepresented.
- Helmet detection hard at small head sizes; signs hard when faded/occluded.
- Not validated for legal enforcement.
