# `data/` — heavy artifacts (gitignored content, tracked structure)

Nothing here except this README and `.gitkeep` files is committed to git (see
`.gitignore`). The folder *structure* is tracked; the *content* (footage, frames,
images, labels) is not — it lives on disk and is released separately on Zenodo / HF.

## Layout

```text
data/
├── raw_videos/     ← drop source videos here (mp4/mov/avi/mkv). One file per session.
├── raw_frames/     ← `neptravision data extract-frames` writes frames here.
├── selected/       ← survivors of dedup + blur selection, ready to annotate.
├── interim/        ← scratch space for any intermediate step.
└── dataset/        ← THE RELEASE ARTIFACT (NepTraVision-Bench)
    ├── images/{train,val,test}/   ← final images, placed by split
    ├── labels/{train,val,test}/   ← YOLO .txt labels, mirroring images/
    ├── splits/                    ← committed split definition (by source-group)
    ├── metadata.csv               ← one row per image (source + conditions)
    └── data.yaml                  ← Ultralytics pointer (generated)
```

## Naming convention (important for leakage-safe splits)

Frame files are named `<source_id>_<frame>.jpg` (e.g. `ringroad_kalanki_000042.jpg`).
The `source_id` prefix is how the pipeline groups frames so that all frames from one
video/session stay in the same split. **Keep one source per video file** and give it
a descriptive, stable name.

## Typical flow

```bash
# put videos in raw_videos/, then:
neptravision data extract-frames
neptravision data deduplicate --apply      # → selected/
neptravision data select                   # drop blurry
neptravision data build-manifest           # → dataset/metadata.csv  (fill conditions!)
# ... annotate selected/ images, export YOLO labels into dataset/labels/...
neptravision annotation validate
neptravision data make-splits
neptravision data write-data-yaml
neptravision data stats
```

See `docs/02_dataset_guide.md` for the full guide.
