# 12-Week Roadmap

> Mapped to the milestones in the [README status table](../README.md#-project-status-living).
> Window: Aug–Nov 2026 (flexible). Solo, compute-light.

| Week | Focus | Milestone | Key deliverables |
|---:|---|:---:|---|
| 1 | **Finalize scope** | M0 | Title, classes frozen, OCR demoted to future work. ✅ (foundation done) |
| 2 | **Literature review** | M0 | YOLO/detection, traffic CV, helmet detection, sign recognition, IOEGC gap survey. |
| 3 | **Data collection** | M1 | Footage across conditions; folder structure; remove low-quality/private; dataset-card draft. |
| 4 | **Frame extraction & cleaning** | M1 | FFmpeg extraction; dedup; select 1,000+ useful images. |
| 5 | **Annotation setup** | M1 | Tool set up; class list; annotate first 300; review quality. |
| 6 | **Complete dataset v0** | M1 | Annotate remainder; export YOLO; leakage-safe split; agreement on QC subset. |
| 7 | **Baseline training** | M2 | Fine-tune YOLOv8n + YOLOv8s; save metrics + confusion matrix (3 seeds). |
| 8 | **Model comparison** | M2/M3 | Add 1–2 baselines; compare mAP/F1/P/R/FPS; efficiency sweep; qualitative errors. |
| 9 | **Prototype integration** | M5 | Replace mock detector with trained model; count + helmet-alert endpoint; dashboard. |
| 10 | **Results & discussion** | M4 | Result tables; Pareto plot; error analysis; resolution + plate-px study. |
| 11 | **Write paper** | M6 | Abstract → conclusion draft. |
| 12 | **Final polish** | M6 | References, figures, plagiarism check, supervisor review, submission. |

## Notes

- Weeks are a *guide*, not a contract — dataset quality (M1) is the gate; do not rush
  it to hit a week number.
- The two-paper split (dataset paper vs. benchmark paper) is decided at end of M4.
- Each completed item is reflected in the README status table and `CHANGELOG.md`.
