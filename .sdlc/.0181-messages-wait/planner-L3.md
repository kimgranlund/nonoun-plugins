<!-- role=planner level=L3 model=opus effort=xhigh -->
## Goal
Add `messages.py wait`, one blocking call that returns as soon as a valid message sits in `new/<receiver>/` and never claims, moves, writes, or prints a body; cover it in the entry files, the messenger agent, and the docs; and record a live proof on Claude Code and Codex.

## Step 1: messages.py wait subcommand and its selftest cases
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Targets: `plugins/sdlc-lite/scripts/messages.py` only. Depends on: none. The system `python3` is 3.9.6, so use no syntax newer than Python 3.9.

1. Add `cmd_wait(a)`, register it in `COMMANDS`, and add a `wait` subparser to `parser()` right after `count`.
   - Subparser: `allow_abbrev=False`, help `block until a message is in new/<receiver>/; never claims it`.
   - Flags: `--receiver NAME` (help `required: the receiver`), `--timeout SECONDS` (help `give up after this many seconds: an integer from 1 to 600 (default 120)`), `--interval SECONDS` (help `check this often, in seconds: an integer of at least 1 (default 5)`).
   - Parse `--timeout` and `--interval` as strings (`default=None`, no `type=`). An argparse `type=int` makes a non-integer a usage error (exit 2), and the handoff requires exit 1.
2. Validate in this order. Each failure raises `Refuse`: exit 1, one `messages.py: <reason>` stderr line, nothing on stdout, nothing written.
   - The receiver goes through `arg_name(a.receiver, '--receiver')`.
   - The timeout (default `'120'`) must fullmatch `[0-9]{1,9}` and lie from 1 to 600. Otherwise the reason is `--timeout must be an integer from 1 to 600: <short(value)>`.
   - The interval (default `'5'`) must fullmatch `[0-9]{1,9}` and be at least 1. Otherwise the reason is `--interval must be an integer of at least 1: <short(value)>`.
   - The 9-digit cap copies `TTL_RE` (messages.py:181) and keeps `int()` under Python 3.11's digit limit. There is no other interval maximum, because each sleep is `min(interval, time left)`.
3. Add a helper `wait_ready(mbox, receiver)`. It returns a list, sorted by id, of `(mid, path)`, with `path = msg_path(mbox, 'new', receiver, mid)`, for each `mid` in `message_ids(os.path.join(mbox, 'new', receiver))` whose `load_or_none(path, 'new', receiver)` is not None.
   - It catches `Refuse` per file and skips that file, so a malformed file never wakes a waiter and never makes `wait` exit 1. Evidence: `load` raises `Refuse` on an invalid file (messages.py:413-420). Reusing `load_or_none` bare, as `count` does, would make `wait` exit 1 (`case_malformed` asserts that `count` refuses). Handoff case 5 says `wait` ignores the file.
   - `path` is never passed through `realpath`, so it equals the path `send` prints for the same mailbox. `mailbox()` makes the path absolute and does not resolve symlinks (messages.py:443-456), and a macOS `mktemp -d` path is a symlink.
   - `count` itself is not changed (a non-goal).
4. `cmd_wait` holds exactly one line with the literal text `ready = wait_ready(mbox, receiver)`, inside its loop. The negative control patches that anchor. It works on a `time.monotonic()` deadline:
   - It checks at once, before any sleep. When `ready` is non-empty, it calls `emit` with one `<id>\t<path>\n` line per entry, in the sorted order, and returns 0.
   - Otherwise, once the deadline has passed, it calls `emit('no new messages\n')` and returns 3. Otherwise it runs `time.sleep(min(interval, remaining))` and loops.
   - A missing mailbox creates nothing. `wait` never calls `claim`, `write_entries`, `deliver`, `write_replace`, or `Lock`, and never prints front matter or a body.
   - `main` already returns the command's code, so exit 3 needs no other change.
5. Update the module docstring:
   - Usage: add `messages.py [--root DIR] wait --receiver NAME [--timeout SECONDS] [--interval SECONDS]` after the `count` line.
   - The exit paragraph: add `Exit 3 only when wait times out.`
   - Commands: add a `wait` entry after `count`. It checks new/<receiver>/ every --interval seconds (default 5, at least 1) for up to --timeout seconds (default 120, 1 to 600). It prints `<id>\t<absolute path>` per valid message, sorted by id, and exits 0. At the timeout it prints `no new messages` and exits 3. It skips an invalid file. It never claims, moves, writes, stamps, or prints a body.
   - The sentence "Every subcommand validates every message file it opens or counts" names `wait` as the one subcommand that skips an invalid file instead of exiting 1.
   - The Layout sentence "list, count, and expire on a missing mailbox create nothing" includes `wait`.
   - The `add_subparsers` metavar becomes `{send,list,read,ack,reply,expire,count,wait,selftest}`.
6. Add seven selftest functions in the existing `Harness`/`Box` style. Append them to `SELFTEST_CASES` with exactly these labels. Use timeouts of 1 to 3 seconds, except case 2's 10, and kill any child process still running in a `finally`.
   1. `wait: a present message returns at once, state unchanged`
      - Factor the body into `st_wait_present(h)`, which raises `SelftestFail`.
      - Send, take `b.snap()`, then run `wait --receiver bob --interval 5 --timeout 3`.
      - Assert: exit 0 in under 2 s; stdout exactly `<id>\t<path>\n`, with the path `send` printed; `b.snap()` equal to the snapshot, else fail with `wait changed the mailbox`; the file only in new/bob, with an empty `read_time`.
   2. `wait: wakes on a message sent mid-wait`
      - Start `subprocess.Popen` on `wait --receiver bob --timeout 10 --interval 1`, sleep about 1.5 s, then `b.send`.
      - Assert it exits 0 before the 10 s timeout and the first tab-separated field of its stdout is the sent id.
   3. `wait: timeout exits 3, state unchanged`
      - On a box holding a message for carol only, run `wait --receiver bob --timeout 1 --interval 1`.
      - Assert exit 3, stdout exactly `no new messages\n`, and `b.snap()` unchanged.
   4. `refused: wait with a bad receiver, timeout, or interval`
      - Call `b.refused` with `--receiver Bob`, `--timeout 601`, `--timeout 0`, `--timeout 1.5`, `--interval abc`, and `--interval 0`.
   5. `wait: ignores a malformed file and another receiver`
      - Use `b.put` to put `b'not a message\n'` in new/bob under the id `20260101T000000000000Z-alice-garbage`, and send a valid message to carol.
      - Assert exit 3 with `no new messages`.
      - Then send to bob, run `wait` again, and assert stdout is exactly that one id line, without the garbage id.
   6. `wait: never prints a body`
      - Send a body holding a unique marker. Assert that neither stdout nor stderr of `wait` holds it.
   7. `wait: a claiming wait is caught`
      - Build the anchor string from two pieces (for example `'ready = wait_' + 'ready(mbox, receiver)'`), so that this file's source holds the anchor text only in `cmd_wait`. Assert the anchor occurs exactly once in the source.
      - Create a fresh folder under `h.tmp` and write the source there as `messages.py`, with the anchor replaced. The replacement is the anchor plus, on the same line after `; `, a list comprehension that calls, for each `(m, p)` in `ready`, `os.makedirs(os.path.join(mbox, 'read', receiver), exist_ok=True)` and `claim(p, msg_path(mbox, 'read', receiver, m))`. Keeping it on one line keeps the indentation valid.
      - Build a second `Harness` on its own fresh subfolder of `h.tmp`, created first, so its `repo-<n>` folders cannot collide with `h`'s. Set its `me` to the patched copy and run `st_wait_present` on it. Assert it raises `SelftestFail`; a normal return fails the case.

Focused check: `python3 plugins/sdlc-lite/scripts/messages.py selftest`.

Contract dependents:
- `case_entry_parses` pins the set of subcommands the entry files run (messages.py:1729). This step leaves `ENTRY_TEMPLATE` unchanged, so `want` stays correct. Step 2 changes both together.
- `run.sh` calls only `count` (run.sh:236), which is unchanged.
### Acceptance criteria
- `out=$(python3 plugins/sdlc-lite/scripts/messages.py selftest) && printf "%s\n" "$out" | grep -qxF "messages selftest: PASS" && for l in "wait: a present message returns at once, state unchanged" "wait: wakes on a message sent mid-wait" "wait: timeout exits 3, state unchanged" "refused: wait with a bad receiver, timeout, or interval" "wait: ignores a malformed file and another receiver" "wait: never prints a body" "wait: a claiming wait is caught"; do printf "%s\n" "$out" | grep -qxF "ok: $l" || exit 1; done`
- `S=plugins/sdlc-lite/scripts/messages.py; d=$(mktemp -d) && p=$(python3 $S --root "$d" send --receiver bob --sender alice --topic t --follow-up false hi) && id=$(basename "$p" .md) && before=$(cat "$p") && s=$SECONDS && out=$(python3 $S --root "$d" wait --receiver bob --interval 5 --timeout 10) && test $((SECONDS - s)) -lt 3 && test "$out" = "$(printf "%s\t%s" "$id" "$p")" && test "$(cat "$p")" = "$before"`
- `S=plugins/sdlc-lite/scripts/messages.py; d=$(mktemp -d); out=$(python3 $S --root "$d" wait --receiver bob --timeout 1 --interval 1); rc=$?; test "$rc" -eq 3 && test "$out" = "no new messages" && test -z "$(ls -A "$d")"`
- `S=plugins/sdlc-lite/scripts/messages.py; d=$(mktemp -d); e=$(mktemp); for a in "--receiver Bob" "--receiver bob --timeout 601" "--receiver bob --timeout 0" "--receiver bob --timeout 1.5" "--receiver bob --interval abc" "--receiver bob --interval 0"; do out=$(python3 $S --root "$d" wait $a 2>"$e"); rc=$?; test "$rc" -eq 1 || exit 1; test -z "$out" || exit 1; grep -q "^messages.py: " "$e" || exit 1; done; test -z "$(ls -A "$d")"`
- `S=plugins/sdlc-lite/scripts/messages.py; d=$(mktemp -d) && mkdir -p "$d/messages/new/bob" && printf "not a message\n" > "$d/messages/new/bob/20260101T000000000000Z-alice-garbage.md" && python3 $S --root "$d" send --receiver carol --sender alice --topic t --follow-up false hi >/dev/null && out=$(python3 $S --root "$d" wait --receiver bob --timeout 2 --interval 1); rc=$?; test "$rc" -eq 3 && test "$out" = "no new messages"`
- `h=$(python3 plugins/sdlc-lite/scripts/messages.py wait --help) && printf "%s\n" "$h" | grep -qF -- "--timeout" && printf "%s\n" "$h" | grep -qF -- "--interval"`
- `grep -qF "wait --receiver NAME [--timeout SECONDS] [--interval SECONDS]" plugins/sdlc-lite/scripts/messages.py`
- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF plugins/sdlc-lite/scripts/messages.py)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vxF plugins/sdlc-lite/scripts/messages.py)"`

## Step 2: Entry files, messenger agent, Codex agent, and docs cover wait
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: step 1 (the `wait` subparser must exist for `case_entry_parses` to pass).

1. `ENTRY_TEMPLATE` in `plugins/sdlc-lite/scripts/messages.py`:
   - Read section: add a sentence with the code span `python3 "{{scripts}}/messages.py" wait --receiver <name> --timeout <seconds> --interval <seconds>`. It says that `wait` blocks until a message is in `new/<name>/`, prints the id and the absolute path per message (the id is the first tab-separated field), exits 3 with `no new messages` at the timeout, and never claims, so each message is then claimed with `read`.
   - Messenger section: add a paragraph after the first one, with the code span `python3 "{{scripts}}/messages.py" wait --receiver <harness> --timeout 100 --interval 10`.
     - It says that `wait` is the cheaper alternative to a polling subagent while the parent is active: the messenger may run it in its loop, or the parent may skip the messenger and run it itself.
     - It says that `wait` returns only into an active parent and does not wake an idle host.
     - It says that `--timeout 100` stays under Claude Code's default 120-second Bash limit, because Claude Code moves a foreground Bash call to the background once it passes its timeout (run.sh:69-70).
     - The entry file is consumer-facing, so it names no ticket id.
   - In the first Messenger sentence, the parenthetical that now names `count`, then `list` and `read` becomes: `wait`, or `count` then `list`, then `read` (command names in backticks, as now).
   - Add no heading, so `ST_HEADINGS` (messages.py:1629) stays unchanged. Leave the Host limits section unchanged.
2. In `case_entry_parses`, add `'wait'` to `want` (messages.py:1729). This is the contract dependent of the template change, because it pins the subcommands the entry files run. `tickets.py roadmap` writes the same template through `messages.write_entries` (tickets.py:846). Its selftest pins only file presence and restore (tickets.py:3594-3623), so it needs no edit; it runs here as a guard.
3. `plugins/sdlc-lite/agents/messenger.md`:
   - Rewrite the Loop list as:
     1. Run `messages.py wait --receiver <harness> --timeout 100 --interval 10`. Exit 3 means nothing arrived: run it again.
     2. Claim each message `wait` printed with `messages.py read <id> --receiver <harness>`, where `<id>` is the first tab-separated field of its line.
     3. The report item, unchanged.
   - After the list, add one sentence: the parent may skip the messenger and run `wait` itself.
   - In the Host limits Claude Code bullet, add that `wait` is one foreground Bash call and needs no Monitor.
   - Keep the three words `MESSENGER_WORDS` pins (check.py:368): `model: claude-haiku-4-5`, `messages.py`, and `.sdlc/messages/AGENTS.md`.
4. Run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` to regenerate `plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml`. Never edit it by hand.
5. `docs/maintenance/sdlc-internals.md`, the `scripts/messages.py` entry (line 15):
   - In the Subcommands list, between the `count` item and `and selftest`, add a `wait` item. It says: `wait` blocks until a valid message is in `new/<receiver>/`, checking every `--interval` seconds (default 5, at least 1) for up to `--timeout` seconds (default 120, 1 to 600); it prints `<id>\t<absolute path>` per message, sorted by id, and exits 0; at the timeout it prints `no new messages` and exits 3; it skips an invalid file; it never claims, moves, writes, or prints a body.
   - After "exit 2 only for a usage error", add "; exit 3 only when `wait` times out".
   - In the selftest coverage sentence, after "one shared mailbox across worktrees", add this text: "the `wait` cases (a present message returns at once with the mailbox unchanged, a message sent mid-wait wakes it, the timeout exits 3 with the mailbox unchanged, bad values are refused, a malformed file and another receiver's message do not wake it, no body is printed, and a claiming wait is caught as a negative control)".
6. `docs/ticket-stages/design.md`:
   - In the Host limits bullet (line 105), add that `messages.py wait` is one blocking call a parent can make instead of running a polling subagent, and that it still does not wake an idle host.
   - In the Status paragraph (line 77), add a sentence that T-0181 built `messages.py wait`.
7. Left unchanged on purpose:
   - `docs/codex-role-execution.md:27`: the messenger still polls every 10 seconds through `messages.py` (now inside `wait`), and its host limits still hold. The handoff does not list it.
   - `docs/ticket-stages/README.md:3`: it lists the tickets that built the bus; the design Status paragraph records T-0181.
   - `docs/reports/messages-live-run/probe.py`: it pins no entry-file text, and its selftest passes now.

Focused checks: the messages selftest, the tickets selftest, and `codex_roles.py generate --check`.
### Acceptance criteria
- `python3 -c 'import sys; sys.path.insert(0, "plugins/sdlc-lite/scripts"); import messages; t = messages.ENTRY_TEMPLATE; r = t.split("\n## Read\n", 1)[1].split("\n## ", 1)[0]; m = t.split("\n## Messenger\n", 1)[1].split("\n## ", 1)[0]; assert "messages.py\" wait --receiver" in r, "read"; assert "messages.py\" wait --receiver" in m, "messenger"; assert "idle" in m, "idle"'`
- (guard) `python3 plugins/sdlc-lite/scripts/messages.py selftest | grep -qxF "messages selftest: PASS"`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`
- `grep -qF "messages.py wait --receiver <harness>" plugins/sdlc-lite/agents/messenger.md`
- `grep -qF "messages.py wait --receiver <harness>" plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `grep -qF "no new messages" docs/maintenance/sdlc-internals.md`
- `grep -qF "a claiming wait is caught" docs/maintenance/sdlc-internals.md`
- `grep -qF "messages.py wait" docs/ticket-stages/design.md`
- `grep -qF "T-0181" docs/ticket-stages/design.md`
- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e plugins/sdlc-lite/scripts/messages.py -e plugins/sdlc-lite/agents/messenger.md -e plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml -e docs/maintenance/sdlc-internals.md -e docs/ticket-stages/design.md)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc")"`

## Step 3: Live proof of wait on Claude Code and Codex
level: L3
### Do
Depends on: steps 1 and 2.

1. Create the probe `docs/reports/messages-wait-live-run/probe.py`, modelled on `docs/reports/messages-live-run/probe.py`. First read that probe's docstring, `clean_env`, `setup`, `send`, `Sampler`, `oracle`, `ClaudeTrace`, `CodexTrace`, `codex_isolation`, `run_host`, and `selftest`. Reuse its setup and the same isolation:
   - setup: a temp project, `git init`, one empty commit, then `tickets.py --root .sdlc roadmap`;
   - an environment without `CLAUDECODE`, `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA`, `CLAUDE_CODE_*`, and `SDLC_*`;
     - It also drops `BASH_DEFAULT_TIMEOUT_MS` and `BASH_MAX_TIMEOUT_MS`, so the Claude host runs with its default Bash limits.
     - Evidence: run.sh passes both as 3600000 to every role it launches (run.sh:67-70), so a builder's child process would otherwise inherit them.
   - Claude `--safe-mode --disable-slash-commands`;
   - Codex `--ignore-user-config`, plus the two control calls;
   - the 2-second state sampler and the probe's own message parser;
   - Python 3.9 syntax only (the system `python3` is 3.9.6).
2. The probe has the arms `claude` and `codex`, plus `selftest`.
   - The prompt, with `<harness>` set to `claude` or `codex` and `<plugin>` set to the absolute plugin path: `Run this as one shell command and wait for it to finish: python3 <plugin>/scripts/messages.py wait --receiver <harness> --timeout 120 --interval 2. If your shell tool takes a timeout, give it at least 130 seconds. When it prints a message id, handle that message as .sdlc/messages/AGENTS.md says: claim it with read, reply when follow_up_requested is true, then ack it. Then stop.`
   - The timeout sentence is in the prompt for two reasons: a shell tool that ends the call before `wait` returns forces a second call, and no record here settles Codex's default shell-tool timeout.
   - The host starts first. The probe sends the message 20 seconds after launch, through the `delayed` hook of `run_host`: `--receiver <harness> --sender probe --topic live-probe --follow-up true "What is 2 + 3? Answer in one line."`.
   - Claude command: `claude -p --safe-mode --disable-slash-commands --dangerously-skip-permissions --model sonnet --effort low --output-format stream-json --verbose --no-session-persistence -- "<prompt>"`.
   - Codex command: `codex exec --ignore-user-config --json --color never -C <project> -m gpt-6.1-sol -c model_reasoning_effort="medium" -c approval_policy="never" --sandbox workspace-write "<prompt>"`. This is the model and effort of the path-only arm in `docs/reports/messages-live-run.md` (its lines 13 and 41).
3. From the host's own stream, the probe derives four values:
   - `wait_calls`: shell calls whose command runs `messages.py` with the subcommand `wait`, each occurrence counted. The subcommand is the first word after the `messages.py` token, skipping `--root DIR`.
   - `poll_calls`: shell calls that run `messages.py count`, `messages.py list`, or `sleep`, plus Claude `Monitor`, `BashOutput`, and `TaskOutput` tool calls.
   - `wait_returned`: the id printed in the wait call's own output, or `-`.
     - On Claude it comes from the `tool_result` block, in a `user` event, whose `tool_use_id` is the wait call's id.
     - On Codex it comes from the completed `command_execution` item's `aggregated_output`, a field the T-0179 Codex streams carry.
   - `wait_before_send`: `yes` when the probe received the wait call's event (Claude: the assistant `tool_use`; Codex: `item.started`) before the message's `send_time`, else `no`.
4. Output, in this order after the trace lines:
   - `wait_calls=<n> poll_calls=<n>`;
   - `wait_returned=<id or ->`;
   - `wait_before_send=<yes|no>`;
   - the stamps line `send_time=... read_time=... ack_time=... outcome=... reply=...`;
   - last, `result=<pass|fail|unverified>`, followed by ` reason=<text>` after a fail or unverified.

   The oracle passes only when every one of these holds:
   - `wait_calls=1` and `poll_calls=0`;
   - `wait_returned` equals the sent id;
   - `wait_before_send=yes`;
   - the message sits only in `done/<harness>/`;
   - `send_time <= read_time <= ack_time`, all three non-empty;
   - the outcome is not an expiry;
   - a reply with `topic: live-probe` and `re: <id>` exists;
   - the run is isolated.

   Exit codes: 0 pass, 1 fail, 2 setup error, 3 unverified.
5. `probe.py selftest` runs offline (no model call) against the real `messages.py`. It feeds synthetic host events to the trace classes and does a real send, read, reply, and ack. It prints `ok: <label>` per case, then `probe selftest: PASS`. Its cases, with exactly these labels:
   - `pass: one wait call returned the id, then read, reply, ack`
   - `fail: two wait calls`
   - `fail: a count call`
   - `fail: a Monitor call`
   - `fail: no wait call`
   - `fail: the wait started after the send`
6. Run each arm once. Save its stdout with `| tee` as `docs/reports/messages-wait-live-run/claude.txt` and `codex.txt`. When a host cannot run, its file holds `result=unverified reason=<why>`. Never use a fixture, and never change the oracle after seeing an arm's result.
7. Write `docs/reports/messages-wait-live-run.md`, modelled on `docs/reports/messages-live-run.md`:
   - a `# Messages wait live run` title, then a `Recorded: <YYYY-MM-DD>` line;
   - an Environment section (heading `## Environment`) with:
     - the `claude --version` and `codex --version` output;
     - the models from each host's own records (the Claude init event's `model`, the Codex rollout's `turn_context`);
     - the plugin commit (`git rev-parse --short HEAD`);
     - the `git status --porcelain -- plugins/` output as run, saying whether the step 1 and 2 changes were committed or uncommitted when the arms ran;
     - a note that the two Bash timeout variables were dropped;
   - a Method section (heading `## Method`): exact commands, the prompt, the send delay, and the oracle;
   - one section per arm, with a quote from its evidence file and a `Result: pass`, `Result: fail`, or `Result: unverified` line;
   - a Limits section (heading `## Limits`): one run per arm, one machine, an active parent only, no idle-host wake (T-0182), and any probe limit found, such as a Codex command whose output was missing from its stream item.
8. In `docs/README.md`, add one line right after the Messages live run line: `- [Messages wait live run](validation/messages-wait-live-run.md): dated live run for T-0181 ...`, ending with each arm's result.
### Acceptance criteria
- `out=$(python3 docs/reports/messages-wait-live-run/probe.py selftest) && printf "%s\n" "$out" | grep -qxF "probe selftest: PASS" && for l in "pass: one wait call returned the id, then read, reply, ack" "fail: two wait calls" "fail: a count call" "fail: a Monitor call" "fail: no wait call" "fail: the wait started after the send"; do printf "%s\n" "$out" | grep -qxF "ok: $l" || exit 1; done`
- `grep -qF "BASH_DEFAULT_TIMEOUT_MS" docs/reports/messages-wait-live-run/probe.py`
- `for a in claude codex; do grep -qE "^result=(pass|fail|unverified)( reason=.*)?$" docs/reports/messages-wait-live-run/$a.txt || exit 1; done`
- `for a in claude codex; do f=docs/reports/messages-wait-live-run/$a.txt; test -f "$f" || exit 1; if grep -qx "result=pass" "$f"; then grep -qx "wait_calls=1 poll_calls=0" "$f" || exit 1; grep -qx "wait_before_send=yes" "$f" || exit 1; grep -qE "^send_time=[^ ]+ read_time=[^ ]+ ack_time=" "$f" || exit 1; fi; done`
- `f=docs/reports/messages-wait-live-run.md; grep -qE "^Recorded: 2026-" $f && for h in "## Environment" "## Method" "## Limits"; do grep -qxF "$h" $f || exit 1; done && test "$(grep -cE "^Result: (pass|fail|unverified)" $f)" -ge 2`
- `grep -qF "validation/messages-wait-live-run.md" docs/README.md`
- `for f in docs/reports/messages-wait-live-run.md docs/reports/messages-wait-live-run/probe.py; do test -f "$f" || exit 1; ! grep -qF "$(printf '\342\200\224')" "$f" || exit 1; done`
- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e plugins/sdlc-lite/scripts/messages.py -e plugins/sdlc-lite/agents/messenger.md -e plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml -e docs/maintenance/sdlc-internals.md -e docs/ticket-stages/design.md -e docs/README.md)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vE "^docs/reports/messages-wait-live-run(\.md|/)")"`

## Step 4: Gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: steps 1, 2, and 3.

1. Run every project gate from the repository root:
   - `bash plugins/sdlc-lite/scripts/check.sh`, which runs `codex_roles.py generate --check`, `check.py`, the tickets, messages, run, and hook selftests, and `claude plugin validate`. It took about 280 s here.
   - `python3 scripts/check-packaging.py`
   - `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
   - `git diff --check`
2. Fix any red the earlier steps introduced, inside the files those steps changed. A gate already red at the build-start HEAD is reported as `inherited red`.
3. Confirm that no em dash (U+2014) was added in any changed or new file, including the untracked step 3 files.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `git diff --check`
- (guard) `! git diff "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -E "^\+" | grep -qF "$(printf '\342\200\224')"`
- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e plugins/sdlc-lite/scripts/messages.py -e plugins/sdlc-lite/agents/messenger.md -e plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml -e docs/maintenance/sdlc-internals.md -e docs/ticket-stages/design.md -e docs/README.md)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vE "^docs/reports/messages-wait-live-run(\.md|/)")"`

## Assumptions
- What this replan changes:
  - Verified by `steps.py lint` on planner-L2.md, which reported exactly one finding: the step 2 criterion that put backticks inside a code span. Two grep criteria with no backticks replace it, and each matches wording that step 2's Do now fixes.
  - Also fixed on review:
    - The L2 step 3 result check, `grep -qxE "result=(pass|fail|unverified)"`, could never match the fail line form `result=fail reason=...` that the T-0179 probe prints (messages-live-run.md:175).
    - The L2 em-dash check passed on missing files without checking anything, and it held a literal em dash. It now requires each file to exist and builds the character with `printf`.
    - Criteria that hold before and after a step are now tagged `(guard)`.
  - `steps.py lint` on a scratch copy of this plan in a /tmp git repo printed `steps lint: ok` and parsed 33 criterion spans.
- `count` refuses a malformed file instead of skipping it. Verified by messages.py:413-427 and `case_malformed` (messages.py:1435-1452). So `wait` skipping such a file is a deliberate departure, made only for `wait`, to honor handoff case 5.
- The path `wait` prints equals the path `send` prints: both come from `mailbox()` with no realpath (messages.py:443-456). Step 1 criterion 2 compares them under a macOS `mktemp -d` path, which is a symlink.
- Builders never commit, and a plain /chain commits nothing (plugins/sdlc-lite/skills/chain/SKILL.md:29). So each scope criterion is an allow-list that grows step by step and holds whether or not the work is committed between steps.
- `case_entry_parses` pins the set of entry-file subcommands (messages.py:1709-1731), and `ST_HEADINGS` pins the headings (messages.py:1629).
- The tickets selftest pins only entry-file presence and restore (tickets.py:3594-3623). `MESSENGER_WORDS` is at check.py:368.
- The generated messenger TOML copies messenger.md verbatim except `${CLAUDE_PLUGIN_ROOT}`, which becomes `@SDLC_PLUGIN_ROOT@`. Verified by comparing plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml line 7 with messenger.md. So `messages.py wait --receiver <harness>` carries into the TOML.
- The Codex path-only arm ran `gpt-6.1-sol` at effort `medium` (docs/reports/messages-live-run.md:13 and :41).
- Both host CLIs are installed and logged in: `claude --version` printed 2.1.286, `codex --version` printed 0.159.2, and `codex login status` printed `Logged in using ChatGPT`.
- Codex `command_execution` items carry `aggregated_output`. Verified from the item keys in a T-0179 raw stream (`/private/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/messages-live-_81ol52h/host-stdout.jsonl`).
- run.sh exports Bash timeouts of 3600000 to every role, and Claude Code moves a foreground Bash call to the background once it passes its timeout (run.sh:67-70).
- `python3` is 3.9.6 (`python3 --version`).
- `__pycache__/` is git-ignored (.gitignore:11, checked with `git check-ignore`). So importing messages.py in step 2's criterion, or from the probe, keeps the scope criteria green.
- The only tracked AGENTS.md files are the root, `.sdlc/`, and the two plugin files (`git ls-files`). So step 3, which changes only `docs/`, has no Read first. None of the files the steps change holds an em dash today (`git grep` with the printf byte form found none).
- Every new-behavior criterion is red now, for the right reason:
  - `wait` is not a valid argparse choice (exit 2);
  - the template, messenger, docs, probe, and evidence files lack the text or do not exist;
  - the scope criteria are green.
- Every guard is green now and side-effect free: `git status --porcelain --untracked-files=all` was the same before and after each run.
  - messages selftest: 12 s;
  - tickets selftest: 31 s;
  - `codex_roles.py generate --check`;
  - check.sh: 277 s;
  - check-packaging;
  - `git diff --check`;
  - the em-dash diff guard.
- Each guard was seen red, in a detached copy under `$SDLC_TMP_WORKTREES`:
  - `codex_roles.py generate --check` exited 2 after a line was appended to messenger.md;
  - the tickets selftest exited 1 after the `messages.write_entries` call was removed;
  - the messages selftest guard exited 1 with `'wait'` added to `want` and the template unchanged;
  - `git diff --check` exited 2 on trailing whitespace;
  - check-packaging exited 1 when a plugin was dropped from `.claude-plugin/marketplace.json`;
  - the em-dash guard went red on a fixture holding the character;
  - check.sh fails whenever `codex_roles.py generate --check` fails, because it sets `fail=1` on that call and exits with `$fail` (check.sh:12 and its last line).

## Risks
- A host may still loop or poll despite the prompt: re-run `wait`, add `sleep`, or background the call and poll it. Then an arm records `result=fail`. The criteria accept a recorded fail or unverified so the evidence stays honest, and the conductor should treat a fail as a finding about the feature, not a build defect.
- Codex's shell tool may end or yield the call before `wait` returns, because its default timeout is not established. The wait output could then be missing from the stream item, so `wait_returned=-` and the arm fails. The builder records what the raw stream and the rollout show under Limits and does not change the oracle after the run.
- A host that takes more than 20 s to make its first call gets `wait_before_send=no` and fails. That is a failure of the experiment, not of the feature, and the record must say so.
- The timing assertions can flake on a heavily loaded host: selftest case 1 (under 2 s), selftest case 2 (wakes before 10 s), and step 1 criterion 2 (under 3 s).
- check.sh took 277 s here, close to the default 300 s `--guard-timeout` of `steps.py split --only`. A `split --only 4` should pass a larger `--guard-timeout`, for example 900.
- Codex auth or network may be unavailable at build time. That arm is then unverified, and the ticket's live-proof condition is only partly met.
- The `[0-9]{1,9}` cap gives `--interval` a de facto maximum of 999999999 seconds, a choice beyond the handoff's "minimum 1". It has no practical effect, because each sleep is capped by the time left, which is at most 600 s.
