<!-- role=planner level=L2 model=opus effort=medium -->
Reviewed tickets.py, the ticket docs, and check.sh; writing the plan now.

## Goal
Make `tickets.py new` and `close` pick ids above the highest id in every `git worktree list` tree's matching `.sdlc` root, and prove with selftests that this works and that `check` fails on a duplicate id.

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

## Step 2: Sync docs with cross-worktree id allocation
level: L1
### Do
- In `CLAUDE.md` (repo root), `scripts/tickets.py` bullet: after "stamps a ticket with the next id", state that `new` and `close` follow-ups take the next id above the max across the same-relative ticket root in every `git worktree list` tree (local root only outside git). Also state that `check` fails on two tickets sharing an id and names both folders. Branches not checked out in any worktree are caught by that `check` after merge.
- `plugins/sdlc-lite/skills/ticket/SKILL.md`: add one Rules bullet with the same behavior.
- `.claude/agents/sdlc-lite-author.md`: add to the sync line (line 16) that cross-worktree id allocation stays in sync across tickets.py, the /ticket skill, and CLAUDE.md.
- No em dashes.
### Acceptance criteria
- `grep -n "worktree" CLAUDE.md plugins/sdlc-lite/skills/ticket/SKILL.md .claude/agents/sdlc-lite-author.md` shows a hit in each of the three files describing id allocation.
- `grep -c "—" CLAUDE.md plugins/sdlc-lite/skills/ticket/SKILL.md .claude/agents/sdlc-lite-author.md` reports no more em dashes than before the step (`git diff` adds none).
- `plugins/sdlc-lite/scripts/check.sh` exits 0. The only warning allowed is the expected CLAUDE.md validate warning.
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` still exits 0 in this repo.

## Risks
- `worktree_roots` uses real paths. On macOS, `/var` resolves to `/private/var`, so comparing unresolved paths can miscount the current tree as a foreign one or break `relative_to`. Both sides need `resolve()`.
- The user's git config, such as `commit.gpgsign` or hooks, could make the selftest's git setup hang or fail. The `-c` overrides cover the known cases, and `GIT_CONFIG_GLOBAL=/dev/null` is an option if needed.
- Every `new` and `close` now makes two git subprocess calls. This is cheap but new, and git's absence must stay a silent fallback.
- Branches that are not checked out in any worktree, and clones on other machines, cannot be seen at allocation time. After a merge, only the `check` duplicate-id gate catches those.
