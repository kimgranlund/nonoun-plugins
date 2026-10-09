<!-- role=verifier level=L2 model=opus effort=high -->
## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/messages.py selftest` exits 0 and includes the cases `entry files: no versioned plugin path, and the watch loop survives a plugin update` and `beat keeps the window; watch extends it`: pass. Evidence: in the built tree it exited 0 with `ok: entry files: no versioned plugin path, and the watch loop survives a plugin update`, `ok: beat keeps the window; watch extends it` and `messages selftest: PASS`. To check that the cases can go red, I ran both through a driver against mutated copies of messages.py under `$SDLC_TMP_WORKTREES/mut`:
  - (A) Commands render the versioned script folder again, which was the pre-fix behavior. Result: `FAIL: entry files ...: AGENTS.md names a versioned plugin folder`.
  - (B) The launcher's sibling fallback is removed. Result: `FAIL: ... the documented watch command exited 2 after the update: messages-run.py: messages.py not found`.
  - (C) `beat` sets `expires` again. Result: `FAIL: beat keeps the window ...: beat moved the expiry`.
  - (D) `watch` never renews. Result: `FAIL: beat keeps the window ...: 'status --receiver bob' exited 3`.
  - Each mutation leaves the other case green, so each case fails only on its own mechanism.
  - No `process-deviations.md` exists, so no failing-first checkpoint was recorded. The mutations above stand in for it.
- `python3 plugins/sdlc-lite/scripts/check.py` exits 0, and fails when a skill, agent, command, hook or Codex adapter file names `sdlc-lite/<digits>.<digits>`: pass. Evidence: in the built tree it printed `ok: 19 role levels, 9 agents, 22 generated definitions checked` and exited 0. In a throwaway worktree at `$SDLC_BASE_SHA` with the built files copied in, I planted versioned paths and it exited 1:
  - Skill, hook and adapter plants: `FAIL skills/board/SKILL.md: names a versioned plugin cache folder "sdlc-lite/0.22"`, `FAIL hooks/_role.sh: ... "sdlc-lite/0.21"` and `FAIL adapters/codex/instructions.md: ... "sdlc-lite/0.22"`.
  - Agent and Codex agent plants (second run): `FAIL agents/scout.md: ... "sdlc-lite/0.22"` and `FAIL adapters/codex/agents/sdlc-scout-l1.toml: ... "sdlc-lite/3.4"`.
  - The plugin has no `commands/` folder (`no matches found: plugins/sdlc-lite/commands/*`). The guard scans it if it ever appears (check.py:1187), so no command file could be planted.
  - check.py also carries in-script negative controls (check.py:1193-1195). I read them, and they ran green in the passing run.
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exits 0: pass. Evidence: printed `ok: 394 tickets, roadmap current` and exited 0; the warnings are about older closed tickets and the layout. Because `entry_files` changed signature and tickets.py calls `messages.write_entries`, I also ran `tickets.py selftest`: `tickets selftest: PASS`, exit 0.
- The generated mailbox `AGENTS.md` runs every command through `<mailbox>/messages-run.py`, and the launcher falls back to the newest sibling `sdlc-lite/<version>/scripts/messages.py` when its recorded folder is gone: pass. Evidence from a live run in a throwaway repo with messages.py installed at `cache/sdlc-lite/0.8.0/scripts`:
  - `register` and `send` generated the entry files. All 24 `python3 "..."` commands in AGENTS.md are `python3 "<repo>/.sdlc/messages/messages-run.py"`.
  - No root or stage AGENTS.md mentions `sdlc-lite/0.8` (`grep -c` gave 0 for all four).
  - The only other `python3` command is `python3 <plugin-root>/scripts/codex_roles.py`, which is not a messages.py command.
  - The launcher records `RECORDED = '.../cache/sdlc-lite/0.8.0/scripts'`.
  - I then renamed 0.8.0 to 0.9.0 and added a 0.10.0 marker script. `messages-run.py count --receiver bob` printed `RAN 0.10.0 ['count', '--receiver', 'bob']`, exit 0, so the sort is numeric and picks the newest.
  - After I removed 0.10.0 it ran 0.9.0 and printed `1`, exit 0.
  - With no version folder left, the selftest's last step (mutation B output above) shows the launcher's clear `CLAUDE_PLUGIN_ROOT` message instead of a traceback.
  - Pre-filing check: I drafted a fail because `docs/references/sdlc-internals.md:43` still says "nine entry files ... rendering `{{scripts}}`" and `scripts/supervisor.py:103` still refers to "mailbox AGENTS.md's {{scripts}}". The builder would answer that no criterion and no part of the Do names those files. I checked the handoff and it does not. I dropped the fail, but both are stale records for a follow-up.

## Out of scope changes
None that matter.
- `.sdlc/0401-messages-stable-entry-point/handoff.md`: the solo appended a 6-line `## Acceptance criteria` section (`git diff`). Each line refines the ticket's Done-when, and no existing text was changed.
- `plugins/sdlc-lite/adapters/codex/agents/sdlc-messenger-l1.toml`: the fingerprint changed from `7b5f7f65b745` to `00fcb5213630` and the messenger.md paragraph was added. This is the regenerated output of the `agents/messenger.md` change, and check.py's generated-definition parity passes.

## For the next attempt
None
