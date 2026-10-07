---
id: T-0115
title: "fanout.py treats a lane that ends on an inherited red builder like..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0101
---

## Goal
When a fanout lane's task stops on an `inherited red` builder, `fanout.py` reports that cause and the inherited tests, and does not merge or close the half-done ticket, so the operator sees "main was already red" instead of a misleading merge or close refusal.

## Context
Follow-up from T-0101 (builder-inherited-red/filer-L1.md):

`fanout.py` treats a lane that ends on an `inherited red` builder like any other non-merged outcome; decide whether lane reports should name the inherited tests so the cause is visible.

## Intent
Literal ask: decide whether lane reports should name the inherited tests so the cause is visible.
Deltas:
- Decision (name the tests or not): defaulted: yes. It matches the existing unattended rule in /chain and the conductor ("stop the task and report the inherited tests"), so it is not a new policy. The user can reverse it at review.
- Hidden scope, what fanout does today: after the driver exits 0, fanout commits the lane, merges it into the integration branch, runs gates, and tries `tickets.py close`; a task stopped on inherited red has no filer file, so the lane reports `merged, close refused: ...` (or `red: <gate>`) with half-done work merged. defaulted: detect the inherited-red stop right after the driver returns, before the lane commit, and skip commit, merge, and close.
- Detection source: defaulted: the lane ticket folder's `step-<n>/` dirs (not `step-<n>.superseded-<k>/`), using `steps.py next` semantics (action `inherited`) and the tests from the newest builder result's `## Status` line (`inherited red: <tests>`). Reuse steps.py/order.py logic rather than re-deriving "newest".
- Outcome text: defaulted: `inherited red: step-<n>: <tests>` in the `[<lane>] <id>` event line and the report.md Outcome cell; it is a non-merged outcome, so the lane stops and later tickets are `skipped`, and the run exits 1.
- Uncommitted lane work: defaulted: left in the lane worktree for inspection, like `driver failed`.
Do: add the inherited-red detection and outcome to `scripts/fanout.py` (run path, docstring/usage text), a selftest case with a stub driver that writes a step dir whose newest builder Status is `inherited red: test_a` (asserting the outcome names step and tests, nothing merged into integration, ticket not closed, the next ticket in the lane skipped), and a negative control showing a lane with a done builder is not flagged. Update docs that describe fanout outcomes: `CLAUDE.md` fanout.py bullet, `.claude/agents/sdlc-lite-author.md` if it describes fanout outcomes, `skills/fanout/SKILL.md` report section, and any doc (conductor.md, chain SKILL.md) that says fanout is unaffected by inherited red.
Non-goals: verifier routing of inherited red (separate follow-up); changing steps.py next semantics; any change to how gates, sync, or close work for other outcomes.
Done when: `python3 scripts/fanout.py selftest` passes with the new inherited-red case (and that case fails against the HEAD fanout.py), and `scripts/check.sh` exits 0.

## Constraints
No change to other fanout outcomes, the lane commit message, or the merge/gate/close flow for merged tickets. Main is never touched. No new dependency.
