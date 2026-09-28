<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: pass. Evidence: run in the tree, printed `fanout selftest: PASS`, exit 0. It bites: in a temp copy of `scripts/` I changed `if p.returncode == 1:` to `if False:`. The selftest then printed `FAIL ... unignored .worktrees/: default-dir --dry-run exits 2 naming .gitignore and .worktrees/, got 2 stderr='fanout: git check-ignore .worktrees/x failed: 1'`. That failure is the stderr-content conjunct biting, since exit 2 alone would have passed.
- Default-dir dry run in a repo with a committed `.gitignore` of `.worktrees/` prints the integration and lane worktrees under `<repo>/.worktrees/fanout`: pass. Evidence: ran the criterion command verbatim, exit 0. At HEAD in a throwaway worktree the same command exits 1, so the check can go red.
- Repo that does not ignore `.worktrees/`: default-dir dry run exits 2, stderr names `.gitignore` and `.worktrees/`, no `.worktrees` created: pass. Evidence: verbatim command exit 0. stderr was `fanout: the default lanes dir .../.worktrees/fanout is inside the work tree ... but .worktrees/ is not gitignored; add .worktrees/ to .gitignore, or pass --lanes-dir outside the repo`. At HEAD the same command exits 1, so it can go red.
- (guard) Explicit `--lanes-dir` outside the repo works in an unignored repo and creates nothing on a dry run: pass. Evidence: verbatim command exit 0. It is green at HEAD too, as expected for a guard.
- `! grep -nE '\{rr\}-fanout' plugins/sdlc-lite/scripts/fanout.py`: pass. Evidence: exit 0. At HEAD it exits 1.
- `! grep -n '<toplevel>-fanout' plugins/sdlc-lite/scripts/fanout.py`: pass. Evidence: exit 0. At HEAD it exits 1.
- Observable: `selftest()` contains an `expect` for the default dir under `.worktrees/fanout` and an `expect` for the unignored refusal: pass. Evidence: fanout.py:635 expects `integration worktree: <rr>/.worktrees/fanout/integration` and `worktree <...>/alpha` in stdout. fanout.py:661 expects exit 2 with `.gitignore` and `.worktrees/` in stderr and no Traceback. Lines 665-667 check that no `.worktrees` dir, no `fanout/*` branch and no extra worktree exist. The selftest run above exercises them.
- Extra Do-list rules, checked by hand in a throwaway repo:
  - `--lanes-dir lanes/here` (inside, unignored) exits 2 and names `lanes/here/`.
  - `--lanes-dir .` exits 2, refused as the toplevel.
  - The diff shows `--lanes-dir` outside the toplevel skips the ignore check.
  - The docstring (fanout.py lines 18-25) and argparse help name the new default, the ignore rule and the refusal.

## Out of scope changes
None. `git diff --stat` shows only `plugins/sdlc-lite/scripts/fanout.py` from this step. `.sdlc/0090-fanout-lanes-in-worktrees-dir/handoff.md` shows a diff that fills the `## Intent` Do/Non-goals/Done-when lines. It is a task-handoff edit made before the build, and the builder says it did not touch it. The step's own artifacts and the planner file are untracked. Stale `<toplevel>-fanout` mentions in CLAUDE.md and the fanout skill belong to step 2.

## For the next attempt
None
