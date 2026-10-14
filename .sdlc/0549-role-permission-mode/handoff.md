---
id: T-0549
title: "Role sub-agents stop inheriting the parent's plan mode (permissionMode: default), so Bash stops prompting"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-14
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Role sub-agents stop asking the maintainer to approve Bash calls, with the cause proven live before any frontmatter change ships.

## Intent
- Do: first reproduce a sub-agent Bash approval prompt in a throwaway project and record the parent's permission mode and the exact prompt. Then fix the proven cause. The candidate is `permissionMode: default` in the role frontmatter that `scripts/claude_roles.py` generates, so roles stop inheriting a parent's plan mode and the user's own allow rules (`"Bash"`) apply.
- Non-goals: `bypassPermissions` in any shipped agent; changing a user's settings.
- Done when: the live probe shows the prompt before the fix and none after; a parent in `bypassPermissions` mode still runs its roles with no prompts (no regression); `claude_roles.py generate --check` and `check.sh` pass.

## Context
Maintainer report 2026-10-14: "I keep having to approve sub-agents use of Bash." The user settings already allow `Bash` and set `defaultMode: plan`. The user says they always run with bypass permissions on. Under a bypassing parent, sub-agent frontmatter modes do not apply (docs/references/claude-hooks.md, probe P1), so inherited plan mode may not be the cause. The probe decides. Other candidates to rule out: a session that started in plan mode before switching, or a prompt from a protected path.

## Constraints
No change ships before the probe identifies the cause.
