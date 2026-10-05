<!-- role=planner level=L3 model=opus effort=xhigh -->
## Goal
Add `messages.py wait`, one blocking call that returns as soon as a valid message is in `new/<receiver>/` and never claims, moves, writes, or prints a body. Cover it in the entry files, the messenger agent, and the docs. Record a live proof on Claude Code and Codex in which the host's single `wait` call returned the message id and the host made no polling calls.

## Step 1: messages.py wait subcommand and its selftest cases
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Targets: `plugins/sdlc-lite/scripts/messages.py` only. Depends on: none. The system `python3` is 3.9.6, so use no syntax newer than Python 3.9.

1. Add `cmd_wait(a)`, register it in `COMMANDS`, and add a `wait` subparser to `parser()` right after `count`.
   - Subparser: `allow_abbrev=False`, help `block until a message is in new/<receiver>/; never claims it`.
   - Flags:
     - `--receiver NAME`, help `required: the receiver`.
     - `--timeout SECONDS`, help `give up after this many seconds: an integer from 1 to 600 (default 120)`.
     - `--interval SECONDS`, help `check this often, in seconds: an integer of at least 1 (default 5)`.
   - Parse `--timeout` and `--interval` as strings (`default=None`, no `type=`). An argparse `type=int` would make a non-integer a usage error (exit 2), and the handoff requires exit 1.
2. Validate in this order. Each failure raises `Refuse`: exit 1, one `messages.py: <reason>` stderr line, nothing on stdout, nothing written.
   - The receiver goes through `arg_name(a.receiver, '--receiver')`.
     - A missing receiver gives `--receiver is required` (`need`, messages.py:720-723).
     - A bad receiver gives `--receiver must match ...` (messages.py:726-731).
   - The timeout (default `'120'`) must fullmatch `[0-9]{1,9}` and lie from 1 to 600. Otherwise the reason is `--timeout must be an integer from 1 to 600: <short(value)>`.
   - The interval (default `'5'`) must fullmatch `[0-9]{1,9}` and be at least 1. Otherwise the reason is `--interval must be an integer of at least 1: <short(value)>`.
   - The 9-digit cap copies `TTL_RE` (messages.py:181) and keeps `int()` under Python 3.11's digit limit. There is no other interval maximum, because each sleep is `min(interval, time left)`.
3. Add a helper `wait_ready(mbox, receiver)`. It returns a list of `(mid, path)`, sorted by id, with `path = msg_path(mbox, 'new', receiver, mid)`. It holds one entry for each `mid` in `message_ids(os.path.join(mbox, 'new', receiver))` whose `load_or_none(path, 'new', receiver)` is not None.
   - It catches `Refuse` per file and skips that file, so a malformed file never wakes a waiter and never makes `wait` exit 1.
     - Evidence: `load` raises `Refuse` on an invalid file (messages.py:413-420).
     - Reusing `load_or_none` bare, as `count` does, would make `wait` exit 1, and `case_malformed` asserts that `count` refuses. Handoff case 5 says `wait` ignores the file.
   - `path` never goes through `realpath`, so it equals the path `send` prints for the same mailbox. `mailbox()` makes the path absolute without resolving symlinks (messages.py:443-456), and a macOS `mktemp -d` path is a symlink.
   - `count` itself is not changed (a non-goal).
4. `cmd_wait` holds exactly one line with the literal text `ready = wait_ready(mbox, receiver)`, inside its loop. The negative control patches that line. The loop works on a `time.monotonic()` deadline:
   - It checks at once, before any sleep. When `ready` is non-empty, it calls `emit` with one `<id>\t<path>\n` line per entry, in sorted order, and returns 0.
   - Otherwise, once the deadline has passed, it calls `emit('no new messages\n')` and returns 3.
   - Otherwise it runs `time.sleep(min(interval, remaining))` and loops.
   - A missing mailbox creates nothing.
   - `wait` never calls `claim`, `write_entries`, `deliver`, `write_replace`, or `Lock`, and never prints front matter or a body.
   - `main` already returns the command's code, so exit 3 needs no other change.
5. Update the module docstring:
   - Usage: after the `count` line, add `messages.py [--root DIR] wait --receiver NAME [--timeout SECONDS] [--interval SECONDS]`.
   - Exit paragraph: add `Exit 3 only when wait times out.`
   - Commands: add a `wait` entry after `count` that says:
     - It checks new/<receiver>/ every --interval seconds (default 5, at least 1) for up to --timeout seconds (default 120, 1 to 600).
     - It prints `<id>\t<absolute path>` per valid message, sorted by id, and exits 0. At the timeout it prints `no new messages` and exits 3.
     - It skips an invalid file. It never claims, moves, writes, stamps, or prints a body.
   - Schema paragraph: "Every subcommand validates every message file it opens or counts" becomes "Every subcommand except wait validates every message file it opens or counts". After that sentence add `wait skips an invalid file instead.`
   - Layout: the sentence "list, count, and expire on a missing mailbox create nothing" (line 74-75) also names `wait`.
   - The `add_subparsers` metavar becomes `{send,list,read,ack,reply,expire,count,wait,selftest}`.
6. Add seven selftest functions in the existing `Harness`/`Box` style and append them to `SELFTEST_CASES` with exactly these labels. Use timeouts of 1 to 3 seconds, except case 2's 10 seconds. Kill any child process still running in a `finally`.
   1. `wait: a present message returns at once, state unchanged`
      - Put the body in `st_wait_present(h)`, which raises `SelftestFail`. It runs `mid, path = b.send()`, then `before = b.snap()`, then `b.run('wait', '--receiver', 'bob', '--interval', '5', '--timeout', '3')` timed with `time.monotonic()`.
      - Assert in exactly this order, each check with its own `st_fail` message:
        - (a) exit 0, else `wait exited <code>: <stderr>`;
        - (b) under 2 s, else `wait took <s> s`;
        - (c) stdout exactly `f'{mid}\t{path}\n'`, else `wait printed <stdout>`;
        - (d) `b.snap() == before`, else a message that starts with `wait changed the mailbox`, followed by the paths that differ;
        - (e) `b.only(mid, 'new', 'bob')`;
        - (f) the file's `read_time` is empty.
   2. `wait: wakes on a message sent mid-wait`
      - Start `subprocess.Popen` on `wait --receiver bob --timeout 10 --interval 1` (cwd `b.repo`, env `h.env`). Sleep about 1.5 s, then run `mid, _ = b.send()`.
      - Assert it exits 0 within 10 s of its start and that the first tab-separated field of its stdout is `mid`.
   3. `wait: timeout exits 3, state unchanged`
      - On a box holding a message for carol only (`b.send(receiver='carol')`), take `b.snap()`, then run `wait --receiver bob --timeout 1 --interval 1`.
      - Assert exit 3, stdout exactly `no new messages\n`, and `b.snap()` unchanged.
   4. `refused: wait with a bad receiver, timeout, or interval`
      - First run `b.send()`, a message for bob, so a `wait` that wrongly accepts a value exits 0 at once instead of blocking.
      - Then make exactly these seven calls:
        - `b.refused('wait', want='--receiver is required')`
        - `b.refused('wait', '--receiver', 'Bob', want='--receiver must match')`
        - `b.refused('wait', '--receiver', 'bob', '--timeout', '601', want='--timeout must be an integer from 1 to 600')`
        - the same call with `'0'` in place of `'601'`
        - the same call with `'1.5'` in place of `'601'`
        - `b.refused('wait', '--receiver', 'bob', '--interval', 'abc', want='--interval must be an integer of at least 1')`
        - the same call with `'0'` in place of `'abc'`
      - Every call after the second passes `--receiver bob`, so the timeout and interval branches are reached, and `want` (`Box.refused`, messages.py:1116-1131) pins which branch refused.
   5. `wait: ignores a malformed file and another receiver`
      - Run `b.put('bob', '20260101T000000000000Z-alice-garbage', b'not a message\n')` and `b.send(receiver='carol')`.
      - Run `wait --receiver bob --timeout 1 --interval 1`. Assert exit 3 and stdout exactly `no new messages\n`.
      - Then run `mid, path = b.send()` and `wait --receiver bob --timeout 3 --interval 1`. Assert exit 0 and stdout exactly `f'{mid}\t{path}\n'`, which excludes the garbage id.
   6. `wait: never prints a body`
      - Send a body holding a unique marker. Assert that `wait` exits 0 and that neither its stdout nor its stderr holds the marker.
   7. `wait: a claiming wait is caught`
      - Build the anchor string from two pieces (`'ready = wait_' + 'ready(mbox, receiver)'`), so the source holds the whole anchor only in `cmd_wait`. Assert the anchor occurs exactly once in this file's source.
      - Create a fresh folder under `h.tmp` and write the source there as `messages.py`, with the anchor replaced. The replacement is the anchor followed, on the same line after `; `, by a list comprehension. For each `(m, p)` in `ready`, the comprehension calls `os.makedirs(os.path.join(mbox, 'read', receiver), exist_ok=True)` and `claim(p, msg_path(mbox, 'read', receiver, m))`. Keeping it on one line keeps the indentation valid.
      - Create a second fresh subfolder of `h.tmp` and build a second `Harness` on it, so its `repo-<n>` folders cannot collide with `h`'s. Set its `me` to the patched copy.
      - Run `st_wait_present` on the second harness inside a `try`.
        - `except SelftestFail as e`: when `str(e)` does not start with `wait changed the mailbox`, call `st_fail(f'the claiming copy failed another check first: {e}')`. Otherwise the case passes.
        - `else`: call `st_fail('the state check passed a wait that claims the message')`.
      - So the case passes only when the state-unchanged check (d) fired. A patched copy that crashes fails check (a), and then this case fails. The patched copy prints the `new/` path, because the path is computed before the claim, so checks (a) to (c) hold and (d) is the first check to fire.

Focused check: `python3 plugins/sdlc-lite/scripts/messages.py selftest`.

Contract dependents:
- `case_entry_parses` pins the set of subcommands the entry files run (messages.py:1729). This step leaves `ENTRY_TEMPLATE` unchanged, so `want` stays correct; step 2 changes both together.
- `run.sh` calls only `count` (run.sh:236), which is unchanged.
### Acceptance criteria
- `out=$(python3 plugins/sdlc-lite/scripts/messages.py selftest) && printf "%s\n" "$out" | grep -qxF "messages selftest: PASS" && for l in "wait: a present message returns at once, state unchanged" "wait: wakes on a message sent mid-wait" "wait: timeout exits 3, state unchanged" "refused: wait with a bad receiver, timeout, or interval" "wait: ignores a malformed file and another receiver" "wait: never prints a body" "wait: a claiming wait is caught"; do printf "%s\n" "$out" | grep -qxF "ok: $l" || exit 1; done`
- `S=plugins/sdlc-lite/scripts/messages.py; d=$(mktemp -d) && p=$(python3 $S --root "$d" send --receiver bob --sender alice --topic t --follow-up false hi) && id=$(basename "$p" .md) && before=$(cat "$p") && s=$SECONDS && out=$(python3 $S --root "$d" wait --receiver bob --interval 5 --timeout 10) && test $((SECONDS - s)) -lt 3 && test "$out" = "$(printf "%s\t%s" "$id" "$p")" && test "$(cat "$p")" = "$before"`
- `S=plugins/sdlc-lite/scripts/messages.py; d=$(mktemp -d); out=$(python3 $S --root "$d" wait --receiver bob --timeout 1 --interval 1); rc=$?; test "$rc" -eq 3 && test "$out" = "no new messages" && test -z "$(ls -A "$d")"`
- `S=plugins/sdlc-lite/scripts/messages.py; d=$(mktemp -d); e=$(mktemp); for a in "--receiver Bob" "--receiver bob --timeout 601" "--receiver bob --timeout 0" "--receiver bob --timeout 1.5" "--receiver bob --interval abc" "--receiver bob --interval 0"; do f=$(printf "%s\n" $a | grep -- "^--" | tail -n 1); out=$(python3 $S --root "$d" wait $a 2>"$e"); rc=$?; test "$rc" -eq 1 || exit 1; test -z "$out" || exit 1; grep -q -- "^messages.py: $f must " "$e" || exit 1; done; test -z "$(ls -A "$d")"`
- `S=plugins/sdlc-lite/scripts/messages.py; d=$(mktemp -d) && mkdir -p "$d/messages/new/bob" && printf "not a message\n" > "$d/messages/new/bob/20260101T000000000000Z-alice-garbage.md" && python3 $S --root "$d" send --receiver carol --sender alice --topic t --follow-up false hi >/dev/null && out=$(python3 $S --root "$d" wait --receiver bob --timeout 2 --interval 1); rc=$?; test "$rc" -eq 3 && test "$out" = "no new messages"`
- `S=plugins/sdlc-lite/scripts/messages.py; d=$(mktemp -d) && python3 $S --root "$d" send --receiver bob --sender alice --topic t --follow-up false "BODYMARK-5e1c" >/dev/null && out=$(python3 $S --root "$d" wait --receiver bob --timeout 2 --interval 1 2>&1) && test -n "$out" && ! printf "%s\n" "$out" | grep -qF "BODYMARK-5e1c"`
- `h=$(python3 plugins/sdlc-lite/scripts/messages.py wait --help) && printf "%s\n" "$h" | grep -qF -- "--timeout" && printf "%s\n" "$h" | grep -qF -- "--interval"`
- `grep -qF "wait --receiver NAME [--timeout SECONDS] [--interval SECONDS]" plugins/sdlc-lite/scripts/messages.py`
- `test "$(grep -cF "wait changed the mailbox" plugins/sdlc-lite/scripts/messages.py)" -ge 2`
- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF plugins/sdlc-lite/scripts/messages.py)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vxF plugins/sdlc-lite/scripts/messages.py)"`

## Step 2: Entry files, messenger agent, Codex agent, and docs cover wait
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: step 1 (the `wait` subparser must exist for `case_entry_parses` to pass). The texts below are settled. Insert them verbatim; they hold no em dash.

1. `ENTRY_TEMPLATE` in `plugins/sdlc-lite/scripts/messages.py`:
   - Read section: after its one paragraph (ending "`read` prints the body between the BEGIN and END data markers."), add a blank line and this paragraph:
     ```text
     To block until a message arrives, run `python3 "{{scripts}}/messages.py" wait --receiver <name> --timeout <seconds> --interval <seconds>`. It checks `new/<name>/` every `--interval` seconds (default 5) for up to `--timeout` seconds (default 120, at most 600). It prints one line per new message, the id and the absolute path separated by a tab, and exits 0; at the timeout it prints `no new messages` and exits 3. `wait` never claims a message: claim each one with `read`.
     ```
   - Messenger section, first paragraph: replace the parenthetical ``(`count`, then `list` and `read`)`` with ``(`wait`, or `count` then `list`, then `read`)``.
   - Messenger section: after the two host bullets and before the Host limits heading, add a blank line and this paragraph:
     ```text
     While the parent is active, `wait` is the cheaper alternative to a polling subagent. The messenger may run it in its loop, or the parent may skip the messenger and run `python3 "{{scripts}}/messages.py" wait --receiver <harness> --timeout 100 --interval 10` itself, then claim each printed id with `read`. On Claude Code, `--timeout 100` keeps the call under the default 120-second Bash timeout. `wait` returns only into an active parent, so it does not wake an idle host.
     ```
   - Add no heading, so `ST_HEADINGS` (messages.py:1629) stays unchanged. Leave the Host limits and Trust sections unchanged. The entry file is consumer-facing, so it names no ticket id.
2. In `case_entry_parses`, add `'wait'` to `want` (messages.py:1729). It is the contract dependent of the template change, because it pins the subcommands the entry files run. Each new command span uses only `--receiver`, `--timeout`, and `--interval`, which step 1's `wait --help` lists.
   - `tickets.py roadmap` writes the same template through `messages.write_entries` (tickets.py:846).
   - The tickets selftest pins only entry-file presence and restore (tickets.py:3594-3623), so it needs no edit. It runs here as a guard.
3. `plugins/sdlc-lite/agents/messenger.md`:
   - Replace the four Loop items with exactly these three, followed by a blank line and the closing sentence:
     ```text
     1. Run `messages.py wait --receiver <harness> --timeout 100 --interval 10`. It blocks until a message is in `new/<harness>/`, then prints one line per message: the id and the absolute path, separated by a tab. Exit 3 with `no new messages` means nothing arrived: run it again.
     2. Claim each message `wait` printed with `messages.py read <id> --receiver <harness>`, where `<id>` is the first tab-separated field of its line. `wait` never claims a message.
     3. End your turn with a report that lists, for each claimed message, its id and its path `read/<harness>/<id>.md` in the mailbox (`.sdlc/messages/` in the main checkout). That report is how your parent is notified. Your parent spawns you again to keep polling.

     Your parent may skip you and run the same `wait` command itself while it is active. `wait` still cannot wake an idle host.
     ```
   - Replace the Host limits Claude Code bullet with:
     ```text
     - Claude Code: you live only while your session runs. Foreground `sleep` is blocked, so polling needs Monitor (an until-loop) or a loop. `wait` is one foreground Bash call and needs neither; `--timeout 100` keeps it under the default 120-second Bash timeout.
     ```
   - Keep the three words `MESSENGER_WORDS` pins (check.py:368): `model: claude-haiku-4-5`, `messages.py`, and `.sdlc/messages/AGENTS.md`.
4. Run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` to regenerate `plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml`. Never edit the TOML by hand.
5. `docs/maintenance/sdlc-internals.md`, the `scripts/messages.py` entry (line 15). Each anchor below occurs exactly once in the file.
   - (a) Replace ``count` (files in `new/<receiver>/`), and `selftest`.`` with:
     ```text
     `count` (files in `new/<receiver>/`), `wait` (blocks until a valid message is in `new/<receiver>/`, checking every `--interval` seconds (default 5, at least 1) for up to `--timeout` seconds (default 120, 1 to 600); prints `<id>\t<absolute path>` per message, sorted by id, and exits 0; at the timeout prints `no new messages` and exits 3; skips an invalid file; never claims, moves, writes, or prints a body), and `selftest`.
     ```
   - (b) Replace `exit 2 only for a usage error.` with ``exit 2 only for a usage error; exit 3 only when `wait` times out.``
   - (c) Replace `Every subcommand validates each file it opens or counts before it writes or moves anything.` with ``Every subcommand except `wait` validates each file it opens or counts before it writes or moves anything; `wait` skips an invalid file.``
   - (d) Replace `, and one shared mailbox across worktrees.` with:
     ```text
     , one shared mailbox across worktrees, and the `wait` cases (a present message returns at once with the mailbox unchanged, a message sent mid-wait wakes it, the timeout exits 3 with the mailbox unchanged, bad values are refused, a malformed file and another receiver's message do not wake it, no body is printed, and a claiming wait is caught as a negative control).
     ```
6. `docs/ticket-stages/design.md`:
   - At the end of the Status paragraph (line 77), add: ``T-0181 adds `messages.py wait`, one blocking call that returns when a message is in `new/<receiver>/` and never claims it.``
   - At the end of the Host limits bullet (line 105), add: ```messages.py wait` (T-0181) is one blocking call a parent can make instead of running a polling subagent; it returns only into an active parent, so it does not wake an idle host.``
7. Left unchanged on purpose:
   - `docs/codex-role-execution.md:27`: it describes the messenger's polling and its host limits, which still hold for `count`-based polling. The handoff names the doc homes this step covers.
   - `docs/ticket-stages/README.md:3`: it lists the tickets that built the bus. The design Status paragraph records T-0181.
   - `docs/reports/messages-live-run/probe.py`: it pins no entry-file text.

Focused checks: the messages selftest, the tickets selftest, and `codex_roles.py generate --check`.
### Acceptance criteria
- `python3 -B -c 'import sys; sys.path.insert(0, "plugins/sdlc-lite/scripts"); import messages; t = messages.ENTRY_TEMPLATE; r = t.split("\n## Read\n", 1)[1].split("\n## ", 1)[0]; m = t.split("\n## Messenger\n", 1)[1].split("\n## ", 1)[0]; assert "messages.py\" wait --receiver <name> --timeout <seconds> --interval <seconds>" in r, "read"; assert "messages.py\" wait --receiver <harness> --timeout 100 --interval 10" in m, "messenger"; assert "does not wake an idle host" in m, "idle"'`
- (guard) `python3 plugins/sdlc-lite/scripts/messages.py selftest | grep -qxF "messages selftest: PASS"`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`
- `grep -qF "messages.py wait --receiver <harness> --timeout 100 --interval 10" plugins/sdlc-lite/agents/messenger.md`
- `! grep -qF "Every 10 seconds, run" plugins/sdlc-lite/agents/messenger.md`
- (guard) `for w in "model: claude-haiku-4-5" "messages.py" ".sdlc/messages/AGENTS.md"; do grep -qF -- "$w" plugins/sdlc-lite/agents/messenger.md || exit 1; done`
- `grep -qF "messages.py wait --receiver <harness> --timeout 100 --interval 10" plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `grep -qF "exit 3 only when" docs/maintenance/sdlc-internals.md`
- `grep -qF "no new messages" docs/maintenance/sdlc-internals.md`
- `grep -qF "a claiming wait is caught as a negative control" docs/maintenance/sdlc-internals.md`
- `grep -qF "T-0181 adds" docs/ticket-stages/design.md`
- `grep -qF "does not wake an idle host" docs/ticket-stages/design.md`
- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e plugins/sdlc-lite/scripts/messages.py -e plugins/sdlc-lite/agents/messenger.md -e plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml -e docs/maintenance/sdlc-internals.md -e docs/ticket-stages/design.md)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc")"`

## Step 3: Live probe for wait, with an offline selftest
level: L3
### Do
Target: the new file `docs/reports/messages-wait-live-run/probe.py`. Use Python 3.9 syntax only. This step makes no model call and runs no live arm.

Depends on: none for its offline selftest, which drives `messages.py` send, read, reply, and ack, all of which exist now. It runs after steps 1 and 2 so that step 4's live arms use the finished plugin.

1. Model the probe on `docs/reports/messages-live-run/probe.py` (T-0179). Read these parts of it first:
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
     - This is the model and effort of the path-only arm in `docs/reports/messages-live-run.md` (its lines 13 and 41).
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

Focused check: `python3 docs/reports/messages-wait-live-run/probe.py selftest`.
### Acceptance criteria
- `out=$(python3 docs/reports/messages-wait-live-run/probe.py selftest) && printf "%s\n" "$out" | grep -qxF "probe selftest: PASS" && for l in "pass: one wait call returned the id, then read, reply, ack" "pass: a Codex wait call with no poll in the rollout" "fail: two wait calls" "fail: a count call" "fail: a Monitor call" "fail: a backgrounded wait call" "fail: no wait call" "fail: the wait started after the send" "fail: the wait returned another id" "fail: a Codex write_stdin poll" "fail: a Codex cell wait" "unverified: a host not on PATH says host cannot run"; do printf "%s\n" "$out" | grep -qxF "ok: $l" || exit 1; done`
- `for v in BASH_DEFAULT_TIMEOUT_MS BASH_MAX_TIMEOUT_MS; do grep -qF "$v" docs/reports/messages-wait-live-run/probe.py || exit 1; done`
- `f=docs/reports/messages-wait-live-run/probe.py; test -f "$f" && ! grep -qF "$(printf '\342\200\224')" "$f"`
- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e plugins/sdlc-lite/scripts/messages.py -e plugins/sdlc-lite/agents/messenger.md -e plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml -e docs/maintenance/sdlc-internals.md -e docs/ticket-stages/design.md)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vxF docs/reports/messages-wait-live-run/probe.py)"`

## Step 4: Live proof of wait on Claude Code and Codex
level: L3
### Do
Targets:
- `docs/reports/messages-wait-live-run/claude.txt`
- `docs/reports/messages-wait-live-run/codex.txt`
- `docs/reports/messages-wait-live-run.md`
- one line in `docs/README.md`

Depends on: steps 1, 2, and 3.

1. Run `python3 docs/reports/messages-wait-live-run/probe.py selftest` first. If it fails, stop with Status blocked.
2. Before the arms, record the output of:
   - `claude --version`, `codex --version`, and `codex login status`;
   - `git rev-parse --short HEAD`;
   - `git status --porcelain -- plugins/`. The step 1 and 2 changes are uncommitted, because builders never commit, and the record says so.
3. Run each arm once, as one foreground Bash call with the Bash timeout at 1200000:
   - `set -o pipefail; python3 docs/reports/messages-wait-live-run/probe.py claude | tee docs/reports/messages-wait-live-run/claude.txt`
   - the same command with `codex` and `codex.txt`.

   Never write or edit an evidence file by hand and never use a fixture. Never change the probe, the prompt, the send delay, or the oracle after an arm has run.
4. Allowed outcomes per arm:
   - The Claude arm must pass. The `claude` CLI is the one that runs this pipeline, and it printed `2.1.286 (Claude Code)` at plan time.
   - The Codex arm must pass, or end with a last line that starts with `result=unverified reason=host cannot run: `. That is the handoff's one fallback: "If a host cannot run, record the arm as unverified with the reason".
5. When an arm's last line is `result=fail ...`, the live proof did not hold.
   - Keep the evidence file and still write the record (item 6) with `Result: fail` for that arm.
   - End with Status blocked. The first line of Notes is `live proof failed: <arm>: <the result line>`.
   - Do not rerun the arm. Whether to rerun, change the prompt, or accept the finding is the user's decision at the replan: /chain 4.2 routes a blocked builder to a planner L3 replan.
6. Write `docs/reports/messages-wait-live-run.md`, modelled on `docs/reports/messages-live-run.md`:
   - `# Messages wait live run`, a blank line, `Recorded: <YYYY-MM-DD>` with the run date, and an intro paragraph on what was shown.
   - `## Environment`:
     - the version and login output from item 2;
     - the models from each host's own records: the Claude init event's `model` in `host-stdout.jsonl`, and the Codex rollout's `turn_context` model and effort;
     - the plugin commit, and whether `plugins/` held uncommitted step 1 and 2 changes;
     - that the probe dropped `BASH_DEFAULT_TIMEOUT_MS` and `BASH_MAX_TIMEOUT_MS`;
     - macOS and the temp project location.
   - `## Method`:
     - the exact probe and host commands, and the prompt verbatim;
     - the 20-second send delay;
     - the definitions of `wait_calls`, `poll_calls`, `wait_returned`, and `wait_before_send`;
     - the oracle, the exit codes, and the isolation proof per host, as in the T-0179 record.
   - `## Claude Code` and `## Codex`, one section per arm:
     - a link to the arm's evidence file and its lines quoted in a fenced block;
     - what the raw stream shows: the wait call, its returned line, and the read, reply, and ack calls;
     - for Codex, also what the rollout shows: the `exec` input with its `yield_time_ms`, and any `write_stdin` or cell `wait`;
     - exactly one line `Result: <pass|fail|unverified>`, equal to the word after `result=` on the evidence file's last line.
   - `## Limits`:
     - one run per arm, on one machine and one account per host;
     - an active parent only, and no idle-host wake (T-0182);
     - `poll_calls` counts only the listed call kinds, and other shell calls appear as `tool=` lines;
     - any probe limit found.
   - Where a quoted evidence line holds U+2014, write `\u2014` in its place and say so under Limits. The record holds no em dash.
7. In `docs/README.md`, add one line right after the `- [Messages live run](validation/messages-live-run.md): ...` line (line 33). Fill in each arm's result word:
   ```text
   - [Messages wait live run](validation/messages-wait-live-run.md): dated live run for T-0181 in which a fresh Claude Code host and a fresh Codex host were each told to make one `messages.py wait` call, then read, reply, and ack; Claude Code <result>, Codex <result>.
   ```
### Acceptance criteria
- `test "$(tail -n 1 docs/reports/messages-wait-live-run/claude.txt)" = "result=pass"`
- `tail -n 1 docs/reports/messages-wait-live-run/codex.txt | grep -qE "^result=(pass|unverified reason=host cannot run: .+)$"`
- `for a in claude codex; do head -n 1 docs/reports/messages-wait-live-run/$a.txt | grep -qxF "arm=$a" || exit 1; done`
- `for f in docs/reports/messages-wait-live-run/claude.txt docs/reports/messages-wait-live-run/codex.txt; do test -f "$f" || exit 1; if test "$(tail -n 1 "$f")" = "result=pass"; then python3 -c 'import re,sys; L=open(sys.argv[1]).read().splitlines(); mid=[l for l in L if l.startswith("message=")][0].rsplit("/",1)[1][:-3]; v=dict(x.split("=",1) for x in [l for l in L if l.startswith("send_time=")][0].split(" ")[:3]); T=re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}[.][0-9]{6}Z"); s=[v["send_time"],v["read_time"],v["ack_time"]]; assert "wait_calls=1 poll_calls=0" in L, "calls"; assert "wait_before_send=yes" in L, "before"; assert "wait_returned="+mid in L, "returned"; assert all(T.fullmatch(x) for x in s), "stamps"; assert sorted(s)==s, "order"' "$f" || exit 1; fi; done`
- `f=docs/reports/messages-wait-live-run.md; grep -qE "^Recorded: 2026-[0-9]{2}-[0-9]{2}$" "$f" && for h in "## Environment" "## Method" "## Claude Code" "## Codex" "## Limits"; do grep -qxF "$h" "$f" || exit 1; done`
- `python3 -c 'import re; t=open("docs/reports/messages-wait-live-run.md").read(); sec=lambda h: t.split("\n"+h+"\n",1)[1].split("\n## ",1)[0]; ev=lambda a: open("docs/reports/messages-wait-live-run/"+a+".txt").read().splitlines()[-1].split(" ")[0].split("=",1)[1]; got=[(re.findall(r"^Result: (\w+)$", sec(h), re.M), ev(a)) for h,a in (("## Claude Code","claude"),("## Codex","codex"))]; assert all(r==[e] for r,e in got), got'`
- `grep -qF "validation/messages-wait-live-run.md" docs/README.md`
- `for f in docs/reports/messages-wait-live-run.md docs/reports/messages-wait-live-run/probe.py; do test -f "$f" || exit 1; ! grep -qF "$(printf '\342\200\224')" "$f" || exit 1; done`
- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e plugins/sdlc-lite/scripts/messages.py -e plugins/sdlc-lite/agents/messenger.md -e plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml -e docs/maintenance/sdlc-internals.md -e docs/ticket-stages/design.md -e docs/README.md)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vE "^docs/reports/messages-wait-live-run(\.md|/)")"`

## Step 5: Gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: steps 1, 2, 3, and 4.

1. Run every project gate from the repository root:
   - `bash plugins/sdlc-lite/scripts/check.sh`. It runs `codex_roles.py generate --check`, `check.py`, the tickets, messages, run, and hook selftests, and `claude plugin validate`. It took 252 s at plan time.
   - `python3 scripts/check-packaging.py`
   - `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
   - `git diff --check`
2. Fix any red the earlier steps introduced, inside the files those steps changed. A gate already red at the build-start HEAD is reported as `inherited red`.
3. Confirm that no em dash (U+2014) was added in any changed or new file, including the untracked step 3 and 4 files.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `git diff --check`
- (guard) `! git diff "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -E "^\+" | grep -qF "$(printf '\342\200\224')"`
- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e plugins/sdlc-lite/scripts/messages.py -e plugins/sdlc-lite/agents/messenger.md -e plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml -e docs/maintenance/sdlc-internals.md -e docs/ticket-stages/design.md -e docs/README.md)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vE "^docs/reports/messages-wait-live-run(\.md|/)")"`

## Assumptions
- This replan answers each `plan review:` finding in the handoff. No step had passed (the task dir holds no `step-*` dir), so steps were renumbered: steps 1 and 2 keep their numbers, the old step 3 is split into step 3 (the probe) and step 4 (the live run), and the old gates step 4 is now step 5.
  - Step 3 goal coverage and acceptance criteria: verified by the step 4 criteria, which can no longer pass on a failed proof.
    - They require the Claude arm's last line to be exactly `result=pass`.
    - They reject a Codex `result=fail`. A Codex `result=unverified` is accepted only with the probe's `host cannot run: ` reason, which the probe emits only for the T-0179 cannot-run conditions.
    - For every passing arm they check `wait_calls=1 poll_calls=0`, `wait_before_send=yes`, a `wait_returned` equal to the `message=` id, and ordered timestamp stamps.
    - They check that each record section's `Result:` line equals its evidence file.
    - A failed arm ends in Status blocked, which /chain 4.2 routes to a planner L3 replan and the user (chain SKILL.md:49).
    - I ran each step 4 check on a scratch fixture outside the tree. It passed a good fixture and went red on `poll_calls=1`, `ack_time` before `read_time`, a Claude `result=fail`, a Codex `result=fail`, a Codex `result=unverified reason=timeout`, a passing Codex arm with polls, and a record `Result:` that disagrees with its evidence.
  - Step 1 negative control: verified by the new case 7 logic and a structural check.
    - Case 7 now passes only when the `SelftestFail` text starts with `wait changed the mailbox`.
    - `st_wait_present` fixes its assertion order (exit 0, time, stdout, then state), so a crashing patched copy fails the case.
    - Criterion 9 requires that message at least twice in the source.
  - Step 1 case 4: verified by messages.py:720-731 and 1116-1131. The case now spells out seven `b.refused` calls, each after the receiver one with `--receiver bob`, and each with a `want` that pins the branch. Shell criterion 4 also checks that stderr names the refused flag.
  - Step 2 level: raised to L3 (four hand-edited files and one regenerated file). Every inserted sentence is now given verbatim.
- `count` refuses a malformed file: verified by messages.py:413-427 and `case_malformed` (messages.py:1435-1452). So `wait` skipping such a file is a deliberate departure, made for `wait` only, to honor handoff case 5.
- A `send` to carol succeeds with a garbage file in new/bob: verified by running that send at plan time (exit 0). So step 1 criterion 5 is red now only because `wait` is missing.
- The path `wait` prints equals the path `send` prints: verified by messages.py:443-456. Both come from `mailbox()`, which does not resolve symlinks.
- `case_entry_parses` pins the entry-file subcommands (messages.py:1709-1731), and `ST_HEADINGS` pins the headings (messages.py:1629): verified by reading them. `MESSENGER_WORDS` is at check.py:368.
- The step 2 doc anchors are unique: verified by `grep -oF` counts of 1 for each sdlc-internals.md anchor and each design.md line end.
- The messenger TOML is generated from messenger.md, with `${CLAUDE_PLUGIN_ROOT}` replaced (codex_roles.py:62): verified because `generate --check` exited 2 on a copy after a line was appended to messenger.md.
- Codex code mode yields long commands, and the model polls them with `tools.write_stdin` or a top-level `wait` function call: verified in `~/.codex/sessions/2026/09/29/rollout-...-01a0ee2f-....jsonl` and `.../09/30/rollout-...-01a0f278-....jsonl`.
  - A cell printed "Script running with cell ID 30" and was then continued by a `function_call` named `wait`.
  - Nested `tools.write_stdin({session_id:...})` calls appear in `exec` inputs.
  - `yield_time_ms: 30000` completed a 28.9 s command.
  - The binary's tool text says `yield_time_ms` "asks exec to yield early if the script is still running".
- Codex `command_execution` items carry `item.started` and `aggregated_output`: verified in the T-0179 raw stream `messages-live-_81ol52h/host-stdout.jsonl`.
- Claude `user` events carry `tool_result` blocks with `tool_use_id`: verified in the T-0179 raw stream `messages-live-0z9zhe6e/host-stdout.jsonl`.
- Both host CLIs are installed and logged in: verified at plan time. `claude --version` printed `2.1.286 (Claude Code)`, `codex --version` printed `codex-cli 0.159.2`, `codex login status` printed `Logged in using ChatGPT`, and `python3 --version` printed 3.9.6.
- The T-0179 unverified conditions are all cannot-run conditions: verified by docs/reports/messages-live-run/probe.py:585-587, 433-452, 510-513, and 650-653.
- run.sh exports Bash timeouts of 3600000 to every role: verified by run.sh:67-70.
- `__pycache__/` is git-ignored (.gitignore:11), and step 2's import check uses `python3 -B` anyway.
- The only tracked AGENTS.md files are the root, `.sdlc/`, and the two plugin files: verified by `git ls-files`. So steps 3 and 4, which change only `docs/`, have no Read first.
- `steps.py lint` printed `steps lint: ok` for a scratch copy of every criterion span (10, 14, 4, 9, and 6 spans per step), placed outside the tree.
- Every new-behavior criterion is red now, for the right reason. `git status --porcelain --untracked-files=all` was unchanged after every probe.
  - Step 1: `wait` is an invalid argparse choice (exit 2), the selftest labels are missing, and the docstring and message text are absent.
  - Step 2: the template, messenger, TOML, and doc texts are absent.
  - Steps 3 and 4: the files do not exist.
  - Every scope criterion is green.
- Every guard is green now at HEAD 4689af2: verified by running each one.
  - messages selftest PASS; tickets selftest PASS;
  - `codex_roles.py generate --check`;
  - check.sh exit 0 in 252 s;
  - check-packaging exit 0;
  - `git diff --check`;
  - the em-dash diff guard;
  - the messenger-words loop.
- Each guard was seen red, on a copy or fixture outside the tree:
  - the messages selftest guard exited 1 on a copy with `'wait'` added to `want` and the template unchanged;
  - the tickets selftest exited 1 on a copy without the `messages.write_entries` call;
  - `codex_roles.py generate --check` exited 2 on a copy with messenger.md edited;
  - the messenger-words loop exited 1 on a fixture without `model: claude-haiku-4-5`;
  - check-packaging exited 1 on a `git archive` copy with a plugin dropped from `.claude-plugin/marketplace.json`;
  - `git diff --check` exited 2 on trailing whitespace in a scratch repo;
  - the em-dash guard exited 1 on a scratch-repo fixture holding the character;
  - check.sh fails whenever `codex_roles.py generate --check` fails, because check.sh:12 sets `fail=1` on that call.

## Risks
- A live host may still poll or loop despite the prompt. It may re-run `wait`, run `count` or `list`, background the call, or (on Codex) skip `yield_time_ms` and poll with `write_stdin`. The arm then records `result=fail`, step 4 ends blocked, and the replan asks the user whether to rerun, change the prompt, or accept the finding. The plan does not hide a fail.
- Codex may clamp `yield_time_ms` below the wait's run time. The observed 30000 ms covers a wait that returns about 20 s after launch, but a slow first call could push past it.
- A host that takes more than 20 s to make its first call gets `wait_before_send=no` and fails. The record must then say that this is a failure of the experiment's timing, not of `wait`.
- `poll_calls` counts call kinds anywhere in the run. A host that runs `list` after `wait` returned, to double-check, fails even though it did not poll for arrival. The prompt asks only for read, reply, and ack.
- If Codex auth or network fails at build time, the Codex arm is unverified (allowed), and only the Claude arm proves the feature.
- Timing checks can flake on a heavily loaded host: selftest case 1 (under 2 s), case 2 (wakes before 10 s), and step 1 criterion 2 (under 3 s).
- check.sh took 252 s, close to the default 300 s `--guard-timeout` of `steps.py split --only`. A `split --only 5` should pass a larger `--guard-timeout`, for example 900.
- The `[0-9]{1,9}` cap gives `--interval` a de facto maximum of 999999999 seconds, a choice beyond the handoff's "minimum 1". It has no practical effect, because each sleep is capped by the time left, at most 600 s.
- `docs/codex-role-execution.md:27` still says the Claude messenger's polling needs Monitor or a loop. That remains true for `count`-based polling, but it does not mention `wait`.
