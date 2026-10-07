<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `grep -qF 'integration dirty' plugins/sdlc-lite/scripts/fanout.py`: pass. Evidence: grep matched at fanout.py:65, :565, and in the selftest case at :1003-1009.
- `grep -qF 'integration dirty' docs/references/sdlc-internals.md`: pass. Evidence: grep exited 0 and printed `ok`. `git diff --stat` shows one line changed in that file.
- `grep -qF 'integration dirty' plugins/sdlc-lite/skills/fanout/SKILL.md`: pass. Evidence: grep exited 0 and printed `ok`. `git diff --stat` shows one line changed in that file.
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 and its source carries the new dirty-integration case: pass. Evidence:
  - On the built tree the selftest printed `fanout selftest: PASS` and exited 0 (`selftest_rc=0`).
  - The `integration dirty` string is in the `expect` lines at fanout.py:1003-1009.
  - Negative control: I copied the built fanout.py into a throwaway worktree at `$SDLC_BASE_SHA` and deleted only the guard lines. The selftest then printed FAIL with two misses: `got 'red: test -z "$(git status ...)" rc=1'` and `the edit survives ... got ''`. I removed the worktree afterwards.
  - The variable that bites is the guard's early return. The merge-commit assertion did not fail in that run, because the red gate resets the merge away either way. The outcome-row and edit-survives assertions are the ones that bite.
- (guard) `check.py` shows no new findings versus base: pass. Evidence: check.py at the built tree exits 0 with `ok: 18 role levels, 8 agents checked`. The same command in the `$SDLC_BASE_SHA` worktree also exits 0, and `diff` of the two outputs is empty (`same`).
- (guard) The diff touches only the three allowed files: pass. Evidence: the `bash -c 'test -z ...'` command exited 0 (`guard=0`). `git diff --stat` lists exactly the three files.

## Out of scope changes
None. The `integration status failed: ...` branch goes beyond the handoff's Do, but it sits inside the same guard in fanout.py. I read the diff: it is a short error return for the case where the status command itself fails. It cannot affect the dirty path, so I am not counting it as scope creep.

## For the next attempt
None
