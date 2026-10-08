---
id: T-0366
title: "dispatch.py prepare verifier prints the pre-build commit as Base sha, not the post-solo HEAD"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
dispatch.py prepare for a verifier prints the commit the build started from as Base sha, so a scope diff against it is not empty.

## Intent
- Do: In scripts/dispatch.py: solo_run.py and fanout.py record the pre-build sha in the solo dispatch file; prepare verifier reads it instead of the current HEAD (the code that prints the Base sha line, around line 504). Coordinate with T-0363 if it touches the same function.
- Non-goals: model or effort changes; anything outside this finding.
- Done when:
  - A selftest: a solo dispatch with a recorded base sha and a later commit makes prepare verifier print the recorded sha (observed failing first, printing HEAD).
  - check.py, tickets.py check, the affected selftests and both generate --check pass.

## Context
agent-ui corrected the Base sha by hand in 8 verifier prompts this session; a missed correction means an empty diff and a wrong verdict. Source: docs/reports/2026-10-08-fleet-retro-06.md (fleet retro 2026-10-08, filed by the user's choice). outcome metric: hand corrections of Base sha reported by the next retro, before: 8

## Constraints
No em or en dashes. No push or publish.
