## Task goal
A parent host can wait for mail with one blocking command instead of a polling subagent, and the command never claims, moves, or prints a message body.

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
   - `docs/validation/messages-live-run/probe.py`: it pins no entry-file text.

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
