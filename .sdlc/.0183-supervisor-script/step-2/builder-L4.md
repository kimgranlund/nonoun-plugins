<!-- role=builder level=L4 model=opus effort=xhigh -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/supervisor.py` (new file). It holds the module docstring, the CLI (`init`, `watch --run/--once/--now/--driver`, `status`, `reset --receiver`, `selftest`), the poll loop, the wake commands, and a selftest with 32 cases (16 positive, 16 patched-copy controls). Standard library only, Python 3.9.
- `plugins/sdlc-lite/scripts/check.sh`: added the `supervisor.py` selftest line after the `messages.py` one, and changed the header comment to "messages.py, and supervisor.py selftests".

## Checks
- AC1 (selftest output, all 32 `ok:` labels, PASS last, main checkout's `.sdlc/supervisor` unchanged, no `./.sdlc/supervisor`): rc=0, run twice. It took 20 s at load ~20, then 29.5 s and 33 s at load ~30, well under the 150 s target.
- AC2 (`import messages`, `messages.wait_ready(`, `messages.mailbox(`, no forbidden `def` names): rc=0.
- AC3 (exactly one `if __name__ == '__main__':` line): rc=0.
- AC4 (no `shell=True`, `os.system(`, `os.popen(`, or em dash): rc=0.
- AC5 (help metavar, the four `watch` options, `reset --receiver`): rc=0.
- AC6 (both `check.sh` edits present): rc=0.
- Guard (diff vs `$SDLC_BASE_SHA` shows only step 1's two docs and `check.sh`; the only untracked file is `supervisor.py`): rc=0.
- `python3 plugins/sdlc-lite/scripts/messages.py selftest`: `messages selftest: PASS`.
- `git diff --check` on `check.sh`: clean. No trailing whitespace in `supervisor.py`.
- The selftest fails on bad copies, run from a mktemp dir:
  - a no-op STOP control patch: FAIL `control: a copy that ignores STOP wakes: the case passed on the patched copy`;
  - a prompt that carries the ids: FAIL `prompt: no body and no topic: the prompt leaked`;
  - a poll that holds `stop_present` in a module alias: FAIL at the STOP control. This shows the call-time lookup rule is enforced.
- Manual runs in temp repos:
  - each refusal exits 1 with one `supervisor.py:` line: missing init, `--now` without `--once`, a bad `--now`, `claude` not on PATH, `reset` without or with a bad `--receiver`;
  - a missing subcommand exits 2;
  - `status` prints `none yet`, then the per-receiver lines;
  - `reset` is refused while a watcher runs;
  - SIGTERM during a wake kills the stub and its grandchild `sleep`, records `stopped`, writes `stopping: true`, and exits 0;
  - Codex gets the prompt on stdin;
  - with `log_keep` 2, two logs remain;
  - the runtime files show as git-ignored.
- shellcheck on `check.sh`: not run, because shellcheck is not installed on this host (`check.sh` would print `skip`).

## Notes
- The rule functions step 3 needs to know about (each is looked up by name at call time):
  - `write_entry_files` (init writer), `validate_limits`, `validate_hosts`;
  - `pending_ids` (pending count), `receiver_state` (D8 decision, returns `(state, reason, action)`);
  - `run_enabled` (dry-run gate), `debounce_met`, `wake_prompt`, `claude_argv`, `codex_argv`, `wake_env`;
  - `mode_action` (mode dispatch), `supervisor_dir` (folder resolver), `take_lock`, `stop_present`.
- Each control patch is a `CTL_*` string. Each check's reason prefix is a module constant; `st_control` requires the prefix to match.
- Step 2 behaviors that step 3 is expected to change:
  - after a notify (D17) or a finished wake the state is `cooling` with reason null and `next_wake` null, but nothing enforces a cooldown yet;
  - the wake `depth` is recorded as null;
  - the `own wake running` rule only knows this process's live children;
  - the AGENTS.md `## Limits` lines describe cooldown, the caps, depth, failures, and `quiet_seconds` as designed, but nothing enforces them yet.
- `status` prints `-` for a null reason as well as a null `last_wake`, so no line ends in an empty field.
- `STOP` is read again after each receiver's pending count, so mail sent after `STOP` is touched never wakes a host. This removed a race in the STOP-while-running case.
- AGENTS.md renders the absolute supervisor folder as `{{folder}}` in the `touch`/`rm STOP` commands, so they work from a linked worktree. Like `{{scripts}}`, this path is specific to the machine.
