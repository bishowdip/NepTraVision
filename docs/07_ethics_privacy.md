# Ethics & Privacy

> Non-optional. Traffic footage contains PII (faces, plates). Reviewers **will**
> check this. It is built into the pipeline from day one, not bolted on at release.

## 1. Collection

- Collect only from **public spaces** or **with explicit permission**.
- **Do not use:** private CCTV without permission; sensitive locations; footage that
  unnecessarily exposes people/faces/plates; anything collected by dangerous
  roadside behaviour.
- **Document every source:** location, date/time, weather, resolution, fps,
  licence/permission. This lives in `data/dataset/metadata.csv`.

## 2. Privacy protection before any image is published

- **Blur faces.**
- **Blur / pixelate readable number plates.**
- **Remove audio.**
- Prefer **wide shots** where individuals aren't identifiable.
- Avoid exact location details if sensitive.
- Do **not** publish raw continuous video unless permission is explicit.

## 3. Use restrictions

- The system is for **research and traffic analytics**, **not legal enforcement**.
- Predictions are **probabilistic** and require **human review**.
- Do **not** link detections to personal identity.
- License-plate OCR is **not** an evaluated contribution (camera-resolution limits);
  where plates are visible, blur or ignore them unless explicit permission + ethical
  clearance exist.

## 4. Data handling

- Store raw video **securely**; delete unnecessary footage **after annotation**.
- Released images are the curated, privacy-processed subset only — never the raw
  archive.

## 5. Release

- Dataset under **CC BY-NC 4.0** (research, non-commercial) with a **data
  statement** describing collection and processing. See [`dataset_card.md`](dataset_card.md).
- Code under **MIT**.

## 6. Honest limitations to state in the paper

Dataset size/coverage is limited; manual annotation contains human error; night/rain
may be underrepresented; helmet detection is hard at small head sizes; signs fail
when faded/occluded; the system is **not** suitable for automatic legal enforcement
without official validation.
