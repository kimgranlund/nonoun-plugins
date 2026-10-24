---
id: T-0735
title: "Audit for run.sh-era assumptions in prepare-launched roles"
type: chore           # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
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
