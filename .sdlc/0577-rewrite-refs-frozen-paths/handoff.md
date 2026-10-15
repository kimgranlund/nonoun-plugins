---
id: T-0577
title: "--rewrite-refs rewrites citations inside frozen records"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`tickets.py ... --rewrite-refs` (close, archive, number, migrate-layout) never rewrites a file under a frozen path. It lists such a file as `kept frozen: <file>` instead, so frozen records (ADRs, dated reports) keep their original citations.

## Repro
1. A repo whose `docs/layout.md` lists frozen paths, for example `.claude/docs/adr/**` (agent-ui, 2026-10-15).
2. Run `tickets.py migrate-layout --rewrite-refs` (or archive or close with `--rewrite-refs`) where a frozen file cites a moved ticket path.

## Expected
Frozen files are left alone and listed; every other citing file is rewritten.

## Actual
`--rewrite-refs` rewrote citations inside frozen ADRs and `.claude/docs/adr/`.

## Context
Frozen paths are already declared in `docs/layout.md` (`Frozen paths`, one glob per line; `onboard.py setup` refuses another format). Read that list, the same way `onboard.py` does, plus an optional `rewrite_skip:` glob line in `.sdlc/config`. Also seen: `onboard.py setup` refused with exit 1 until the Frozen paths list was one glob per line. If that refusal's message does not say so, make it say so. Reported by the agent-ui conductor.

## Constraints
Non-frozen rewrite behavior is unchanged.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0. Its new case shows a fixture with a frozen `docs/adr/0001.md` and a non-frozen doc, both citing a ticket path that `archive --rewrite-refs` moves: the frozen file is unchanged and listed as `kept frozen:`, and the other file is rewritten. The case failed before the change.
2. The onboard refusal for a malformed Frozen paths list names the expected one-glob-per-line format. Show it with a selftest line or a command and its output.
3. `git diff --check` exits 0.
