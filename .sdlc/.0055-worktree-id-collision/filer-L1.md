<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0055: Allocate ticket ids across git worktrees

## PR body
### Summary
Each worktree picked the next ticket id from its own `.sdlc/` only. So when two worktrees filed tickets in parallel, both could hand out the same id, and a merge then carried two tickets with that id (two T-0050s in the reported case). Now `tickets.py new` and `close` both pick an id above the highest one in the same-relative ticket root of every `git worktree list` tree. Outside git, or if git fails, only the local root counts, as before. For branches not checked out in any worktree, the fallback is the duplicate-id check that `tickets.py check` already runs. It fails and names both folders.

### Changes
- `plugins/sdlc-lite/scripts/tickets.py`
  - New `worktree_roots(root)`. It runs `git rev-parse --show-toplevel` and `git worktree list --porcelain` from the nearest existing ancestor of the root, with `GIT_DIR`, `GIT_WORK_TREE` and `GIT_INDEX_FILE` removed. It returns `[]` on any failure.
  - New `id_floor(root)`. It returns the highest id across the other trees and ignores malformed tickets there.
  - `stamp` takes `floor`. `cmd_new` passes it. `cmd_close` computes the floor once, then uses it for the numbered folder id and for every follow-up stamp.
  - Updated the module and `stamp` docstrings.
  - Selftest additions:
    - worktree cases for `new`, plain close and numbered close follow-ups
    - a worktree with no `.sdlc` dir
    - an explicit expect that a non-git root starts at T-0001
    - the duplicate-id expectation now requires both folders to be named (`beta: duplicate id T-0001, also used by alpha`)
- `CLAUDE.md`, `plugins/sdlc-lite/skills/ticket/SKILL.md`, `.claude/agents/sdlc-lite-author.md`: document the cross-worktree allocation and the duplicate-id check, and add the sync rule to the author agent.

### Verification
- Step 1, builder L3, verifier L2: **pass**
  - The new selftest cases were written first and failed on the unfixed code (`gamma='T-0002'`). After the fix, `tickets.py selftest` prints PASS.
  - Negative control 1: making `id_floor` return 0 turned all 6 worktree cases red.
  - Negative control 2: dropping `also used by` from the duplicate-id message turned the `duplicate id` case red.
  - The verifier ran both controls again independently in a throwaway worktree.
  - Manual scratch repro: the worktree's `new` stamped T-0003 after main had used T-0002.
  - A non-git root gets T-0001 with no stderr.
  - `check.sh` exits 0.
- Step 2, builder L1, verifier L1: **pass**
  - `grep` finds a line describing id allocation in each of the three docs. At HEAD, none of those files had one.
  - No em dashes added.
  - The verifier captured `check.sh` rc=0 directly, since the builder's rc came from `tail`.
  - `tickets.py --root .sdlc check` prints `ok: 60 tickets, roadmap current`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Fixed: `tickets.py new` and `close` no longer hand out a ticket id that another git worktree of the same repo already uses. Ids are allocated above the highest id across every `git worktree list` tree (local root only outside git), and `check` names both folders when two tickets share an id. (T-0055)

## Follow-ups
None
