---
id: T-0736
title: "split's environment error requires declared dependencies"
type: bug             # feature | bug | chore | spike | idea
status: ready     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`steps.py split` calls a module-not-found red guard an environment error only when the tree declares dependencies it has not installed (a `package.json` with `dependencies` or `devDependencies` and no `node_modules`), and when the missing module is a package, not a relative local file.

## Intent
- Do: narrow the T-0727 classifier in `plugins/sdlc-lite/scripts/steps.py` (about line 1096). Add selftest cases for a dependency-free Node repo and for a missing relative module; each must stay a `plan defect`.
- Non-goals: other environment classes.
- Done when: the criteria pass.

## Context
T-0727 verifier-L2 (landed):
- decide: plugins/sdlc-lite/scripts/steps.py:1096 treats a module-not-found line as an environment error whenever the tree root has no node_modules. A Node repo with no dependencies, or a guard whose missing module is a local file the step creates, is then reported as `environment error` with an `npm ci` hint that cannot fix it, and the split never reaches a plan defect. Also requiring a package.json would narrow this.

## Acceptance criteria
1. `steps.py` selftest cases: a missing relative module (`./x.mjs`) and a module error in a repo whose `package.json` has no dependencies both report `plan defect`; the T-0727 env-error cases still pass; with the narrowing reverted, the new cases fail (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
