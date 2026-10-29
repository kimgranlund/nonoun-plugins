---
id: T-0805
title: "tickets.py claim refuses over an unrelated ticket's depends: id held only in a lane worktree"
type: bug             # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-29
claimed_by: sdlc-lite-author 2026-10-29
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`tickets.py claim <id>` refuses only for a defect in the claimed ticket, so an unrelated ticket's unresolved `depends:` no longer blocks a claim or the `lanes.py open --claim` that follows.

## Repro
1. In a repo with lane worktrees, close T-0552 inside a lane worktree only, so its `.0552-*` folder exists there and not in main.
2. Leave another open ticket whose `depends:` names T-0552.
3. From main run `tickets.py --root .sdlc claim T-0563`.

## Expected
The claim succeeds; at most a warning names the unrelated ticket's unresolved dependency.

## Actual
"depends on T-0552, which no ticket has ... nothing written" (agent-ui conductor, fleet retro 2026-10-29). `lanes.py open` then fails "not claimed".

## Context
- Fleet retro row 4: `docs/reports/2026-10-29-fleet-retro.md`; interview `.sdlc/runtime/tasks/fleet-retro-2026-10-29/agent-ui-interview.md`.
- Suspected cause [U]: `claim` runs the full `check` and treats any `depends:` miss in any ticket as fatal.
- Cost reported: 2 wasted solo runs (T-0563, T-0559), about 15 min [U].
- Filed by the user's choice although the row failed rubric gate G3 (unsourced cost).

## Constraints
- Red check: a `tickets.py selftest` case with an unrelated ticket whose `depends:` id lives only in another worktree; it fails before the fix and passes after.
- outcome metric: `tickets.py claim` refusals naming a ticket other than the claimed one, before: 2 in agent-ui (2026-10-29).

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0, including the `(T-0805)` case (claim over an unrelated ticket whose `depends:` id lives only in a lane worktree succeeds with a `warning:` line naming that ticket) and its control (the same miss in the claimed ticket still refuses, nothing written).
- `python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0 (lane open writes `branch:` through the same claim write).
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0.
