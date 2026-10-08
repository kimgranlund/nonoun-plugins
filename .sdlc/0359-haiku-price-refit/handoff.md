---
id: T-0359
title: "Refit the Haiku rows in prices.json for claude-haiku-5-5"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-07
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The cost estimator prices claude-haiku-5-5 runs within the 35 percent band of the host's cost.

## Intent
- Do: refit the haiku rows in prices.json (find it with git ls-files) for Haiku 5.5: $0.10/$0.50 per MTok up to 100K prompt tokens, $0.50/$2.50 above, cache read $0.01, write $0.125 (5m) / $0.20 (1h), about 30 percent more tokens than 4.5. Use the recorded scout runs (resolved model claude-haiku-5-5) and the eval 0002 numbers (host cost 0.0056 against the 0.034 estimate) as calibration, following how T-0332 refit the other rows, and keep the calibration selftest in cost_estimate.py green with a haiku fixture and a negative control.
- Non-goals: model or effort changes.
- Done when:
  - cost_estimate.py selftest passes including a claude-haiku-5-5 row inside the band and a rejected out-of-band table.
  - check.py and tickets.py check pass; the prices.json note matches the new rows.

## Context
User approved the refit on 2026-10-07 for 0.21.3. The T-0353 verifier noted the note quotes only the lower cache tier.

## Constraints
No em or en dashes. No push or publish.
