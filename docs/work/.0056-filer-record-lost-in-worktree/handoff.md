---
id: T-0056
title: "filer-L1.md stays uncommitted in a lane worktree, so close on main finds no filer file"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
close on main finds the filer record of work done in a lane worktree.

## Repro
1. In a repo with a second git worktree (a lane), both holding `.sdlc/<slug>/handoff.md` for the same ticket.
2. In the lane worktree, write `.sdlc/<slug>/filer-L1.md` (as /file does) and leave it uncommitted.
3. In the main worktree, run `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc close <slug>`.

## Expected
close refuses (writes nothing, exit 1), but its message names every other worktree whose same-relative ticket root holds `<slug>/filer-L*.md` (full path of the folder), so the user knows where the record is and can commit or copy it, then rerun close.

## Actual
`<slug>: no filer-L*.md in <main>/.sdlc/<slug>; run /file on the task first; nothing written`, with no hint that the record exists in the lane worktree.

## Decision (conductor, unattended)
Of the two suggested fixes, take "close names the worktree holding it". "/file commits its record" is a publish-class action (commit) that needs user approval, so it is out of scope here. close must never read or use a filer file from another worktree (no silent cross-tree reads): it only names them in the refusal. Reuse `worktree_roots` in `scripts/tickets.py`. Look only for the same folder name close resolved locally (`<other root>/<slug>/`), not other folder forms. Outside git, or with no other worktree holding one, the message is unchanged.

## Acceptance criteria
- A new selftest case in the worktree section of `tickets.py selftest` (git-backed, like the existing worktree id cases) fails on the current code and passes after the fix: a filer file only in the other worktree makes close in main refuse with rc 1, write nothing, and name the other worktree's folder path in stderr.
- The existing (e) case (no filer anywhere) still passes, and its message still names /file.
- The `close` usage/docstring text in `tickets.py` and the tickets.py line in the root `CLAUDE.md` mention the new hint; `skills/file/SKILL.md` step 3.1 says what to do on that refusal (commit or copy the record from the named worktree, then rerun).
- `plugins/sdlc-lite/scripts/check.sh` passes.

## Context
From peer session setup-sdlc-lite-generative-ui (gen-ui-system-svelte-lite), on 0.6.0, 2026-09-24.

/chain commits only on a step pass and the filer runs after the last step, so filer-L1.md stays uncommitted in the lane worktree, the merge to main misses it, and close on main says "no filer-L*.md". Suggested: /file commits its record, or close names the worktree holding it.

## Constraints
The failing test lands before or with the fix, never after.
