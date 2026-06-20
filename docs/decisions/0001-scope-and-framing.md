# ADR-0001: Scope and framing — reconcile the two source proposals

- **Status:** Accepted
- **Date:** 2026-06-20

## Context

The project was specified across two overlapping document sets:

- **Track A** (`Nepali_Traffic_CV_*`): "NepTraVision" — an 18-class benchmark
  (vehicles + helmet + signs) and a full FastAPI/WebSocket prototype. Rich scope;
  the prototype is foregrounded.
- **Track B** (`files (1)/`): "NepalTraffic" — a tighter, more rigorous
  *dataset + edge-efficiency benchmark + resolution/failure analysis*, with the
  honest "ANPR is infeasible at CCTV resolution, so measure the threshold" framing.
  Methodologically stronger; the prototype is explicitly *context, not claim*.

A single paper cannot foreground both "look at my dashboard" and "here is a
rigorous benchmark." Foregrounding the system is the classic trap that makes an
engineering project *not* a research contribution.

## Decision

We **merge the scope of Track A with the rigor and framing of Track B.**

1. **Project name:** **NepTraVision** (Track A's name; more distinctive). Dataset
   artifact: **NepTraVision-Bench**.
2. **Taxonomy:** adopt Track A's concrete **18-class** scheme (vehicles + helmet +
   signs) as canonical, because it is the most complete and is already frozen in
   the annotation guide. A `simple` profile (merged two-wheeler / helmet-only) is
   provided in `configs/classes.yaml` for a reduced first pass if annotation volume
   is tight. The merge rationale is documented, per the dataset guide's rule to
   "freeze merges before annotating."
3. **The paper's claims are Track B's three:** (C1) dataset, (C2) edge-efficiency
   benchmark, (C3) failure & resolution analysis incl. the plate-px threshold.
4. **The prototype is deployment context**, demonstrated but not evaluated as the
   contribution.
5. **Methodology is Track B's rigor:** leakage-safe split *by source/location/time*;
   3 seeds, mean±std; multi-hardware efficiency tiers; resolution sweep; INT8;
   condition breakdown.
6. **Two-paper option kept open:** a dataset paper (A) and a benchmark paper (B) can
   split one collection effort. Default is one strong combined paper; revisit at M4.

## Consequences

- One coherent, reviewer-proof narrative: *data + measurement for an
  underrepresented setting*, with a working demo as a bonus.
- The 18-class scope is ambitious for a solo annotator; the `simple` fallback and
  the staged roadmap mitigate this. Helmet and sign classes may ship as a v1.1 if
  vehicle-only annotation already hits the publishable bar.
- We must resist scope creep back toward "the dashboard is the paper." The charter
  and this ADR are the guardrail.

## Supersedes / superseded by

None. Revisit the one-vs-two-paper question at milestone M4.
