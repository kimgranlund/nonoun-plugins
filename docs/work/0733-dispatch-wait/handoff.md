---
id: T-0733
title: "dispatch.py wait blocks until a role result lands"
type: feature        # feature | bug | chore | spike | idea
status: claimed        # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
claimed_by: sdlc-lite-author 2026-10-25
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`dispatch.py wait <dispatch.json> [--timeout S]` blocks until the result file is non-empty or the attempt leaves running, then prints the status line; the conductor can run it in the background right after a spawn.

## Intent
- Do: Per the issue; proposed for the maintainer to schedule.
- Non-goals: other issues in the same batch.
- Done when: the criteria pass.

## Context
GitHub issue #63 (quoted):

> ## Idea
> In a long interactive conductor session, sub-agent completion notices were unreliable. Some arrived hours late in a batch (`idle_notification` stamped 06:31 and delivered after 12:00), and some never arrived. The conductor relies on them to record and advance, so the run stalled until a goal check-in.
>
> The workaround that held was a hand-written background Bash loop per role, which waited for the role's report file to appear. That loop is the same for every role.
>
> ## Proposal
> `dispatch.py wait <dispatch.json> [--timeout S]` blocks until the dispatch's `result` file is non-empty, or the attempt leaves `running`, then prints the status line. The conductor runs it as a background Bash call right after spawning, so the session wakes on the file itself, not on the notice. The conductor and chain skills could say to start it after each spawn.
>
> ## Evidence
> One ui-kit-neue conductor session (G6 to G9) on Claude Code; about 20 watcher loops were written by hand.

## Constraints
The failing test lands before or with the fix, never after.

## Acceptance criteria
1. A `dispatch.py` selftest case reproduces the issue's repro and passes; with the change reverted it fails (state the FAIL line in the Outcome).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
