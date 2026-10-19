---
id: T-0581
title: "close --preflight at merge-ready, --reason skip lines, serialized closes"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-17
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Closing a ticket holds no surprises. `tickets.py close <slug> --preflight` lists in one pass everything close will demand: verdict, filer, `## Skipped` lines, refs needing `--rewrite-refs` or `--keep-refs`, and open warnings. `--reason` writes the skip lines it needs, and closes take a lock so they run one at a time.

## Context
Source: ui-kit-maison lessons 2026-10-15, `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0597-7b-gate-and-close-friction-review/lessons-2026-10-15.md`, item 2. Each close needed a filer run, `## Skipped` lines, `--keep-refs` and `--ack-warnings`, and took about a minute of admission. 21 parallel close dry-runs crashed maison's host (their T-0597 item 20). This repo hit the same `## Skipped` refusal on T-0563 (2026-10-15).

## Intent
- Do: add `--preflight`, read-only, exit 0 with `ready` or exit 1 with one line per missing item; make `--reason` append the `## Skipped` lines its lane needs; and add a repo-level close lock (`.sdlc/runtime/close.lock`, flock) so a second close waits.
- Non-goals: changing what close requires.
- Done when: the criteria pass.

## Constraints
Close output and requirements stay the same apart from these.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0. Its new cases show: preflight on a full-lane ticket with no skips.md entry lists it and exits 1; `--reason` on that ticket closes with the skip line written; and two concurrent closes run one after the other (the second reports waiting). The cases failed before the change.
2. `git diff --check` exits 0.

## Plan review
- amend: scope adds the two selftest negative controls that relied on `close --reason` refusing a ticket with no `## Skipped` lines: `plugins/sdlc-lite/scripts/steps.py` (lane solo close case, about line 6471) and `plugins/sdlc-lite/scripts/fanout.py` (case 16). Each control moves to a close that still refuses (a plain or `--filer` close); `steps.py selftest` and `fanout.py selftest` must exit 0. Found by the solo; decided: maintainer conductor, 2026-10-17.

## Outcome

2026-10-17 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full; verifier notes: note: tickets.py `close_lock` is taken in `main` and not in `run`, so in-process `cmd_close` callers (selftests, other scripts that import tickets) take no lock. Intended per its docstring. | note: scratch fixtures under /var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/sdlc-lite/sdlc-lite-0a5e021b/0581-verifier-L2 could not be removed (rm was denied); the throwaway git worktree under tmp/0581-verifier-L2 was removed.) · verifier: verifier-L2 (sonnet) · base: e02e01164de9
- Changed: see commits
- Commits: df8fcc7 T-0581: close --preflight at merge-ready, --reason skip lines, serialized closes; 3b5ee76 T-0581: amend scope to the two negative controls that relied on --reason refusing
- Check: 1 `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0 with the new cases (preflight lis...: pass
- Check: 2 `git diff --check` exits 0: pass
- Check: 3 Plan review amend (steps.py and fanout.py negative controls): pass
- Check: 4 Conductor check: `--preflight` writes nothing: pass
- Check: 5 Conductor check: `close --reason` refuses nothing it refused before except the missing-skip case: pass
