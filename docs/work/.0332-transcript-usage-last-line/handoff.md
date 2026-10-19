---
id: T-0332
title: "Transcript usage takes the first partial line per message id"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`cost_estimate.transcript_usage` sums the last usage line per message id (the final counts), and the calibration in `adapters/claude/prices.json` is refit so a live fable verifier row lands within 35 percent of the host.

## Repro
1. `python3 plugins/sdlc-lite/scripts/cost_estimate.py selftest` with a transcript fixture whose first line per id has output 8 and last line 10.
2. Price any real sub-agent transcript: the first line per id holds early partial counts (output 8), the cache fields of the last line match the host's modelUsage exactly.

## Expected
Estimate within 35 percent of the host cost.

## Actual
Final-rerun verifier stored at $1.769 against host $3.638 (0.49).

## Context
Found by the final live rerun (docs/reports/2026-10-07-subagent-mode-live.md, `Final rerun after T-0329 to T-0331`). Root cause confirmed: first line per message id wins in `transcript_usage`.

## Constraints
The failing test lands with the fix. No em or en dashes. No push or publish.

## Closed

## Closed

2026-10-06: fixed in the final live rerun commit; cost_estimate selftest passes
