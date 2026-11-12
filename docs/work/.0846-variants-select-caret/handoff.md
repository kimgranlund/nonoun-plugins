---
id: T-0846
title: "Style the component-variants select caret on the compiled select__root wrapper"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P3         # P1 | P2 | P3
depends: [T-0843]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-12
claimed_by: nonoun-author 2026-11-12
branch: lane/T-0846-t0846
worktree: ../sdlc-lite.worktrees/T-0846-t0846
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The select indicator in a built component-variants review page is styled.

## Context
- Found by the T-0843 solo: `plugins/design/skills/component-variants/assets/shell.css` styles `.select-control`, but the compiled wrapper class is `select__root`, so the caret indicator gets no style. Present before T-0843.

## Acceptance criteria
- A built review page's select wrapper matches a `shell.css` rule (an observed check that fails on the current selector).
- `node scripts/check-build.mjs` in `component-variants` exits 0.

## Outcome

## Outcome

2026-11-12 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L1 (opus) · base: fc51c3a1728b
- Changed: see commits
- Commits: 1ead199 T-0846: style the component-variants select caret on select__root
- Check: 1 A built review page's select wrapper matches a `shell.css` rule (an observed check that fails on ...: pass
- Check: 2 `node scripts/check-build.mjs` in `component-variants` exits 0: pass
- Follow-up: note: redck.py deviations printed no process deviation lines. -> notes.md
