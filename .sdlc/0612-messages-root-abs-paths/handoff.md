---
id: T-0612
title: "messages.py send --root rewrites tracked entry files with absolute paths"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-17
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A `messages.py send` with an absolute `--root` leaves the tracked mailbox entry files byte-identical to a send with the relative root, and a test that failed before the fix passes after it.

## Repro
1. From another repo: `python3 <plugin>/scripts/messages.py --root /Users/kimgranlund/Projects/nonoun/sdlc-lite/.sdlc send --receiver fleet-retro --sender x --topic t --follow-up false -`.
2. In sdlc-lite: `git status --short .sdlc/messages`.

## Expected
No tracked file changes; entry-file commands stay `python3 ".sdlc/messages/messages-run.py" ...`.

## Actual
`.sdlc/messages/AGENTS.md`, `new/`, `read/` and `done/AGENTS.md` change (21 lines): every command becomes `python3 "/Users/kimgranlund/Projects/nonoun/sdlc-lite/.sdlc/messages/messages-run.py" ...`.

## Context
Found in the 2026-10-17 fleet retro: three conductors sent replies with an absolute `--root` (the interview template fills it that way). Reverted by hand before commit `3ba4be34`. Guess: the entry-file writer embeds `os.path.join(mbox, 'messages-run.py')` with `mbox` as given, not relative to the repo root (`plugins/sdlc-lite/scripts/messages.py` near line 2467 shows the same join in its selftest).

## Constraints
The failing test lands before or with the fix, never after.
