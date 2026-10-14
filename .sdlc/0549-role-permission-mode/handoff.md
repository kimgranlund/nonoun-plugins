---
id: T-0549
title: "Role Bash calls stop tripping the host's plan mode (permissionMode: default), so Bash stops prompting"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-14
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Role sub-agents stop triggering Claude Code's built-in "This shell -c script runs rm and could not be checked" approval, which asks even under bypass permissions.

## Intent
- Do: add one rule to the shared role command guidance (the place every role reads it, e.g. `skills/handoff-format` or the agent contracts `claude_roles.py` generates from): run each check as a plain command, and never pass a built string to `bash -c "$var"`, `sh -c`, or `eval`. A helper like `run(){ bash -c "$2"; }` is exactly the pattern to avoid. When a criterion is itself a shell string, run it as written in its own call.
- Do: a live probe in a throwaway project under a bypassing parent: the old pattern prompts, and the new guidance produces a run with no prompt.
- Non-goals: `bypassPermissions` or `permissionMode` in any shipped agent (the user always runs bypass, and the parent mode already wins); changing a user's settings.
- Done when: the rule is in the role guidance, `claude_roles.py generate --check` and `check.sh` pass, and the live probe shows the prompt before and none after.

## Context
Maintainer report 2026-10-14, with a screenshot from the maison `0535-planner-L3-4` agent. The command defined `run(){ out=$(bash -c "$2" 2>&1); ... }` and passed criteria strings into it, along with `sed -i` and `git worktree add`. The host showed "This shell -c script runs rm and could not be checked. Do you want to proceed?" while the user ran bypass permissions. That text is not from an sdlc-lite hook (grep of `plugins/sdlc-lite/hooks/` finds none), so it is Claude Code's own check on a `bash -c` script whose content it cannot read. Inherited plan mode is ruled out: the user always runs bypass, and under a bypassing parent the sub-agent's mode does not apply (docs/references/claude-hooks.md, probe P1).

## Constraints
Wording only, plus the probe; no hook that rewrites commands.
