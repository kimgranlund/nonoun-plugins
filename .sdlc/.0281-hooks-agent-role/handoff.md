---
id: T-0281
title: "Hooks key on agent_type; spawn gate replaces block-role-spawn"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
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

## Acceptance criteria
Paths are under `plugins/sdlc-lite/` unless a command starts with `plugins/`; commands run from the repository root. A hook is run by piping a JSON payload to it with `SDLC_ROLE` and `SDLC_TMP_WORKTREES` unset (`env -u SDLC_ROLE`); exit 2 is a deny, exit 0 a pass.
1. `bash plugins/sdlc-lite/scripts/hook-selftest.sh` prints `hook selftest: PASS`; `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --selftest` prints `hook live probe selftest: PASS`; `python3 scripts/check-packaging.py` exits 0; `bash plugins/sdlc-lite/scripts/check.sh` exits 0 (it runs shellcheck over `hooks/*.sh` when installed).
2. `hooks/_role.sh` defines `sdlc_role <json>`: with `SDLC_ROLE` unset, `{"agent_type":"sdlc-lite:builder-L3"}` prints `builder`, `sdlc-lite:plan-reviewer-L1` prints `plan-reviewer`, `sdlc-lite:solo-M` prints `solo`; `sdlc-lite:conductor`, `general-purpose`, and a payload with no `agent_type` print nothing; with `SDLC_ROLE=verifier` it prints `verifier` whatever the `agent_type`.
3. `block-publish.sh`, `block-pattern-kill.sh`, `block-disk-scan.sh`, and `block-stray-worktree.sh` each exit 2 for a payload with `"agent_type":"sdlc-lite:verifier-L2"` and a command that role run blocks (a push, a pattern kill, a search of `/`, a worktree add with `-b`), and exit 0 for the same command with no `agent_type`; `block-repo-format.sh` exits 2 for `npm run format` with `"agent_type":"sdlc-lite:builder-L2"` and 0 for the same with `sdlc-lite:verifier-L2` or none. All five source `_role.sh` (no remaining `SDLC_ROLE` test decides the block).
4. `block-role-spawn.sh`, for a conductor Agent spawn, exits 0 for `subagent_type: sdlc-lite:verifier-L3`, `name: verifier-L3-<slug>`, a `verifier-L3.dispatch.json` beside the prompt's `Handoff:` path holding that `name` and `model: opus`, and `model: opus`; and exits 2 for each of: `subagent_type` `sdlc-lite:verifier` (no level); a `name` that is not `verifier-L3-<slug>`; no dispatch record naming the agent; a `model` that differs from the record's. A Bash payload that runs `run.sh` as the conductor exits 0, and `adapters/claude/hooks.json` registers `block-role-spawn.sh` only under the `Agent` matcher.
5. `block-role-spawn.sh` exits 2 for `subagent_type: fork` with a name starting `verifier-` or `plan-reviewer-` even with a `Fork reason:` line, exits 2 for a fork of `builder-L3-x` with no `Fork reason:` line, and exits 0 for it with a `Fork reason: <text>` line.
6. `block-role-write.sh` (registered under the `Edit|Write|NotebookEdit` matcher) exits 0 for a `sdlc-lite:verifier-L3` Write whose `file_path` is the `result` of the `verifier-L3.dispatch.json` beside it; exits 2 for that role writing any other path, for an Edit, and for a NotebookEdit; exits 0 for `sdlc-lite:builder-L3` writing, editing, or notebook-editing any path.
7. `docs/maintenance/claude-hooks.md` has sections for `hooks/_role.sh`, the rewritten `hooks/block-role-spawn.sh` (four conditions, fork rules), and `hooks/block-role-write.sh`; `git diff --check` is clean and no changed file holds an em dash.
8. Scope: only files under `plugins/sdlc-lite/hooks/`, `plugins/sdlc-lite/scripts/hook-selftest.sh`, the header comment of `plugins/sdlc-lite/scripts/check.sh`, `plugins/sdlc-lite/adapters/claude/hooks.json`, `docs/maintenance/claude-hooks.md`, and this task folder changed.

## Closed

2026-10-06: delivered by the solo agent (tier M); one independent batched verifier passed before the merge
