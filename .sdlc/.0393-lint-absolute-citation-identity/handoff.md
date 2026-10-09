---
id: T-0393
title: "steps lint resolves absolute evidence citations against the wrong tree"
type: bug             # feature | bug | chore | spike | idea
status: done
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`steps.py lint` resolves a cited absolute path exactly as written, so an existing shared evidence file passes and a removed one fails even when a same-suffix file exists in the owned tree.

## Intent
- Do: fix the citation resolver in scripts/steps.py (the code that slices a matched path at its first `.sdlc/`, about lines 1257 to 1261, and its lint consumer about lines 1326 to 1336 that joins the suffix to the owned tree). Keep the path kind: absolute stays absolute, relative resolves against the documented authoring base. Keep the span rewrite separate from the resolution target. `:line` trimming and the superseded-report guidance must refer to the original target. Do not require extra report copies as the fix.
- Non-goals: model or effort changes; changing what lint cites or when.
- Done when:
  - Selftest cases, each observed failing first: an existing absolute external target passes with no local mirror; a nonexistent absolute target fails even with a local same-suffix file; a valid relative and a repository-root citation still pass; `:line` trimming and the superseded-report guidance still name the original target.
  - steps.py selftest, check.py and tickets.py check pass.

## Repro
Two temp dirs: `shared/.sdlc/tickets/0001-evidence/verifier.md` and `owned/.sdlc/tickets/0002-work/step-1/handoff.md` whose Do line cites the absolute shared verifier path. `steps.py lint <absolute handoff>` exits 1 with `cited path does not exist`. Remove the shared file and create a different `owned/.sdlc/tickets/0001-evidence/verifier.md`: lint exits 0.

## Context
Maison and Codex, 2026-10-08, 0.22.0: full report at maison .sdlc/tickets/0311-form-control-adapters-change-path/sdlc-bug-absolute-evidence-citations.md. Related to T-0381 (stale root vs owned worktree).

## Constraints
No em or en dashes. No push or publish.

## Closed

2026-10-08: delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed
