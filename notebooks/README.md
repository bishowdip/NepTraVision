# `notebooks/`

Exploration and figure-prototyping only. Notebooks **import** `neptravision` and call
into it; they never define reusable logic (that belongs in `src/`, where it can be
tested). Keep them numbered and short, e.g.:

- `01_explore_frames.ipynb` — eyeball extracted frames, sanity-check dedup.
- `02_class_distribution.ipynb` — visualise the dataset card stats.
- `03_pareto_draft.ipynb` — prototype the headline figure before scripting it.

Clear outputs before committing (or keep notebooks out of git entirely).
