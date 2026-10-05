---
id: T-0225
title: "Solo sessions write no cost record, so the budget gate cannot see the default lane"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P1
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A solo session started through its documented start path writes one runs.jsonl record with its real cost and usage, so budget.py, the board Budget column and footprint count the default lane.

## Intent
- Do: add scripts/solo_run.py (one wrapper: start solo at the tier's model and effort, parse the result event, append a role solo record in the run.sh record shape to the task folder's runs.jsonl, cost_usd null with a reason and never zero when the result has no usage); make agents/solo.md name it as the way to start solo (raw command stays as the fallback); selftest with a stub claude and a negative control; check.py guard.
- Non-goals: model or effort defaults; fanout's solo driver (it keeps the raw command until solo-skips has merged, a follow-up); Codex cost (codex_exec.py reports none, recorded as null with a reason); a version bump, tag, push, or publish.
- Done when: the selftest passes, one live headless solo run through the wrapper shows a solo record whose cost matches the result event and budget.py status reports it, an independent L3 verifier passed.

## Context
0.20.6 release limit: "solo sessions' own cost wasn't captured". budget.py sums cost_usd over every runs.jsonl under the ticket (any role) and counts a record with no numeric cost as unmetered, so writing the record is enough. User decision 2026-10-04: include in 0.20.7.

## Constraints
Keep it small. One authoritative location per fact. Philosophy: "Done is better than perfect." No em dashes.
