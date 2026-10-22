---
id: T-0714
title: "Review-fix resume refreshes the recorded end tree and keeps the report header"
type: bug             # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
After a review-fix resume (builder recorded, ui-designer changes-required, builder resumed by SendMessage and fixes), the verifier's Diff range covers the fix and the builder's result file keeps a valid `<!-- role=... -->` header.

## Intent
- Do: in `plugins/sdlc-lite/scripts/dispatch.py`, add a re-record path for a resumed attempt (for example `dispatch.py record --update <dispatch file>`) that re-reads the report file, re-adds the header (about line 1796) when missing, and refreshes the stored end tree hash / end-sha so the next verifier `prepare` Diff range ends at the fix. Name the new step in the review relay text where the conductor is told to resume the builder (search `skills/` and `agents/conductor.md` for the review relay). Add selftest cases for both gaps.
- Non-goals: changing the review flow itself.
- Done when: the criteria pass.

## Context
GitHub issue #47 (quoted):

> ## What happened
> This follows #21, which gave the verifier a diff range. Two gaps remain when a ui-designer review sends a build back:
>
> 1. The verifier's `Diff range` ends at the tree hash that `dispatch.py record` saved for the builder. Fixes the same builder makes after record, resumed by SendMessage per the review relay, fall outside that range. The brief even says "later edits in Tree are not this step's". I had to add a `## Review fix` note to every such step handoff telling the verifier to check the working tree.
> 2. When the resumed builder rewrites its report file, the `<!-- role=... -->` header that record added is lost. `steps.py next` then prints `invalid result: ... first line is not a <!-- role=<r> level=<L> ... --> header`, and I restored the header by hand.
>
> ## Expected
> - One option is a `dispatch.py record --update <dispatch>`, or a re-record path, that refreshes the end tree hash and re-adds the header after a review-fix resume.
> - Another is to have prepare for the verifier take the current working tree hash when the step handoff carries a review-fix marker.
>
> ## Repro
> 1. builder (record) → ui-designer changes-required → SendMessage the builder → it fixes and rewrites builder-L<n>.md.
> 2. `steps.py next` reports an invalid result, and the verifier brief's Diff range omits the fix.
>
> Seen on 0.30.0.

## Constraints
The failing test lands before or with the fix, never after.

## Acceptance criteria
1. A `dispatch.py` selftest case: record a builder, change the tree, rewrite the report without its header, run the re-record path, then prepare a verifier: the result file starts with a valid header and the Diff range ends at the new tree; with the change reverted, the case fails (state the FAIL line in the Outcome).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0, and `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
