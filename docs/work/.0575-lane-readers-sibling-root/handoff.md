---
id: T-0575
title: "Trace, fleet and migrate readers miss lanes under the sibling root"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: [T-0563]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---


## Goal
Every script that looks for lanes finds them under `wtroot.py root`, the sibling root included, and a migrated lane's ticket points at its new path.

## Intent
- Do:
  1. Make each of these readers take its lane paths from `wtroot.py` (`root()` plus the legacy roots) and stop naming the folders itself: `plugins/sdlc-lite/scripts/traces/ingest.py:189`, `traces/sources/git.py:57`, `fleet_doctor.py:136-145` and `fleet_collect.py:195`. The line numbers are from the T-0563 tree.
  2. When `migrate-worktrees.sh --apply` moves a lane whose ticket has a `worktree:` line, it rewrites that line (`tickets.py branch <id> <branch> --worktree <new path>`), so `tickets.py check` stays quiet.
- Non-goals: docs (T-0564).
- Done when: the criteria pass.

## Context
Found by the T-0563 solo (2026-10-15). T-0563 moved the default root to `<parent>/<repo>.worktrees`, and `lanes.py open` now writes `worktree: ../<repo>.worktrees/<leaf>`, relative to the main checkout. The four readers above still glob only `.worktrees/` and `.claude/worktrees/`.

## Constraints
Legacy roots stay readable for one release.

## Acceptance criteria
1. Each of the four scripts' selftests exits 0. Each gains a fixture with a lane under a sibling root that the script now finds; that fixture failed before the change.
2. `bash plugins/sdlc-lite/scripts/migrate-worktrees.sh --selftest` exits 0. Its new case shows that a moved lane's ticket `worktree:` line names the new path, and that `tickets.py check` prints no worktree warning for it.
3. `git diff --check` exits 0.

## Outcome

2026-10-15 · lane: full L2 · verdict: pass · verifier: verifier-L2 (sonnet) · base: f81c82776029
- Changed: trace, fleet and migrate readers find sibling-root lanes; migrate retargets ticket worktree lines
- Commits: ac37f05 T-0575: trace, fleet and migrate readers find lanes under the sibling root
- Check: 1 Each of the four scripts' selftests exits 0, each with a sibling-root fixture that failed before ...: pass
- Check: 2 `bash plugins/sdlc-lite/scripts/migrate-worktrees.sh --selftest` exits 0, and its new case shows ...: pass
- Check: 3 `git diff --check` exits 0: pass
- Follow-up: note: redck.py deviations printed no process deviation: lines; the... -> notes.md
- Follow-up: note: dependents of the changed contract still pass: fleet_detect... -> notes.md
