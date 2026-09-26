---
id: T-0107
title: "Role throwaway worktrees created outside $SDLC_TMP_WORKTREES for..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0095
---

## Goal
Inside a role run, a throwaway git worktree created outside `$SDLC_TMP_WORKTREES` (for example under `/tmp`) or created with a new branch (`git worktree add -b`/`-B`) can no longer leave a worktree or branch behind unnoticed: it is blocked before it is created, or detected and reported when the run ends.

Done when: an automated selftest (wired into `scripts/check.sh`) proves that, with `SDLC_ROLE` set, `git worktree add /tmp/x HEAD` and `git worktree add -b tmpbr <path under $SDLC_TMP_WORKTREES> HEAD` are caught (denied or reported), that `git worktree add --detach "$SDLC_TMP_WORKTREES/x" HEAD` still passes, and that nothing changes when `SDLC_ROLE` is unset.

## Context
Follow-up from T-0095 (role-worktrees-left-behind/filer-L1.md):

Role throwaway worktrees created outside `$SDLC_TMP_WORKTREES` (for example in `/tmp`) or with `-b` are never cleaned, and `-b` leaves its branch behind; add a guard or a check that detects them.

## Constraints
- Interactive sessions (no `SDLC_ROLE`) are unaffected.
- `scripts/fanout.py` creates lane worktrees with branches from its own process (not through a role's Bash tool); it must keep working.
- Never remove or delete worktrees or branches a role did not create in this run (concurrent lanes share one `git worktree list`).
- The existing T-0095 cleanup in `run.sh` (EXIT trap over the `$SDLC_TMP_WORKTREES` prefix) stays.
- Records that describe the hooks or run.sh (`CLAUDE.md`, `.claude/agents/sdlc-lite-author.md`, `hooks/hooks.json` if a hook is added) are updated in the same change; `scripts/check.sh` stays green.

## Clarify (unattended)
- Guard vs. check is left to the planner; a PreToolUse(Bash) hook in the style of `hooks/block-pattern-kill.sh` is the likely fit because it prevents the leak rather than reporting it.
