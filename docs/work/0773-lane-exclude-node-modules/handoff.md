---
id: T-0773
title: "Lane commits never add a node_modules symlink; open warns when lane_setup is unset"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The defect GitHub issue #81 reports no longer happens (title: Lane commits never add a node_modules symlink; open warns when lane_setup is unset).

## Intent
- Do: first confirm it still reproduces on main (0.36 work changed nearby code: owner trees T-0749 to T-0755, host lanes T-0756 to T-0764); if it no longer does, add the regression case and say so in the Outcome. Otherwise fix it in `plugins/sdlc-lite/scripts/lanes.py` (the issue names the lines and a proposed fix; take it unless the code shows a better one) and update the docs that describe the behaviour.
- Non-goals: other issues.
- Done when: the criteria pass.

## Context
GitHub issue #81 (quoted):

> **Observed:** a repo without `lane_setup:` in `.sdlc/config` got lanes with no dependencies; a `node_modules` symlink added by hand was committed by the lane's `git add -A` because `.gitignore`'s `node_modules/` (directory pattern) does not match a symlink, and the land's naming check then failed on it.
>
> **Root cause:** `lane_setup` (T-0692, #41) works but is opt-in with no warning; the lane commit (`scripts/lanes.py:1253`, `scripts/fanout.py:1436`) excludes logs and local settings but not a `node_modules` symlink (the plugin already warns a symlink is no fix, `fanout.py:1198-1207`).
>
> **Proposed fix:** add `/node_modules` (no trailing slash) to the lane's `info/exclude` the way `lanes.py:1540` does for local settings, and warn at `lanes.py open` when `package.json` exists but `lane_setup` is unset.
>
> Found in sdlc-lite 0.35.0 while conducting a fanout run; root cause traced in the plugin source.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A `lanes.py` selftest case reproduces the issue's report and passes; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/lanes.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
