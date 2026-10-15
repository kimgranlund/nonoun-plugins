---
id: T-0599
title: "lanes.py open leaves its ticket record uncommitted in main, so settle --forward refuses"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
After `lanes.py open`, `fanout.py land` and `fanout.py settle --forward` bring the ticket to `status: done` in main with no hand commit between them. A test that failed before the fix passes after it.

## Repro
1. In a throwaway repo with one claimed, committed ticket: `lanes.py open greeting --kind solo --ticket T-0001`.
2. Commit a change on `lane/T-0001-greeting`, then from main: `fanout.py land lane/T-0001-greeting --ticket T-0001 --gate "sh check.sh" --no-gate-lock`.
3. `fanout.py settle fanout/<date> --forward --gate "sh check.sh" --no-gate-lock`.

## Expected
Settle fast-forwards main, and the ticket reads `status: done` in main.

## Actual
`git status` in main after step 1 shows ` M .sdlc/AGENTS.md`, ` M .sdlc/<slug>/handoff.md`, ` M .sdlc/roadmap.md` (the `branch:` and `worktree:` lines the opener writes). Step 3 exits 2: `fanout: fanout/2026-10-15 is not a fast-forward of main: error: Your local changes to the following files would be overwritten by merge:; stop with state written, the branch is kept`. Committing those three files and rerunning settle passed.

## Context
Found by the T-0570 live run (codex-cli 0.162.1, full access), report `docs/reports/2026-10-15-codex-live-lane.md`. This repo's conductors commit `T-NNNN: record lane` by hand after open. Guess: open either commits its record or prints the commit the caller must make; land or settle could also name the files.

## Constraints
The failing test lands before or with the fix, never after.
