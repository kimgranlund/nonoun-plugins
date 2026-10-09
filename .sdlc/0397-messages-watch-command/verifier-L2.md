<!-- role=verifier level=L2 model=opus effort=high -->
## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/messages.py selftest` exits 0 and prints `ok: watch: one process polls, beats and renews, so status reads listening`: pass. Evidence: I ran it on the built tree. It exited 0 with 47 `ok` lines, line 46 was `ok: watch: one process polls, beats and renews, so status reads listening`, and it ended `messages selftest: PASS`. The ticket says the case must be "observed failing first", so I checked that it can go red. A driver under `$SDLC_TMP_WORKTREES/drv` ran only `case_watch_command` in four setups:
  - Built tree: `CASE: ok`.
  - Pre-build base worktree at `9ac1231d` with the new case transplanted in (there is no `watch` command there): `CASE: FAIL ... should read listening: 3 {... 'status': 'expired' ...}`.
  - Mutant with the beat line `lease['last_beat'] = stamp(now)` removed: `FAIL ... 'status': 'stalled'`, while `expires` was still renewed. So the beat part bites.
  - Mutant with the renew assignment replaced by `pass`: `FAIL ... 'status': 'expired'`, while `last-beat` was fresh. So the renew part bites.
  - The case's stop leg needs `stalled` or `expired`, plus `reader alive: no...`, 3.6 s after the kill, and it passed in the full selftest.
  - No `process-deviations.md` exists. The case's own failing-first record is the base run above.
- `messages.py watch --help` exits 0 and lists --receiver, --worker, --interval and --timeout: pass. Evidence: it exited 0, and the usage line was `messages.py watch [-h] [--receiver NAME] [--worker NAME] [--interval SECONDS] [--timeout SECONDS]`, with a help line for each option.
- `python3 plugins/sdlc-lite/scripts/check.py` and `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exit 0: pass. Evidence: `check exit=0`, with the last line `ok: 19 role levels, 9 agents, 22 generated definitions checked`. `tickets exit=0`, with `ok: 390 tickets, roadmap current`. The only other output was warnings about closed tickets and the layout, which the diff did not touch.
- The mailbox AGENTS.md template (Watch expiry bullet) and `agents/messenger.md` document `watch`, and `claude_roles.py generate --check` and `codex_roles.py generate --check` pass: pass. Evidence:
  - `plugins/sdlc-lite/scripts/messages.py:366`: the Watch expiry bullet now says `make its command python3 "{{scripts}}/messages.py" watch --receiver <name> --worker <worker>, which polls ... beats on every poll, renews the window when half of it is left`.
  - `plugins/sdlc-lite/agents/messenger.md:38`: the Monitor command should be `messages.py watch --receiver <name> --worker <worker>`.
  - `Claude agent definitions verified (22 files)` with exit 0, and `Codex agent definitions verified` with exit 0.
- Ticket Done-when, "a receiver run through watch for longer than 3 x interval is reported alive, and one that stops is reported stalled": pass. Evidence: the same case and red controls as the first criterion. It ran for 4.6 s at a 1 s interval (more than 3 x interval) and read `listening` with `reader alive` `yes`. After the kill it read non-listening with exit 3.
- Contract dependents of the new subcommand: pass. Evidence: `git grep` over the repo, excluding messages.py, found no other copy of the subcommand list. `case_entry_parses` now expects `watch` in the entry files and passes in the selftest. `python3 scripts/check-packaging.py` gave `PASS`. `git diff --check` was clean, and a grep of added lines for em and en dashes found none (exit 1).

## Out of scope changes
None.
- `plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml` is generated from `messenger.md`. `codex_roles.py generate --check` confirms parity, so it belongs to the change.
- `.sdlc/0397-messages-watch-command/handoff.md` gained an `## Acceptance criteria` section, the solo lane's own criteria. I read the diff: it adds lines only, does not change the Goal, Intent or Done-when, and matches the ticket.
- There is no `builder-*.md`. `runs.jsonl` shows a solo L2 run, so I checked every claim directly on the tree.

## For the next attempt
None.
