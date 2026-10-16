---
id: T-0606
title: "close --ticket follow-ups and docs miss the T-0588 claim and id refs"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
branch: lane/T-0606-t0606
worktree: ../sdlc-lite.worktrees/T-0606-t0606
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Every path that stamps a ticket id reserves `refs/sdlc/ids/<id>`, and the docs describe the claim and id refs.

## Context
From the T-0588 solo and verifier (2026-10-15).
- `tickets.py close --ticket N` stamps the follow-up ticket's id without reserving its ref, so a concurrent `new` can reuse it.
- The generated router block in `.sdlc/AGENTS.md` (in `tickets.py`) still says `--by` takes one lowercase word; T-0588 made `--by` win over `SDLC_HOST` and host detection (`claude:<session8>`, `codex:<thread>`).
- `docs/references/sdlc-internals.md` around line 55 describes `claim` without the refs.

## Intent
- Do: reserve the id ref in the follow-up path, reusing T-0588's helper; update the router text and the internals entry.
- Non-goals: changing claim precedence.
- Done when: the criteria pass.

## Constraints
Outside git, nothing changes.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0. Its new case runs a `close --ticket N` follow-up and a concurrent `new`, which get distinct ids. The case failed before the fix.
2. `grep -n 'refs/sdlc' docs/references/sdlc-internals.md` prints at least one line.
3. `git diff --check` exits 0.
