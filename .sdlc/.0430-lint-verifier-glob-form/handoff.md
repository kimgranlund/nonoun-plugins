---
id: T-0430
title: "steps.py lint misses a circular criterion written with a verifier-L* glob"
type: bug             # feature | bug | chore | spike | idea
status: done
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-10
claimed_by: claude 2026-10-10
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`steps.py lint` refuses a criterion that depends on the same step's verifier result when it names the result with a glob (`verifier-L*`), not only with a level digit.

## Intent
- Do: in scripts/steps.py, `VERIFIER_RESULT_RE` (about line 1529) and the per-step check `\bstep-{n}/verifier-L\d` (about line 1541) need a digit, so `step-2/verifier-L*.md` passes lint and the circular criterion escapes (T-0415). Accept `verifier-L` followed by a digit, `*`, `?` or `[`. Keep the `[owner: <stage>]` exemption working for the glob form.
- Non-goals: changing what counts as circular; model or effort changes.
- Done when:
  - A steps selftest case, observed failing first: a criterion with `step-2/verifier-L*.md` in step 2 is refused ending in `plan defect:`, the same with `[owner: integration]` passes, and the digit form still behaves as before.
  - steps.py selftest, check.py and tickets.py check pass.

## Context
0.22.3 batch verifier (.sdlc/verify-0.22.3-batch/verifier-L3.md), criterion T-0415: the glob form `step-2/verifier-L*.md` printed `steps lint: ok` (steps.py:1529 and 1541). The batch's T-0408 failure is a defect in the batch handoff, not in the build: `tickets.py selftest` prints only `tickets selftest: PASS`, so a criterion that greps for `ok:` lines can never pass.

## Constraints
No em or en dashes. No push or publish.

## Closed

2026-10-10: delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed
