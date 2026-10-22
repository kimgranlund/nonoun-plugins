---
id: T-0740
title: "Solo lanes in host worktrees commit and report where land reads"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
claimed_by: sdlc-lite-author 2026-10-22
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A solo running in a Claude Code host worktree (`isolation: worktree`) ends with its change committed on its lane branch and its report where `dispatch.py record` and `fanout.py land` read it, with no manual conductor step.

## Intent
- Do: First establish which layer refuses the git commands ("too complex to verify" is not in `plugins/sdlc-lite/hooks/`; check whether it is Claude Code's own worktree isolation) and record it in the Outcome. Then fix the plugin side: either the brief from `fanout.py prep` stops asking a host-worktree solo to run git (it leaves changes uncommitted) and `land` commits a dirty host lane itself, or the hooks allow git inside the agent's own worktree if a plugin hook is the cause. Make the brief's `Report file:` point at a path the solo can write, and make `record` and `land` read it there (reuse the T-0720 fallback where it fits).
- Non-goals: the other parts of the same issue.
- Done when: the criteria pass.

## Context
GitHub issue #68 (quoted):

> **Version:** sdlc-lite 0.33.0, Claude Code host, `fanout.py prep` sub-agent lanes (`isolation: worktree`). Seen in ui-kit-neue 2026-10-22 (T-0294, T-0295, T-0296, T-0298, T-0299).
>
> **What happened**
> In all five solo lanes the worktree guard hook refused every git command, even `git status` and `git log`, as "too complex to verify". So the solo could not:
> - run the brief's first step, `git merge --ff-only <base sha>`;
> - make the `WIP <id>` commits or the final `<id>: <title>` commit the brief asks for;
> - write its report to the brief's `Report file:` path in the primary checkout (`<repo>/.sdlc/runtime/tasks/<task>/<id>-solo.md`). The Write was refused as outside the worktree.
>
> Each solo ended `done` (or `blocked` only for git) with its change uncommitted and its report at the worktree copy of the report path.
>
> **Expected**
> A solo in a host worktree can run git inside its own worktree and commit on its branch, and it can write the report where `dispatch.py record` and `fanout.py land` look for it. Otherwise the brief should not ask for any of these.
>
> **Workaround used**
> The conductor read each report from `<worktree>/.sdlc/runtime/tasks/<task>/`, ran `git add <named files> && git commit -m "<id>: <title>"` in the worktree, and copied the report into the primary checkout's records dir before `fanout.py land`. This happened 5 of 5 times.
>
> **Ask**
> Either allow git (status, log, diff, add, commit, merge --ff-only) inside the agent's own worktree in the guard hook, or make the solo brief say "leave changes uncommitted; the conductor commits" and have `land` commit a dirty lane itself. Point the brief's report path at the worktree copy, or have `record` and `land` read from there. Related to #45 (closed; that one was about shell variables).

## Constraints
The failing test lands before or with the fix, never after.

## Acceptance criteria
1. A `fanout.py` selftest case reproduces the issue's report and passes; with the change reverted it fails (state the FAIL line in the Outcome).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0.
3. `python3 plugins/sdlc-lite/scripts/check.py` exits 0, `python3 scripts/check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
Layer: host-side. No plugin hook emits "too complex to verify" (`grep -rn "too complex"` hits only this handoff). `block-stray-worktree.sh` exits 0 for any command without the word `worktree` and its refusals start `Blocked for sdlc role`; `block-role-write.sh` applies only to read-only roles, never solo; `block-publish.sh` has no git status or commit rule. The git refusals and the refused Write outside the worktree come from Claude Code's own `isolation: worktree` sandbox for a background sub-agent, which cannot answer a permission prompt. The plugin-side defect was that the prep brief asked for git and a Report file outside that sandbox, and that only the primary report path was read.

Plugin-side fix (no hook change):
- `fanout.py` `SOLO_SUBAGENT_PROMPT`: the solo leaves its change uncommitted and writes its report at the worktree copy of the Report file (`<records dir rel>/<id>-solo.md` under its worktree root); a refused `git merge --ff-only` stops it only when the handoff is still missing.
- `fanout.py` `land_ticket`: a solo lane on a host branch (`worktree-<id>-solo`, `worktree-agent-<id>`) with a dirty worktree is committed there as `<id>: <title>` before the no-changes check; the existing records carry brings the report into main.
- `fanout.py` prep writes `artifacts_dir` into the solo's `<id>-solo.dispatch.json`, so `dispatch.py record` accepts it; `dispatch.py` `solo_report_file` falls back to `host_report_copy` (`.claude/worktrees/agent-<agent_id>/<rel>`, else the one worktree holding a copy) and copies it to the primary path.
- Records: fanout.py docstring, `skills/fanout/SKILL.md`, `docs/references/sdlc-internals.md`.

Checks: `fanout.py selftest` (new case 30b) exits 0; `dispatch.py selftest` exits 0; `check.py` exits 0; `check-packaging.py` exits 0; `git diff --check 8f08aaab` exits 0.
Negative control (fix reverted, case 30b kept): FAIL lines `case 30b host worktree: the brief asks for no commit and names the worktree copy .sdlc/runtime/tasks/t1/T-0001-solo.md of the Report file`, `case 30b host worktree: dispatch.py record --agent-id y takes the report from the worktree copy, got rc=2 ... is not a dispatch file (missing tmp_prefix, tree, artifacts_dir, ...)`, and `case 30b host worktree: land commits the uncommitted host lane as T-0001: Ticket t1 ... got rc=1 subject='sizes'`.
Open: when the host refuses git, the ff sync to the base sha cannot run either, so a claim commit absent from origin still ends in a blocked report.
