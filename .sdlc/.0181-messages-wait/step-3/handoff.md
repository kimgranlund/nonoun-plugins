## Task goal
A parent host can wait for mail with one blocking command instead of a polling subagent, and the command never claims, moves, or prints a message body.

## Step 3: Live probe for wait, with an offline selftest
level: L3
### Do
Target: the new file `docs/validation/messages-wait-live-run/probe.py`. Use Python 3.9 syntax only. This step makes no model call and runs no live arm.

Depends on: none for its offline selftest, which drives `messages.py` send, read, reply, and ack, all of which exist now. It runs after steps 1 and 2 so that step 4's live arms use the finished plugin.

1. Model the probe on `docs/validation/messages-live-run/probe.py` (T-0179). Read these parts of it first:
   - its docstring, `clean_env`, `run_checked`, `setup`, and `send`;
   - `parse_message`, `locate`, `find_reply`, `oracle`, and `Sampler`;
   - `ClaudeTrace`, `CodexTrace`, `codex_home`, `find_rollout`, `codex_control`, and `codex_isolation`;
   - `kill_group`, `run_host`, `run_arm`, and `selftest`.

   Copy what the new probe needs. Do not import or edit the T-0179 probe.
   - `PLUGIN` is `Path(__file__).resolve().parents[3] / 'plugins' / 'sdlc-lite'`, the same depth as in the T-0179 probe.
   - `clean_env` drops what the T-0179 one drops (`CLAUDECODE`, `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA`, `CLAUDE_CODE_*`, `SDLC_*`). It also drops `BASH_DEFAULT_TIMEOUT_MS` and `BASH_MAX_TIMEOUT_MS`, so the Claude host runs with its default Bash limits. Evidence: run.sh passes both as 3600000 to every role (run.sh:67-70), so the builder that runs this probe would hand them down.
   - `setup` works as in T-0179:
     1. Make a temp project from `tempfile.mkdtemp(prefix='messages-wait-live-')`.
     2. Run `git init -q` and make one empty commit.
     3. Run `tickets.py --root .sdlc roadmap`.

     There is no defect fixture and no `codex_roles.py install`.
2. Usage is `probe.py <claude|codex> [--timeout SECONDS]` and `probe.py selftest`. Constants:
   - `SENDER = 'probe'`, `TOPIC = 'live-probe'`, `BODY = 'What is 2 + 3? Answer in one line.'`;
   - `SEND_DELAY = 20`, `SAMPLE_EVERY = 2`;
   - `PATH_TIMEOUT = 600`, the default `--timeout`.
3. The prompt, with `<harness>` set to the arm and `<plugin>` set to the absolute `PLUGIN` path:
   ```text
   Run this as one shell command and wait for it to finish: python3 <plugin>/scripts/messages.py wait --receiver <harness> --timeout 120 --interval 2. If your shell tool takes a timeout or a yield time, set it to at least 130000 milliseconds, so the call returns only when the command ends. When it prints a message id, handle that message as .sdlc/messages/AGENTS.md says: claim it with read, reply when follow_up_requested is true, then ack it. Then stop.
   ```
   Why the yield sentence: Codex 0.159.2 runs shell commands through a code-mode `exec` tool, and the `~/.codex/sessions` rollouts from 2026-09-29 and 2026-09-30 show how it handles a long command:
   - The nested `tools.exec_command` returns a `session_id` instead of an exit code when the command outlives its `yield_time_ms`.
   - The model then polls with `tools.write_stdin`.
   - A cell that outlives its own yield is continued by a top-level `wait` function call.
   - A `yield_time_ms` of 30000 was honored there.
4. Host commands, run with the project as cwd:
   - claude: `claude -p --safe-mode --disable-slash-commands --dangerously-skip-permissions --model sonnet --effort low --output-format stream-json --verbose --no-session-persistence -- "<prompt>"`.
   - codex: `codex exec --ignore-user-config --json --color never -C <project> -m gpt-6.1-sol -c model_reasoning_effort="medium" -c approval_policy="never" --sandbox workspace-write "<prompt>"`.
     - This is the model and effort of the path-only arm in `docs/validation/messages-live-run.md` (its lines 13 and 41).
     - Before the arm, the two T-0179 isolation control calls run (`codex_isolation`).
   - The host starts first. `SEND_DELAY` seconds after launch, `run_host`'s `delayed` hook does three things:
     - sends the message with `messages.py send --receiver <harness> --sender probe --topic live-probe --follow-up true "<BODY>"`;
     - prints `message=<path>`;
     - starts the 2-second `Sampler`.
5. The trace derives four values from the host's own events.
   - Command classification, applied to each shell command string:
     - each match of `messages\.py["']?\s+(?:--root\s+\S+\s+)?([a-z]+)` names one `messages.py` subcommand;
     - each match of `(?<![\w.-])sleep(?![\w-])` is one sleep.
   - Shell commands are Claude `Bash` tool_use `command` values and Codex `command_execution` item `command` values. A Codex item is counted once per item id.
   - `wait_calls`: the number of `wait` subcommands across all shell commands.
   - `poll_calls`: the sum of these:
     - `count` and `list` subcommands and `sleep` words across all shell commands;
     - Claude tool_use blocks named `Monitor`, `BashOutput`, or `TaskOutput`;
     - Claude `Bash` tool_use blocks with `run_in_background` true;
     - Codex calls found in the arm's rollout, located with `find_rollout(codex_home(env), thread_id)` and retried for up to 10 s:
       - each line whose `payload` has `type` `function_call` and `name` `wait` or `write_stdin`;
       - each occurrence of `write_stdin(` in the `input` of a `payload` with `type` `custom_tool_call`.

       A missing rollout gives the fail reason `no rollout file for thread <id>, so polls cannot be counted`.
   - `wait_returned`: the first tab-separated field of the first line of the first wait call's output, or `-` when that field is not an id.
     - Claude: the output is the `tool_result` block, in a `user` event, whose `tool_use_id` is the `id` of the first wait tool_use. Its `content` is a string or a list of `{type: text, text}` blocks.
     - Codex: the output is the completed `command_execution` item's `aggregated_output`.
   - `wait_before_send`: `yes` when the probe's `utc_now()` at receipt of the first wait call's event is earlier than the message's `send_time`, else `no`. The event is the assistant `tool_use` on Claude, and the first event for that item id (normally `item.started`) on Codex.
6. One function, `judge`, holds the verdict. Both `run_arm` and `selftest` call it, so the selftest exercises the same decision code the live run uses.
   - Pass only when all of these hold:
     - `wait_calls == 1` and `poll_calls == 0`;
     - `wait_returned` equals the sent id;
     - `wait_before_send` is `yes`;
     - the T-0179 `oracle` checks for a path-only arm hold: the message is only in `done/<harness>/`; `send_time`, `read_time`, and `ack_time` are non-empty timestamps with `send_time <= read_time <= ack_time`; the outcome is not an expiry; a reply with `topic: live-probe` and `re: <id>` exists; the run is isolated;
     - the arm did not time out.
   - Each failed condition adds its own reason naming the value, for example `poll_calls=1`.
7. Unverified (exit 3) is only for a host that cannot run. Its line always reads `result=unverified reason=host cannot run: <detail>`. The probe emits it in these cases, the T-0179 conditions at probe.py:585-587, 433-452, 510-513, and 650-653:
   - the host is not on PATH (`shutil.which` with the clean env's PATH);
   - the host could not start;
   - a Codex control call failed or left no rollout;
   - the host made no tool call before it timed out or exited nonzero.

   Every other problem gives `result=fail reason=<reasons joined with "; ">` and exit 1. Setup errors exit 2, as in T-0179.
8. Output on stdout, in this order:
   1. `arm=<arm>`, `project=<path>`, `plugin=<path>`;
   2. `message=<path>`, when the message was sent;
   3. the isolation line;
   4. the `tool=` trace lines;
   5. the `state=` lines;
   6. `wait_calls=<n> poll_calls=<n>`;
   7. `wait_returned=<id or ->`;
   8. `wait_before_send=<yes|no>`;
   9. the T-0179 stamps line (`send_time=... read_time=... ack_time=... outcome=... reply=...`);
   10. last, the `result=` line.

   Progress notes go to stderr. Raw host stdout and stderr are saved next to the project as `host-stdout.jsonl` and `host-stderr.txt`, as in T-0179.
9. `probe.py selftest` runs offline, with no model call. It feeds synthetic host events to the trace classes, writes synthetic rollout files under a temp `CODEX_HOME`, and does a real `messages.py` send, read, reply, and ack in a throwaway project.
   - It prints `ok: <label>` per case, then `probe selftest: PASS`. The first failing case prints `probe selftest: FAIL: <label>: <reason>` and exits 1.
   - Each fail case asserts that the verdict is fail and that a reason names the defect the case plants (for example `poll_calls=1` or `wait_before_send=no`), so it cannot pass on an unrelated failure. Each pass case asserts no reasons.
   - Cases, with exactly these labels:
     - `pass: one wait call returned the id, then read, reply, ack` (Claude events)
     - `pass: a Codex wait call with no poll in the rollout` (Codex events, and a rollout holding one `exec` call that uses `tools.exec_command` only)
     - `fail: two wait calls`
     - `fail: a count call`
     - `fail: a Monitor call`
     - `fail: a backgrounded wait call` (a `Bash` wait with `run_in_background` true)
     - `fail: no wait call`
     - `fail: the wait started after the send` (the wait event is fed after the send)
     - `fail: the wait returned another id`
     - `fail: a Codex write_stdin poll` (the rollout's `exec` input also calls `tools.write_stdin`)
     - `fail: a Codex cell wait` (the rollout holds a `function_call` named `wait`)
     - `unverified: a host not on PATH says host cannot run` (the PATH check, run with `PATH` set to an empty temp folder, returns a reason that starts with `host cannot run: `)

Focused check: `python3 docs/validation/messages-wait-live-run/probe.py selftest`.
### Acceptance criteria
- `out=$(python3 docs/validation/messages-wait-live-run/probe.py selftest) && printf "%s\n" "$out" | grep -qxF "probe selftest: PASS" && for l in "pass: one wait call returned the id, then read, reply, ack" "pass: a Codex wait call with no poll in the rollout" "fail: two wait calls" "fail: a count call" "fail: a Monitor call" "fail: a backgrounded wait call" "fail: no wait call" "fail: the wait started after the send" "fail: the wait returned another id" "fail: a Codex write_stdin poll" "fail: a Codex cell wait" "unverified: a host not on PATH says host cannot run"; do printf "%s\n" "$out" | grep -qxF "ok: $l" || exit 1; done`
- `for v in BASH_DEFAULT_TIMEOUT_MS BASH_MAX_TIMEOUT_MS; do grep -qF "$v" docs/validation/messages-wait-live-run/probe.py || exit 1; done`
- `f=docs/validation/messages-wait-live-run/probe.py; test -f "$f" && ! grep -qF "$(printf '\342\200\224')" "$f"`
- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e plugins/sdlc-lite/scripts/messages.py -e plugins/sdlc-lite/agents/messenger.md -e plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml -e docs/maintenance/sdlc-internals.md -e docs/ticket-stages/design.md)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vxF docs/validation/messages-wait-live-run/probe.py)"`
