---
id: T-0593
title: "A repo pins the minimum plugin version every host must run"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P1         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
No host runs a role in a repo with an older plugin than the repo needs. A `plugin_min: X.Y.Z` line in `.sdlc/config` makes `dispatch.py prepare`, `run.sh` and `lanes.py open` refuse, with exit 2, when the running plugin's version is lower. The refusal names both versions and the update command for that host.

## Context
Maintainer decision 2026-10-15 (risk 1 of the multi-host review). Claude Code and Codex install the plugin separately, so one repo can run two versions with different worktree roots and rules. On 2026-10-15 this repo's session ran 0.23.1 hooks while the code expected the 0.24 sibling root, and verifiers had to work around it. The version is in each plugin manifest (`.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`).

## Intent
- Do: read the version from the running plugin's own manifest; compare it with `plugin_min:`; refuse below it. `onboard.py setup` and the release steps can set the line. `tickets.py check` warns when `plugin_min:` is above the running version.
- Non-goals: auto-updating a plugin.
- Done when: the criteria pass.

## Constraints
No `plugin_min:` line means no check. The comparison is numeric per part (0.10.0 > 0.9.0).

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0. Its new case shows `plugin_min:` above the manifest version refusing with exit 2 and both versions named, and an equal version passing. The case failed before the change.
2. `bash plugins/sdlc-lite/scripts/run-selftest.sh` exits 0 with the same refusal for `run.sh`, and `lanes.py selftest` exits 0 with it for `open`.
3. `git diff --check` exits 0.
