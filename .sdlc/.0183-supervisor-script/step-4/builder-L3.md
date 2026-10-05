<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `docs/reports/supervisor-live-run/probe.py` (new): the live probe. It has seven arms (`dry-run`, `claude`, `codex`, `claude-attached`, `codex-attached`, `claude-push`, `codex-push`), a pure `oracle(facts)`, and an offline `selftest` that uses a stub host.
- `docs/reports/supervisor-live-run/AGENTS.md` (new): says what the folder holds (`probe.py`, the `<arm>.txt` evidence files step 5 writes, and the dated record), what each arm shows, and how to rerun the selftest and each arm.
- `docs/reports/supervisor-live-run/CLAUDE.md` (new): contains `@AGENTS.md`.

## Checks
- AC1 (selftest prints every `ok:` label and `probe selftest: PASS` last): exit 0. The selftest takes about 13 s.
- AC2 (AGENTS.md is non-empty, CLAUDE.md is `@AGENTS.md`, AGENTS.md names `probe.py`): exit 0.
- AC3 (no `run.sh` in the file, `probe-remote` and `--driver` present, the `^BODY = "...git push probe-remote HEAD:refs/heads/wake-probe"$` regex matches): exit 0.
- AC4 (the selftest leaves the main checkout's `.sdlc/supervisor` listing unchanged and creates no `.sdlc/supervisor` in the worktree): exit 0.
- AC5 (no em dash in the three files): exit 0.
- (guard) The changed and untracked file sets are limited to the allowed paths: exit 0.
- `git diff --check`: clean. `python3 -m py_compile` on probe.py: ok. I removed the `__pycache__` it created.
- I also ran the three end-to-end arms with output visible, against the stub:
  - wake arm: `wakes=1`, `message_state=done`, `reply=yes`, stamps ordered, `push_attempt=denied`, `result=pass`.
  - push arm: `push_argv` is the watcher's exact Claude argv with the last argument replaced by the push prompt, `result=pass`.
  - dry-run arm: two messages, `dry_run_lines=4`, `wakes=0`, `message_state=new`, `result=pass`.
  - No `supervisor-live-*` temp dirs were left behind.
- No live arm was run, since that belongs to step 5. No model was called.

## Notes
- Three small choices the handoff left open:
  - **When the wake arms stop waiting:** they wait until a wake record has an end, or until `wake_timeout_seconds` + 60 s, instead of stopping as soon as the message reaches `done/`. A wake ends only after the host acks, so the host is not killed mid-turn, its final push attempt and cost event are captured, and the outcome is already settled at that point.
  - **A fourth `push_attempt` value:** `unclassified` covers a `git push` attempt with no denial evidence and no remote movement. The oracle fails it.
  - **A nonzero watcher exit after STOP** gives `result=fail reason=the watcher exited <n> after STOP`.
- Extra evidence lines beyond the item 8 list:
  - `watcher_exit=`
  - `dry_run_lines=` (dry-run only; the oracle does not judge it)
  - `push_argv=` (push arms)
  - `session_cmd=`, `session=`, `transcript=` (attached arms)
- `cost=` is Claude's summed `total_cost_usd`. It is `unknown` for Codex, which reports no cost, and `0` when no host ran (the dry-run arm).
- Exit codes are 0 pass, 1 fail, 2 setup error, 3 unverified.
- The probe environment drops `GIT_*` as well as the T-0181 list and the supervisor's scrub names, so the throwaway repo always resolves its own mailbox.
- Live arms keep their throwaway repo and print its path on stderr. The selftest removes all of its temp dirs.
