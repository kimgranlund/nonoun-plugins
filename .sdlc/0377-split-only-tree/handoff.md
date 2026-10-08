---
id: T-0377
title: "steps.py split --only runs guard and red spans in the lane tree, not the main checkout"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`steps.py split --only N` evaluates a step's guard and red spans in the lane tree, not the main checkout.

## Intent
- Do: scripts/steps.py split --only runs the step's (guard) and (red) spans at the main checkout cwd, so on a stale main it reports a false plan defect (maison T-0152 step 12). Run them in the lane tree: accept `--tree PATH` and default to the handoff's own git toplevel (as dispatch.py prepare does for the verifier prompt).
- Maison's detail (2026-10-08): `steps.py split --only 12` for T-0152 ran the (guard) span `node --test tests/gen-ui-renderers/adapters.checks.mjs` at the main checkout cwd (a stale candidate-8 without the step 1 code), got exit 1 'Could not find', reported 'plan defect: step 12 red guard' and wrote nothing, so the conductor hand-wrote step-12/handoff.md as a byte copy of the plan section. Wanted: `split --only N --tree <lane worktree>`, or run the spans in the Tree: path, and the same for the `steps.py lint` and `widen` criterion runs.
- Non-goals: model or effort changes; anything outside this ticket.
- Done when:
  - A selftest: a handoff in a lane worktree whose main checkout lacks the file the guard greps reports ok when run with --only, and fails without the fix (observed failing first).
  - check.py, tickets.py check, the affected selftests and both generate --check pass.

## Context
Maison reported a false plan defect on T-0152 step 12 because the guard ran against a stale main. Source: feedback from the maison conductor, 2026-10-08 (about 30 lanes across Claude and Codex, 3 bases, 2 peer repos); its specifics are in the maison repo's .sdlc/notes.md and handoffs. Maison ran plugin 0.21.2; check each claim against 0.21.3 and main before building.

## Constraints
No em or en dashes. No push or publish.
