<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0170: Keep a role's result when it edits the running run.sh

## PR body
### Summary
A builder that edited `plugins/sdlc-lite/scripts/run.sh` during its own run lost its result. Bash reads a script from disk as it runs. When the file got shorter, the child `run.sh` hit EOF, exited 0, and wrote no `<role>-<level>.md` and no `runs.jsonl` line. The attempt was recorded as `completed`. This was seen on T-0163 step 1.

Two changes fix it:
- `run.sh` now parses its whole body before running any of it, so a later edit of the file cannot change the running process.
- `run_lifecycle.py` now treats an exit 0 with no result file as a failed run (exit 1). This backs up the stated exit-code contract ("1 run failed or returned no result").

The ticket's hook option (refusing role writes to `run.sh`) was not chosen.

### Changes
- `plugins/sdlc-lite/scripts/run.sh`:
  - Everything after `set -euo pipefail` is now one `{ ... }` group ending in `exit 0`.
  - Added a "Self-edit:" header paragraph.
  - Updated the `Exit codes` header line.
  - The body is not re-indented. Logic, traps, exit codes, the `exec run_lifecycle.py` hand-off, and the dry-run path are unchanged.
- `plugins/sdlc-lite/scripts/run_lifecycle.py`: in `run()`, a child that was not interrupted, exited 0, and left no `<name>.md` prints a `wrote no result` stderr line and sets rc to 1. The attempt record becomes `failed` with `exit_code` 1.
- `plugins/sdlc-lite/scripts/run-selftest.sh`: new `self-edit` case.
  - It copies the plugin into a temp dir and never touches the real `run.sh`.
  - A stub `claude` truncates the copy's `run.sh` in place, then prints a `## Goal` result.
  - It runs a real `planner L3` through the copy.
  - It asserts that the truncation happened, exit 0, the stdout result path, the result file text, the `runs.jsonl` line, and attempt status `completed`.
- `plugins/sdlc-lite/scripts/lifecycle-selftest.py`: new `test_exit_zero_without_result_fails`. It runs `run_lifecycle.run` with a runner that is just `exit 0`. It asserts rc 1, status `failed`, `exit_code` 1, and the stderr line.
- `docs/maintenance/sdlc-internals.md`: two sentences in the `scripts/run.sh` entry. One covers `edits run.sh while it runs` and one covers `exits 0 without a result`.

### How each was verified
Each step was checked by an independent verifier. All three passed.
- Step 1, wrap and selftest:
  - The full `run-selftest.sh` printed `run selftest: PASS`.
  - Negative control: the new selftest against the base runner at the base SHA exited 1 with `FAIL: self-edit: stdout is '', want '.../planner-L3.md'`.
  - `git diff --check` was clean on the three files.
- Step 2, lifecycle guard:
  - `lifecycle-selftest.py` ran 6 tests and passed.
  - Negative control: the new test against the base lifecycle failed with `AssertionError: 0 != 1`.
  - `run-selftest.sh` still printed PASS.
- Step 3, gates:
  - `check.sh` exited 0 with every selftest passing.
  - `scripts/check-packaging.py` printed PASS.
  - `codex_roles.py generate --check` printed "Codex agent definitions verified".
  - `git diff --check` was clean.
  - The verifier removed the `{ ... }` wrap in a throwaway worktree and `run-selftest.sh` failed with `self-edit: run.sh exited 1, want 0`, so the gate covers the new behavior.

Limitations:
- shellcheck is not installed, so it did not run on the changed `run.sh`.
- The compound worktree-based negative-control commands in the criteria are refused by `hooks/block-stray-worktree.sh` inside role runs. The builders and verifiers ran the same steps as separate commands.
- No live host run of a role editing its own runner was done. Coverage is the stub-based selftest.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Fixed: a role that edits `scripts/run.sh` during its own run now still saves its result file and `runs.jsonl` line. A run that exits 0 without a result file is now recorded as failed with exit 1.

## Follow-ups
- note: the fix protects only a `run.sh` child that has already started. A role that corrupts `run.sh` still breaks later runs, and the hook option to refuse role writes to `run.sh` and `run_lifecycle.py` was not built.
- note: the criteria's one-line worktree negative controls are blocked by `block-stray-worktree.sh` in role runs, so verifiers must split them into separate commands.
- note: shellcheck was not installed, so the changed `run.sh` was never shellchecked.
