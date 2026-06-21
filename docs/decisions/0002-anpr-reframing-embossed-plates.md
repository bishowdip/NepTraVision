# ADR-0002: Reframe the ANPR / plate-resolution sub-study for the embossed-plate era

- **Status:** Accepted
- **Date:** 2026-06-21
- **Supersedes part of:** ADR-0001's ANPR rationale and `05_experiment_protocol.md` §E6.

## Context

The Nepal landscape research ([`09_nepal_landscape.md`](../09_nepal_landscape.md) §5)
surfaced a fact that changes one of the project's framing claims: Nepal made
**ANPR-readable high-security embossed number plates mandatory nationwide from Ashoj 1,
2082 (17 September 2025)**. The new plates are standardized, Latin alphanumeric, designed
to be camera-readable, and encode the vehicle category (A–K), province, and age code
([ITS International](https://www.itsinternational.com/its4/news/nepal-government-implements-anpr-readable-number-plates)).

Our original framing (from the source proposals and ADR-0001) leaned on *"Nepali plates
are unreadable Devanagari script"* as the reason plate-OCR is hard. With the rollout,
**script is no longer the core blocker** — and pretending otherwise would be factually
wrong and easy for a reviewer to reject.

## Decision

1. **Reframe E6 around resolution, not script.** The measured finding becomes:
   *"Usable plate OCR needs ≥ N px plate height; typical Nepali standoff/CCTV footage
   yields M < N — independent of plate design."* The blocker is **pixels-on-plate**, which
   the embossed standard does not fix.
2. **Measure both plate generations.** Where data allows, report the legibility threshold
   for **old (embossed-pre-2020 / Devanagari) and new (embossed) plates** separately, so
   the result is robust to the transition.
3. **Note the category-encoding angle.** Because the new plate encodes vehicle category,
   future ANPR work could read category without OCR-ing the full number — record this as
   a future-work observation, not a v1 claim.
4. **Keep plate-OCR as a sub-study / future work**, exactly as ADR-0001 set out. The
   reframing changes the *justification*, not the scope.

## Consequences

- The ANPR rationale is now factually current and reviewer-proof.
- `05_experiment_protocol.md` §E6 and `configs/experiments/e6_plate_resolution.yaml`
  should mention the old/new plate split when the plate data is assembled (M3/M4).
- The charter's "ANPR reality" bullet should be softened from "unreadable script" to
  "resolution-limited at standoff distance, regardless of the new ANPR-ready plates."
- No code changes required now; `plate_resolution.py`'s threshold logic already supports
  reporting per-subset curves.
