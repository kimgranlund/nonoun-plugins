<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
A role that edits `plugins/sdlc-lite/scripts/run.sh` during its own run still gets its result file and `runs.jsonl` line saved. An exit 0 that leaves no result file is reported as a failed run. Regression tests that fail on the base code pass after the fix.

## Step 1: Make run.sh immune to edits of its own file, with a failing-first selftest case
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Root cause: bash reads a script file as it executes it. `run_lifecycle.py` starts a child `bash run.sh` (with `SDLC_LIFECYCLE_CHILD=1`), and that child is still reading `run.sh` from disk while the role runs. If a builder writes `run.sh` in place (same inode), the child resumes at its old byte offset in the new content. If the file got shorter, it hits EOF, runs the EXIT trap with status 0, and writes no result. `run_lifecycle.py` is Python and is compiled whole at start, so this bug is only in `run.sh`.

1. In `plugins/sdlc-lite/scripts/run.sh`, make bash parse the whole executable body before running any of it. Recommended approach: wrap everything after `set -euo pipefail` in one `{ ... }` group whose last command inside the braces is an explicit `exit` (the final exit status), so bash never reads the file again after starting the group. Bash must parse a compound command completely before it executes it. Keep `$0`-based `plugin_root`, all traps, the `exec python3 run_lifecycle.py` hand-off, the dry-run path, and every exit code unchanged. Another approach is fine if it gives the same guarantee, for example copying itself to a temp file and exec-ing the copy while still resolving `plugin_root` from the original path. Add a short header paragraph ("Self-edit: ...") explaining the guarantee.
2. In `plugins/sdlc-lite/scripts/run-selftest.sh`, add a "self-edit" case (and a line in the header comment). Copy the whole plugin directory (`$here/..`) into `$tmp`. Never touch the real `run.sh`: the repository forbids editing runtime scripts while a role uses them. Use a stub `claude` on PATH that truncates the copy's `scripts/run.sh` in place (same inode, e.g. `: >"$copy/scripts/run.sh"`) and then prints a normal `## Goal` result event. Run the copy's `scripts/run.sh planner L3 <handoff>` (a real run, not dry, so it goes through `run_lifecycle.py` and the child). Assert all of these, and prefix every failure message with `self-edit:` so the output reads `run selftest: FAIL: self-edit: ...`:
   - exit 0;
   - stdout names the result path;
   - the result file exists and holds the stub's text;
   - `runs.jsonl` has a line whose `file` is that result name;
   - the `.attempt.json` status is `completed`.

   Do not add a variant that inserts bytes before the current offset: on the base code it can re-run earlier lines and loop.
3. In `docs/maintenance/sdlc-internals.md`, add to the run.sh entry one sentence containing the exact phrase `edits run.sh while it runs`. It should say that the whole body is parsed before execution, so the running process keeps its behavior and still saves its result.
### Acceptance criteria
- `grep -qF 'FAIL: self-edit' plugins/sdlc-lite/scripts/run-selftest.sh`
- `bash plugins/sdlc-lite/scripts/run-selftest.sh | grep -qx "run selftest: PASS"`
- The new case fails on the base runner: `w="${SDLC_TMP_WORKTREES:?}/base-s1"; git worktree add -q --detach "$w" "$SDLC_BASE_SHA" && cp plugins/sdlc-lite/scripts/run-selftest.sh "$w/plugins/sdlc-lite/scripts/run-selftest.sh" && out=$(bash "$w/plugins/sdlc-lite/scripts/run-selftest.sh" 2>&1); rc=$?; git worktree remove --force "$w"; test "$rc" -ne 0 && printf '%s\n' "$out" | grep -q "run selftest: FAIL: self-edit"`
- `grep -qF 'edits run.sh while it runs' docs/maintenance/sdlc-internals.md`
- `git diff --check "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/run-selftest.sh docs/maintenance/sdlc-internals.md`

## Step 2: run_lifecycle.py fails an exit 0 that wrote no result
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Defense in depth for the stated exit code contract ("1 run failed or returned no result"). In `plugins/sdlc-lite/scripts/run_lifecycle.py` `run()`, after the child exits: if it was not interrupted, `rc == 0`, and `directory / (name + '.md')` does not exist, print one stderr line containing `wrote no result` (naming the expected result path and the `.log`), set `rc = 1`, and let the attempt record become `failed` with `exit_code` 1. Leave interrupted, failed, and normal completed paths unchanged.

In `plugins/sdlc-lite/scripts/lifecycle-selftest.py`, add `test_exit_zero_without_result_fails` and append it to the `names` list in `__main__`. It drives `run_lifecycle.run` with a runner that exits 0 without writing a result. For example, point `readiness.ROOT` (as seen by `run_lifecycle`) at a temp root whose `scripts/run.sh` is just `exit 0`, with readiness patched to ready. It asserts return code 1, attempt status `failed`, and the stderr line.

Update the `Exit codes` line in the `run.sh` header, and add a sentence to the run.sh entry in `docs/maintenance/sdlc-internals.md` containing the exact phrase `exits 0 without a result`: the lifecycle owner records such a run as failed with exit 1.
### Acceptance criteria
- `grep -q "'test_exit_zero_without_result_fails'" plugins/sdlc-lite/scripts/lifecycle-selftest.py`
- `grep -qF 'wrote no result' plugins/sdlc-lite/scripts/run_lifecycle.py`
- `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`
- The new test fails on the base lifecycle: `w="${SDLC_TMP_WORKTREES:?}/base-s2"; git worktree add -q --detach "$w" "$SDLC_BASE_SHA" && cp plugins/sdlc-lite/scripts/lifecycle-selftest.py "$w/plugins/sdlc-lite/scripts/lifecycle-selftest.py" && out=$(python3 "$w/plugins/sdlc-lite/scripts/lifecycle-selftest.py" 2>&1); rc=$?; git worktree remove --force "$w"; test "$rc" -ne 0 && printf '%s\n' "$out" | grep -q "test_exit_zero_without_result_fails"`
- `grep -qF 'exits 0 without a result' docs/maintenance/sdlc-internals.md`
- `bash plugins/sdlc-lite/scripts/run-selftest.sh | grep -qx "run selftest: PASS"`

## Step 3: Gates green
level: L1
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Run every gate below from the repository root and fix any red that steps 1 and 2 introduced, keeping their behavior. If a gate was already red at the build-start HEAD, report builder Status `inherited red`.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `git diff --check`

## Risks
- The brace-group fix only protects a `run.sh` child that has already started. A `run.sh` launched after the edit runs the edited code, which is intended.
- A builder that corrupts `run.sh` still breaks later runs. That is out of scope; the hook option in the ticket was not chosen.
- Copying the whole plugin in the selftest assumes `readiness.inspect` passes on the copy (it resolves `ROOT` from `__file__`, so the copy's manifests and hooks are checked). If it fails, the builder must copy whatever readiness needs.
- The negative controls create and remove a worktree under `SDLC_TMP_WORKTREES`, which run.sh cleans up on exit anyway.
