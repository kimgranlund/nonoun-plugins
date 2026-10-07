---
id: T-0175
title: "Opt-in tickets/ root and generated .sdlc/AGENTS.md router"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-09-30
---

## Goal
`tickets.py` can use a `tickets/` ticket root under `.sdlc/` when `<root>/config` says `ticket_root: tickets`, and `tickets.py roadmap` keeps a managed router block in `.sdlc/AGENTS.md` current, so an agent reads one short file and opens only the tickets in the stage it needs.

## Intent
- Do:
  - Honor an opt-in `ticket_root: <dir>` line in `<root>/config` (this build supports the value `tickets`): ticket folders live at `<root>/<dir>/NNNN-<slug>` and `.NNNN-<slug>`. Without the line, behavior is exactly today's. Ids, closure, cite scan, roadmap, cross-worktree id floor, and `check` all follow the resolved ticket root. `roadmap.md`, `config`, `notes.md`, `_templates/` stay at `<root>`.
  - Give `board.py` task discovery the same resolution so tasks under `<root>/tickets/` show on the board. Any other script that lists ticket or task folders under `.sdlc` and would miss them gets the same resolution when the fix is small; otherwise name it in the result as a follow-up.
  - `tickets.py roadmap` writes a managed router block into `<root>/AGENTS.md` (created if missing; text outside the block untouched) and ensures `<root>/CLAUDE.md` holds a line `@AGENTS.md` (created if missing; existing content kept). The block lists per stage (proposed, ready, blocked, done, dropped) a count, and one line `T-NNNN title (folder)` per proposed, ready, and blocked ticket; done and dropped get counts only. It also holds three short procedures: create (`tickets.py new`, never pick an id by hand), claim (set to in progress by starting a run through `run.sh`; an optional `claimed_by: <harness> <date>` front matter line is accepted by the parser and shown on the active line; a second claimant checks it first), close (`/file`, then `tickets.py close`; follow-ups follow the tag rules). It names the `messages/` root as git-ignored mailbox, read per `scripts/messages.py` (T-0176).
  - `check` fails when the router block is missing or stale, as it does for a stale `roadmap.md`, and prints which.
  - `tickets.py selftest` gains cases for each rule, including a negative control proving a stale router fails `check`, and a case proving a repo with no `ticket_root` line is unchanged.
  - Router behavior is tested, not just implemented (user requirement). The selftest and the verifier criteria must cover: when the router's stage lists and counts are regenerated (`roadmap` run after `new`, after `close`, and after a status edit), what each regeneration contains per stage, what makes `check` fail (missing block, stale count, stale ticket line, missing `CLAUDE.md` import) with one negative control per cause, that text outside the block is untouched, and a live run in a throwaway repo with `ticket_root: tickets` showing the block change as a ticket moves proposed to ready to done. The verifier injects at least one defect (for example leaving the count unchanged after a close) to show a test fails, and states it.
  - Self-describing folders (user principle): add no new skill for tickets or the router. `.sdlc/AGENTS.md` and a new `.sdlc/tickets/AGENTS.md` carry the full create, claim, and close procedures in plain steps with the exact commands, so reading the folder entry file is sufficient. A ticket handoff points to its stage rules through its router line. The live run in a throwaway repo has a fresh role, given only the ticket path and no skill, follow `tickets/AGENTS.md` to claim and close a ticket; record the result in a dated validation doc under `docs/reports/` (linked from `docs/README.md`), or report it unverified with the reason.
- Non-goals: moving existing tickets (no migration command in this ticket), stage folders, version bump, publishing, the mailbox (T-0176), Codex hooks.
- Done when: `python3 plugins/sdlc-lite/scripts/tickets.py selftest` passes with the new cases; `bash plugins/sdlc-lite/scripts/check.sh` passes; the repo's own `.sdlc` (no `ticket_root` line) still passes `tickets.py --root .sdlc check` after `roadmap` adds the router block; in a throwaway repo with `ticket_root: tickets`, `new`, `roadmap`, `check`, and `close` all work under `.sdlc/tickets/`.

## Context
Design: `docs/specs/ticket-stages/design.md` (sections Option A design and Two roots). Mechanics: `plugins/sdlc-lite/scripts/tickets.py` (about 3000 lines; `load()`, `worktree_pairs`, `id_floor`, `cmd_new`, `cmd_close`, `cmd_roadmap`, `cmd_check`, config parsing for `ticket_folders: numbered` and `external_branch:`), `plugins/sdlc-lite/scripts/board.py`, reference `docs/references/sdlc-internals.md` section `scripts/tickets.py`. `scripts/onboard.py` already writes managed blocks with version and sha256 in a start marker; reuse its approach and helpers for the router block instead of inventing a second format. Update `docs/references/sdlc-internals.md`, the `handoff-format` skill layout, and `skills/ticket/SKILL.md` for the new behavior, and `docs/specs/ticket-stages/design.md` status for Option A and the `tickets/` root. Handwrite no ticket ids. No em dashes in any file written.

## Constraints
Default `.sdlc` layout and every existing selftest case stay unchanged. Do not edit `.sdlc/roadmap.md` by hand. Do not bump versions. Claude hook behavior is not Codex behavior; do not claim Codex enforcement.
