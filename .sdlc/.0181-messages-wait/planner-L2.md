<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Add `messages.py wait`, one blocking call that returns as soon as a valid message sits in `new/<receiver>/`. It never claims, moves, writes, or prints a body. Document it in the entry files, the messenger agent, and the docs, and record a live proof on Claude Code and Codex.

## Step 1: messages.py wait subcommand and its selftest cases
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Targets: `plugins/sdlc-lite/scripts/messages.py` only. Depends on: none.

1. Add `cmd_wait(a)`, register it in `COMMANDS`, and add a `wait` subparser to `parser()`.
   - Subparser: `allow_abbrev=False`, help `block until a message is in new/<receiver>/; never claims it`.
   - Flags: `--receiver NAME`, `--timeout SECONDS` (help: default 120, 1 to 600), and `--interval SECONDS` (help: default 5, at least 1).
   - Parse `--timeout` and `--interval` as strings (`default=None`, no `type=`). An argparse `type=int` would make a non-integer a usage error (exit 2), and the handoff requires exit 1.
2. Validate in this order, each failure raising `Refuse` with a `messages.py: <reason>` stderr line (exit 1, nothing on stdout, nothing written):
   - receiver through `arg_name(a.receiver, '--receiver')`;
   - timeout: the value must fullmatch `[0-9]+` and lie between 1 and 600, otherwise `--timeout must be an integer from 1 to 600: <short(value)>`;
   - interval: the value must fullmatch `[0-9]+` and be at least 1, otherwise `--interval must be an integer of at least 1: <short(value)>`. There is no interval maximum; each sleep is `min(interval, time left)`.
3. Add a helper `wait_ready(mbox, receiver)`. It returns a sorted list of `(mid, path)` for each id in `message_ids(os.path.join(mbox, 'new', receiver))` whose `load_or_none(path, 'new', receiver)` is not None.
   - It catches `Refuse` from an invalid file and skips that file, so a malformed file never wakes a waiter and never makes `wait` exit 1. Evidence: `load` raises `Refuse` on an invalid file (messages.py:413-420), so a bare `load_or_none` reuse would make `wait` exit 1 like `count` (`case_malformed` asserts `count` refuses). Handoff case 5 says wait "ignores" a malformed file, with no wake.
   - `count` itself is not changed (non-goal).
4. `cmd_wait` holds exactly one line with the literal text `ready = wait_ready(mbox, receiver)`. The negative control patches that anchor. It works on a monotonic deadline:
   - Check at once, before any sleep. When `ready` is non-empty, `emit` one `<id>\t<absolute path>\n` line per entry (sorted by id) and return 0.
   - Otherwise, once the deadline has passed, `emit('no new messages\n')` and return 3. Otherwise `time.sleep(min(interval, remaining))` and loop.
   - A missing mailbox creates nothing. `wait` never calls `claim`, `write_entries`, `deliver`, or `Lock`, and never prints front matter or a body.
   - `main` already returns the command's code, so exit 3 needs no other change.
5. Docstring updates:
   - Usage gets `messages.py [--root DIR] wait --receiver NAME [--timeout SECONDS] [--interval SECONDS]`.
   - The exit paragraph adds `Exit 3 only when wait times out.`
   - Commands gets a `wait` entry stating the polling, output, defaults, ranges, that it skips an invalid file, and that it never claims, moves, writes, stamps, or prints a body.
   - The "Every subcommand validates every message file it opens or counts" sentence names `wait` as the exception that skips an invalid file.
   - The Layout sentence "list, count, and expire on a missing mailbox create nothing" includes `wait`.
   - The metavar list in `add_subparsers` gets `wait`.
6. Add seven selftest functions in the existing `Harness`/`Box` style, appended to `SELFTEST_CASES` with exactly these labels. Use timeouts of 1 to 3 seconds except case 2's 10.
   1. `wait: a present message returns at once, state unchanged`
      - Factor the body into `st_wait_present(h)`, which raises `SelftestFail`.
      - Send, snapshot with `b.snap()`, then run `wait --receiver bob --interval 5 --timeout 3`.
      - Assert: exit 0 in under 2 s; stdout exactly `<id>\t<path>\n`; the file still sits only in new/bob with the same bytes and an empty `read_time`. A failure says `wait changed the mailbox` when the snapshot differs.
   2. `wait: wakes on a message sent mid-wait`
      - Start `subprocess.Popen` on `wait --receiver bob --timeout 10 --interval 1`, sleep about 1.5 s, then `b.send`.
      - Assert it exits 0 before the timeout and its stdout's first field is the sent id.
   3. `wait: timeout exits 3, state unchanged`
      - On a box holding a message for carol only, run with `--timeout 1 --interval 1`.
      - Assert exit 3, stdout exactly `no new messages\n`, and `snap()` unchanged.
   4. `refused: wait with a bad receiver, timeout, or interval`
      - Call `b.refused` with `--receiver Bob`, `--timeout 601`, `--timeout 0`, `--timeout 1.5`, `--interval abc`, and `--interval 0`.
   5. `wait: ignores a malformed file and another receiver`
      - `b.put('bob', '20260101T000000000000Z-alice-garbage', b'not a message\n')` plus a valid message for carol.
      - Assert exit 3 with `no new messages`.
      - Then send to bob, run wait again, and assert stdout is exactly that one id line, without the garbage id.
   6. `wait: never prints a body`
      - Use a body holding a unique marker and assert neither stdout nor stderr contains it.
   7. `wait: a claiming wait is caught`
      - Copy this file's source into `h.fresh('patched')/messages.py` with the anchor replaced. The replacement keeps the anchor line, then for each `(mid, path)` calls `os.makedirs(os.path.join(mbox, 'read', receiver), exist_ok=True)` and `claim(path, msg_path(mbox, 'read', receiver, mid))`.
      - Assert the anchor occurs exactly once in the source.
      - Run `st_wait_present` on a `Harness` whose `me` is the patched copy. Assert it raises `SelftestFail`; a normal return fails the case.

Focused check: `python3 plugins/sdlc-lite/scripts/messages.py selftest`. Contract dependents: `case_entry_parses` pins the set of subcommands the entry files run. This step leaves `ENTRY_TEMPLATE` unchanged, so that set stays correct; step 2 extends both together.
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
Depends on: step 1.

1. `ENTRY_TEMPLATE` in `plugins/sdlc-lite/scripts/messages.py`:
   - Read section: add a sentence with the code span `python3 "{{scripts}}/messages.py" wait --receiver <name> --timeout <seconds> --interval <seconds>`. It says that `wait` blocks until a message is in `new/<name>/`, prints `<id>` and the path per message (the id is the first tab-separated field), exits 3 with `no new messages` at the timeout, and never claims, so the message is then claimed with `read`.
   - Messenger section: add a paragraph with the code span `python3 "{{scripts}}/messages.py" wait --receiver <harness> --timeout 100 --interval 10`. It says that `wait` is the cheaper alternative to a polling subagent while the parent is active: the messenger may run it in its loop, or the parent may skip the messenger and call it itself. It also says `wait` returns only into an active parent and does not wake an idle host (T-0180), and that the timeout stays under Claude Code's default 120-second Bash command limit.
   - Change the first Messenger sentence's `(count, then list and read)` to `(wait, or count then list, then read)`.
   - Add no new heading, so `ST_HEADINGS` stays unchanged.
2. In `case_entry_parses`, add `'wait'` to `want`. This is the contract dependent of the template change, since it pins the subcommands the entry files run. `tickets.py roadmap` writes the same template through `messages.write_entries`, and its selftest pins only file presence and restore behavior (tickets.py:3594-3623). It needs no edit; run it as a check.
3. `plugins/sdlc-lite/agents/messenger.md` Loop, rewritten:
   1. Run `messages.py wait --receiver <harness> --timeout 100 --interval 10`. Exit 3 means nothing arrived: run it again.
   2. Claim each message `wait` printed with `messages.py read <id> --receiver <harness>`, where `<id>` is the first tab-separated field of its line.
   3. Report as now.
   - Add a sentence that the parent may skip the messenger and call `wait` itself.
   - Under Host limits, note that on Claude Code `wait` is one foreground Bash call and needs no Monitor.
   - Keep the words `check.py` `MESSENGER_WORDS` pins (`model: claude-haiku-4-5`, `messages.py`, `.sdlc/messages/AGENTS.md`).
4. Run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` to regenerate `plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml`. Never edit it by hand.
5. `docs/maintenance/sdlc-internals.md`, the `scripts/messages.py` entry:
   - Add `` `wait` `` to the subcommand list, with its output, exit 3 on timeout, the defaults and ranges, that it skips an invalid file, and that it never claims.
   - Add the seven wait selftest cases to the coverage sentence.
6. `docs/ticket-stages/design.md`:
   - In the Host limits bullet, add that `messages.py wait` is one blocking call a parent can make instead of a polling subagent, and that it still does not wake an idle host.
   - In the line-77 Status paragraph, add that T-0181 built `messages.py wait`.
7. `docs/codex-role-execution.md` line 27 is left unchanged on purpose. It describes the messenger's polling and host limits, which stay true, and the handoff does not list it.

Focused checks: messages selftest, tickets selftest, `codex_roles.py generate --check`.
### Acceptance criteria
- `python3 -c 'import sys; sys.path.insert(0, "plugins/sdlc-lite/scripts"); import messages; t = messages.ENTRY_TEMPLATE; r = t.split("\n## Read\n", 1)[1].split("\n## ", 1)[0]; m = t.split("\n## Messenger\n", 1)[1].split("\n## ", 1)[0]; assert "messages.py\" wait --receiver" in r, "read"; assert "messages.py\" wait --receiver" in m, "messenger"; assert "idle" in m, "idle"'`
- `python3 plugins/sdlc-lite/scripts/messages.py selftest | grep -qxF "messages selftest: PASS"`
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`
- `grep -qF "messages.py wait --receiver <harness>" plugins/sdlc-lite/agents/messenger.md`
- `grep -qF "messages.py wait --receiver <harness>" plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `grep -qF "\`wait\`" docs/maintenance/sdlc-internals.md`
- `grep -qF "messages.py wait" docs/ticket-stages/design.md`
- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e plugins/sdlc-lite/scripts/messages.py -e plugins/sdlc-lite/agents/messenger.md -e plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml -e docs/maintenance/sdlc-internals.md -e docs/ticket-stages/design.md)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vxF -e plugins/sdlc-lite/scripts/messages.py)"`

## Step 3: Live proof of wait on Claude Code and Codex
level: L3
### Do
Depends on: steps 1 and 2.

1. Create the probe `docs/reports/messages-wait-live-run/probe.py`, modelled on `docs/reports/messages-live-run/probe.py`. Reuse its setup and the same isolation:
   - setup: temp project, `git init`, empty commit, `tickets.py --root .sdlc roadmap`;
   - environment stripped of `CLAUDECODE`, `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA`, `CLAUDE_CODE_*`, and `SDLC_*`;
   - Claude `--safe-mode --disable-slash-commands`;
   - Codex `--ignore-user-config` plus the two control calls;
   - the 2-second state sampler and an independent message parser.
2. The probe has arms `claude` and `codex`, plus `selftest`.
   - Prompt, with `<harness>` set to `claude` or `codex` and `<plugin>` the absolute plugin path: `Run this as one shell command and wait for it to finish: python3 <plugin>/scripts/messages.py wait --receiver <harness> --timeout 120 --interval 2. When it prints a message id, handle that message as .sdlc/messages/AGENTS.md says: claim it with read, reply when follow_up_requested is true, then ack it. Then stop.`
   - The host starts first. A separate process sends `--receiver <harness> --sender probe --topic live-probe --follow-up true "What is 2 + 3? Answer in one line."` 20 seconds later.
   - Claude command: `claude -p --safe-mode --disable-slash-commands --dangerously-skip-permissions --model sonnet --effort low --output-format stream-json --verbose --no-session-persistence -- "<prompt>"`.
   - Codex command: `codex exec --ignore-user-config --json --color never -C <project> -m gpt-6.1-sol -c model_reasoning_effort="medium" -c approval_policy="never" --sandbox workspace-write "<prompt>"`. These are the model and effort of `messages-live-run.md`'s path-only arm.
3. From the host's own tool-call trace, the probe counts the shell calls that run `messages.py` with `wait`, and the ones with `count` or `list` or a `sleep`. It also takes the message ids printed in the wait call's output. It prints:
   - `wait_calls=<n> poll_calls=<n>`;
   - `wait_returned=<id or ->`;
   - the stamps line `send_time=... read_time=... ack_time=...`;
   - `result=pass|fail|unverified`.
   - The oracle passes only when all of these hold: `wait_calls=1`; `poll_calls=0`; `wait_returned` equals the sent id; the message is only in `done/<harness>/`; `send_time <= read_time <= ack_time`; the outcome is not expired; a reply with `re: <id>` exists; the run is isolated.
   - Exit codes: 0 pass, 1 fail, 2 setup error, 3 unverified.
4. `probe.py selftest` runs offline against the real `messages.py` and prints `probe selftest: PASS`. It must show:
   - one wait returning the id plus read, reply, and ack gives pass;
   - two wait calls give fail;
   - a `count` call gives fail;
   - no wait call gives fail.
5. Run each arm once and save its stdout with `| tee` as `docs/reports/messages-wait-live-run/claude.txt` and `codex.txt`. If a host cannot run, the arm's file holds `result=unverified` and the reason. Never use a fixture.
6. Write `docs/reports/messages-wait-live-run.md` with:
   - a `Recorded: <date>` line;
   - `## Environment`: host versions, models from the hosts' own records, the plugin commit (`git rev-parse --short HEAD`), and a statement that steps 1 and 2 were uncommitted working-tree changes when the arms ran (show `git status --porcelain -- plugins/`);
   - `## Method`: exact commands and prompts;
   - one section per arm with its evidence quote and a `Result: pass`, `Result: fail`, or `Result: unverified` line;
   - `## Limits`: a single run per arm, one machine, an active parent only, no idle-host wake.
7. Add one line for it to the validation list in `docs/README.md`, next to the Messages live run line.
### Acceptance criteria
- `python3 docs/reports/messages-wait-live-run/probe.py selftest | grep -qxF "probe selftest: PASS"`
- `for a in claude codex; do grep -qxE "result=(pass|fail|unverified)" docs/reports/messages-wait-live-run/$a.txt || exit 1; done`
- `for a in claude codex; do f=docs/reports/messages-wait-live-run/$a.txt; if grep -qx "result=pass" "$f"; then grep -qx "wait_calls=1 poll_calls=0" "$f" || exit 1; grep -qE "^send_time=[^ ]+ read_time=[^ ]+ ack_time=" "$f" || exit 1; fi; done`
- `f=docs/reports/messages-wait-live-run.md; grep -qE "^Recorded: 2026-" $f && for h in "## Environment" "## Method" "## Limits"; do grep -qxF "$h" $f || exit 1; done && test "$(grep -cE "^Result: (pass|fail|unverified)" $f)" -ge 2`
- `grep -qF "validation/messages-wait-live-run.md" docs/README.md`
- `! grep -rqF "—" docs/reports/messages-wait-live-run.md docs/reports/messages-wait-live-run/probe.py`
- `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e plugins/sdlc-lite/scripts/messages.py -e plugins/sdlc-lite/agents/messenger.md -e plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml -e docs/maintenance/sdlc-internals.md -e docs/ticket-stages/design.md -e docs/README.md)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" | grep -vE "^docs/reports/messages-wait-live-run(\.md|/)")"`

## Step 4: Gates green
level: L2
### Do
Depends on: steps 1, 2, and 3.

1. Run every project gate from the repository root:
   - `bash plugins/sdlc-lite/scripts/check.sh`, which includes the messages selftest, `check.py`, and the tickets and run selftests;
   - `python3 scripts/check-packaging.py`;
   - `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`;
   - `git diff --check`.
2. Fix any red the earlier steps introduced, inside the files those steps changed. A gate already red at the build-start HEAD is reported as `inherited red`.
3. Confirm no em dash was added in any changed file.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `git diff --check`
- (guard) `! git diff "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -E "^\+" | grep -qF "—"`

## Assumptions
- `count` refuses a malformed file instead of skipping it. Verified by messages.py:413-427 (`load` raises `Refuse`) and `case_malformed`, which asserts `count` is refused with `invalid message`. So `wait` catching `Refuse` and skipping is a settled departure, and only for `wait`, to honor handoff case 5.
- Builders never commit, so every step shares the same `SDLC_BASE_SHA` and the scope criteria grow step by step. Verified by the planner rules and the run.sh base-sha description in docs/maintenance/sdlc-internals.md:11.
- `case_entry_parses` pins the set of entry-file subcommands, so adding a `wait` span to `ENTRY_TEMPLATE` requires adding `'wait'` to `want`. Verified at messages.py:1729-1731. `ST_HEADINGS` is unaffected because no heading is added (messages.py:1629).
- The tickets.py selftest does not pin entry-file text, only presence and restore. Verified at tickets.py:3594-3623.
- The Codex path-only model is `gpt-6.1-sol` at effort `medium`. Verified in docs/reports/messages-live-run.md (Environment and Host commands).
- Both host CLIs are installed: `claude --version` printed 2.1.286 and `codex --version` printed 0.159.2.
- The current gates are green and side-effect free: `bash plugins/sdlc-lite/scripts/check.sh` exited 0 and left `git status --porcelain` unchanged, and `check-packaging.py`, `codex_roles.py generate --check`, `check.py`, and `git diff --check` all exited 0.
- Every step-1 to step-3 new-behavior criterion is red now for the right reason: `wait` is an invalid argparse choice, and the docs, template, and probe files lack the text.

## Risks
- Claude Code's interactive Bash tool stops a command at 120 s by default. The live-proof prompt uses `--timeout 120` as the handoff requires, which is safe only because the send comes at about 20 s. The messenger uses `--timeout 100` for that reason.
- A host may still loop (re-run `wait`, or add `ls` or `sleep` calls) despite the prompt, so a Claude or Codex arm can record `result=fail`. Step 3 then reports a fail, not a pass. The criteria accept a recorded fail or unverified so the evidence stays honest, and the conductor should treat a fail as a finding.
- The timing assertions in selftest cases 1 and 2 (under 2 s; wake before the 10 s timeout) can flake on a heavily loaded host.
- Codex auth or network may be unavailable at build time. That arm is then recorded as unverified, and the ticket's "live proof recorded" condition is only partly met.
