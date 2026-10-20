---
id: T-0584
title: "tickets.py inventory: landed state by content and patch identity"
type: idea            # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P3         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: sdlc-lite-author 2026-10-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`tickets.py inventory` reports each open or recently closed ticket's real state: its branch, whether that branch's content is on main or a named integration branch (by ancestry, patch identity or equal files), and its newest verdict in correct order.

## Context
Source: ui-kit-maison lessons 2026-10-15, `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0597-7b-gate-and-close-friction-review/lessons-2026-10-15.md`, item 6. maison hand-built `collect.py` and `classify.py`, and their architect found four defects: verifier sort order (lexical `verifier-L3-2` before `verifier-L3`), stale sibling branches, pointer branches, and records under unusual paths. This repo already owns the pieces: `order.py` (newest-result ordering), `lanes.py` landed tests, `order.py records-dir`. Idea ticket: shape before building.

## Intent
- Do: propose the command's output and which existing functions it composes. Note whether `order.py` already sorts `verifier-L3-2` after `verifier-L3` (it should; maison's bug was in their own script).
- Non-goals: building it in this ticket.
- Done when: the Outcome holds the design and the ordering check result.

## Constraints
None.

## Acceptance criteria
1. The Outcome holds the output format, the functions reused, and the `order.py` ordering result with the command that showed it.

## Outcome
Design only; nothing built.

### Ordering check
`order.py` already sorts `verifier-L3-2` after `verifier-L3`; maison's lexical-sort bug does not exist here. Shown with a temp records dir holding empty `verifier-L3.md` and `verifier-L3-2.md`:
`python3 plugins/sdlc-lite/scripts/order.py newest <tmp>/.sdlc/runtime/tasks/x verifier` printed `.../verifier-L3-2.md` both with no `runs.jsonl` (unrecorded key `(0, level, k, name)`, so k=2 > k=1) and with a `runs.jsonl` listing L3 then L3-2 (recorded rank wins).

### Output
`tickets.py inventory [--into <branch>]... [--days N] [--json]`, read-only, one row per ticket that is open or closed in the last N days (default 7):
```
T-0584  claimed  lane/T-0584-t0584  landed:main(ancestor)    verifier-L2  pass  verifier-L2-2.md
T-0590  ready    -                  -                          -            -     -
T-0577  claimed  lane/T-0577-x      not landed (scripts/a.py)  verifier-L3  fail  verifier-L3.md
```
Columns: id, status, branch (or `-`), landed state, newest verifier role-level, its verdict, its file. Landed state is `landed:<into>(ancestor|pr merged|patch|content)`, `not landed (<first differing path>)`, or `cannot decide (<why>)`; the first `--into` that lands wins, default the default branch then any named integration branch. Several branches for one ticket print one row each, so a stale sibling or a pointer branch shows as its own row rather than hiding the real one. `--json` emits the same fields per row.

### Functions reused
- Tickets and status: `tickets.load`, `tickets.problems` filtering as `delivered_warnings` does (open ids).
- Ticket to branch: `tickets.worktree_pairs` and `tickets.branch_tickets` (inverted), plus `lanes.discover` for lane records.
- Landed: `lanes.landed(cwd, ref, into, branch)` (ancestor, merged PR, equal files). Add one step between `pr merged` and the file compare: the `git cherry` patch-identity test from `lanes.orphans`, factored into a shared `patch_landed(top, into, ref)` helper so both callers use it.
- Default branch: `tickets.default_branch`.
- Records under any path: `order.records_dir(task_dir)` (handles runtime, legacy and step dirs), then `order.newest(dir, 'verifier')`; verdict from the result file's verdict line as `results.py` parses it.

### Follow-up
Build ticket: `tickets.py inventory` as above, with selftests for a `-2` verifier, a cherry-picked branch, a stale sibling and a legacy records path.
