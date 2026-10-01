# Messages wait live run

Recorded: 2026-10-01

Live run for ticket T-0181. A fresh Claude Code host and a fresh Codex host were each started with a prompt naming one blocking `messages.py wait` call, and the probe sent them a message 20 seconds after launch. On both hosts the one wait call started before the send, returned the sent id on one line with its path and no body, and the host then claimed the message with `read`, replied, and acked it. Neither host made a `count` or `list` call, a `sleep`, a Monitor or background poll, or a Codex `write_stdin` or cell `wait`. One run per arm.

## Environment

- `claude --version`: `2.1.286 (Claude Code)`.
- `codex --version`: `codex-cli 0.159.2`. `codex login status` printed `Logged in using ChatGPT`.
- Models, from each host's own records:
  - Claude Code: the arm ran `--model sonnet --effort low`, and the init event's `model` in `host-stdout.jsonl` was `claude-sonnet-5-5`.
  - Codex: the rollout's `turn_context` records `gpt-6.1-sol`, effort `medium`, approval `never`, sandbox `workspace-write` with no network. The isolation control calls ran `gpt-6-luna`, effort `low`, sandbox `read-only`.
- Plugin commit `bc21b53` (`git rev-parse --short HEAD`). `git status --porcelain -- plugins/` printed three modified files: `plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml`, `plugins/sdlc-lite/agents/messenger.md`, and `plugins/sdlc-lite/scripts/messages.py`. These are the uncommitted T-0181 step 1 and 2 changes, because builders never commit, so both arms ran the `wait` subcommand from the working tree, not from `bc21b53`. Every arm used this worktree's `plugins/sdlc-lite`, not an installed copy.
- The session that launched the probe had `BASH_DEFAULT_TIMEOUT_MS=3600000` and `BASH_MAX_TIMEOUT_MS=3600000` set. The probe dropped both from every host process, so the Claude host ran with its default Bash limits.
- macOS 26.6.2, Darwin 25.6.0. Each run made its own throwaway Git project under `/private/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/messages-wait-live-*/project`. The projects and the raw host streams (`host-stdout.jsonl` and `host-stderr.txt`, next to each project) stay on this machine and are not in this repository.

## Method

[`messages-wait-live-run/probe.py`](messages-wait-live-run/probe.py) runs one arm per call and never runs `run.sh`. `python3 docs/validation/messages-wait-live-run/probe.py selftest` ran first and printed `probe selftest: PASS` after 12 cases: two pass cases (Claude, Codex), fail cases for two wait calls, a `count` call, a Monitor call, a backgrounded wait, no wait, a wait that starts after the send, a wait that returns another id, a Codex `write_stdin` poll, and a Codex cell `wait`, and one unverified case for a host not on `PATH`. Each arm then ran once, as one foreground call:

```
set -o pipefail; python3 docs/validation/messages-wait-live-run/probe.py claude | tee docs/validation/messages-wait-live-run/claude.txt
set -o pipefail; python3 docs/validation/messages-wait-live-run/probe.py codex | tee docs/validation/messages-wait-live-run/codex.txt
```

Setup, per run, with exit 2 on any failure:

1. `tempfile.mkdtemp(prefix='messages-wait-live-')`, then `project/` in it, `git init -q`, and one empty commit made with `-c user.name=probe -c user.email=probe@example.invalid -c commit.gpgsign=false`.
2. `python3 <plugin>/scripts/tickets.py --root .sdlc roadmap`, which writes `.sdlc/AGENTS.md` and the mailbox entry files before any message exists.
3. The host starts. 20 seconds after launch, unless the host has exited, the probe sends from the project root: `python3 <plugin>/scripts/messages.py send --receiver <claude|codex> --sender probe --topic live-probe --follow-up true "What is 2 + 3? Answer in one line."`, and starts the mailbox sampler.

Every host process got a copy of the environment without `CLAUDECODE`, `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA`, `BASH_DEFAULT_TIMEOUT_MS`, `BASH_MAX_TIMEOUT_MS`, and every `CLAUDE_CODE_*` and `SDLC_*` variable. The host timeout was 600 seconds.

Host commands, run with the project as cwd:

- Claude Code: `claude -p --safe-mode --disable-slash-commands --dangerously-skip-permissions --model sonnet --effort low --output-format stream-json --verbose --no-session-persistence -- "<prompt>"`
- Codex: `codex exec --ignore-user-config --json --color never -C <project> -m gpt-6.1-sol -c model_reasoning_effort="medium" -c approval_policy="never" --sandbox workspace-write "<prompt>"`

Prompt, with `<plugin>` set to this worktree's `plugins/sdlc-lite` and `<harness>` to `claude` or `codex`:

> Run this as one shell command and wait for it to finish: python3 <plugin>/scripts/messages.py wait --receiver <harness> --timeout 120 --interval 2. If your shell tool takes a timeout or a yield time, set it to at least 130000 milliseconds, so the call returns only when the command ends. When it prints a message id, handle that message as .sdlc/messages/AGENTS.md says: claim it with read, reply when follow_up_requested is true, then ack it. Then stop.

The trace values:

- `wait_calls`: the number of `messages.py wait` subcommands in the host's shell commands (Claude `Bash` calls, Codex `command_execution` items).
- `poll_calls`: `messages.py count` and `list` subcommands and `sleep` words in those shell commands, plus, on Claude Code, `Monitor`, `BashOutput`, and `TaskOutput` calls and any `Bash` call with `run_in_background: true`, plus, on Codex, rollout `function_call` items named `wait` or `write_stdin` and each `write_stdin(` in an exec cell's input.
- `wait_returned`: the first tab-separated field of the first line of the first wait call's output, when it is a message id.
- `wait_before_send`: `yes` when the probe received the first wait call's event (the Claude `tool_use`, or the first Codex event for that item) before the message's `send_time`.

A sampler thread checks the mailbox every 2 seconds and records the first time it sees the message in `new/`, `read/`, and `done/`. The stamps are read from the message files with the probe's own parser, not `messages.py`. The verdict passes only when all of these hold:

- no host timeout, `wait_calls=1`, `poll_calls=0`, and on Codex the rollout file was found so polls could be counted;
- `wait_returned` is the sent id and `wait_before_send=yes`;
- the T-0179 path-only oracle: the message is only in `done/<host>/`; `send_time`, `read_time`, and `ack_time` are timestamps with `send_time <= read_time <= ack_time`; the outcome is not `expired` or `expired, no reply`; some file in `new/probe/`, `read/probe/`, or `done/probe/` has `topic: live-probe` and `re: <id>`; and the arm is isolated.

Exit codes: 0 pass, 1 fail, 2 setup error, 3 unverified (the host cannot run).

Isolation proof per host, as in the T-0179 record:

- Claude Code: `--safe-mode` turns off `CLAUDE.md`, skills, installed plugins, hooks, MCP servers, and custom agents, and `--disable-slash-commands` turns off skills. The probe prints `isolation=yes` only when the run's own init event has empty `skills` and `slash_commands`, no `agents` entry starts with `sdlc-lite:`, and no tool call is named `Skill`. The init event still listed the installed plugins in its `plugins` field, sdlc-lite 0.20.2 among them, but its `tools` list had no `Skill` tool and its `agents` were only `claude`, `Explore`, `general-purpose`, and `Plan`.
- Codex: before the arm, two control calls ran `codex exec --json --color never --sandbox read-only -C <project> -m gpt-6-luna -c model_reasoning_effort="low" "Reply with exactly OK. Do not call tools."`, one with `--ignore-user-config` and one without. For each, the probe read `thread_id` from the `thread.started` event, found `~/.codex/sessions/**/rollout-*<thread_id>*.jsonl`, and counted `sdlc-lite`. The user config is where the sdlc-lite plugin is enabled on this host. The arm ran with the same `--ignore-user-config` flag.

## Claude Code

Evidence: [`messages-wait-live-run/claude.txt`](messages-wait-live-run/claude.txt).

```
arm=claude
project=/private/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/messages-wait-live-mjp7xh_h/project
plugin=/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/idle-host/plugins/sdlc-lite
message=/private/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/messages-wait-live-mjp7xh_h/project/.sdlc/messages/new/claude/20261001T161417595639Z-probe-live-probe.md
isolation=yes skills=0 slash_commands=0 sdlc_agents=0 skill_calls=0
tool=Bash sub=- in_subagent=no background=no cmd=python3 /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/idle-host/plugins/sdlc-lite/scripts/messages.py wait --receiver claude --timeout 120 --interval
tool=Read sub=- in_subagent=no background=no cmd=-
tool=Read sub=- in_subagent=no background=no cmd=-
tool=Bash sub=- in_subagent=no background=no cmd=S=/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/idle-host/plugins/sdlc-lite/scripts/messages.py; I=20261001T161417595639Z-probe-live-probe\npython3 $S
state=new 2026-10-01T16:14:17.679501Z
state=done 2026-10-01T16:14:25.694207Z
wait_calls=1 poll_calls=0
wait_returned=20261001T161417595639Z-probe-live-probe
wait_before_send=yes
send_time=2026-10-01T16:14:17.595639Z read_time=2026-10-01T16:14:24.598511Z ack_time=2026-10-01T16:14:24.905212Z outcome=answered: 5 reply=20261001T161424746631Z-claude-live-probe
result=pass
```

The raw stream (`host-stdout.jsonl`, 15 lines, empty `host-stderr.txt`) shows four tool calls:

1. A foreground `Bash` call with `command` `python3 <plugin>/scripts/messages.py wait --receiver claude --timeout 120 --interval 2` and `timeout: 140000`, with no `run_in_background`. Its tool result was one line, `20261001T161417595639Z-probe-live-probe<TAB><project>/.sdlc/messages/new/claude/20261001T161417595639Z-probe-live-probe.md`, with no front matter and no body.
2. `Read` of `.sdlc/messages/AGENTS.md`.
3. `Read` of the message file in `new/claude/`. This is the role reading the file, not the wait command.
4. One `Bash` call that ran `read <path> --receiver claude`, `reply <id> "2 + 3 = 5"`, and `ack <id> --outcome "answered: 5"`, joined with `&&`.

The init event's `tools` list held `Monitor`, which the role did not call. The claim and the ack fell between two samples, so there is no `state=read` line; the stamps show the order.

Result: pass

## Codex

Evidence: [`messages-wait-live-run/codex.txt`](messages-wait-live-run/codex.txt).

```
arm=codex
project=/private/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/messages-wait-live-59j88hq7/project
plugin=/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/idle-host/plugins/sdlc-lite
message=/private/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/messages-wait-live-59j88hq7/project/.sdlc/messages/new/codex/20261001T161459947049Z-probe-live-probe.md
isolation=yes ignore_config_sdlc_mentions=0 with_config_sdlc_mentions=68
tool=shell cmd=/bin/zsh -lc 'python3 /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/idle-host/plugins/sdlc-lite/scripts/messages.py wait --receiver codex --timeout 12
tool=shell cmd=/bin/zsh -lc 'cat .sdlc/messages/AGENTS.md'
tool=shell cmd=/bin/zsh -lc 'python3 /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/idle-host/plugins/sdlc-lite/scripts/messages.py read /private/var/folders/n0/b1pq0
tool=shell cmd=/bin/zsh -lc "python3 /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/idle-host/plugins/sdlc-lite/scripts/messages.py reply 20261001T161459947049Z-probe
tool=shell cmd=/bin/zsh -lc "python3 /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/idle-host/plugins/sdlc-lite/scripts/messages.py ack 20261001T161459947049Z-probe-l
state=new 2026-10-01T16:14:59.975465Z
state=read 2026-10-01T16:15:10.002698Z
state=done 2026-10-01T16:15:18.023884Z
wait_calls=1 poll_calls=0
wait_returned=20261001T161459947049Z-probe-live-probe
wait_before_send=yes
send_time=2026-10-01T16:14:59.947049Z read_time=2026-10-01T16:15:09.346637Z ack_time=2026-10-01T16:15:16.678218Z outcome=Replied: 2 + 3 = 5. reply=20261001T161516495214Z-codex-live-probe
result=pass
```

The probe cuts each command at 160 characters, so the wait line ends at `--timeout 12`; the raw stream holds the full command, `... messages.py wait --receiver codex --timeout 120 --interval 2`.

The raw stream (`host-stdout.jsonl`, 15 lines; `host-stderr.txt` held only `Reading additional input from stdin...`) shows five `command_execution` items. The wait item completed with exit code 0 and `aggregated_output` of one line, `20261001T161459947049Z-probe-live-probe<TAB><project>/.sdlc/messages/new/codex/20261001T161459947049Z-probe-live-probe.md`, with no body. Then came `cat .sdlc/messages/AGENTS.md`, `read <path> --receiver codex`, `reply <id> '2 + 3 = 5.'`, and `ack <id> --outcome 'Replied: 2 + 3 = 5.'`.

The rollout, thread `01a0f83f-193a-7443-876f-aa387ff555eb`, shows the same calls as `custom_tool_call` items named `exec`:

- At 16:14:48.251Z, before the 16:14:59.947Z send: `const r = await tools.exec_command({cmd:"python3 <plugin>/scripts/messages.py wait --receiver codex --timeout 120 --interval 2",yield_time_ms:130000,max_output_tokens:2000});text(r);`. Its output, at 16:15:00.602Z, reads `Script completed`, `Wall time 12.2 seconds`, `exit_code` 0, and the one id and path line.
- One cell each for the `cat` and the `read`, then one cell with two `tools.exec_command` calls, the `reply` and the `ack`.
- No `function_call` named `wait` or `write_stdin`, and no `write_stdin(` in any cell.

Result: pass

## Limits

- One run per arm, on one machine and one account per host.
- An active parent only: each host was told to make the wait call at the start of its turn. Waking an idle host when mail arrives was not tested (T-0182).
- `poll_calls` counts only the kinds listed under Method. Other shell calls appear as `tool=` lines and are not judged; here they were the `cat` of `.sdlc/messages/AGENTS.md` on Codex and the handling calls.
- `wait_before_send` compares the time the probe received the call's event with `send_time`, not the time the command started. The Codex rollout puts the wait cell 11.7 seconds before the send; the Claude stream has no per-event timestamps.
- The probe cuts `tool=` lines at 160 characters, which drops the end of the Codex wait command in the evidence file.
- Both arms ran the uncommitted step 1 and 2 changes in `plugins/`, not a commit.
- No quoted evidence line held U+2014, so no `\u2014` substitution was needed. The Codex agent messages in the raw stream held curly quotes, which are not quoted here.
