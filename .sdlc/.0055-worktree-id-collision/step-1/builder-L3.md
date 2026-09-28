<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`: added `worktree_roots(root)`, `id_floor(root)` and `GIT_ENV_DROP`. `stamp` takes `floor=0` and stamps `max(nums + [floor]) + 1`. `cmd_new` passes `floor=id_floor(root)`. `cmd_close` computes the floor once before planning follow-ups and uses it in the numbered `tid` line and in every `stamp` call. Added `import subprocess`, a module docstring paragraph and an updated `stamp` docstring. Selftest additions: the worktree cases, the explicit non-git T-0001 expect, and the tightened `duplicate id` string.

## Checks
- 🟢 Selftest first, on the unfixed code: `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exited 1 with 6 worktree misses, including `gamma='T-0002'`.
- 🟢 After the fix: `python3 plugins/sdlc-lite/scripts/tickets.py selftest` printed `tickets selftest: PASS` and exited 0.
- 🟢 Negative control 1: `id_floor` patched to `return 0`. The selftest exited 1, and all 6 worktree cases were listed as misses. File restored from backup; selftest PASS again.
- 🟢 Negative control 2: dropped `, also used by {ids[i]}` from the duplicate-id message in `problems()`. The selftest exited 1 on `duplicate id: check did not fail with 'beta: duplicate id T-0001, also used by alpha'`. File restored; selftest PASS.
- 🟢 Manual repro in a `mktemp -d` scratch dir: `git init`, `new feature a`, commit, `git worktree add ../wt2 -b x`, `new bug b` in main, then `(cd ../wt2 && tickets.py --root .sdlc new bug c)`. `../wt2/.sdlc/c/handoff.md` has `id: T-0003`.
- 🟢 Non-git temp dir: `tickets.py --root <tmp>/.sdlc new feature x` returned 0 with `id: T-0001` and 0 bytes of stderr. `git rev-parse` there confirmed "not a git repository".
- 🟢 `grep -n "worktree" plugins/sdlc-lite/scripts/tickets.py`: lines 50-54 are the docstring paragraph describing the allocation.
- 🟢 `git diff --stat`: of the tracked files, only `tickets.py` changed from this step. The em dash count in `tickets.py` is 0.
- 🟢 `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`: `ok: 60 tickets, roadmap current`, rc 0.
- 🟢 `plugins/sdlc-lite/scripts/check.sh`: rc 0. The tickets, order and run selftests passed, plus shellcheck and plugin validate.

## Notes
- `.sdlc/0055-worktree-id-collision/handoff.md` was already modified before this step (planner output). I did not touch it.
- The selftest's git fixture commit adds `--no-verify`, and its git calls strip `GIT_DIR`, `GIT_WORK_TREE` and `GIT_INDEX_FILE`. This keeps user hooks and an outer git context out of the fixture. The commit otherwise matches the `-c user.name=t -c user.email=t@t -c commit.gpgsign=false commit -qam` form.
- One extra selftest case goes beyond the handoff's list: a `new` run inside the worktree whose `.sdlc` was removed gets T-0008. It exercises the "nearest existing ancestor" path in `worktree_roots`.
- In the worktree cases, the numbered close runs on `alpha` in `wt`. `alpha` is a plain-slug folder, so only its follow-up folder is numbered (`0007-quote-the-docs`, id T-0007).
- The docstring states that branches not checked out in any worktree are not seen, and that `check` catches a clash after merge. Step 2 repeats this in the docs.
