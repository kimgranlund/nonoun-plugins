---
id: T-0794
title: "dispatch.py prepare refuses a lane that renames a guidance file its handoff names"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-25
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`dispatch.py prepare` accepts a lane whose own commits since its base renamed or deleted a guidance file the handoff names, so a rename ticket can get its verifier.

## Repro
1. A ticket handoff names `plugins/progressive-context/AGENTS.md`; its lane `git mv`s `plugins/progressive-context/` to `plugins/context/` and commits.
2. `dispatch.py prepare verifier L2 <lane handoff>`.

## Expected
The verifier is prepared: the path is missing in the lane because the lane's own diff since its base removed it, not because the lane is stale.

## Actual
T-0793, 2026-10-25: `rc=5`, "guidance missing in lane: plugins/progressive-context/AGENTS.md (present on main at e64133f)" and "dispatch.py: sync the guidance into the lane (fanout.py sync --paths) or fix the handoff, then rerun prepare". No flag skips it, so the T-0793 verifier ran on a hand-written brief with no dispatch record.

## Context
`lane_guidance` in plugins/sdlc-lite/scripts/dispatch.py (about line 727, the `missing` loop near line 757; T-0655, T-0674). The lane's base is in `.lane.json` or the recorded base sha.

## Acceptance criteria
1. A dispatch selftest case: a lane that renames a named guidance file in a commit since its base prepares without the missing line; a lane that merely lacks the file (no such change in its diff) still refuses. With the change reverted the first case fails (state the FAIL line).
2. dispatch selftest through gate_lock exits 0, `check.py` exits 0, `git diff --check <base sha>` exits 0.

## Constraints
The failing test lands before or with the fix.
