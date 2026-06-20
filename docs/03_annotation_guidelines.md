# Annotation Guidelines (the 1-pager — follow it exactly)

> Re-read this at the **start of every annotation session**. Consistency beats
> coverage. When in doubt, follow the rule, not your intuition. Classes are defined
> in [`04_class_definitions.md`](04_class_definitions.md).

## Bounding boxes

- Draw a **tight** box around the **visible** object. Do not estimate the hidden
  part of an occluded object.
- **Box every object** whose majority (>~60%, ≥ ~15 px) is visible.
- **Skip** if < ~30% visible / < ~15 px / < ~5% of the object resolvable — *unless*
  it is still clearly identifiable.
- **Occlusion:** annotate the visible extent; if > ~70% occluded, skip.
- **Truncation (frame edge):** annotate the visible part only.
- **Crowded scenes:** annotate all distinct objects you can resolve.
- **Ambiguous type:** use the catch-all (`other`/`car_van_jeep` per the rule below);
  **do not guess** a specific local type you can't actually see.

## Riders & helmets

- Annotate the **rider** separately from the motorcycle where possible.
- Annotate **helmet** / **no_helmet** around the **head/helmet region**, only if the
  head region is visible enough to judge.
- **Passengers** use the same helmet / no_helmet classes.
- A motorcycle + rider together → annotate **both** the vehicle and the
  helmet-related class.
- Do **not** confuse a cap, hood, or hair for a helmet. If unsure, prefer
  `no_helmet` only when clearly bare-headed; otherwise skip the head box.

## Vehicles

- Classify by **what you can see**, not by ownership (ownership needs plate
  colour/text → a separate, resolution-limited problem, out of scope here).
- For buses and microbuses, use `bus_microbus` unless a separate dataset has enough
  samples to split them.
- Confusable pairs to watch: motorcycle ↔ scooter (merge to two-wheeler in the
  `simple` profile); bus ↔ truck; tempo/e-rickshaw ↔ car.

## Traffic signs

- Annotate **visible physical signs** only.
- Do **not** annotate text painted on the road (unless a separate class is created).
- For **traffic lights**, annotate the **signal head**, not the pole.
- Faded/partially-occluded signs: annotate if the type is still identifiable.

## Golden rules

1. **Freeze the taxonomy before you start.** Any merge/split decision is made once,
   documented in [`04_class_definitions.md`](04_class_definitions.md), and never
   changed mid-dataset.
2. **Consistency > coverage.** A consistently-labelled smaller set beats a noisy
   larger one.
3. **When unsure, skip rather than guess.** A missing box is recoverable; a wrong
   label silently corrupts the benchmark.
4. **Validate after every batch:** `neptravision annotation validate <labels_dir>`.
