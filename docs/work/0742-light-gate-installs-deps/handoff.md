---
id: T-0742
title: "The light gate set runs with dependencies installed"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
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
