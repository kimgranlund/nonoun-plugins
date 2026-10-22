---
id: T-0736
title: "split's environment error requires declared dependencies"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
claimed_by: sdlc-lite-author 2026-10-22
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

## Outcome
`missing_deps` in `plugins/sdlc-lite/scripts/steps.py` now reports an environment error for a module-not-found line only when `package.json` declares dependencies or devDependencies, `node_modules` is absent, and the missing name is a package (a bare name or a path under `node_modules`). A relative or absolute local path stays a plan defect. The T-0727 module cases now write a `package.json` with a devDependency; three T-0736 cases added (relative `./x.mjs`, empty dependencies, no package.json).
- Negative control: with the narrowing reverted, the selftest prints `steps selftest: FAIL` for the three `(T-0736)` cases (relative module, no declared dependencies, no package.json).
- `gate_lock.py run ... steps.py selftest` exit 0 (PASS); `check.py` exit 0; `check-packaging.py` exit 0; `git diff --check 7778924a` exit 0.

## Outcome

2026-10-22 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: 7778924af93c
- Changed: see commits
- Commits: eb0ae78 T-0736: split's environment error requires declared dependencies
- Check: 1 `steps.py` selftest cases: a missing relative module (`./x.mjs`) and a module error in a repo who...: pass
- Check: 2 `gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/steps.py sel...: pass
- Follow-up: note: conductor probes were run directly against steps.missing_deps on... -> notes.md
- Follow-up: note: plugins/sdlc-lite/scripts/steps.py:1116 the command not found... -> notes.md
- Follow-up: decide: plugins/sdlc-lite/scripts/steps.py:1090 declares_deps reads only... -> notes.md
- Follow-up: note: plugins/sdlc-lite/scripts/steps.py:1086 the regex no longer matches... -> notes.md
