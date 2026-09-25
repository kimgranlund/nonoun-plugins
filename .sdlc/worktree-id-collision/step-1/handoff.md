## Task goal
No two tickets ever get the same id when worktrees file tickets in parallel.

## Step 1: Allocate ids across worktrees, with selftests that fail before the fix
level: L3
### Do
All edits go in `plugins/sdlc-lite/scripts/tickets.py`.
- Add `worktree_roots(root)`:
  - Resolve `root`. Take its nearest existing ancestor and run `git -C <ancestor> rev-parse --show-toplevel` and `git -C <ancestor> worktree list --porcelain` through `subprocess.run`.
  - Pass an env with `GIT_DIR`, `GIT_WORK_TREE` and `GIT_INDEX_FILE` removed, so an outer git context cannot redirect the lookup.
  - Compute `rel = root.resolve().relative_to(toplevel.resolve())`.
  - Return `<worktree>/rel` for every `worktree <path>` line whose resolved path is not the current root and is an existing dir.
  - Return `[]` on any failure: git missing (`FileNotFoundError`/`OSError`), a non-zero exit, or a root outside the toplevel (`ValueError`).
- Add `id_floor(root)`: the max numeric part of every id matching `ID_RE` in `load(r)` over `worktree_roots(root)`, default 0. Ignore malformed tickets in other trees; never fail on them.
- `stamp(...)` gains `floor=0`. The id becomes `max(nums + [floor]) + 1`.
- `cmd_new` passes `floor=id_floor(root)`.
- `cmd_close` computes `floor = id_floor(root)` once, before planning follow-ups. It uses the floor in the numbered-mode `tid` line (`max(... for _, x in after), floor) + 1`) and passes it to every `stamp` call. Follow-ups after the first still count up from `after`.
- Update the module docstring: `new` and `close` stamp ids above the max across the same-relative `.sdlc` root in every git worktree, falling back to the local root outside git. Also update the `stamp` docstring.
- Selftest additions, inside `selftest()`:
  - (a) Worktree case:
    - Set up the repo:
      - In a temp dir, `git init -q main`, then `run(main/.sdlc, 'new', ('feature','alpha'))` to get T-0001.
      - Commit with `git -c user.name=t -c user.email=t@t -c commit.gpgsign=false commit -qam`, after `git add -A`.
      - `git worktree add -q ../wt -b wt`.
    - Then `new` beta in main (T-0002) and `new` gamma in wt. Expect gamma to be T-0003, not T-0002.
    - Close with a follow-up: put a `filer-L1.md` with one Follow-ups bullet and no open Warnings into a wt ticket, and add one more ticket in main first so main's max is above wt's. Expect the follow-up id to be above main's max. Run this in plain mode and, with `--numbered`, check that the folder prefix matches that id.
    - A worktree with no `.sdlc` dir yet is skipped without error.
    - If `shutil.which('git')` is None, print a skip note instead of failing.
  - (b) Fallback: a root under a plain temp dir (not in git) still gets T-0001 as its first id (the existing base fixture already covers this; add one explicit expect).
  - (c) Tighten the existing `duplicate id` mutation's expected string to `beta: duplicate id T-0001, also used by alpha`, so the test proves both folders are named.
- Write the selftest first and confirm it fails on the unfixed code (the gamma id comes out T-0002), then implement.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` prints `tickets selftest: PASS` and exits 0.
- Negative control: temporarily make `id_floor` return 0. `tickets.py selftest` then exits 1 and lists the worktree-id cases among the misses. Restore it afterward (`git diff` shows only the intended change).
- Negative control: temporarily change the duplicate-id message in `problems()` to drop `also used by {ids[i]}`. The selftest then fails on `duplicate id`. Restore it afterward.
- Manual repro in a scratch dir (not this repo):
  - Setup: `git init`, run `tickets.py --root .sdlc new feature a`, commit, `git worktree add ../wt2 -b x`, then `tickets.py --root .sdlc new bug b` in main.
  - Check: `(cd ../wt2 && tickets.py --root .sdlc new bug c)` stamps `id: T-0003` in `../wt2/.sdlc/c/handoff.md`.
- `tickets.py --root <non-git temp dir>/.sdlc new feature x` succeeds with `id: T-0001` and no stderr.
- `grep -n "worktree" plugins/sdlc-lite/scripts/tickets.py` shows the docstring text describing the new allocation.
