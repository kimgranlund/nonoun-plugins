---
id: T-0336
title: "The L3 verifier row of the live evidence prices at 0.57 of host after the T-0332 refit (T-0328 and T-0331 finding)"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P3         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
T-0328's and T-0331's stated condition (the L2 and L3 verifier rows within 35 percent of the host figure) either holds on a stored record, or a new dated record states the L3 row as an accepted outlier and narrows the claim. The bug is fixed and a test that failed before the fix passes after it.

## Repro
1. Price the L3 fable verifier transcript of the live run (agent a904ad1cad883ca4b, usage 198 input, 8288 output, 332971 cache read, 51769 cache write) with `cost_estimate.estimate('fable', usage, cost_estimate.load())`: about 1.41 USD against the host figure 2.4762 in `docs/reports/2026-10-07-subagent-mode-live/host-cost.txt`.
2. The stored rows: `L3-runs.jsonl` holds only a notice count that prices at 0.17 USD, and `transcript-summary.txt` holds an all-lines sum that prices at 3.56 USD.

## Expected
The L3 row prices within 0.65 to 1.35 of the host figure, or the report set says plainly that it does not and why.

## Actual
0.570 of host from its surviving transcript, 0.069 from its stored row, 1.438 from the stored all-lines sum. The L2 row holds (0.93 to 1.09). The T-0332 refit (input x225, output x1.27) was fitted on the R1, F and L2 rows and dropped the L3 fixture (`cost_estimate.py:165-170`).

## Context
Found by the independent verifiers of T-0328 (T0328-1) and T-0331 (T0331-3), `.sdlc/verify-subagent/T-0328.md` and `.sdlc/verify-subagent/T-0331.md`. Already conceded in `docs/reports/2026-10-07-subagent-mode-live.md:185` and in the release record's known limitations ("one earlier verifier row stays outside the 35 percent band"), so this is a known limit now stated as a failed criterion. Reports are immutable dated evidence (`docs/reports/AGENTS.md`): the fix is a new record, either a refit that puts all four stored fable rows (L3 0.570, G 0.745, F 0.830, R1 0.847) inside the band, or an accepted-outlier record. Suspected cause, a guess: the L3 run's cache-read and cache-write counts differ in kind from the other rows.

## Constraints
No model or effort change. The failing check lands before or with the fix. No em or en dashes. No push or publish.

## Closed

2026-10-07: built and merged by fanout lane (batch fix021)
