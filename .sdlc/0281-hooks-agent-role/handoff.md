---
id: T-0281
title: "Hooks key on agent_type; spawn gate replaces block-role-spawn"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: [T-0275, T-0277]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Role-scoped hooks identify the role from the hook input `agent_type` (sub-agents inherit the parent env), and `block-role-spawn.sh` becomes the gate that allows only prepared dispatches.

## Intent
- Do: Hooks key on agent_type; spawn gate replaces block-role-spawn.
- Non-goals: anything outside this deliverable; a new idea is a new ticket.
- Done when:
  - A shared resolver (`hooks/_role.sh`) returns the role from `SDLC_ROLE`, else `agent_type` with the `sdlc-lite:` prefix and `-L<n>` suffix removed; publish, pattern-kill, stray-worktree, repo-format, and disk-scan hooks use it, and `hook-selftest.sh` proves each still blocks for a sub-agent role input and passes for an input with no role (negative control per hook).
  - `block-role-spawn.sh` allows a conductor Agent spawn only when `subagent_type` is `sdlc-lite:<role>-L<n>`, `name` matches `<role>-L<n>-<slug>[-<k>]`, a `<name>.dispatch.json` exists next to the named handoff, and the `model` parameter equals the dispatch model; each of the four conditions has a deny case, and a `run.sh` invocation is unaffected.
  - `subagent_type: fork` is denied when the name starts with `verifier-` or `plan-reviewer-`; a fork of any other role needs a `Fork reason:` line in the prompt.
  - A read-only role sub-agent may Write only the dispatch result path; a Write elsewhere is denied; the builder is unrestricted (deny and allow cases).
  - `bash plugins/sdlc-lite/scripts/hook-selftest.sh` passes, and `docs/maintenance/claude-hooks.md` describes the new rules.

## Context
Design section 4. If probe P2 fails (hooks do not see agent_type for sub-agent calls), stop and replan: the fallback is `tools:` allowlists in the generated definitions and the spawn gate only.

## Constraints
The old deny of conductor spawns is removed in the same change that adds the gate, so conductor sessions that still call run.sh keep working. No em dashes. No push, tag, or publish.
