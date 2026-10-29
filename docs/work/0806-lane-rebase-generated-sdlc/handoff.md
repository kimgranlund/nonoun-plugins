---
id: T-0806
title: "Lane rebases conflict on generated .sdlc files (notes, roadmap, router)"
type: bug             # feature | bug | chore | spike | idea
status: ready        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-29
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A lane rebase or land that conflicts only on generated `.sdlc` files (the notes file, the roadmap, the router block) resolves without a person: notes are unioned and the roadmap and router are regenerated.

## Repro
1. Close two tickets in two parallel lanes, each appending to the notes file and regenerating roadmap and router.
2. Land the first, then rebase the second onto main.

## Expected
The rebase completes, or a single `tickets.py` command resolves the generated files and continues.

## Actual
`/tmp/claude-501/qm-rebase-2371.log`: "CONFLICT (content): Merge conflict in .sdlc/AGENTS.md", ".sdlc/notes/notes.md", ".sdlc/tickets/roadmap.md". The agent-ui conductor resolved it by hand, about 20 min [U]; ui-kit reports the same class on its own generated files.

## Context
- Correction (agent-ui conductor, 2026-10-29): its queue script already resolves `.sdlc` notes and records; the 2371 drop was a real conflict in `.claude/docs/rubrics/a2ui-payload.md`. The agent-ui log is therefore not evidence of a plugin-caused drop. Remaining evidence: this repo resolves `.sdlc/AGENTS.md` and the roadmap by hand with `tickets.py roadmap` at lane merges, and a repo with no resolver hits the same conflicts. First reproduce with a two-lane selftest; close as not reproduced if lanes.py land already resolves these files.
- Fleet retro row 3: `docs/reports/2026-10-29-fleet-retro.md`; interview `.sdlc/runtime/tasks/fleet-retro-2026-10-29/agent-ui-interview.md`.
- This repo resolves the same conflicts by hand with `tickets.py roadmap` at every merge.
- Filed by the user's choice although the row failed rubric gate G3 (unsourced cost).

## Constraints
- Red check: a selftest that makes two lanes close tickets and rebases one onto the other; it ends in conflict before the fix and clean after.
- outcome metric: hand-resolved `.sdlc` conflicts per lane landing, before: 1 dropped queue PR in agent-ui (2026-10-29).
