---
id: T-0226
title: "Fanout solo lanes start the raw command, so their cost is not recorded"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P1
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A fanout solo lane starts the solo agent through scripts/solo_run.py, so each lane writes a `role solo` record with its cost into the ticket's runs.jsonl and budget.py, the board and footprint count the parallel default path.

## Intent
- Do: change fanout.py solo_command so the Claude and Codex solo paths run `solo_run.py run --task-dir <ticket folder> --tier <S|M|L> --brief <prompt> --backend <claude|codex>`; keep --driver overriding everything, keep `steps.write_solo_skips` (T-0224) and the tier table; keep a selftest-only escape that restores the raw command; add a selftest case with a stub claude printing a result event with total_cost_usd: a solo lane writes a solo record with that cost into the ticket's runs.jsonl, and with the wrapper bypassed it writes none (negative control); update the existing case 15 command assertions; update sdlc-internals.md and the solo-cost live-run record line that says fanout is unmetered.
- Non-goals: model or effort defaults; a live run (the stub selftest plus the wrapper's existing live proof are the evidence, recorded as a limit); Codex cost (null by design); a version bump, tag, push, or publish.
- Done when: fanout and solo_run selftests pass including the new case and its control, check.sh passes, an independent verifier passed.

## Context
Coordinator decision 2026-10-05: fanout solo lanes are the parallel default path, so leaving them unmetered undercuts the 0.20.7 claim that default lanes are metered. Follows T-0225 (merged at 46c9f51) and T-0224 (merged). Time box about 45 minutes from T-0224's merge; otherwise record fanout metering as a known limit. Philosophy: "Done is better than perfect." Budget about $8.

## Constraints
Keep it small. No em dashes. One authoritative location per fact.
