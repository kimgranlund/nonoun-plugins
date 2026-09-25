## Task goal
Running ticket lanes in parallel needs no hand-written driver.

## Step 1: `board.py --lanes`, a per-worktree view from `git worktree list`
level: L3
### Do
In `plugins/sdlc-lite/scripts/board.py`:
- Add `--lanes` to `main()`'s argparse. With it, `main()` renders a lanes table instead of the task board and returns; it never calls `render()` and never touches the state file. `--waiting` still prints its line above the table; `--summary`, `--task`, and `--sort` are ignored under `--lanes`. Nothing else in `main()` or `render()` changes: the default board output must stay byte-identical.
- Add `lanes(root)`: find the repo of `root` the way `tickets.worktree_roots` does (`git -C <root or nearest existing parent> rev-parse --show-toplevel`, with `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE` dropped from the env), compute `rel = root.resolve() relative to the toplevel`, then read `git worktree list --porcelain` and build one row per `worktree <path>` entry, in list order: Lane = the worktree path's basename, Branch = the `branch refs/heads/<name>` short name or `(detached <7-char sha>)`, Board = `summary(<worktree>/<rel>)` or `no tasks` when that dir has no task, resolving both paths with `.resolve()` (macOS `/var` vs `/private/var`). Outside a git work tree (any git failure), print `<root>: not inside a git work tree` on stderr and exit 1.
- Render as `| Lane | Branch | Board |` then `|---|---|---|` then one row per worktree.
- Add a selftest case: a temp git repo (set `user.name`, `user.email`, `commit.gpgsign false` locally) with a committed `.sdlc/t/handoff.md`, plus two worktrees added with `git worktree add -b alpha <tmp>/lanes/alpha` and `-b beta`; run `board.py --lanes --root <repo>/.sdlc` as a subprocess and assert: exit 0, the header line, exactly three data rows (main, alpha, beta) whose Branch cells are the branch names; touch `<lanes>/alpha/.sdlc/t/planner-L1.running` and assert alpha's Board cell says `t planning` while beta's says `t not planned` (proves each row reads its own worktree's root); a `--root` in a plain temp dir exits 1 with `git` in stderr. Keep case 1 (byte-for-byte 4-column render) as is.
- Update the module docstring (Usage line and a `--lanes` paragraph).

Docs in the same step: `plugins/sdlc-lite/skills/board/SKILL.md` (argument-hint gains `[--lanes]`; step 2 says to pass `--lanes` for a "lanes" or "worktrees" ask; a rule that `--lanes` lists every `git worktree list` entry with its branch and that worktree's `--summary` line and leaves the default board unchanged) and the `scripts/board.py` bullet in the root `CLAUDE.md` (one sentence describing `--lanes`, the exit 1 outside git, and that the default board is unchanged).
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/board.py --lanes --root .sdlc | grep -q '^| Lane | Branch | Board |$'`
- `test "$(python3 plugins/sdlc-lite/scripts/board.py --lanes --root .sdlc | grep -c '^| ')" -eq "$(( $(git worktree list | wc -l) + 1 ))"` (one data row per worktree plus the header)
- `python3 plugins/sdlc-lite/scripts/board.py --lanes --root .sdlc | grep -q "| $(git branch --show-current) |"`
- `d=$(mktemp -d) && out=$(python3 plugins/sdlc-lite/scripts/board.py --lanes --root "$d" 2>&1 >/dev/null; echo "rc=$?") && grep -q 'rc=1' <<<"$out" && grep -qi 'git' <<<"$out"`
- `grep -q -- '--lanes' plugins/sdlc-lite/skills/board/SKILL.md && grep -q -- '--lanes' CLAUDE.md`
- Reading `selftest()` in `board.py` shows the `--lanes` case: two added worktrees, three data rows with branch names, a `planner-L1.running` in one lane changing only that lane's Board cell, and the outside-git exit 1.
- (guard) `python3 plugins/sdlc-lite/scripts/board.py selftest` prints `board selftest: PASS` and exits 0.
- (guard) `t=$(mktemp -d) && for f in board tickets order; do git show HEAD:plugins/sdlc-lite/scripts/$f.py > "$t/$f.py"; done && diff <(SDLC_BOARD_STATE_DIR=$(mktemp -d) python3 "$t/board.py" --root .sdlc) <(SDLC_BOARD_STATE_DIR=$(mktemp -d) python3 plugins/sdlc-lite/scripts/board.py --root .sdlc)` (the default board is unchanged versus the base commit)
- (guard) `bash plugins/sdlc-lite/scripts/check.sh` exits 0.
