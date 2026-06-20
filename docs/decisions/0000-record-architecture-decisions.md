# ADR-0000: Record architecture decisions

- **Status:** Accepted
- **Date:** 2026-06-20

## Context

This is a first research paper that must withstand supervisor and reviewer scrutiny.
Decisions about scope, taxonomy, splits, and methodology will be questioned ("why
did you merge those classes?", "how did you prevent data leakage?"). Re-deriving the
reasoning months later, or defending it in a viva, is error-prone if it lives only
in someone's head.

## Decision

We keep **Architecture Decision Records (ADRs)** in `docs/decisions/`. Each
significant, hard-to-reverse choice gets a short numbered file: context, the
decision, and consequences. ADRs are immutable once accepted; a later ADR can
supersede an earlier one (note it in both).

## Consequences

- The "why" behind the project is auditable and citable in the paper's methodology.
- Onboarding a co-author or supervisor is a matter of reading `docs/`.
- Small overhead per decision; worth it for a publishable artifact.

## Format

```
# ADR-NNNN: short title
- Status: Proposed | Accepted | Superseded by ADR-XXXX
- Date: YYYY-MM-DD
## Context   (forces at play)
## Decision  (what we chose, in active voice)
## Consequences  (trade-offs, what becomes easier/harder)
```
