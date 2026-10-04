## Task goal
Make the verifier model-family rule fire for a verifier launched at the task directory, on Claude and on Codex.

## Step 4: Gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: steps 1, 2, and 3.

This replan changes only step 4, after `plan-reviewer-L1-2.md` (verdict replan).
- The old step 4 ran `bash plugins/sdlc-lite/scripts/check.sh` as one `(guard)`. `steps.py split --only` runs each guard span under a 300 s default timeout and refuses a timed-out guard as `plan defect` (`steps.py:28`, `steps.py:496-500`, `steps.py:519-522`). The reviewer measured check.sh at 417 s at load averages 12 to 20.
- A full split is not available, because `step-1/` and `step-2/` hold role output (`steps.py:885-889`). So `--only` runs the step 4 guards before any builder starts.
- The criteria below therefore run each command check.sh runs as its own guard. At replan time, at load average 21, the longest took 59 s (`run-selftest.sh`) and all of them together took 258 s, so the split needs no `--guard-timeout`.

1. From the repository root, run `bash plugins/sdlc-lite/scripts/check.sh` once in full, because the handoff's Done-when names it. Report its exit code and wall time under Checks. It is not a criterion, for the reason above. A command check.sh runs that no criterion names (a sync from main can add one) is covered by this full run.
2. Run every criterion below. The check.sh guards map `plugins/sdlc-lite/scripts/check.sh` lines 12-27 and 33, one guard per command, in the script's order, with `$root` written as `plugins/sdlc-lite`.
   - `claude plugin validate plugins/sdlc-lite` is judged by exit status only, as check.sh judges it. Its one warning, about the plugin-root `CLAUDE.md`, exits 0.
   - check.sh's shellcheck pass (lines 28-32) has no criterion. shellcheck is not installed on this host, so check.sh prints `skip: shellcheck not installed` and that pass cannot go red here. This step does not prove it.
   - check.sh itself is not on the scope guard's allow-list, so this step cannot change the list the guards map.
3. The other Done-when gates are guards too: `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`, and the whole-task whitespace and em dash checks. `codex_roles.py generate --check` is the first check.sh guard.
4. The whole-task checks diff against the task's build-start commit, which is the first line of `.sdlc/0195-runner-family-task-dir/step-1/base-sha` (171e13b at replan time). They do not diff against `$SDLC_BASE_SHA`.
   - Why: the conductor commits each verified step (d87cc4b, aa59ebc). This step's `$SDLC_BASE_SHA` therefore already holds steps 1 to 3, and a diff against it sees only this step's own fixes.
   - The checks name the task's own files and leave out `docs/validation/runner-family-task-dir-live-run/`. The dry-run files there end with the trailing space that run.sh's `printf '%q '` writes, so `git diff --check` flags them. Copied evidence stays verbatim.
5. Fix any red that steps 1 to 3 introduced, inside the files those steps changed. A gate already red at the build-start HEAD is reported as Status `inherited red`.
6. If a fix changes `plugins/sdlc-lite/scripts/run.sh`, the step 3 evidence belongs to the earlier blob. Say so under Limits in `docs/validation/runner-family-task-dir-live-run.md`, naming both `git hash-object` values. Never edit the evidence files.
### Acceptance criteria
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py`
- (guard) `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- (guard) `python3 plugins/sdlc-lite/skills/decompose/scripts/coverage_check.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/board.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/order.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/onboard.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/traces.py selftest`
- (guard) `python3 plugins/sdlc-lite/scripts/messages.py selftest`
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh`
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`
- (guard) `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --selftest`
- (guard) `claude plugin validate plugins/sdlc-lite`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- (guard) `b=$(head -n 1 .sdlc/0195-runner-family-task-dir/step-1/base-sha); test -n "$b" && git diff --check "$b" -- plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/run-selftest.sh plugins/sdlc-lite/scripts/codex_roles.py plugins/sdlc-lite/scripts/codex-selftest.py docs/maintenance/sdlc-internals.md docs/codex-role-execution.md docs/README.md docs/validation/runner-family-task-dir-live-run.md`
- (guard) `b=$(head -n 1 .sdlc/0195-runner-family-task-dir/step-1/base-sha); test -n "$b" && ! git diff "$b" -- plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/run-selftest.sh plugins/sdlc-lite/scripts/codex_roles.py plugins/sdlc-lite/scripts/codex-selftest.py docs/maintenance/sdlc-internals.md docs/codex-role-execution.md docs/README.md docs/validation/runner-family-task-dir-live-run.md | grep -E "^\+" | grep -qF "$(printf '\342\200\224')"`
- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e plugins/sdlc-lite/scripts/run.sh -e plugins/sdlc-lite/scripts/run-selftest.sh -e docs/maintenance/sdlc-internals.md -e plugins/sdlc-lite/scripts/codex_roles.py -e plugins/sdlc-lite/scripts/codex-selftest.py -e docs/codex-role-execution.md -e docs/README.md -e docs/validation/runner-family-task-dir-live-run.md)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc")"`
