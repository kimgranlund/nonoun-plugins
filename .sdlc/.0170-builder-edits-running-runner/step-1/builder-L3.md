<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/run.sh`: everything after `set -euo pipefail` now sits in one `{ ... }` group that ends in `exit 0`, so bash parses the whole body before running any of it. Added a "Self-edit:" header paragraph. The body is not re-indented, and all logic, traps, exit codes, the `exec run_lifecycle.py` hand-off and the dry-run path are unchanged.
- `plugins/sdlc-lite/scripts/run-selftest.sh`: new `self-edit` case plus a header paragraph. It copies `$here/..` into `$tmp/plugin-copy`, uses a stub `claude` that empties the copy's `scripts/run.sh` in place (`: >`) and then prints a `## Goal` result, and makes a real `planner L3` run through the copy. It asserts:
  - the truncation happened;
  - exit 0;
  - stdout is the result path;
  - the result file exists and holds the stub's text;
  - `runs.jsonl` has a line with `"file":"planner-L3.md"`;
  - the attempt status is `completed`.

  Every failure message starts with `self-edit:`.
- `docs/maintenance/sdlc-internals.md`: one sentence added to the `scripts/run.sh` entry, containing `edits run.sh while it runs`.

## Checks
- `grep -qF 'FAIL: self-edit' plugins/sdlc-lite/scripts/run-selftest.sh`: exit 0.
- `bash plugins/sdlc-lite/scripts/run-selftest.sh | grep -qx "run selftest: PASS"`: exit 0 (about 21s).
- Base negative control, run as split commands (see Notes): the new selftest run against the base runner at `$SDLC_BASE_SHA` exited 1 with `run selftest: FAIL: self-edit: stdout is '', want '.../erepo/planner-L3.md'`. The criterion's test evaluated true. Run twice (before and after the last comment edit), same result both times, and the worktree was removed after each run.
- `grep -qF 'edits run.sh while it runs' docs/maintenance/sdlc-internals.md`: exit 0.
- `git diff --check "$SDLC_BASE_SHA" -- <the three files>`: exit 0, no output.
- `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`: exit 0.
- `python3 plugins/sdlc-lite/scripts/check.py`: `ok: 18 role levels, 8 agents checked`.
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0, every selftest PASS. It printed `skip: shellcheck not installed`, so shellcheck did not run on the changed `run.sh`.
- `bash -n` on both scripts: ok.

## Notes
- The verifier cannot run the third acceptance criterion as one Bash call inside a role run. `hooks/block-stray-worktree.sh` blocks a `git worktree add` it cannot parse safely, and the one-liner's `w=...; git worktree add ... "$w"` chain is one of those. What works is running `git worktree add -q --detach "$SDLC_TMP_WORKTREES/base-s1" "$SDLC_BASE_SHA"` as its own command, then the cp, run and grep, then `git worktree remove --force`. That is how it was run here, with the same logic.
- On the base runner the failure matches the root cause: the child `run.sh` reaches EOF with status 0 and writes no result, so stdout is empty. The lifecycle would also mark that attempt `completed`.
- The `FAIL: self-edit` text the first criterion greps for comes from the header comment. The failure messages themselves say `self-edit:`, and the shared `fail()` adds the `run selftest: FAIL: ` prefix when printing.
- The role run that was executing this step used the main checkout's `run.sh` (pid 88209), not this worktree's copy, so editing this worktree's `run.sh` did not affect the live run.
