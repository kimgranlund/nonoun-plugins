# Release 0.20.2

Recorded: 2026-10-01. SDLC Lite 0.20.2. Progressive Context stays at 0.1.2 (no change since 0.19.0). Previous release: SDLC Lite 0.20.1 (8766f3d, tag `v0.20.1`).

## What changed for consumers

Two additions to the `.sdlc/` folder system. The `tickets/` root is opt-in and a repository that changes nothing keeps its flat ticket folders. The router and mailbox entry files are written on the first `new`, `close`, `roadmap`, `archive` or `number` call (see Upgrade notes).

| Change | Detail | Ticket |
| --- | --- | --- |
| Ticket root and router | `ticket_root: tickets` in `.sdlc/config` keeps ticket folders under `.sdlc/tickets/`; the default `.sdlc/` is unchanged and a ticket left directly in `.sdlc/` fails `check` once the line is set. `tickets.py roadmap`, `new`, `close`, `archive` and `number` regenerate a managed router block in `.sdlc/AGENTS.md` (stage counts, open tickets, and the create, claim, and close procedures) and keep `.sdlc/CLAUDE.md` importing it, plus `tickets/AGENTS.md` and `tickets/CLAUDE.md` when `ticket_root` is set; `check` fails when any is missing or stale. New optional front matter `claimed_by`; `new`, and the follow-up tickets `close` files, stamp a `router:` line. `board.py` lists tickets under the ticket root | T-0175 |
| Mailbox | `scripts/messages.py` (`send`, `list`, `read`, `ack`, `reply`, `expire`, `count`, `selftest`) writes a git-ignored mailbox at `.sdlc/messages/` with `new/`, `read/`, `done/` per receiver. A message carries `send_time`, `read_time`, `sender`, `receiver`, `topic`, `follow_up_requested` and `protocol`; `read_time` and `ack_time` are stamped by the script at the transition. A message with `follow_up_requested: true` cannot be acked without a reply. Claim is an atomic rename, so one of two readers wins. Bodies are data and cannot authorize a publish. `run.sh` prints one stderr line when new messages wait for the role or backend, and never changes its exit code | T-0177 |
| Messenger agent | `agents/messenger.md`, a session sub-agent (not a `run.sh` role) that polls `messages.py count` every 10 seconds and tells its parent. Claude: `claude-haiku-4-5`. Codex: generated `sdlc-messenger-l1` on `gpt-5.6-terra` low from `adapters/codex/models.json`, with `sandbox_mode = workspace-write` so it can move message files. `check.py` checks its file and Codex mapping and excludes it, like the conductor, from the `run.sh` agreement check | T-0178 |
| Self-describing folders | `.sdlc/AGENTS.md`, `.sdlc/tickets/AGENTS.md`, `.sdlc/messages/AGENTS.md` and a short `AGENTS.md` with a `CLAUDE.md` import in each of `new/`, `read/`, `done/` carry the procedures (`.sdlc/tickets/AGENTS.md` exists only when `ticket_root: tickets` is set), so a role that reads one message or ticket learns the system with no skill | T-0179 |
| Also in the diff | Root `AGENTS.md` names the `conductor` and `messenger` as session agents; `onboard.py` gives mailbox ignore guidance; `traces/ingest.py` reads tickets under `ticket_root` (`fanout.py` does not, see limits). T-0176 was filed for the mailbox, then split into T-0177, T-0178 and T-0179 and never built as filed | T-0176 |
| Design and docs | `docs/ticket-stages/design.md` (design, with the transition table), `docs/maintenance/sdlc-internals.md`, `docs/codex-role-execution.md`, plugin `AGENTS.md` and the ticket, handoff-format and level-rubric skills describe the above | T-0175 to T-0179 |

Every ticket change was built by a builder role and checked by an independent verifier through `scripts/run.sh`. The version bump and this record were made by hand and fact-checked by an independent Opus reviewer in two passes on 2026-10-01; the first failed on points corrected here and the second passed. The review text is not committed. A plan-reviewer sent the T-0177 and T-0179 plans back for replans before any build, and T-0178 was replanned once after a step criterion proved wrong.

## Upgrade notes

- Run `tickets.py --root .sdlc roadmap` once after upgrading (from the plugin's `scripts/` folder; in this repository `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc roadmap`). Until then `tickets.py check` fails with `AGENTS.md: router block missing` and `CLAUDE.md: no @AGENTS.md import`, even for a repository that keeps flat ticket folders. The command writes `.sdlc/AGENTS.md`, `.sdlc/CLAUDE.md` and the `.sdlc/messages/` entry files.
- To adopt the `tickets/` layout, add `ticket_root: tickets` to `.sdlc/config` and move the ticket folders; `check` names any left behind.
- Codex projects that installed generated agents should run `python3 plugins/sdlc-lite/scripts/codex_roles.py install` to receive `sdlc-messenger-l1`; the planner and plan-reviewer agents were regenerated for the updated skill text.
- `.sdlc/messages/` is added to this repository's `.gitignore`. The mailbox also ignores itself through a generated `.gitignore`; `onboard.py` still tells consumers to keep `.sdlc/messages/` in their own `.gitignore` as well.

## Known limits

- The router live run for T-0175 is unverified: the fresh role found the router through nested entry-file loading, so it does not show a path-only reader (`docs/validation/ticket-root-router-live-run.md`).
- The mailbox live runs (`docs/validation/messages-live-run.md`) ran once per arm on one machine, on plugin commit f93894d (T-0179 steps 1 and 2), not the release tip. The Claude path-only arm ran in safe mode, so nested `CLAUDE.md` loading was not exercised. They show a fresh role given only a message path doing read, reply and ack on both hosts, with `send_time <= read_time <= ack_time`, and the real `messenger` moving a message new, read, done on both hosts. The negative control failed as intended, on Claude Code only.
- A conductor session cannot spawn the `messenger`: `block-role-spawn.sh` denies every `sdlc-lite:` agent spawn from `sdlc-lite:conductor` (`messages-live-run.md`). A parent must start it another way until that hook is changed.
- The 10-second poll cadence was not measured. The Claude `messenger` sometimes returns "polling" without claiming, so a parent may need to spawn it again (noted in `.sdlc/notes.md`).
- The two-reader race control catches a non-atomic claim only when the copy and delete straddle the barrier (noted in `.sdlc/notes.md`).
- `fanout.py` does not support `ticket_root` yet (noted in `.sdlc/notes.md`).
- `shellcheck` is not installed, so `run.sh` and `run-selftest.sh` were not shellchecked.
- No stage folders (`inbox/`, `ready/`, `done/`) for tickets were built; the design chose a router with generated stage lists instead.

## Checks run for the release

Run from the repository root on main after the merge (f6366f6) and the version bump, 2026-10-01, all exit 0:

- `bash plugins/sdlc-lite/scripts/check.sh` (shellcheck skipped, not installed)
- `python3 scripts/check-packaging.py`
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- `python3 plugins/sdlc-lite/scripts/messages.py selftest`
- `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`
- `python3 plugins/sdlc-lite/scripts/codex-selftest.py`
- `git diff --check`
- Version parity: both SDLC Lite manifests read 0.20.2; Progressive Context manifests read 0.1.2.

The branch (4204bad, before the merge into main) passed a second independent L3 verifier after a first pass failed; its result files are in the build worktree and are not committed, and the checks above were rerun on main after the merge. The first pass failed (the first-pass causes were a stale router, from closing tickets with the older `tickets.py`, and a verification criterion that miscounted pre-existing em dashes in generated Codex agent files). The verifier injected defects (`read_time` stamped at send, router counts left stale after a close, a removed Codex mapping) and each was caught.
