<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/fanout.py`: The default lanes dir is now `top / '.worktrees' / 'fanout'`. The old "inside the work tree" refusal is replaced by three rules, all checked in preflight, which runs before any write, so `--dry-run` refuses too:
  - `lanes_dir == top` is refused.
  - Using the default dir runs `git check-ignore -q .worktrees/x` from top and refuses (exit 2) when that path is not ignored, naming `.worktrees/` and `.gitignore`.
  - An explicit `--lanes-dir` inside top gets the same check on `<rel>/x`, and the refusal names `<rel>/`. An explicit dir outside top is not checked.
- Same file: the module docstring and the `--lanes-dir` help now name the new default, the ignore rule, and the refusal.
- Same file, selftest:
  - `make_repo` takes an optional `extra` dict of files.
  - The `rr` fixture commits a `.gitignore` containing `.worktrees/`.
  - The default-dir dry run now expects `rr/.worktrees/fanout/integration` and `rr/.worktrees/fanout/alpha`.
  - The "no lanes dir" expect checks `rr/.worktrees/fanout`.
  - New case 3: a repo with no `.gitignore`. Its default-dir dry run must exit 2 with `.gitignore` and `.worktrees/` on stderr and no Traceback, and must create no `.worktrees`, no `fanout/*` branch, and no extra worktree.

## Checks
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: PASS (exit 0).
- Criterion 2 (default-dir dry run in a repo that ignores `.worktrees/` prints paths under `<repo>/.worktrees/fanout`): exit 0.
- Criterion 3 (repo that does not ignore `.worktrees/`: exit 2, stderr names `.gitignore` and `.worktrees/`, no `.worktrees` created): exit 0.
- Criterion 4 (guard: explicit `--lanes-dir` outside the repo, dry run, creates nothing): exit 0.
- `! grep -nE '\{rr\}-fanout' plugins/sdlc-lite/scripts/fanout.py`: exit 0.
- `! grep -n '<toplevel>-fanout' plugins/sdlc-lite/scripts/fanout.py`: exit 0.
- Negative controls, each on a temp copy that I then deleted:
  - Turning off the ignore refusal made the selftest FAIL on the new unignored-repo expect.
  - Restoring the sibling `-fanout` default made it FAIL on the default-dir expect and the unignored expect.
- Manual check of the explicit `--lanes-dir` rules:
  - `lanes/here` in a repo that does not ignore it: exit 2, and the message names `lanes/here/`.
  - `--lanes-dir .`: exit 2, refused as the toplevel.
  - `lanes/here` after adding `lanes/` to `.gitignore`: exit 0.
- Observable criterion: `selftest()` has an expect for the default dir under `.worktrees/fanout` and an expect for the exit-2 refusal whose stderr names `.gitignore`.

## Notes
- Two cases give their own messages. When `git check-ignore` returns something other than 0 or 1, preflight refuses with a separate "git check-ignore … failed" message. An explicit `--lanes-dir` that equals the default path is checked on `.worktrees/fanout/x`, which a `.worktrees/` entry covers.
- I did not run `scripts/check.sh` because no criterion names it. CLAUDE.md and the fanout skill still describe the sibling `<toplevel>-fanout` dir; step 2 repairs those docs.
- `.sdlc/0090-fanout-lanes-in-worktrees-dir/handoff.md` was already modified before this build and I did not touch it.
