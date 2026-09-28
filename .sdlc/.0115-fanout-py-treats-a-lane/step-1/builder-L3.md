<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- plugins/sdlc-lite/scripts/fanout.py: added `import steps`, `STEP_DIR_RE`, and `inherited_red(ticket_dir)`. `run_ticket` now calls it after the driver-failed check and before `git add -A`. The docstring has a new per-ticket step 3 (later steps renumbered to 4 and 5) and a line naming the case 5 selftest. Added selftest case 5: an inherited-red repo, plus a negative control whose builder Status is `done`.

## Checks
- `grep -qE "^import steps\b" plugins/sdlc-lite/scripts/fanout.py`: passed.
- `python3 -c "... fanout.inherited_red(d) == 'inherited red: step-1: test_a'"`: passed.
- `python3 -c "... step-1 done + step-2.superseded-1 inherited ... r is None"`: passed.
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: `fanout selftest: PASS`, rc 0, about 32s.
- (guard) `plugins/sdlc-lite/scripts/check.sh`: rc 0. Every selftest passed, plus shellcheck and plugin validate. My first try got rc 1 only because I redirected output into a log path whose directory did not exist yet; the script never ran. The rerun with a `mktemp` log is the result above.
- Does the case catch a broken `inherited_red`: I copied `plugins/sdlc-lite/scripts/` to a `mktemp -d` dir and made the copy's `inherited_red` return `None` at the top. `python3 <tmp>/scripts/fanout.py selftest` exited 1 with 7 failures from case 5: exit code, exact outcome, T-0002 skipped, no merges, no work file, status still ready, and the uncommitted lane file. I then removed the temp dir, and `git status` showed only fanout.py changed.
- `git diff --name-only HEAD -- plugins/sdlc-lite/scripts`: lists only `plugins/sdlc-lite/scripts/fanout.py`.

## Notes
- If reading the tests out of the Status line throws, `inherited_red` treats that step dir as not inherited, the same as a `steps.Fail` from `next_action`.
- Case 5 uses `--lanes-dir` in the temp dir, and each gate is `true`. The negative control also checks that the ticket is `done` on the integration branch, which goes beyond the handoff.
