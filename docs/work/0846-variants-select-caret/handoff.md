---
id: T-0846
title: "Style the component-variants select caret on the compiled select__root wrapper"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P3         # P1 | P2 | P3
depends: [T-0843]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-12
claimed_by: nonoun-author 2026-11-12
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
