---
id: T-0565
title: "Lane merges stop conflicting on generated .sdlc/AGENTS.md and roadmap.md"
type: chore           # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0564]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Merging a lane into main never stops on a conflict in the generated `.sdlc/AGENTS.md` (and nested `messages/**/AGENTS.md`) or `.sdlc/roadmap.md`; they come out equal to what `tickets.py roadmap` writes for the merged tree.

## Intent
- Do:
  1. Pick the smaller fix that holds: a git merge driver (`.gitattributes` plus a `merge.sdlc-roadmap.driver` that takes either side, then regenerates with `tickets.py roadmap` after the merge) installed by onboarding and `lanes.py open`, or stop tracking the generated files and regenerate on read. State the choice and why in the Outcome.
  2. `fanout.py land` and the lane merge path regenerate after the merge so the committed files match.
- Non-goals: changing what the generated files contain.
- Done when: the criteria pass.

## Context
Every wave in this repo hit this: two lanes each regenerate the router and roadmap, and the merge into main conflicts. Today the conductor resolves by `git checkout` of one side plus `tickets.py roadmap`. Code: `plugins/sdlc-lite/scripts/tickets.py` (`roadmap`), `fanout.py` (`land_command`, line ~1916), `lanes.py open`.

## Constraints
A conflict in any non-generated file still stops the merge.

## Acceptance criteria
1. A selftest case (in `fanout.py selftest` or `tickets.py selftest`) builds two lanes that each file a ticket, merges both into main, and shows no conflict and a router and roadmap equal to a fresh `tickets.py roadmap`; it failed before the change.
2. The same fixture with a real conflict in a non-generated file still stops the merge.
3. `bash plugins/sdlc-lite/scripts/run-selftest.sh` and `git diff --check` exit 0.
