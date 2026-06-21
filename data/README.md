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
neptravision data probe-videos             # → raw_videos/capture_log.csv (auto metadata)
#   ↳ open capture_log.csv and fill `weather` + `density` per clip
neptravision data extract-frames
neptravision data deduplicate --apply      # → selected/
neptravision data select                   # drop blurry
neptravision data build-manifest           # → dataset/metadata.csv (inherits conditions)
# ... annotate selected/ images, export YOLO labels into dataset/labels/...
neptravision annotation validate
neptravision data make-splits
neptravision data write-data-yaml
neptravision data stats
```

See `docs/02_dataset_guide.md` for the full guide.

---

## 📱 Filming on a phone (iPhone 14 Pro Max, etc.)

You do **not** need the camera to overlay time, temperature, or location on the video.

**What the phone embeds automatically** (extracted by `neptravision data probe-videos`
via `ffprobe`): capture timestamp → `time_of_day`, GPS lat/lon (if Location is on),
resolution, fps, and device model.

**What no camera records — you note these by hand** (once per clip, in
`capture_log.csv`): `weather` (clear/rain/dust/fog), `density` (low/medium/high), and
`location` name if GPS was off.

**Practical tips:**
- **Turn on Location for the Camera** (Settings → Privacy & Security → Location Services
  → Camera → *While Using*) so GPS is embedded. Optional but nice for the dataset card.
- **Transfer with AirDrop, Finder/USB, or the Files app** — these preserve the embedded
  metadata. Sending through some chat apps re-encodes the file and **strips** it; if that
  happens, just fill `time_of_day`/`location` by hand.
- **`.mov`/HEVC is fine** — `ffmpeg`/`ffprobe` read it directly.
- **One clip = one `source_id`.** Give each file a stable, descriptive name (e.g.
  `ringroad_kalanki_morning_01.mov`); all its frames inherit that group for leakage-safe
  splitting. Don't merge multiple locations into one file.
- **Shoot for diversity, safely:** a fixed, elevated, *public* vantage (overpass,
  footbridge, upper floor); steady framing; vary location × time-of-day × weather. Never
  film from a moving vehicle you're operating or in unsafe roadside positions.
- **Privacy:** wide shots where individuals aren't identifiable; faces and plates get
  blurred before any release (see `docs/07_ethics_privacy.md`). This is also a legal
  requirement under Nepal's Privacy Act 2075.
