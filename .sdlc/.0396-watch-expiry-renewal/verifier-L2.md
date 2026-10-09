<!-- role=verifier level=L2 model=opus effort=high -->
## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/messages.py selftest` exits 0 and its case `watch: a lapsed watch reads as no reader, and renew clears it` is ok (the case failed before the change): pass. Evidence: on the built tree the selftest exits 0 (`selftest exit=0`) and prints `ok: watch: a lapsed watch reads as no reader, and renew clears it` and `messages selftest: PASS`. Red control: in a throwaway worktree at `$SDLC_BASE_SHA` (bba732b6), I added the new `case_watch_lapse` to the base `messages.py` and ran it. Result: exit 1 and `FAIL: watch: ... a fresh watch should read reader alive yes with no lapsed line: 0 {... 'listening': 'yes, until ...', ...}`. The base status kv has no `reader alive` key, which matches the criterion's claim that status printed no `reader alive` line. No process-deviations.md exists.
- A lease past its window: `status` exits 3 and prints `reader alive: no` and `lapsed: yes`; a timed-out `handshake` prints `watch lapsed` and the `renew` command: pass. Evidence: CLI scenario on the built tree (register bob, `activate --kind watcher --interval 1 --window 1`, wait 2.2 s). `status` printed `status: expired`, `reader alive: no (expired)` and `lapsed: yes (expired: window ended ...); renew with messages.py renew --receiver bob --worker watch-bob`, exit 3. `handshake --timeout 1` exited 3 with `...; watch lapsed (expired: ...), renew it: messages.py renew --receiver bob --worker watch-bob`. The same scenario against the base script printed only `status: expired` with no reader or lapsed lines, and its handshake had no `watch lapsed` text. Separately, a stalled lease (interval 1, no beat for 4 s) printed `reader alive: no (stalled)` and `lapsed: yes (stalled: ...)`.
- `messages.py renew --receiver R --worker W` on that lease exits 0, `status` then exits 0 with `reader alive: yes`, and `renew` refuses a non-holder, a missing lease and a released lease: pass. Evidence from the built-tree scenario:
  - `renew --receiver bob --worker watch-bob --window 600` exited 0 and printed `renewed bob: watch-bob, was expired, now listening until ...`.
  - `status` then exited 0 with `listening: yes, until ...`, `reader alive: yes` and `renew-by: ...`.
  - Non-holder: exit 1, `other is not the holder of bob (held by watch-bob)`.
  - Missing lease (carol): exit 1, `receiver carol has no activated worker; run messages.py activate first`.
  - After `release`: exit 1, `bob lease is stopped (done); start a new one with messages.py activate`.
  - Renewing the stalled lease also cleared it: `was stalled`, then `status: listening`, `reader alive: yes`.
  - On the base tree, `renew` is an invalid choice (exit 2), so these checks bite.
- `check.py` and `tickets.py check` pass; `codex_roles.py generate --check` and `claude_roles.py generate --check` pass: pass. Evidence: `check.py exit=0` (`ok: 19 role levels, 9 agents, 22 generated definitions checked`). `tickets exit=0`: it printed only warnings about closed tickets and the flat layout, none for 0396. `codex exit=0` (`Codex agent definitions verified`) and `claude exit=0` (`Claude agent definitions verified (22 files)`).
- Intent's "Done when" (a selftest case observed failing first, and the renewal path clears it): pass. Evidence: the red-then-green runs above. The base fails the case and the built tree passes it, and `renew` clears both the expired and the stalled lapse.
- Constraints (no em or en dashes, no push): pass. Evidence: `git diff | grep -nP '[\x{2013}\x{2014}]'` found nothing. `git diff --check` exited 0. `git log` shows HEAD is still bba732b6 with only working-tree changes, so nothing was committed or pushed.

## Out of scope changes
None. Each changed file was checked against the step:
- `.sdlc/0396-watch-expiry-renewal/handoff.md` adds only the `## Acceptance criteria` section. The solo contract requires this at `plugins/sdlc-lite/agents/solo.md:48` ("write the task handoff's `## Acceptance criteria` if it has none").
- `plugins/sdlc-lite/agents/messenger.md` adds one sentence on leasing and renewing a watcher, which is the guidance the step asked for.
- `plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml` carries the same sentence plus a regenerated version hash. `codex_roles.py generate --check` exited 0, so it is in parity.
- `messages.py` holds the `renew` command, the status and handshake lapse lines, the docs, the entry-file `want` set and the selftest case. `case_entry_parses` passes with `renew` added to `want`.

## For the next attempt
None
