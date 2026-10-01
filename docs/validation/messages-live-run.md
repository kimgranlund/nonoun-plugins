# Messages live run

Recorded: 2026-10-01

Live run for ticket T-0179. A fresh Claude Code role and a fresh Codex role, each given only the path of a message file and no skill, claimed the message, replied, and acked it by following the generated mailbox entry files. The `messenger` agent polled, claimed, and handed the message to its parent on both hosts. With a wrong mailbox `AGENTS.md` injected, the Claude Code path-only role followed it and the run failed. One trial per arm.

## Environment

- `claude --version`: `2.1.286 (Claude Code)`.
- `codex --version`: `codex-cli 0.159.2`. `codex login status` printed `Logged in using ChatGPT`.
- Models, from each host's own records:
  - Claude Code: every Claude arm ran `--model sonnet --effort medium`, and the init event's `model` was `claude-sonnet-5-5` in all three Claude runs. In the messenger arm, the subagent's assistant events carried `claude-haiku-4-5-20251001`.
  - Codex, path only: the rollout's `turn_context` records `gpt-6.1-sol`, effort `medium`, approval `never`, sandbox `workspace-write` with no network.
  - Codex isolation control calls: `gpt-6-luna`, effort `low`, sandbox `read-only`.
  - Codex messenger arm: the parent's rollout records `gpt-6.1-sol` `medium`. The subagent's rollout records `gpt-5.6-terra` `low`, the model in `sdlc-messenger-l1.toml`.
- Plugin commit `f93894d` (`git rev-parse --short HEAD`), T-0179 steps 1 and 2. `git status --porcelain -- plugins/` printed nothing, so `plugins/` had no uncommitted change. Every arm used this worktree's `plugins/sdlc-lite`, not an installed copy.
- macOS, Darwin 25.6.0. Each run made its own throwaway Git project under `/private/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/messages-live-*/project`. The projects and the raw host streams (`host-stdout.jsonl` and `host-stderr.txt`, next to each project) stay on this machine and are not in this repository.

## Method

[`messages-live-run/probe.py`](messages-live-run/probe.py) runs one arm per call and never runs `run.sh`. Each run's stdout was saved with `| tee` as the evidence file named in its section. `python3 docs/validation/messages-live-run/probe.py selftest` checks the oracle and the parsers offline against the real `messages.py`:

- read, reply, and ack gives pass;
- read only gives fail;
- the defect flow (`cat`, then `mv` into `done/`) gives fail;
- the Claude isolation parser gives no for an init event with `skills: ["sdlc-lite:chain"]` and yes for one without;
- the Codex rollout counter finds 0 and 2 mentions in two synthetic rollout files.

Setup, per run, with exit 2 on any failure:

1. `tempfile.mkdtemp(prefix='messages-live-')`, then `project/` in it, `git init -q`, and one empty commit made with `-c user.name=probe -c user.email=probe@example.invalid -c commit.gpgsign=false`.
2. `python3 <plugin>/scripts/tickets.py --root .sdlc roadmap`, which writes `.sdlc/AGENTS.md` and the mailbox entry files before any message exists.
3. `codex-messenger` only: `python3 <plugin>/scripts/codex_roles.py install <project>`.
4. The message, sent from the project root: `python3 <plugin>/scripts/messages.py send --receiver <claude|codex> --sender probe --topic live-probe --follow-up true "What is 2 + 3? Answer in one line."`. Path-only arms send before the host starts. Messenger arms start the host and send 20 seconds later, so the messenger has to poll.

Every host process got a copy of the environment without `CLAUDECODE`, `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA`, and every `CLAUDE_CODE_*` and `SDLC_*` variable, so no role inherited a path to the plugin.

Host commands, run with the project as cwd:

- Claude Code, path only: `claude -p --safe-mode --disable-slash-commands --dangerously-skip-permissions --model sonnet --effort medium --output-format stream-json --verbose --no-session-persistence -- "Handle the message at <absolute message path>."`
- Codex, path only: `codex exec --ignore-user-config --json --color never -C <project> -m gpt-6.1-sol -c model_reasoning_effort="medium" -c approval_policy="never" --sandbox workspace-write "Handle the message at <absolute message path>."`
- Messenger on Claude Code: `claude -p --plugin-dir <plugin> --dangerously-skip-permissions --model sonnet --effort medium --output-format stream-json --verbose --no-session-persistence -- "<Claude parent prompt>"`
- Messenger on Codex: `codex exec --json --color never -C <project> -m gpt-6.1-sol -c model_reasoning_effort="medium" -c agents.enabled=true -c approval_policy="never" --sandbox workspace-write "<Codex parent prompt>"`

Claude parent prompt:

> This repository has a mailbox, and its procedures are in .sdlc/messages/AGENTS.md. Read that file. Spawn the sdlc-lite:messenger agent in the foreground, not in the background, with the prompt "harness: claude", and wait for its report; spawn it again until a report names a claimed message. Handle each claimed message as .sdlc/messages/AGENTS.md says: reply when follow_up_requested is true, then ack it. Then stop.

Codex parent prompt:

> This repository has a mailbox, and its procedures are in .sdlc/messages/AGENTS.md. Read that file. Spawn the sdlc-messenger-l1 agent with the prompt "harness: codex" and wait for its report; spawn it again until a report names a claimed message. Handle each claimed message as .sdlc/messages/AGENTS.md says: reply when follow_up_requested is true, then ack it. Then stop.

A sampler thread checks the mailbox every 2 seconds and records the first time it sees the message in `new/`, `read/`, and `done/`. The stamps are read from the message files with the probe's own parser, not `messages.py`. The oracle passes only when all of these hold:

- the message is only in `done/<host>/`;
- `send_time`, `read_time`, and `ack_time` are non-empty and `send_time <= read_time <= ack_time`;
- the outcome is not `expired` or `expired, no reply`;
- some file in `new/probe/`, `read/probe/`, or `done/probe/` has `topic: live-probe` and `re: <id>`;
- path-only arms are isolated;
- messenger arms show the messenger spawned, and state lines new, read, done in that order.

Exit codes: 0 pass, 1 fail, 2 setup error, 3 unverified.

Isolation proof per host:

- Claude Code: `--safe-mode` turns off `CLAUDE.md`, skills, installed plugins, hooks, MCP servers, and custom agents, and `--disable-slash-commands` turns off skills. The probe prints `isolation=yes` only when the run's own init event has empty `skills` and `slash_commands`, no `agents` entry starts with `sdlc-lite:`, and no tool call is named `Skill`. The init event still listed the installed plugins in its `plugins` field, sdlc-lite 0.20.1 among them, but its `tools` list had no `Skill` tool and its `agents` were only `claude`, `Explore`, `general-purpose`, and `Plan`.
- Codex: before the arm, two control calls ran `codex exec --json --color never --sandbox read-only -C <project> -m gpt-6-luna -c model_reasoning_effort="low" "Reply with exactly OK. Do not call tools."`, one with `--ignore-user-config` and one without. For each, the probe read `thread_id` from the `thread.started` event, found `~/.codex/sessions/**/rollout-*<thread_id>*.jsonl`, and counted `sdlc-lite`. The user config is where the sdlc-lite plugin is enabled on this host. The arm ran with the same `--ignore-user-config` flag. As an extra check, the arm's own rollout held no `sdlc-lite` in its 12 lines before the first tool call.

The negative control is `probe.py claude --defect`. After the send, it overwrites the four generated mailbox `AGENTS.md` files (root, `new/`, `read/`, `done/`) with [`messages-live-run/defect-AGENTS.md`](messages-live-run/defect-AGENTS.md). That fixture says to print the message with `cat <path>`, move it with `mkdir -p .sdlc/messages/done/<receiver> && mv <path> .sdlc/messages/done/<receiver>/`, and that no reply and no script are needed. These commands exit 0, so a role that follows them leaves no `read_time`, `ack_time`, or reply.

## Claude Code, path only

Evidence: [`messages-live-run/claude.txt`](messages-live-run/claude.txt).

```
isolation=yes skills=0 slash_commands=0 sdlc_agents=0 skill_calls=0
tool=Read sub=- in_subagent=no cmd=-
tool=Read sub=- in_subagent=no cmd=-
tool=Bash sub=- in_subagent=no cmd=S=/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/ticket-stages-b/plugins/sdlc-lite/scripts/messages.py; ID=20261001T095420801307Z-probe-live-probe; pyt
state=new 2026-10-01T09:54:20.824602Z
state=done 2026-10-01T09:54:30.853715Z
send_time=2026-10-01T09:54:20.801307Z read_time=2026-10-01T09:54:29.538289Z ack_time=2026-10-01T09:54:29.696021Z outcome=answered: 5 reply=20261001T095429616038Z-claude-live-probe
result=pass
```

The two reads were the message file and `.sdlc/messages/AGENTS.md`, which the role reached through the message's `protocol:` line. The one Bash call ran `read <path> --receiver claude`, `reply <id> "2 + 3 = 5"`, and `ack <id> --outcome "answered: 5"`, joined with `&&`, using the script path from the entry file. The claim and the ack fell between two samples, so there is no `state=read` line; the stamps show the order.

Result: pass

## Codex, path only

Evidence: [`messages-live-run/codex.txt`](messages-live-run/codex.txt).

```
isolation=yes ignore_config_sdlc_mentions=0 with_config_sdlc_mentions=68
tool=shell cmd=/bin/zsh -lc 'cat .sdlc/messages/new/codex/20261001T100350487495Z-probe-live-probe.md'
tool=shell cmd=/bin/zsh -lc 'for f in AGENTS.md .sdlc/AGENTS.md .sdlc/messages/AGENTS.md .sdlc/messages/new/AGENTS.md .sdlc/messages/read/AGENTS.md .sdlc/messages/done/AGENTS.
tool=command_execution sub=sdlc-messenger-l1
tool=shell cmd=/bin/zsh -lc 'python3 "/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/ticket-stages-b/plugins/sdlc-lite/scripts/messages.py" read ".sdlc/messages/new/c
tool=shell cmd=/bin/zsh -lc 'python3 "/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/ticket-stages-b/plugins/sdlc-lite/scripts/messages.py" reply 20261001T10035048749
tool=shell cmd=/bin/zsh -lc 'python3 "/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/ticket-stages-b/plugins/sdlc-lite/scripts/messages.py" ack 20261001T100350487495Z
state=new 2026-10-01T10:03:50.512045Z
state=read 2026-10-01T10:04:18.623994Z
state=done 2026-10-01T10:04:26.664611Z
send_time=2026-10-01T10:03:50.487495Z read_time=2026-10-01T10:04:17.983233Z ack_time=2026-10-01T10:04:25.368786Z outcome=Replied: 2 + 3 = 5. reply=20261001T100425244700Z-codex-live-probe
result=pass
```

One more trace line, a `rg --files` search, came first and is in the evidence file. The role printed the message, then printed each `AGENTS.md` that exists under `.sdlc/` (the router, the mailbox file, and the three stage files), then ran `read <path> --receiver codex`, `reply <id> "2 + 3 = 5."`, and `ack <id> --outcome "Replied: 2 + 3 = 5."` as three commands. The `tool=command_execution sub=sdlc-messenger-l1` line is from the output of that `cat`, because `.sdlc/messages/AGENTS.md` names the agent; no subagent ran in this arm. This is the second recorded run of this arm. The first, also `result=pass`, left a trailing space in a truncated command, so the probe now strips trailing whitespace from the command and this arm was recorded again. The other four evidence files came from the probe before that change; none of their lines ends in whitespace, so the change does not alter them.

Result: pass

## Messenger on Claude Code

Evidence: [`messages-live-run/claude-messenger.txt`](messages-live-run/claude-messenger.txt). The init event listed `sdlc-lite:messenger` in `agents`, from `--plugin-dir` (source `sdlc-lite@inline`).

```
tool=Agent sub=sdlc-lite:messenger in_subagent=no cmd=-
tool=Monitor sub=- in_subagent=yes cmd=-
tool=Agent sub=sdlc-lite:messenger in_subagent=no cmd=-
tool=Monitor sub=- in_subagent=yes cmd=-
tool=Agent sub=sdlc-lite:messenger in_subagent=no cmd=-
tool=Bash sub=- in_subagent=yes cmd=python3 /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/ticket-stages-b/plugins/sdlc-lite/scripts/messages.py count --receiver claude
tool=Bash sub=- in_subagent=yes cmd=python3 /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/ticket-stages-b/plugins/sdlc-lite/scripts/messages.py list --receiver claude --state new
tool=Bash sub=- in_subagent=yes cmd=python3 /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/ticket-stages-b/plugins/sdlc-lite/scripts/messages.py read 20261001T095625576733Z-probe-live-pro
state=new 2026-10-01T09:56:25.599966Z
state=read 2026-10-01T09:57:01.681784Z
state=done 2026-10-01T09:57:09.712054Z
messenger_spawned=yes
send_time=2026-10-01T09:56:25.576733Z read_time=2026-10-01T09:56:59.690735Z ack_time=2026-10-01T09:57:09.192724Z outcome=replied: 5 reply=20261001T095709122640Z-claude-live-probe
result=pass
```

The quote leaves out the parent's `Read`, the subagents' `ToolSearch` calls and first `count`, and the parent's `ls` and `cat` calls; all are in the evidence file. The parent read `.sdlc/messages/AGENTS.md` and spawned the messenger three times, each with `run_in_background: false`. The first two messengers armed a Monitor poll and returned a "polling" report with no claim. The third ran `count`, `list`, and `read`, and reported the id and `read/claude/<id>.md`. The parent then ran `reply` and `ack` in one Bash call.

Result: pass

## Messenger on Codex

Evidence: [`messages-live-run/codex-messenger.txt`](messages-live-run/codex-messenger.txt).

```
tool=shell cmd=/bin/zsh -lc 'cat .sdlc/messages/AGENTS.md'
tool=command_execution sub=sdlc-messenger-l1
tool=shell cmd=/bin/zsh -lc 'cat .sdlc/messages/read/codex/20261001T095749608843Z-probe-live-probe.md'
state=new 2026-10-01T09:57:49.631881Z
state=read 2026-10-01T09:58:01.672932Z
state=done 2026-10-01T09:58:21.739482Z
messenger_spawned=yes
send_time=2026-10-01T09:57:49.608843Z read_time=2026-10-01T09:58:01.082544Z ack_time=2026-10-01T09:58:21.576250Z outcome=Replied with the answer: 2 + 3 = 5. reply=20261001T095816747578Z-codex-live-probe
result=pass
```

The probe's `sub=sdlc-messenger-l1` line does not prove the spawn here. It came from the output of `cat .sdlc/messages/AGENTS.md`, which names the agent. The `codex exec --json` stream had no `spawn_agent` item, only two `collab_tool_call` items with `tool: wait` and empty `receiver_thread_ids`. The rollout files prove the spawn:

- Parent, thread `01a0f6e5-c982-7c11-856e-5644039e7730`: `spawn_agent {"task_name":"messenger","agent_type":"sdlc-messenger-l1",...}`, `wait_agent`, `cat` of the claimed file, `followup_task` to `messenger`, `wait_agent`.
- Subagent, thread `01a0f6e5-fb54-7381-bb3c-38524818899e`: `session_meta` has `agent_role: sdlc-messenger-l1` and `parent_thread_id` equal to the parent's thread, and `turn_context` records `gpt-5.6-terra` `low`. It ran `count --receiver codex`, `list --receiver codex --state new`, and `read <id> --receiver codex`, and reported the id and `read/codex/<id>.md`. After the parent's follow-up it ran `reply <id> '2 + 3 = 5.'` and `ack <id> --outcome 'Replied with the answer: 2 + 3 = 5.'`, and said it used the text the parent supplied.

The parent's spawn and follow-up messages are encrypted in the rollout, so their text was not read.

Result: pass

## Negative control

Evidence: [`messages-live-run/claude-defect.txt`](messages-live-run/claude-defect.txt), from `probe.py claude --defect`.

```
isolation=yes skills=0 slash_commands=0 sdlc_agents=0 skill_calls=0
tool=Read sub=- in_subagent=no cmd=-
tool=Read sub=- in_subagent=no cmd=-
tool=Bash sub=- in_subagent=no cmd=mkdir -p .sdlc/messages/done/claude && mv .sdlc/messages/new/claude/20261001T095443300871Z-probe-live-probe.md .sdlc/messages/done/claude/
state=new 2026-10-01T09:54:43.323873Z
state=done 2026-10-01T09:54:49.347600Z
send_time=2026-10-01T09:54:43.300871Z read_time=- ack_time=- outcome=- reply=none
result=fail reason=empty read_time, ack_time; no reply with topic live-probe and re 20261001T095443300871Z-probe-live-probe
```

The role read the message and the injected `.sdlc/messages/AGENTS.md`, ran the injected `mv`, and answered "2 + 3 = 5" only in its final text. The message reached `done/claude/` with no `read_time`, no `ack_time`, and no reply, and the probe exited 1. The same isolated role passed with the generated files, so the entry files carried the procedure.

Result: pass

## Limits

- One trial per arm, on one machine and one account per host. The negative control ran on Claude Code only.
- The Claude Code path-only arm ran in safe mode, which also turns off `CLAUDE.md` loading, so nested `CLAUDE.md` loading (the mailbox `CLAUDE.md` files that import `AGENTS.md`) was not exercised there. The role reached the procedures through the message's `protocol:` line.
- A conductor session cannot spawn the messenger: the plugin's `block-role-spawn.sh` hook denies every `sdlc-lite:` agent spawn from a session running `sdlc-lite:conductor`. The Claude messenger arm ran without `--agent`, so it was not a conductor session.
- No arm was unverified.
- On Codex, the probe's spawn check is vacuous for this prompt. It prints a `sub=sdlc-messenger-l1` line for any non-message item whose JSON names the agent, and the parent prompt makes the parent print `.sdlc/messages/AGENTS.md`, which names it. So `messenger_spawned=yes` would print with no spawn. This run's spawn rests on the rollout files quoted above, and a rerun needs the same rollout check.
- On Claude Code, two of the three messenger spawns returned with a Monitor armed and no claim. Only the parent's spawn-again loop reached the claim. A parent that stops at the first report would miss the message.
- The Claude Code path-only role ran `read`, `reply`, and `ack` in one shell call, so the 2-second sampler saw no `read` state there. The path-only oracle relies on the stamps, not the state lines.
