---
id: T-0164
title: "/fix lints the task folder, which has no planner file"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-29
---

## Goal
The lint command that `/fix` tells the conductor to run passes for a well-formed handwritten step handoff, and a test that failed before the fix passes after it.

## Repro
1. In a Git repository, create `.sdlc/fixtask/handoff.md` and a well-formed `.sdlc/fixtask/step-1/handoff.md` by hand, with no planner file in the task folder.
2. Run `python3 plugins/sdlc-lite/scripts/steps.py lint .sdlc/fixtask`, which is the command `skills/fix/SKILL.md` step 2 gives.
3. Run `python3 plugins/sdlc-lite/scripts/steps.py lint .sdlc/fixtask/step-1/handoff.md`.

## Expected
The command in the skill lints the step handoff that `/fix` just wrote.

## Actual
Observed 2026-09-29:

- Step 2 prints `steps: no planner-*.md in .sdlc/fixtask` and exits 1.
- Step 3 prints `steps lint: ok` and exits 0.

## Context
Found in the third onboarding design review, `docs/reports/repo-onboarding-design-review-3.md` finding N13, and rerun by the author on the reviewer's fixture.

`skills/fix/SKILL.md` step 2 has the conductor write the step handoff by hand and never run `steps.py split`, so the task folder has no planner file. `skills/chain/SKILL.md` section 5 step 3 lints the step handoff path, which works.

Guess: the `/fix` text should name the step handoff path, as `/chain` does. Not checked: whether `/fix` has been run live since this text was written, and whether `scripts/check.py` covers the command.

## Constraints
The failing test lands before or with the fix, never after. Generated Codex agents are regenerated if a preloaded skill body changes.

## Closed

2026-09-29: fixed in session by /fix: /fix lints the step handoff, guarded by a check.py contract check
