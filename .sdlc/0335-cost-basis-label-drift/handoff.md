---
id: T-0335
title: "cost_basis label for transcript pricing drifted from the T-0280 criterion and its docstring is stale (T-0280 finding)"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P3         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The `cost_basis` label for transcript pricing is one agreed string across the code, the docs and the T-0280 criterion, and `cost_estimate.py`'s docstring no longer says transcript pricing is not assumed. The bug is fixed and a test that failed before the fix passes after it.

## Repro
1. `grep -n 'transcript usage x price' plugins/sdlc-lite/scripts/cost_estimate.py` finds only the docstring at line 12.
2. `grep -n 'BASIS_USAGE' plugins/sdlc-lite/scripts/cost_estimate.py` shows the label the code writes at line 25: `usage fields x rates`.
3. In a temp git repo, `dispatch.py prepare verifier L1 <handoff>` then `dispatch.py record <dispatch.json> --transcript <jsonl>`: the runs.jsonl line holds `cost_basis "usage fields x rates"`.

## Expected
T-0280 says `record` writes `cost_basis` as `tokens x blended`, or `transcript usage x price` when the transcript is priced. The code and the docstring agree with one label.

## Actual
The tree writes `usage fields x rates`. The docstring at `cost_estimate.py:12` still says "Probe P5 (transcript usage x price) is not assumed" although `dispatch.py:702` and `:735-737` implement it. Every behavioral clause of T-0280 holds (observed); only the label and the stale text differ.

## Context
Found by the independent verifier of T-0280 (criterion T0280-2), `.sdlc/verify-subagent/T-0280.md`. Stored history rows keep the old strings, so a rename must keep readers (`dispatch.py:70-71`, the solo_run and fanout selftest cases) in step; fixing the docstring and treating `usage fields x rates` as the label is the smaller change. The owner decides.

## Constraints
No change to prices or calibration values. The failing check lands before or with the fix. No em or en dashes. No push or publish.
