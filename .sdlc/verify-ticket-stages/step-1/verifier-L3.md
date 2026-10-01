<!-- role=verifier level=L3 model=fable effort=xhigh -->
## Verdict
fail

## Criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: exit 0 on the tree at a38735e (3:02 wall, 343 `ok` lines, `messages selftest: PASS`, `run selftest: PASS`, `ok: plugin validate`). It can go red: under my injections in a throwaway worktree its component legs exited non-zero (messages selftest, tickets selftest, `check.py`, `run-selftest.sh`, `generate --check`). Unverified part: `skip: shellcheck not installed`, so the `run.sh` and `run-selftest.sh` edits were not shellchecked on this host.
- (guard) `python3 scripts/check-packaging.py`: pass. Evidence: `PASS: catalog parity, identity, skill routes, hook isolation and context links`, exit 0. Red on a fixture (Claude manifest version bumped alone): `FAIL: sdlc-lite: version differs by host`, exit 1.
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: pass. Evidence: `Codex agent definitions verified`, exit 0. Red on three fixtures (mapping removed, TOML removed, TOML hand-edited): `generated agent drift`, exit 2.
- (guard) `python3 plugins/sdlc-lite/scripts/messages.py selftest`: pass. Evidence: exit 0, 24 `ok` cases, `messages selftest: PASS`. Red under 11 injections (listed under the injected-defects criterion).
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: pass. Evidence: exit 0, `tickets selftest: PASS`. Red under 5 router injections.
- (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py`: pass. Evidence: exit 0, `Installed 25 project agents`. Red on a fixture (planner TOML replaced with invalid TOML): `FAILED (failures=4, errors=10)`, exit 1. It stays green when the messenger mapping is removed from `models.json`; `check.py` and `generate --check` cover that case.
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`: fail. Evidence: `AGENTS.md: router block stale; run tickets.py --root .sdlc roadmap`, exit 1. Same output and exit 1 in a throwaway worktree at `$SDLC_BASE_SHA` (a38735e, equal to HEAD because this step has no build), so it is inherited by the gate rule. Main is green (`ok: 176 tickets, roadmap current`), so the branch brings this red. The committed `.sdlc/AGENTS.md` still lists `ready: 1` with T-0179 and `done: 159`. Each close commit (c211572, 4fb8238, 23be1ad) changed `roadmap.md` and not `.sdlc/AGENTS.md`.
- (guard) `git diff main --name-only -- plugins/sdlc-lite/.claude-plugin plugins/sdlc-lite/.codex-plugin plugins/progressive-context | { ! grep -q .; }`: pass. Evidence: exit 0; both manifests read `"version": "0.20.1"`, as on main; `git diff main --stat -- .claude-plugin .agents` is empty. Red on the version-bump fixture (exit 1).
- (guard) `git diff --check main -- . ":(exclude).sdlc"`: pass. Evidence: exit 0, no output. Red on a fixture (trailing spaces appended to `docs/README.md` in a throwaway worktree): exit 2.
- (guard) em dash count over added lines of `git diff main` (criterion 10): fail. Evidence: exit 1 on the tree and at `$SDLC_BASE_SHA`; the count is 2. Both lines are the single-line `developer_instructions` field in `sdlc-plan-reviewer-l1.toml` and `sdlc-plan-reviewer-l1-alternate.toml`. Em dash characters added are 26 and removed are 26. They come from `skills/checks-that-bite/SKILL.md`, which is unchanged against main. With the generated agents folder excluded, the added-line count is 0, and no file new on the branch holds one. The criterion counts lines, so it cannot pass while `generate --check` holds.
- No requirement in the four closed ticket handoffs is unmet or silently dropped; each gap is named with evidence: fail.
  - T-0175, unmet: the Done-when "the repo's own `.sdlc` still passes `tickets.py --root .sdlc check`" fails at the tip (the check criterion above). It was already unmet at T-0175's own close commit: `git show c211572:.sdlc/AGENTS.md` still lists T-0175 under `ready: 4` with `done: 156`.
  - T-0175, met:
    - The branch's `close` does regenerate the router. Live run in `/tmp/vts-router.e6gzzz` with `ticket_root: tickets`: `new` gave `proposed: 1` with the ticket line; a status edit plus `roadmap` gave `ready: 1`; `claimed_by` showed on the line; `close --reason` gave `done: 1` and `.0001-alpha`.
    - `check` exited 1 for a stale count, a missing `CLAUDE.md` import and a missing block, then 0 after restore. Text added outside the block survived both regenerations.
    - `board.py` selftest has the `ticket_root` cases. `fanout.py` lacking `ticket_root` support is named as a `decide:` item in `.sdlc/notes.md`.
  - T-0175, recorded unverified by the ticket (allowed by its wording): the fresh-role run, `docs/validation/ticket-root-router-live-run.md:99`. I did not rerun it.
  - T-0177, met:
    - Live run in `/tmp/vts-live.YtiNoR`: send, read, reply, ack, with `send_time` 10:35:50.943 <= `read_time` 10:35:51.646 <= `ack_time` 10:35:51.950.
    - Refusals observed: `--read-time` exit 2 (`unrecognized arguments`); `--follow-up maybe`, missing `--follow-up` and receiver `../x` each exit 1 with the count unchanged; ack of an unread message; read by a non-recipient; a second read; ack before a reply on a follow-up message (file stayed in `read/`); ack and read on a done message.
    - Hand-written files with a different `protocol` or `follow_up_requested: maybe` were refused by `read`.
    - `--help` carries the transition table and trust rule. `read` prints the trust line and data markers.
    - The `run.sh` notice is covered by `run-selftest.sh`, which passes.
  - T-0177, coverage gaps (behavior present, no regression test): with the `protocol` value check removed, or the `follow_up_requested` value check removed at send and in files, the selftest still passes.
  - T-0177, race control: it bites only through the test hook. A copy-then-delete placed after the barrier passed the selftest 3 of 3 runs. This is already recorded in `.sdlc/notes.md`, so it is not silently dropped.
  - T-0178, met:
    - `agents/messenger.md` pins `model: claude-haiku-4-5`, defers to `.sdlc/messages/AGENTS.md`, and states authority and host limits per host.
    - `grep -c messenger plugins/sdlc-lite/scripts/run.sh` is 0, and the `run.sh` diff has no model or effort line.
    - `sdlc-messenger-l1.toml` is generated with `gpt-5.6-terra` low.
    - `check.py` item 12 fails on a removed file, mapping or TOML.
  - T-0179, met:
    - No skill added: the skill folder lists match main, and the only files added under `plugins/` are `messages.py`, `messenger.md` and the messenger TOML.
    - Nine entry files are written by `send` and by `roadmap`. Both validation docs are linked from `docs/README.md`.
    - Live evidence rerun on a38735e with `probe.py`: `claude` pass (isolation=yes), `claude --defect` fail exit 1 (empty `read_time`, `ack_time`, no reply), `codex` pass (isolation=yes, 0 sdlc-lite mentions with config ignored), `claude-messenger` pass (new, read, done), `codex-messenger` pass.
    - The Codex spawn was confirmed from rollout files: parent `spawn_agent` with `agent_type` `sdlc-messenger-l1`; child `agent_role` `sdlc-messenger-l1` on `gpt-5.6-terra`. One trial per arm.
  - Unverified: the 10-second polling cadence was not measured. On Claude the messenger claimed only on its fourth spawn.
  - Stale prose, not a ticket requirement:
    - `docs/README.md` still calls the mailbox "(proposed)".
    - `docs/ticket-stages/README.md` says only the router and `tickets/` root are built; `design.md:3` says the bus is built.
    - The `docs/README.md` link text says a fresh role claimed and closed a ticket "from `tickets/AGENTS.md` alone", while that doc's result is unverified.
- At least two injected defects were each caught by a selftest or check, with the defect and the failure stated: pass. Evidence, all in throwaway worktrees at HEAD, each restored after:
  - `read_time` stamped at send in `compose`: `messages selftest: FAIL: create: ... read_time is set in new/`. With the `new/` schema guard also removed: `FAIL: create: created message: read_time is '2026-10-01T10:37:08.729917Z', expected ''`.
  - Router left unchanged after a close (close writes `roadmap.md` only): `tickets selftest: FAIL`, first case `(a) check passes after close: rc=1 AGENTS.md: router block stale`, plus 10 more close cases.
  - `check` ignoring a stale block: `FAIL` on `router: stale count` and `router: claimed_by added`.
  - Three more router injections (missing import ignored, text outside the block overwritten, done tickets listed) each made the tickets selftest exit 1.
  - Messenger mapping removed from `models.json`: `check.py` printed `FAIL messenger: adapters/codex/models.json has no messenger entry`, exit 1; `generate --check` reported an orphan TOML, exit 2.
  - Wrong command in `messages/AGENTS.md`: `--result` in place of `--outcome` failed `entry files: every command parses`; `count` in place of `read` in step 1 failed `entry files: scripted path-only run` with `not read yet`.
  - Follow-up gate removed from `ack`: `FAIL: read to done, follow-up true after a reply`.
  - `run.sh` notice counting the role only: `run selftest: FAIL: notice: role plus backend`. Notice never printed: `FAIL: notice: one message: stderr is ''`.
  - Also caught: non-recipient read allowed, ack of an unread message (both guards removed), reply rule ignoring the topic, `ack_time` not stamped, size cap raised, backward move allowed, expiry notice dropped, mailbox not shared across worktrees.
  - One injection was inert, not a miss: removing only the `state == 'new'` refusal in `ack` left the `read_time` guard to refuse.

## Out of scope changes
None. `git status --short` at the end shows only the runner's own `base-sha` and `verifier-L3.attempt.json` in the step folder, and HEAD is still a38735e. The three throwaway worktrees were removed (`git worktree list` shows none under the tmp prefix).

## For the next attempt
plan defect: criterion 10 (the em dash count guard) counts added lines, and two regenerated single-line TOML fields carry em dashes that already exist on main in `skills/checks-that-bite/SKILL.md`, so it stays red while `generate --check` holds (26 characters added, 26 removed, 0 added lines outside `plugins/sdlc-lite/adapters/codex/agents`). No swap is proposed because the tree also needs a change.

What the branch still needs:
1. Regenerate the router with the branch's own script and commit it: `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc roadmap`. In a throwaway worktree at HEAD this changed only `.sdlc/AGENTS.md` (`ready: 1` to `ready: 0`, T-0179 line dropped, `done: 159` to `done: 160`), and `check` then printed `ok: 179 tickets, roadmap current`.
2. Close tickets with the branch's `tickets.py` from here on. A script without router support leaves the block stale on every close, and main's copy has no `write_router` (count 0). The handoffs say roles run from the main checkout's copy, which fits; I did not confirm which copy ran the closes.
3. Steelman record. Likely rebuttal to item 1: the router went stale only from later closes, so T-0175 was met. It does not hold: the block was already stale in T-0175's own close commit, and the handoff's own check criterion requires green at the tip. One draft fail was dropped: the race control not biting on the production path, because T-0177 asked for exactly that hooked control and the limit is already in `.sdlc/notes.md`.
4. Optional, not blocking: fix the three stale doc lines named above, and add selftest controls for a different `protocol` value and a non-boolean `follow_up_requested` value.
