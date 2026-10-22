---
id: T-0742
title: "The light gate set runs with dependencies installed"
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
`fanout.py land` runs the light gate set in a gate worktree with the repo's dependencies installed, the same as the full set, so a Node repo's light gates do not fail with rc=127 for missing `node_modules`.

## Intent
- Do: Before the light set, run the repo's `lane_setup` lines (or the full set's install step, or reuse the integration tree's install); if none can apply, `prep` warns when a light gate runs an npm script and no gate installs.
- Non-goals: the other parts of the same issue.
- Done when: the criteria pass.

## Context
GitHub issue #70 (quoted):

> **Version:** sdlc-lite 0.33.0, repo with `merge_gate: light` and `light_scope:` in `.sdlc/config`. Seen in ui-kit-neue 2026-10-22.
>
> **What happened**
> `fanout.py land <branch> --ticket T-0296 ... --gate 'npm ci' --gate 'npm run typecheck' ... --light-gate 'npm run typecheck' --light-gate 'npm test'` classified the merge as light and failed it:
> `red: npm run typecheck rc=127 (no node_modules in the gate worktree: start the gate with \`npm ci && ...\`)`
>
> The full set starts with `npm ci`, but the light set runs in a fresh gate worktree with no dependencies installed. So any light set for a Node repo fails unless every user writes `npm ci &&` into the first light gate.
>
> **Expected**
> The light set runs with the dependencies installed, the same as the full set. That could be the repo's `lane_setup`, or the install step of the full set run first.
>
> **Workaround used**
> `--light-gate 'npm ci && npm run typecheck' --light-gate 'npm test'` on every later land. Each light install costs a full `npm ci`.
>
> **Ask**
> Run the lane setup or install step before the light set, or reuse the integration tree's `node_modules`. If not, make `prep` warn when a light gate names an npm script and no gate installs. Related to #41 (closed) and #51.

## Constraints
The failing test lands before or with the fix, never after.

## Acceptance criteria
1. A `fanout.py` selftest case reproduces the issue's report and passes; with the change reverted it fails (state the FAIL line in the Outcome).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
Fixed in `plugins/sdlc-lite/scripts/fanout.py`: a light merge into an integration tree with a package.json and no node_modules now runs the full set's install-only gates (`light_installs`) before the light set, unless a light gate installs itself. `deps_note` (dry run and prep) also warns when a light gate runs an npm script and no gate installs. Selftest case T-0742 added (fake `npm` on PATH; `ci` creates node_modules, `run` exits 127 without it).
- Red before the change: `fanout selftest: FAIL` with `T-0742 light set installs: the full set's npm ci runs before a light npm script ... red: npm run typecheck rc=127 (no node_modules in the gate worktree ...)` and `T-0742 prep warns when a light gate runs an npm script and no gate installs`.
- `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py selftest` exit 0; `python3 plugins/sdlc-lite/scripts/check.py` exit 0; `python3 scripts/check-packaging.py` exit 0; `git diff --check ee6c6693` exit 0.
- Not done: the `lane_setup` alternative (the full set's install step covers the report).

## Outcome

2026-10-22 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: ee6c6693da57
- Changed: see commits
- Commits: 46e7527 T-0742: the light gate set runs with dependencies installed
- Check: 1 A `fanout.py` selftest case reproduces the issue's report and passes; with the change reverted it...: pass
- Check: 2 `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plug...: pass
- Check: 3 `check.py` exits 0, `check-packaging.py` passes, `git diff --check <base sha>` exits 0: pass
- Follow-up: decide: plugins/sdlc-lite/scripts/fanout.py:1210-1216 An install folded... -> notes.md
- Follow-up: note: plugins/sdlc-lite/scripts/fanout.py:1884 A non-Node repo is... -> notes.md
- Follow-up: note: plugins/sdlc-lite/scripts/fanout.py:1188 INSTALL_ONLY accepts flags... -> notes.md
