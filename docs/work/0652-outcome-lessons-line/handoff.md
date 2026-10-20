---
id: T-0652
title: "Outcome gains an optional Lessons line"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A closed ticket's Outcome can carry the reusable lessons the work taught, on one optional `- Lessons:` line, so they survive in a tracked file after the runtime records are pruned.

## Intent
- Do: (1) `tickets.py close` gains a repeatable `--lessons TEXT` on every route (default, `--filer`, `--reason`); `outcome_section` in `plugins/sdlc-lite/scripts/tickets.py` writes one `- Lessons: <text>` line per value after the Follow-up lines, and none without the flag. (2) The usage text, the Outcome description in the `cmd_close` docstring and the router close steps (`ROUTER_TEMPLATE`) name the flag with one line: route each lesson to a named repo skill or NOTES.md.
- Non-goals: filling the line automatically from ui-designer `Rule: gap` items (T-0649 defines those; a later ticket can read them); review `## Carry forward` scraping; the follow-ups register (T-0653).
- Done when: the criteria pass.
- If Do needs more steps than this level allows (L1-L2 3, L3 6, L4 10, L5 15), file two tickets.

## Context
Source: GitHub issue #13, ui-kit-neue audit 2026-10-20. This ticket is part (b) of #13 (lessons); part (a) is T-0651, part (c) T-0653.
- ui-kit-neue: the T-0050 review carry-forward (scrollbar clearance, inset focus target, `onShell` duplication) is in no tracked file; closed handoffs `.0049`, `.0050`, `.0051`, `.0080` hold no lessons.
- `outcome_section` at `plugins/sdlc-lite/scripts/tickets.py:3249` builds the header, Changed, Commits, Check, Deviation and Follow-up lines; the local `outcome()` wrapper in `cmd_close` at `plugins/sdlc-lite/scripts/tickets.py:3481` calls it on every route.
- Argument parsing: `close` arguments near `plugins/sdlc-lite/scripts/tickets.py:8552` (`--changed`, `--reason`); usage line `plugins/sdlc-lite/scripts/tickets.py:8`; Outcome usage text `plugins/sdlc-lite/scripts/tickets.py:121-128`.
- `Rule: gap` is optional input here: the flag takes any text, so this ticket does not depend on T-0649.

## Constraints
An Outcome written without `--lessons` is byte-identical to today's. An empty `--lessons ""` refuses, writing nothing.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0 with a new case: `close --reason x --lessons "focus rings need forced-colors" --lessons "rtl: logical props"` writes exactly two `- Lessons:` lines after the Follow-up lines, and a close without the flag writes none. The case fails with the change reverted.
2. `python3 plugins/sdlc-lite/scripts/tickets.py close --help 2>&1 | grep -c -- '--lessons'` prints at least 1.
3. `git diff --check` exits 0.
