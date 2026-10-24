---
id: T-0735
title: "Audit for run.sh-era assumptions in prepare-launched roles"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-22
claimed_by: sdlc-lite-author 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
No role, hook, brief, skill or script assumes the run.sh environment (SDLC_TMP_WORKTREES, SDLC_ROLE, the run.sh prompt lines, run.sh cleanup) for a role launched by `dispatch.py prepare`; every remaining assumption is fixed or listed as deliberate.

## Intent
- Do: grep `plugins/sdlc-lite` for `SDLC_TMP_WORKTREES`, `SDLC_ROLE`, `run.sh`, `SDLC_BASE_SHA`, `BASH_DEFAULT_TIMEOUT_MS` and each env var `run.sh` exports (`run.sh` about line 710). For each hit in a hook, brief builder, agent definition, skill or script that a prepare-launched sub-agent reaches, decide: works without run.sh, fix it, or deliberate. Fix the small ones here; file a new ticket for any fix larger than a few lines. Record the full list (path:line, verdict) in the Outcome.
- Non-goals: changing run.sh itself; Codex-only paths.
- Done when: the criteria pass.

## Context
Root-cause review 2026-10-22: roles moved from run.sh to `dispatch.py prepare` sub-agents, and run.sh-era assumptions kept surfacing one at a time: T-0707, T-0708, T-0709, T-0711, T-0726, #50 (SDLC_TMP_WORKTREES unset for prepare roles). Nobody has swept the rest.

## Acceptance criteria
1. The Outcome lists every hit of the grep set with a verdict (works, fixed, deliberate, or a new ticket id).
2. Each fix has a selftest case or hook-selftest case that fails without it (state the FAIL lines).
3. `bash plugins/sdlc-lite/scripts/hook-selftest.sh`, the dispatch and steps selftests (through gate_lock), `check.py` and `check-packaging.py` pass; `git diff --check <base sha>` exits 0.

## Outcome
Grep set: `SDLC_TMP_WORKTREES`, `SDLC_ROLE`, `SDLC_BASE_SHA`, `BASH_DEFAULT_TIMEOUT_MS`, `BASH_MAX_TIMEOUT_MS` (the env `run.sh:713` and `run.sh:566` export), `SDLC_LANE_OVERRIDE_APPLIED` (`run.sh:396`), and `run.sh`, over `plugins/sdlc-lite` at base 16f3c066. Generated files (`agents/*-L<n>.md`, `adapters/codex/agents/*.toml`) take the verdict of their source.

Fixed here:
- `scripts/dispatch.py:1373` (Base sha brief line): fixed. A prepare-launched builder or verifier has no `SDLC_BASE_SHA` in its shell, so a planner criterion such as `test -z "$(git diff --name-only "$SDLC_BASE_SHA" ...)"` ran `git diff ""` (exit 128) and passed vacuously. The line now says to run such a span as written after `export SDLC_BASE_SHA=<base> &&`. Negative control: the new case on the base tree prints `FAIL: T-0735 the brief has the builder export SDLC_BASE_SHA before a criterion that names it` and `dispatch selftest: FAIL`.
- `hooks/block-stray-worktree.sh:56` and `hooks/block-role-rm.sh:116` (deny text): fixed. For a sub-agent (variable unset) the allowed form said `"$SDLC_TMP_WORKTREES/<name>"`, the form the same message's reason refuses (seen live in this run); it now names the literal prefix, and the variable form only when the variable is set. Negative control: the new hook-selftest case on the base hooks prints `hook selftest: FAIL: block-stray-worktree 'git worktree add --detach "$SDLC_TMP_WORKTREES/base" HEAD' with the variable unset: the allowed form names $SDLC_TMP_WORKTREES`.

New ticket: T-0753 (solo briefs from `solo_run.py` carry no Base sha line and `fanout.py:2159` `SOLO_SYNC` no export instruction, so a solo span naming `$SDLC_BASE_SHA` expands it to empty).

Works without run.sh (each falls back for a sub-agent or is set by its own launcher):
- `hooks/_role.sh:7,13,39-40`, `block-background.sh:2,7,12`, `block-disk-scan.sh:2`, `block-pattern-kill.sh:2`, `block-publish.sh:2`, `block-repo-format.sh:2`, `block-role-write.sh:2`, `block-role-spawn.sh:3,32`: SDLC_ROLE else the sub-agent's agent_type.
- `hooks/block-stray-worktree.sh:2-21,45-49,238-299,338` and `block-role-rm.sh:2,12,15,35-36,94-96,112`: the prefix falls back to `wtroot.py root`/tmp (and the scratch root) when the variable is unset; the variable form is refused when unset (T-0708).
- `scripts/steps.py:46-66,154-155,442,499,1004-1067,1257,2456,7969,8014,8024`, `specgate.py:39`, `redck.py` (base via `steps.base_sha`): set SDLC_BASE_SHA and SDLC_TMP_WORKTREES per span themselves (T-0726).
- `scripts/dispatch.py:2,37,39,74,99,113,119-122,142-182,247,269,513-610,1256-1260,1361,1444`: prepare and record mirror run.sh; record removes the prefix and scratch dir (T-0711, T-0712); the brief forbids `$SDLC_TMP_WORKTREES` in paths (T-0707).
- `scripts/traces/rerun.py:13,96`: uses the variable when set, else its own temp root.
- `scripts/fanout.py:184,260-262,697,712,1542-1543`, `solo_run.py:42,642`, `bench.sh:32`, `supervisor.py:125-127,212,803,1366`: these launchers set SDLC_ROLE and the timeouts for their own headless children; not a prepare path.
- `agents/builder.md:22,25`, `verifier.md:20-21`, `plan-reviewer.md:44`, `planner.md:36,38,46,47,51`: name the brief's prefix first (T-0707); `$SDLC_BASE_SHA` now works through the dispatch.py fix; record removes the prefix (T-0712).
- `agents/conductor.md:40,52`, `solo.md:44,46`, `skills/chain/references/dispatch.md:5`, `skills/fanout/SKILL.md:69`, `skills/fanout/references/solo-lanes.md:5`, `skills/file/SKILL.md:33`, `skills/ask/SKILL.md:54`, `skills/open-questions/SKILL.md:51`, `skills/plan/references/plan-rules.md:54`, `skills/run-plan/SKILL.md:20`, `skills/clarify/SKILL.md:123`, `skills/handoff-format/references/step-handoff-rules.md:11`, `skills/handoff-format/run-operations.md:31,58,86`, `AGENTS.md:28,31,38`: conductor-facing text that states which launcher sets what; accurate for prepare roles.
- `scripts/check.py:22,119,215-216,419,1021,1163-1164`, `plan_check.py:1654-1667`, `traces/detectors/hygiene.py:138`: contract phrase checks and fixtures, no runtime assumption.

Deliberate:
- `scripts/run.sh` (all hits): run.sh itself, out of scope.
- `scripts/codex_exchange.py:56`, `codex_exec.py:40`, `adapters/codex/**`, `scripts/reap-tmp-worktrees.sh:9`, `scripts/run-selftest.sh`, `scripts/codex-selftest.py`: Codex-only or run.sh-only paths (reap targets run.sh `<role>-<pid>` prefixes).
- `scripts/hook-live-probe.sh:87,119,376`, `scripts/hook-selftest.sh`, `lifecycle-selftest.py`, `supervisor.py:2341-2875`, `fanout.py:3523-5125`, `steps.py:5167-7140`, `dispatch.py:2589-3831`, `specgate.py:179-299`: selftest fixtures that set the variables on purpose.
- `bench/results/**`, `scripts/traces/fixtures/**`: historical records.
- Remaining `run.sh` mentions (about 125 files, mostly "as run.sh does" parity notes in scripts, and Codex dispatch in skills, `agents/conductor.md`, `adapters/codex/instructions.md`): Codex still dispatches through run.sh (`dispatch.py:1161`), and parity notes describe run.sh rather than an assumption a prepare role relies on.

Checks: `bash plugins/sdlc-lite/scripts/hook-selftest.sh` exit 0; `dispatch.py selftest` and `steps.py selftest` through gate_lock exit 0; `check.py` exit 0; `check-packaging.py` exit 0; `git diff --check 16f3c066` exit 0.

## Outcome

2026-10-24 · lane: solo L2 · verdict: closed by reason (delivered by the solo agent (level L2); one independent batched verifier passed before the merge; gate: full) · verifier: verifier-L2 (sonnet) · base: 16f3c066c7bc
- Changed: see commits
- Commits: 19fa545 T-0735: audit run.sh-era assumptions in prepare-launched roles
- Check: 1 The Outcome lists every hit of the grep set with a verdict: pass
- Check: 2 Each fix has a selftest case that fails without it: pass
- Check: 3 Gates pass: pass
- Follow-up: decide: plugins/sdlc-lite/scripts/dispatch.py:1374: the SDLC_BASE_SHA fix... -> notes.md
- Follow-up: decide: a steps.py lint rule could flag a criterion span that names... -> notes.md
- Follow-up: note: criterion #2 c, the block-role-rm.sh case, was verified by diff... -> notes.md
