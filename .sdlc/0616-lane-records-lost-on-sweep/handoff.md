---
id: T-0616
title: "Lane run records vanish when gen-ui-kit lanes are swept, so fleet_collect undercounts"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-18
claimed_by: sdlc-lite-author 2026-10-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A lane's run records (runs.jsonl, attempt and result files) survive the lane's sweep or close and reach the main checkout's records dir, so `fleet_collect.py` counts the runs, proven by a selftest that sweeps a lane and still finds its runs.

## Repro
1. `python3 plugins/sdlc-lite/scripts/fleet_collect.py collect /Users/kimgranlund/Projects/adia/ui-kit/main --gh --since 2026-10-17` prints `runs: 1 deduped, $0.00`.
2. The gen-ui-kit conductor reports 13 merged lanes (#575 to #590) and one solo run recorded at `cost_usd 62.529069` in that window (`.sdlc/runtime/tasks/fleet-retro-2026-10-18/gen-ui-kit-interview.md`).
3. `ls /Users/kimgranlund/Projects/adia/ui-kit/lanes` holds none of the cf1 to cf7 lanes; `find /Users/kimgranlund/Projects/adia/ui-kit/main/.sdlc -name runs.jsonl -mtime -2` finds nothing.

## Expected
Closing or sweeping a lane copies its `.sdlc/runtime/tasks/<ticket>/` records into the main checkout (as `lanes.py finish` does here), so the collector sees every lane run.

## Actual
The fingerprint holds 1 run from 1 runs file (`.sdlc/runtime/tasks/fleet-retro-2026-10-18/gen-ui-kit.json :: runs.sources`), while 13 lanes ran and merged. Which sweep removed the lanes (gen-ui-kit's own sweep, `lanes.py sweep`, or the maintainer `~/.claude/lane/sweep.py`) is not yet known [U].

## Context
Found by the 2026-10-18 fleet retro (`docs/reports/2026-10-18-fleet-retro.md`, Observation): 5 of its 9 rows failed the rubric's G1 gate because their evidence lived in swept lanes. First step is diagnosis: find which sweep path gen-ui-kit uses and whether it archives records (AGENTS.md Lanes: "archive its untracked records").
outcome metric: `fleet_collect.py collect <gen-ui-kit>` runs count over a window with merged lanes, before: 1 run for 13 lanes

## Constraints
The failing test lands before or with the fix, never after. Read-only toward gen-ui-kit; reproduce with a throwaway repo.
