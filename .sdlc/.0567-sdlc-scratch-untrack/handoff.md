---
id: T-0567
title: "Tracked scratch under .sdlc moves to reports or runtime"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P3         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`.sdlc/` in this repo tracks only durable records: tickets, plans, notes, config and the generated router and roadmap; past scratch folders are gone from it.

## Intent
- Do:
  1. Move each `fleet-retro-*` folder's report-worthy content to `docs/reports/` when no report there already holds it, and `git rm` the rest; `git rm -r` `verify-*`, `merge-tickets-*`, `.codex-scout-luna` and other one-off scratch that no ticket or report links to (check with `grep -rn '<name>' docs .sdlc/*.md plugins`).
  2. Run `tickets.py --root .sdlc tidy --apply` for loose entries.
  3. Make the fleet-retro skill and verify recipes write scratch under `.sdlc/runtime/` from now on, if they still write it to `.sdlc/` top level.
- Non-goals: archiving closed `.NNNN-*` ticket folders.
- Done when: the criteria pass.

## Context
`git ls-files .sdlc` on 2026-10-15 lists 11 `fleet-retro-*` folders (17 to 22 files each), `verify-subagent` (49 files) and other one-off folders; `.sdlc/runtime/` and `.sdlc/messages/` are already ignored.

## Constraints
Do not remove anything a tracked file links to; move it instead.

## Acceptance criteria
1. `git ls-files .sdlc | grep -E '^\.sdlc/(fleet-retro-|verify-|merge-tickets-)'` prints nothing.
2. `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc tidy` lists nothing to move.
3. `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exits 0 and `git diff --check` exits 0.

## Outcome

2026-10-15 · lane: full L1 · verdict: pass · verifier: verifier-L2 (opus) · base: d438b220edd8
- Changed: untracked 82 one-off .sdlc scratch folders; 6 cited verifier files moved to docs/reports
- Commits: 64409c6 T-0567: untrack one-off scratch under .sdlc, move cited verifier files to docs/reports
- Check: 1 `git ls-files .sdlc | grep -E '^\.sdlc/(fleet-retro-|verify-|merge-tickets-)'` prints nothing: pass
- Check: 2 `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc tidy` lists nothing to move: pass
- Check: 3 `tickets.py --root .sdlc check` exits 0 and `git diff --check` exits 0: pass
- Follow-up: fix-now: docs/reports/2026-10-08-fleet-retro-06.md:38... -> notes.md
- Follow-up: decide: docs/reports/release-0.20.6.md:19 and about 60 more report lines... -> notes.md
- Follow-up: note: .sdlc/notes.md:186 and .sdlc/notes.md:233 mention... -> notes.md
