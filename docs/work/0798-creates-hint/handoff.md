---
id: T-0798
title: "steps.py lint cited-path refusal does not name the [creates:] marker (#84)"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-28
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A builder or conductor who hits `cited path does not exist` for a path the step itself creates learns the fix from the message, and a Do line "write output to <path>" counts as declaring it (GitHub #84).

## Repro
1. A step whose `### Do` says "write output to `.sdlc/runtime/tasks/<task>/parity/idshift.json`" and whose criteria compare that file.
2. `steps.py lint <handoff>` (or `dispatch.py prepare builder`).

## Expected
The path counts as created by the step; or, when it is not declared, the refusal names the `[creates: <path>]` marker and the `Outputs:` line as the fix.

## Actual
GitHub #84 (0.36.0): `steps.py lint refused the links ... cited path does not exist: .../parity/idshift.json` and `plan defect: replan this step`; the reporter created placeholder files. The MacBook retro (`docs/reports/2026-10-28-sdlc-retro-Kims-MacBook-Pro.md` row U6) reports the refusal stopped once `[creates: <path>]` tags were added, so the marker works but the message does not point to it.

## Context
`plugins/sdlc-lite/scripts/steps.py` line 2249 (the refusal) and `declared_future_paths` / `CREATES_MARK_RE` (line 2124, T-0457). Contract: `plugins/sdlc-lite/skills/handoff-format/references/step-handoff-rules.md` line 31.

## Acceptance criteria
1. A steps selftest case: a Do line "write output to `<.sdlc path>`" exempts that path; reverted, lint refuses it (state the FAIL line).
2. A steps selftest case: an undeclared missing path's refusal names `[creates: <path>]`.
3. steps selftest through gate_lock exits 0, `check.py` exits 0.

## Constraints
The failing tests land before or with the fix, never after.
