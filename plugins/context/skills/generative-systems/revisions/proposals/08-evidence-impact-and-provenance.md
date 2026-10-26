---
id: GS-P08
type: spec
status: implemented
created: 2026-10-11
target:
  - references/verification-and-drift.md
  - references/generation-and-revision.md
  - references/evidence-index.md
---
# Keep evidence qualification and provenance current

Priority: follow-up after reuse and isolation.

## Problem and responsibility

Generative Systems already requires checker controls and reuse of unaffected evidence. The missing detail is how to trace a shared change to affected claims. Its evidence index also does not route to the local split-consumption follow-up records. This is a provenance-discovery gap, not evidence that those records establish efficacy.

Generative Systems owns the reliability of generation checks and its lesson provenance. Progressive Context owns the general capability assessment format. Keep existing project records and avoid a second assessment registry.

## Proposed edits

In verification and drift (`references/verification-and-drift.md`), retain the existing known-valid case and intentional-fault requirement. Clarify that unchanged checker qualification can be reused within its tested scope, and that changed assertions require affected controls to be rerun. Do not duplicate this rule elsewhere.

Add one compact change-impact example to generation and revision (`references/generation-and-revision.md`):

> Follow existing source-to-consumer links to identify affected claims. A changed shared validation helper requires its consumers' affected invalid-input and recovery checks; unrelated typography evidence can remain current if its sources and environment are unchanged. A changed assertion requires checker qualification and reanalysis of affected retained outputs, not a claim of improved generation. Record uncertain dependencies as unresolved rather than assuming evidence remains current.

Reconcile the evidence index (`references/evidence-index.md`) with the split-consumption follow-up (`resources/reports/split-consumption-followup-2026-10-11/handoff.md`). Inspect the relevant protocol, criterion/evidence matrix, and result records before adding an index entry. Identify the lesson owner, exact evaluated versions, observation type, and limitations. Link retained local evidence where available; preserve historical reports and verdicts. Do not infer success from file existence, task status, or a publication record.

## Acceptance and verification

- A helper change leads to affected consumer checks without invalidating unrelated evidence by default.
- A changed evaluator leads to qualified reanalysis, distinguished from fresh generation.
- Index claims can be traced to identified result records and distinguish observations, proposals, unrun conditions, and efficacy conclusions.
- No sealed holdout is opened to choose improvements; use existing result records for provenance reconciliation.
- Inspect local links and run skill validation. A source-review walkthrough establishes guidance coverage only; do not claim new behavioral or cross-domain efficacy.

Keep all additions in existing references and the optional evidence index. No new runtime, registry, default evidence read, or benchmark batch.

## Disposition, 2026-10-11

Merged change-impact guidance into existing paragraph, clarified checker qualification reuse, reconciled index with retained protocol/matrix/results; no rerun claimed. Evidence: implementation and research report (`resources/reports/context-architecture-research-2026-10-11.md`). Documentation implementation does not demonstrate efficacy.
