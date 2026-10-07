<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: pass. On the built tree it printed `fanout selftest: PASS` and exited 0. The check can go red. In a throwaway worktree with the reaper call stubbed out, it printed `fanout selftest: FAIL ... lane tmp prefix reaped: .../rplanes/alpha/.worktrees/tmp/builder-45490 gone and unlisted, got exists=True`. I did not run this gate at the pre-build HEAD because it was green on the built tree.
- `grep -qF reap-tmp-worktrees.sh plugins/sdlc-lite/scripts/fanout.py`: pass. The diff adds the call `subprocess.run(['bash', str(SCRIPTS / 'reap-tmp-worktrees.sh'), str(wt)], ...)` at fanout.py:544. It sits right after the driver `subprocess.run` and before `inherited_red`. The docstring step 2 and `docs/references/sdlc-internals.md` are updated.
- `grep -qF "lane tmp prefix reaped" plugins/sdlc-lite/scripts/fanout.py`: pass. Selftest case 10 in the diff has two `expect('lane tmp prefix reaped: ...')` calls. It uses `REAP_STUB` and a dead pid from a waited `true` child.
- The builder report quotes a `fanout selftest: FAIL` output naming `lane tmp prefix reaped`: pass. builder-L2.md quotes it. I reproduced the red myself with the same failure, as the first criterion's evidence shows.

Steelman: I drafted a fail on the builder's admitted `/tmp` backup file, which breaks the throwaway-files rule. The rebuttal holds. It is not an acceptance criterion, the backup was deleted, and `git status` shows no stray files. Dropped.

## Out of scope changes
None from this step. The uncommitted changes to `run.sh`, `run-selftest.sh`, and `reap-tmp-worktrees.sh` belong to step 1. The only step-2 files are `fanout.py` and `docs/references/sdlc-internals.md`, and the docs diff is limited to the fanout paragraph clause. It also carries step 1's `run.sh` paragraph text.

## For the next attempt
None
