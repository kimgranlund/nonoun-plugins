---
id: T-0673
title: "Skills say record reads the transcript, not the final message on stdin"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0667]    # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-20
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Every skill that tells the conductor to run `dispatch.py record` says what `conductor.md` says after T-0667: run `record --agent-id <id>` with the notice figures and nothing on stdin; stdin only when the role's transcript is missing.

## Intent
- Do: reword the `record` sentence in `skills/{build,fix,agent,architect,dig,file,scout,research,verify,bench,fleet-retro,review-traces}/SKILL.md` and `skills/plan/references/steps.md` under `plugins/sdlc-lite/` to match the T-0667 wording in `agents/conductor.md` "How you run roles" step 3.
- Non-goals: any script change.
- Done when: the criteria pass.

## Context
Found by the T-0667 builder: those 13 files still say "with the sub-agent's final message on stdin", which contradicts `conductor.md` after T-0667 (stale guidance makes conductors scrape transcripts by hand, issue #27).

## Constraints
None.

## Acceptance criteria
1. `grep -rln "final message on stdin" plugins/sdlc-lite/skills` prints nothing.
2. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, and `python3 scripts/check-packaging.py` exits 0.
3. `git diff --check <base sha>` exits 0.
