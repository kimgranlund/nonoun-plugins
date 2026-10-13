---
id: T-0527
title: "Close references, router links, launcher and root guard (maison T-0546)"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0526]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Close references, router links, launcher and root guard, closing maison T-0546 observations 4, 5, 6, 12.

## Intent
- **Files:** `plugins/sdlc-lite/scripts/tickets.py`: the reference scan (lines 859-868), `ROUTER_PROCEDURES` (around line 1558), `write_router` (around line 1745), `cmd_check`, `main` (around line 5461). Also `plugins/sdlc-lite/skills/ticket/SKILL.md` (config keys).
- **Behavior:**
  - The scan that runs with ignore rules off covers the whole `<root>`, not only the ticket root. A gitignored `.sdlc/AGENTS.md` is then found and rewritten.
  - `check` warns on a relative link in `<root>/AGENTS.md`, outside the managed block, whose target is missing but whose dot-folder exists.
  - A new config key `tickets_cmd:` replaces the raw `tickets.py` command in the generated procedures. The Close steps name `--rewrite-refs`.
  - Every subcommand except `new` refuses a `--root` that holds no `config`, `roadmap.md` or ticket folder.
- **Done-when:** `tickets.py selftest` exits 0 with these new cases:
  - Fixture: `.sdlc/` gitignored, `ticket_root: tickets`, and `.sdlc/AGENTS.md` citing `tickets/0002-b/handoff.md`. `close 0002-b --dry-run` lists that file and `--rewrite-refs` rewrites it. The same fixture against HEAD's script lists nothing (negative control).
  - With `tickets_cmd: python3 .sdlc/tickets-run.py`, the managed block contains that string and no bare `tickets.py --root` line.
  - `tickets.py --root <empty dir> check` exits nonzero.

## Context
- Source: maison `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0546-sdlc-lite-work-record-improvements/observations.md` (the numbered observations named above) and the triage `.sdlc/.0525-maison-0546-triage/architect-L1.md` (group C; read its Constraints and Risks).
- Maison's hand-written rules are the working reference: `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/AGENTS.md`, `.sdlc/tickets/AGENTS.md`, `.sdlc/writing-rules.md` in that repo. Read only; never edit maison.
- Tickets A, C, B, G, D all edit `plugins/sdlc-lite/scripts/tickets.py`; they run one after another in that order (depends chain).

## Constraints
Preserve reference-safe closure, cross-worktree id uniqueness and explicit follow-up selection. A new or changed check needs a positive case and an observed negative control.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0, and the selftest holds the Done-when cases: with `.sdlc/` gitignored, `ticket_root: tickets` and `.sdlc/AGENTS.md` citing `tickets/0002-b/handoff.md`, `close 0002-b --dry-run` names `.sdlc/AGENTS.md`, `--dry-run --rewrite-refs` lists `rewrite .sdlc/AGENTS.md`, and `--rewrite-refs` rewrites it to `tickets/.0002-b/`; with `tickets_cmd: python3 .sdlc/tickets-run.py` both managed blocks hold that string and no `tickets.py --root`; `tickets.py --root <empty dir> check` exits nonzero.
- Each new case bites: the old scan (ignore rules off under the ticket dir only) finds nothing in that fixture, which the selftest asserts as its negative control; with no `tickets_cmd:` the block keeps the raw command; a root holding only `config` and `new` on an empty root are not refused; a link to an open ticket folder, or one fixed to the dot folder, gives no link warning.
- `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check` exits 0 (the regenerated `.sdlc/AGENTS.md` router is current).
- The router "Close a ticket" steps name `--rewrite-refs`, and `plugins/sdlc-lite/skills/ticket/SKILL.md` describes the whole-root ignore-off scan, `tickets_cmd:`, the link warning and the root guard.
- `bash plugins/sdlc-lite/scripts/check.sh` exits 0.
- `git diff --check` exits 0.

## Closed

2026-10-13: solo L2 built and verified, merged from fanout/wave65-c (the lane's merge conflict was the generated router block)
