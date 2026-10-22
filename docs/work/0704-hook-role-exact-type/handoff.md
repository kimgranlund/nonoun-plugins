---
id: T-0704
title: "Role hooks resolve a named teammate by its real agent type"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-21
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Every role hook knows the role of a named teammate from its real agent type, not from a pattern in its spawn name.

## Intent
- Do: find where a named teammate's real type is available to a PreToolUse hook (the payload, or the transcript `meta.json` field `customAgentType` that T-0702 found), and have `plugins/sdlc-lite/hooks/_role.sh` use it before the T-0702 name inference; keep the name inference only as a fallback.
- Non-goals: changing spawn names.
- Done when: the criteria pass.

## Context
T-0702 Outcome: "For a teammate the hook payload's `agent_type` is the spawn name (`solo-0702`, `0702-solo-L2`), not `sdlc-lite:solo-L1`." Still open there: "a teammate whose name matches neither pattern still gets no role. An exact fix would need the payload to carry the real type, or the hook to read `customAgentType` from `meta.json`."

## Acceptance criteria
1. `bash plugins/sdlc-lite/scripts/hook-selftest.sh` exits 0 with a new case: a teammate named `reviewer-x` whose real type is `sdlc-lite:builder-L2` is resolved as builder; the case fails with the change reverted.
2. The Outcome names where the real type was read from and how that was observed.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0 and `git diff --check <base sha>` exits 0.
