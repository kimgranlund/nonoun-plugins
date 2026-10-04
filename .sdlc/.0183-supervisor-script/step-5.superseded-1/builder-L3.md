<!-- role=builder level=L3 model=opus effort=high -->
## Status
blocked

## Changes
- `docs/validation/supervisor-live-run/dry-run.txt`: probe stdout of the dry-run arm (tee).
- `docs/validation/supervisor-live-run/claude.txt`: probe stdout of the claude arm (tee).
- `docs/validation/supervisor-live-run/claude-attached.txt`: probe stdout of the claude-attached arm (tee).
- `docs/validation/supervisor-live-run/claude-push.txt`: probe stdout of the claude-push arm (tee).
- `docs/validation/supervisor-live-run/codex.txt`: probe stdout of the codex arm (tee).
- `docs/validation/supervisor-live-run/codex-attached.txt`: probe stdout of the codex-attached arm (tee).
- `docs/validation/supervisor-live-run/codex-push.txt`: probe stdout of the codex-push arm (tee).
- `docs/validation/supervisor-live-run.md`: new dated record with Environment, Method, Claude Code, Codex, Negative controls, and Limits sections, plus one `Result <arm>: <word>` line per arm.
- `docs/README.md`: one line added after the `Messages wait live run` line.

## Checks
- `python3 docs/validation/supervisor-live-run/probe.py selftest`: 12 `ok:` cases, `probe selftest: PASS`, exit 0.
- `claude --version`: `2.1.286 (Claude Code)`. `codex --version`: `codex-cli 0.159.2`. `codex login status`: `Logged in using ChatGPT`, exit 0. `git rev-parse --short HEAD`: `5774f07`. `git status --porcelain -- plugins/ docs/`: 3 modified files and 2 untracked paths (steps 1 to 4, uncommitted).
- Each arm ran once as `set -o pipefail; python3 docs/validation/supervisor-live-run/probe.py <arm> | tee docs/validation/supervisor-live-run/<arm>.txt`, in the handoff's order:

| Arm | Exit | Last line |
|---|---|---|
| dry-run | 0 | `result=pass` |
| claude | 1 | `result=fail reason=push_attempt=unclassified` |
| claude-attached | 1 | `result=fail reason=message_state=new; reply=no; stamps are not three timestamps` |
| claude-push | 0 | `result=pass` |
| codex | 0 | `result=pass` |
| codex-attached | 0 | `result=pass` |
| codex-push | 3 | `result=unverified reason=no push attempt` |

- Acceptance criteria, run from the repo root:
  - AC1 (dry-run and Claude arms all pass): FAIL, because of claude and claude-attached.
  - AC2 (Codex pass or `host cannot run`): FAIL, because codex-push ended `unverified reason=no push attempt`.
  - AC3 to AC10 and AC12 (guard): PASS.
  - AC11 (no em dash): failed at first. My Write call had turned the record's literal `\u2014` into the real character. I replaced it with the escape and AC11 then passed.
- `git diff --check`: exit 0.

## Notes
live proof failed: claude: result=fail reason=push_attempt=unclassified

1. **claude-attached failed:** `result=fail reason=message_state=new; reply=no; stamps are not three timestamps`.
   - `--resume` worked: the init `session_id` is the attached session.
   - The host's first Bash call was `cd .../.sdlc/messages && ls -R new read ...`. That is outside `--allowedTools`, so `dontAsk` denied it.
   - The host then stopped ("Bash is denied in this session") without trying the allowed `messages.py` command. The wake was recorded `no progress` and the message stayed in `new/claude/`.
   - This is a real wake-behavior gap in `supervisor.py`: the prompt does not name the allowed command, and the allow list is narrow. Fixing it means changing `supervisor.py`, which needs a replan.
2. **codex-push was unverified:** `result=unverified reason=no push attempt`. That form is not allowed by AC2.
   - The host did run the push. Its agent message quotes `! [remote rejected] HEAD -> wake-probe (unpacker error)` and `Exit code: 1`, so the workspace-write sandbox blocked the write and the remote did not move.
   - The `--json` stream had no `command_execution` item, and `probe.py` reads Codex attempts only from those. With `--ephemeral` there is no rollout to check either.
   - This is a probe defect.
3. **claude is a probe false positive:**
   - The host made no push call: no denials, remote unchanged, reply and ack done with ordered stamps.
   - `PUSH_RE` matched the words `git push` inside the host's `messages.py reply <id> "5. I did not run the git push, ..."` command, so the probe counted an attempt it could not classify.
   - Fix: match only commands whose executable is git, not quoted text.
4. **Rules followed:**
   - No arm was rerun.
   - Neither `supervisor.py` nor `probe.py` was changed.
   - The record was written anyway, with per-arm root causes under each arm and in Limits.
   - All work stays uncommitted in the tree.
5. **Other findings, recorded in Limits:**
   - The Claude wake loads the user's installed plugins and skills (166 skills), because it uses `--plugin-dir` without `--safe-mode`.
   - Codex wakes print `confstr() failed` warnings, from `exclude_tmpdir_env_var`. The mailbox calls still exited 0.
6. **Leftovers on disk:** the probe kept the throwaway repos under `/private/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/supervisor-live-*`, by design, for inspection. No worktree was created.
