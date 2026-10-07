<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- `grep -qF 'FAIL: self-edit' plugins/sdlc-lite/scripts/run-selftest.sh`: pass. Evidence: exit 0. The match is in the new header comment. The case's `fail "self-edit: ..."` calls print with the shared `run selftest: FAIL: ` prefix.
- `bash plugins/sdlc-lite/scripts/run-selftest.sh | grep -qx "run selftest: PASS"`: pass. Evidence: exit 0 on the built tree.
- The new case fails on the base runner: pass. Evidence: ran the criterion's steps in a throwaway worktree at `$SDLC_BASE_SHA`.
  - The `git worktree add` had to be its own command, as the builder noted. The remaining steps ran as written.
  - Base `run.sh` with the new selftest gave rc=1 and `run selftest: FAIL: self-edit: stdout is '', want '.../erepo/planner-L3.md'`. The criterion's final test then exited 0.
  - The base tree's only diff was the copied selftest, and the worktree was removed afterwards.
  - Green on the built tree (criterion 2) and red on base together show the case can go red, and that the `{ ... }` wrap is the variable that fixes it.
- `grep -qF 'edits run.sh while it runs' docs/references/sdlc-internals.md`: pass. Evidence: exit 0. The sentence sits in the `scripts/run.sh` entry and says the whole body is parsed first, the process keeps its behavior, and it still saves its result.
- `git diff --check "$SDLC_BASE_SHA" -- <the three files>`: pass. Evidence: exit 0 with no output.
- Wiring and assertions in the diff:
  - `run.sh` wraps everything after `set -euo pipefail` in `{ ... }` ending `exit 0` and a closing brace, plus a "Self-edit:" header paragraph.
  - The selftest case copies `$here/..` to `$tmp/plugin-copy` and never touches the real `run.sh`. The stub truncates the copy's `run.sh` in place with `: >`.
  - It runs a real `planner L3` through the copy and asserts exit 0, stdout path, result-file text, the `runs.jsonl` line, and attempt status `completed`. Every failure message is prefixed `self-edit:`.
  - The selftest also asserts the truncation happened, so the stub cannot pass vacuously.
- Builder claim that neighbors are unbroken: accepted on my own run. `bash -n run.sh` is ok. `bash plugins/sdlc-lite/scripts/check.sh` exited 0 with every selftest PASS, including `run selftest`, `hook selftest` and `fanout selftest`. It printed `skip: shellcheck not installed`, so shellcheck did not run on `run.sh`.

## Out of scope changes
None. The tracked diff is exactly the three named files (`git status --short`). The untracked `.sdlc/0170-*` entries are the task's own artifacts. I dismissed the one-line trailing `exit 0` in `run.sh` as in scope because it is the explicit final exit the Do calls for. The original tail was `echo "$result"`, which also exits 0.

## For the next attempt
None
