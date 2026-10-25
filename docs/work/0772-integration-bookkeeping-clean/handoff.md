---
id: T-0772
title: "Ticket and lane commands leave no tracked file dirty in the integration tree"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The defect GitHub issue #80 reports no longer happens (title: Ticket and lane commands leave no tracked file dirty in the integration tree).

## Intent
- Do: first confirm it still reproduces on main (0.36 work changed nearby code: owner trees T-0749 to T-0755, host lanes T-0756 to T-0764); if it no longer does, add the regression case and say so in the Outcome. Otherwise fix it in `plugins/sdlc-lite/scripts/fanout.py` (the issue names the lines and a proposed fix; take it unless the code shows a better one) and update the docs that describe the behaviour.
- Non-goals: other issues.
- Done when: the criteria pass.

## Context
GitHub issue #80 (quoted):

> **Observed:** `tickets.py new` / `tickets.py roadmap` run in the integration worktree left `.sdlc/AGENTS.md` (and the roadmap) modified; the next `fanout.py land` refused `integration dirty: .sdlc/AGENTS.md`. `steps.py lane` writes `skips.md` into the tracked ticket folder; run from the primary checkout it left an untracked file on main that would block a fast-forward settle.
>
> **Root cause:** these commands regenerate tracked files without committing; `record_lane` writes `skips.md` into the tracked task folder (`scripts/steps.py:4078-4099`); land refuses any tracked change (`scripts/fanout.py:1840-1846`). Gap in #29 (T-0669 moved dispatch records but left `skips.md`); #46/#57 only covered lane-close bookkeeping on main.
>
> **Proposed fix:** commit their own writes in a plugin-managed tree (as `lanes.py open` does, T-0599), or have land commit regenerable router/roadmap/skips paths as bookkeeping before its dirty check; move `skips.md` to the records dir.
>
> Found in sdlc-lite 0.35.0 while conducting a fanout run; root cause traced in the plugin source.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A `fanout.py` selftest case reproduces the issue's report and passes; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
- Reproduced on main: the new fanout selftest case 5e (`tickets.py roadmap` run in the integration worktree before land) gave `integration dirty: .sdlc/AGENTS.md`, as #80 reports.
- Fix: `merge_gate_close` in `plugins/sdlc-lite/scripts/fanout.py` commits tracked changes as one `bookkeeping: <paths>` commit when every one is a file `generated_files` names (roadmap, router, mailbox entry files, notes.md); any other tracked change still refuses with `integration dirty: <first such path>` (case 5d unchanged and green). Docs: the fanout.py usage text and `docs/references/sdlc-internals.md`. The fanout SKILL.md sits at its 18,000 character limit, so it is unchanged.
- Negative control (case 5e run before the fix): `integration bookkeeping: outcome is merged, got 'integration dirty: .sdlc/AGENTS.md' stderr=''`, plus the bookkeeping-commit and clean-tree lines.
- Checks: `gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py selftest` exit 0, `check.py` exit 0, `check-packaging.py` exit 0, `git diff --check <base>` exit 0.
- Not done: moving `skips.md` to the records dir. It has about ten writers and readers outside `record_lane` (steps.py step cap, dispatch.py lane gate, lane override, replan and time approvals, tickets.py `skips_path` and `add_skip_line`), and moving only `record_lane` would split the file so close misses the lane record. In a fanout lane skips.md is committed with the lane and moved at close, so land never sees it dirty; the leftover is an untracked file on main when `steps.py lane` runs in the primary checkout. Suggested follow-up ticket: one skips.md location helper for every writer and reader.
