---
id: T-0187
title: "board.py --overview: queue, running roles, supervisor, unread mail from the folders"
type: feature
status: dropped
size: L2
priority: P2
depends: [T-0183]
created: 2026-10-01
---

## Goal
One command shows the work queue, the running roles, the supervisor status, and the unread messages, read from the existing folders alone.

## Intent
- Do: add `board.py --overview` (in `plugins/sdlc-lite/scripts/board.py`) that prints four labeled sections: Queue (tickets by `status` with counts and the ready and blocked lists, from ticket front matter under the ticket root), Running (every `*.running` marker with role, level, task, and age), Supervisor (`.sdlc/supervisor/status.json` when present, else `not configured`; per receiver state and last wake), and Mail (per receiver, the counts in `new/`, `read/`, `done/` from `.sdlc/messages/`, and the ids of unread messages in `new/`, never a body). It uses no new store, writes nothing, tolerates every missing folder with a `none` line, and keeps the existing default board, `--summary`, and `--lanes` outputs unchanged. Document it in `docs/references/sdlc-internals.md`, the `board` skill, and the router in `.sdlc/AGENTS.md` (through the code that generates it).
- Non-goals: any new state file, color, or interactive mode; changing the supervisor or mailbox.
- Done when: the selftest and common checks pass.

## Context
`board.py` already reads tickets with `tickets.py`'s parser and has `--lanes`; `*.running` markers are written by `run.sh`; the mailbox layout is `new/`, `read/`, `done/` per receiver (`plugins/sdlc-lite/scripts/messages.py`); the supervisor status file is defined in T-0183 (`status.json`, one object per receiver with `state`, `last_wake`, `wakes_hour`, `wakes_day`). Until T-0183 lands, the Supervisor section reads whatever `status.json` holds and is tested on a hand-written file in the documented format.

Selftest (board selftest): each section on a seeded temp project (tickets in several statuses, a `*.running` marker, a status file, messages in each folder); a project with none of them prints `none` lines and exits 0; the output holds no message body (a planted marker never appears); the tree is byte-identical after the command (nothing written); the default board output is unchanged (a recorded snapshot). Negative control: a patched copy that prints a body fails the no-body case. Live proof (`docs/reports/board-overview-live-run.md`): run the command in a throwaway project with a running role, a message in each state, and a supervisor status file, and show each section; then in an empty project.

## Constraints
Read-only, folder-driven, no new store. Existing board behavior is unchanged.

## Common rules
Rules for this ticket, from the user (2026-10-01): every folder this ticket adds is self-describing through its own `AGENTS.md` (with a `CLAUDE.md` containing `@AGENTS.md`), so a role that reads one file learns the system and no skill is added; progressive disclosure holds (a short router line in `.sdlc/AGENTS.md`, details in the folder); every status or state transition is covered by a selftest case that asserts the folder or file state and the stamped fields, plus a negative control that fails when the rule is removed; a live run proves the behavior with a negative control and is recorded in a dated `docs/reports/<name>.md` (environment, exact commands, evidence, limits; an arm that cannot run is recorded unverified, never replaced by a fixture); checks to run before merging locally: `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py`, `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`, `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`, and every selftest; update `docs/references/sdlc-internals.md`, `plugins/sdlc-lite/skills/handoff-format/SKILL.md` layout list, and `plugins/sdlc-lite/AGENTS.md` when behavior or layout changes; do not bump versions, tag, push, or publish; generated Codex agent TOML is never edited by hand; no em dashes anywhere.

## Dropped
2026-10-06, by user decision (review of parked tickets): Merged into T-0312: per-repo unread-mail ids and supervisor state go in the fleet-status Moving rows. board.py has no overview and fleet_status.py owns cross-folder status.

## Deferred (history)
Parked by the user on 2026-10-04 (solo is the default lane, chain tuning is parked): not started; resume as a solo ticket after T-0183 lands.
