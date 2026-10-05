## Task goal
A harness that reads `.sdlc/*` learns the ticket and message folder systems from the entry files alone, and a fresh Claude role and a fresh Codex role, given only a path to a message file and no skill, ack it and reply correctly.

## Step 3: Isolated live runs on Claude Code and Codex, messenger runs, and the validation doc
level: L4
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: steps 1 and 2.

Create:
- `docs/reports/messages-live-run/probe.py` (Python 3, standard library)
- `docs/reports/messages-live-run/defect-AGENTS.md`
- the evidence files listed under Runs to record
- `docs/reports/messages-live-run.md`, linked from `docs/README.md`

Edit `plugins/sdlc-lite/scripts/messages.py` only if a run shows the entry files are wrong or unclear. In that case keep its selftest green and rerun every arm.

**`probe.py` interface**
- Usage: `python3 probe.py <claude|codex|claude-messenger|codex-messenger> [--defect] [--timeout SECONDS]` and `python3 probe.py selftest`. `--defect` is accepted only with `claude` or `codex`.
- The plugin is `Path(__file__).resolve().parents[3] / 'plugins' / 'sdlc-lite'`, this worktree's built copy. The probe never runs `run.sh`.
- Every host process gets a copy of the environment with these removed: `CLAUDECODE`, `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA`, and every name starting with `CLAUDE_CODE_` or `SDLC_`. This is the scrub of the `W` wrapper in docs/reports/plan-reviewer-live-run.md, plus the plugin root, so no role inherits a path to the plugin.

**Setup** (exit 2 on any failure)
- `tempfile.mkdtemp(prefix='messages-live-')`, project `<tmp>/project`, `git init -q`, and one empty commit made with `-c user.name=probe -c user.email=probe@example.invalid -c commit.gpgsign=false`.
- `python3 <plugin>/scripts/tickets.py --root .sdlc roadmap` in the project. This is the step 2 writer: it writes the router and the mailbox entry files, so they exist before any message.
- `codex-messenger` also runs `python3 <plugin>/scripts/codex_roles.py install <project>`.
- The project is kept and its path printed, so the evidence can be inspected.

**Message**: from the project root, `python3 <plugin>/scripts/messages.py send --receiver <host> --sender probe --topic live-probe --follow-up true "What is 2 + 3? Answer in one line."`, where `<host>` is `claude` or `codex`.
- Path-only arms send before launching the host, because the path goes into the prompt.
- Messenger arms launch the host first and send 20 seconds later, so the messenger's polling is exercised.

**`--defect`** (the injected wrong command)
- After the send, overwrite each generated `AGENTS.md` (mailbox root, `new/`, `read/`, `done/`) with the bytes of `defect-AGENTS.md`.
- The fixture is titled `# Mailbox`. It tells the reader to handle a message by printing it with `cat <path>` and moving it with `mkdir -p .sdlc/messages/done/<receiver> && mv <path> .sdlc/messages/done/<receiver>/`, and says no reply and no script are needed.
- These wrong commands exit 0. A role that follows the entry file therefore leaves no `read_time`, no `ack_time`, and no reply, and the oracle fails.

**Arms** (exact flags; cwd is the project)
- `claude`: `claude -p --safe-mode --disable-slash-commands --dangerously-skip-permissions --model sonnet --effort medium --output-format stream-json --verbose --no-session-persistence -- "Handle the message at <absolute message path>."`
  - Plan-time probes on Claude Code 2.1.286, with `--safe-mode --disable-slash-commands`: the init event had `skills: []`, `slash_commands: []`, agents only `claude`, `Explore`, `general-purpose`, `Plan`, and `mcp_servers: []`, and Bash ran.
  - `--disable-slash-commands` alone still listed the installed sdlc-lite 0.20.1 agents.
  - Safe mode also disables `CLAUDE.md` loading, so the role reaches the procedures only through the message's `protocol:` line, as the Codex role does.
- `codex`: `codex exec --ignore-user-config --json --color never -C <project> -m gpt-6.1-sol -c model_reasoning_effort="medium" -c approval_policy="never" --sandbox workspace-write "Handle the message at <absolute message path>."`
  - `--ignore-user-config` skips `$CODEX_HOME/config.toml`, which is where `[plugins."sdlc-lite@sdlc-lite"] enabled = true` lives on this host. Auth still uses `CODEX_HOME`.
  - `gpt-6.1-sol` is the config default and completed a live probe (docs/reports/codex-account-models-2026-09-30.md).
- Codex isolation proof, run before the `codex` arm:
  - Two control calls: `codex exec --json --color never --sandbox read-only -C <project> -m gpt-6-luna -c model_reasoning_effort="low" "Reply with exactly OK. Do not call tools."`, one with `--ignore-user-config` and one without.
  - For each, read `thread_id` from the `thread.started` event. Find `$CODEX_HOME/sessions/**/rollout-*<thread_id>*.jsonl` (`CODEX_HOME` defaults to `~/.codex`) and count occurrences of `sdlc-lite`.
  - A plan-time probe on codex-cli 0.159.2 counted 0 with `--ignore-user-config` and 2 without.
- `claude-messenger`: `claude -p --plugin-dir <plugin> --dangerously-skip-permissions --model sonnet --effort medium --output-format stream-json --verbose --no-session-persistence -- "<Claude parent prompt>"`.
  - A plan-time probe showed that `--plugin-dir` with this worktree's plugin lists `sdlc-lite:messenger` in the init `agents`. The cached 0.20.1 copy has no messenger and is replaced.
  - A plan-time probe also showed that a `sleep` loop runs in headless `claude -p`.
- `codex-messenger`: `codex exec --json --color never -C <project> -m gpt-6.1-sol -c model_reasoning_effort="medium" -c agents.enabled=true -c approval_policy="never" --sandbox workspace-write "<Codex parent prompt>"`. This mirrors the runner's conductor launch (codex_exec.py:39-50: install the project agents, then `agents.enabled=true`).
- Claude parent prompt, exactly: `This repository has a mailbox, and its procedures are in .sdlc/messages/AGENTS.md. Read that file. Spawn the sdlc-lite:messenger agent in the foreground, not in the background, with the prompt "harness: claude", and wait for its report; spawn it again until a report names a claimed message. Handle each claimed message as .sdlc/messages/AGENTS.md says: reply when follow_up_requested is true, then ack it. Then stop.`
- Codex parent prompt, exactly: `This repository has a mailbox, and its procedures are in .sdlc/messages/AGENTS.md. Read that file. Spawn the sdlc-messenger-l1 agent with the prompt "harness: codex" and wait for its report; spawn it again until a report names a claimed message. Handle each claimed message as .sdlc/messages/AGENTS.md says: reply when follow_up_requested is true, then ack it. Then stop.`
- Timeouts: 600 s for path-only arms and 900 s for messenger arms, unless `--timeout` is given. On timeout, kill the host's process group.

**Output** (stdout, one `key=value` per line, in this order)
- `arm=`, `project=`, `plugin=`, `message=` (the message path).
- Path-only arms, the isolation line:
  - Claude: exactly `isolation=yes skills=0 slash_commands=0 sdlc_agents=0 skill_calls=0` when the init event's `skills` and `slash_commands` are empty, no `agents` entry starts with `sdlc-lite:`, and no tool_use is named `Skill`. Otherwise `isolation=no` with the four counts.
  - Codex: exactly `isolation=yes ignore_config_sdlc_mentions=0 with_config_sdlc_mentions=<n>` when the ignore-config count is 0. Otherwise `isolation=no` with both counts.
- Trace lines:
  - Claude, one per tool_use: `tool=<name> sub=<subagent_type or -> in_subagent=<yes|no> cmd=<first 160 characters of the Bash command, or ->`. `in_subagent` is yes when the event has a `parent_tool_use_id`.
  - Codex, one per `command_execution` item: `tool=shell cmd=<first 160 characters>`.
  - Codex, one per item that is neither `agent_message` nor `reasoning` and whose JSON holds `sdlc-messenger-l1`: `tool=<item type> sub=sdlc-messenger-l1`.
- `state=<new|read|done> <UTC time>`: a sampler thread checks the mailbox every 2 seconds and prints a line the first time it sees the message in each state folder.
- Messenger arms: `messenger_spawned=yes|no`. For Claude, yes when a tool_use named `Agent` or `Task` has `subagent_type` `sdlc-lite:messenger`. For Codex, yes when a `tool=<item type> sub=sdlc-messenger-l1` line was printed.
- `send_time=<v> read_time=<v> ack_time=<v> outcome=<v> reply=<id or none>`, read from the files with the probe's own parser, not `messages.py`.
- Last line: `result=pass`, `result=fail reason=<text>`, or `result=unverified reason=<text>`.

**Oracle**: pass only when all of these hold:
- the message is only in `done/<host>/`;
- `send_time`, `read_time`, and `ack_time` are non-empty and `send_time <= read_time <= ack_time`;
- the outcome is not `expired` or `expired, no reply`;
- some file in `new/probe/`, `read/probe/`, or `done/probe/` has `topic: live-probe` and `re: <id>`;
- path-only arms have `isolation=yes` (else `result=fail reason=not isolated`);
- messenger arms have `messenger_spawned=yes` and the state lines new, read, done in that order.

**Exit codes**
- 0: pass.
- 1: fail. An oracle miss, an isolation miss, or a timeout after the host made a tool call.
- 2: setup error.
- 3: unverified. The host CLI is not on PATH; a Codex control call exits non-zero; the host exits non-zero before any tool call (auth or model failure); the `claude-messenger` init lacks `sdlc-lite:messenger`; or `codex-messenger` printed no `sub=sdlc-messenger-l1` line (`reason=no native subagent spawn observed`).

**`selftest`** (offline, no model call; exit 0 only when every verdict matches): a temp project set up as above, then these cases through the real CLI:
- (a) read, reply, ack gives pass;
- (b) read only gives fail;
- (c) the defect flow (`mv` into `done/`) gives fail;
- (d) the Claude isolation parser on two synthetic init events, one with `skills: ["sdlc-lite:chain"]`, gives no, then yes;
- (e) the Codex rollout counter on two synthetic rollout files gives 0 and 2.

It prints `ok: <case>` per case and `probe selftest: PASS`.

**Runs to record**, each saved with `| tee`:
- `python3 docs/reports/messages-live-run/probe.py <arm>` into `docs/reports/messages-live-run/<arm>.txt`, for each of `claude`, `codex`, `claude-messenger`, and `codex-messenger`.
- `python3 docs/reports/messages-live-run/probe.py claude --defect` into `docs/reports/messages-live-run/claude-defect.txt`.

**`docs/reports/messages-live-run.md`**
- Title `# Messages live run`, then a line `Recorded: <YYYY-MM-DD>`.
- These exact `##` sections: `## Environment`, `## Method`, `## Claude Code, path only`, `## Codex, path only`, `## Messenger on Claude Code`, `## Messenger on Codex`, `## Negative control`, `## Limits`.
- Environment: `claude --version`, `codex --version`, the models used, the plugin commit (`git rev-parse --short HEAD`), and whether `plugins/` had uncommitted changes.
- Method: setup, the exact prompts and flags, the oracle, and how isolation was proved per host.
- Each of the five arm sections quotes its evidence lines (isolation, state, oracle, result) and has one line starting `Result: `. That line is `Result: pass`, `Result: fail`, or `Result: unverified: <reason>`.
  - `## Claude Code, path only` and `## Messenger on Claude Code` must read `Result: pass`.
  - `## Negative control` reads `Result: pass` when the defect run printed `result=fail`.
- Limits:
  - one trial per arm on one machine;
  - the Claude path-only arm ran in safe mode, so nested `CLAUDE.md` loading was not exercised there;
  - a conductor session cannot spawn the messenger (`block-role-spawn.sh`);
  - every unverified arm, with its reason.

**`docs/README.md`**: after the `Ticket root and router live run` line, add `- [Messages live run](validation/messages-live-run.md): dated live run for T-0179 showing that a fresh Claude Code role and a fresh Codex role, given only a message path and no skill, read, reply, and ack from the entry files alone, with the messenger on both hosts and a negative control.`

No em dashes in any file. The live model calls are this step's runtime evidence. An arm that cannot run is recorded as unverified with its reason, never faked.
### Acceptance criteria
- `python3 docs/reports/messages-live-run/probe.py selftest`
- `python3 docs/reports/messages-live-run/probe.py claude`
- `out=$(python3 docs/reports/messages-live-run/probe.py claude --defect); rc=$?; test "$rc" -eq 1 && printf "%s\n" "$out" | grep -q "^result=fail"`
- `python3 docs/reports/messages-live-run/probe.py codex; rc=$?; test "$rc" -eq 0 -o "$rc" -eq 3`
- `d=docs/reports/messages-live-run && grep -qx "result=pass" "$d/claude.txt" && grep -q "^result=fail" "$d/claude-defect.txt" && grep -qE "^result=(pass|unverified)" "$d/codex.txt" && grep -qE "^result=(pass|unverified)" "$d/codex-messenger.txt"`
- `f=docs/reports/messages-live-run/claude-messenger.txt && grep -qx "result=pass" "$f" && grep -qx "messenger_spawned=yes" "$f" && awk '/^state=new /{n=NR} /^state=read /{r=NR} /^state=done /{d=NR} END{exit !(n && r && d && n < r && r < d)}' "$f"`
- `d=docs/reports/messages-live-run && grep -qx "isolation=yes skills=0 slash_commands=0 sdlc_agents=0 skill_calls=0" "$d/claude.txt" && awk '/^result=unverified/{u=1} /^isolation=yes ignore_config_sdlc_mentions=0 /{i=1} END{exit !(u || i)}' "$d/codex.txt"`
- `f=docs/reports/messages-live-run.md && grep -qE "^Recorded: 20[0-9]{2}-[0-9]{2}-[0-9]{2}" "$f" && for h in "## Environment" "## Method" "## Claude Code, path only" "## Codex, path only" "## Messenger on Claude Code" "## Messenger on Codex" "## Negative control" "## Limits"; do grep -qxF -- "$h" "$f" || exit 1; done`
- `python3 -c "import re; t = open('docs/reports/messages-live-run.md').read(); parts = re.split(r'(?m)^## ', t); secs = {p.split(chr(10), 1)[0]: p for p in parts[1:]}; need = {'Claude Code, path only': 'Result: pass', 'Codex, path only': 'Result: ', 'Messenger on Claude Code': 'Result: pass', 'Messenger on Codex': 'Result: ', 'Negative control': 'Result: pass'}; bad = [k for k, v in need.items() if not re.search('(?m)^' + re.escape(v), secs.get(k, ''))]; assert not bad, bad"`
- `grep -qF "(validation/messages-live-run.md)" docs/README.md`
- `d=docs/reports/messages-live-run && test -f "$d/probe.py" && ! grep -rqF "$(printf '\342\200\224')" "$d" docs/reports/messages-live-run.md`
- (guard) `python3 plugins/sdlc-lite/scripts/messages.py selftest`
- (guard) `git diff "$SDLC_BASE_SHA" -- plugins/sdlc-lite/scripts/messages.py docs/README.md | grep '^+' | { ! grep -qF "$(printf '\342\200\224')"; }`
- (guard) `{ git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxE "plugins/sdlc-lite/scripts/(messages|tickets)\.py|plugins/sdlc-lite/skills/ticket/SKILL\.md|docs/README\.md|docs/reports/messages-live-run\.md|docs/reports/messages-live-run/.*" | { ! grep -q .; }`
