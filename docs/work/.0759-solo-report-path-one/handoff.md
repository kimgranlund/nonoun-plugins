---
id: T-0759
title: "A host-lane solo brief names one report path"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-24
claimed_by: sdlc-lite-author 2026-10-24
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The solo brief for a host lane names one report path, inside the worktree, in both the `Report file:` line and the end line, so a solo never ends naming a path that does not exist.

## Intent
- Do: reproduce first (a selftest case built from the observation below), then make the smallest fix in `plugins/sdlc-lite/scripts/fanout.py` and its docs.
- Non-goals: the other rehearsal findings (each has its own ticket).
- Done when: the criteria pass.

## Context
Observed: the brief says `Report file: /Users/kimgranlund/Projects/nonoun/live036/.sdlc/runtime/tasks/add-sub/T-0001-solo.md` (main checkout) and later `write the report to .sdlc/runtime/tasks/add-sub/T-0001-solo.md under your worktree root`; T-0003 ended `solo blocked /Users/kimgranlund/Projects/nonoun/live036/.sdlc/runtime/tasks/add-div/T-0003-solo.md` and no file existed there.

Evidence: the 0.36 release rehearsal 2026-10-24 (sdlc-lite 8f98f1f1, Claude Code 2.1.309, `fanout.py prep`/`land`/`settle` with `isolation: worktree` sub-agents) in the throwaway repo /Users/kimgranlund/Projects/nonoun/live036 (state kept); report /Users/kimgranlund/Projects/nonoun/live036-run/report.md, step log /Users/kimgranlund/Projects/nonoun/live036-run/log.md, the conductor transcript under ~/.claude/projects/-Users-kimgranlund-Projects-nonoun-live036/.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A `fanout.py` selftest case: the host-lane brief's `Report file:` and end line name the same worktree-relative path and no main-checkout path; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
- `fanout.py` `subagent_dispatch`: the host-lane brief now passes the worktree-relative report path to `solo_run.report_lines`, so the `Report file:` line, the end line (`solo <status> <path>`) and the write instruction all name `<records dir rel>/<name>.md`; the dispatch `result` stays the absolute primary path, which `dispatch.py record` (host worktree copy, T-0740) and `advance` (`solo_blocked`, T-0760) still read. The prep docstring says so.
- Tests: new case 30c (host brief names the one relative path, no main-checkout path); case 22 now expects the relative path in both lines.
- Negative control (fix absent, case 30c present): `fanout selftest: FAIL` with `case 30c host brief: the Report file line and the end line name the worktree-relative .sdlc/runtime/tasks/t1/T-0001-solo.md and the prompt holds no main-checkout path '.../host-dirty/.sdlc/runtime/tasks/t1/T-0001-solo.md'`, the only miss.
- Checks: `gate_lock.py run ... fanout.py selftest` exit 0 (PASS), `dispatch.py selftest` exit 0 (PASS, record and advance), `check.py` exit 0, `check-packaging.py` exit 0, `git diff --check b1f910d9` exit 0.

## Outcome

2026-10-24 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: b1f910d927cf
- Changed: see commits
- Commits: 6f4b362 T-0759: a host-lane solo brief names one worktree-relative report path
- Check: 1 A `fanout.py` selftest case: the host-lane brief's `Report file:` and end line name the same work...: pass
- Check: 2 `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plug...: pass
- Follow-up: note: conductor question 1 can the solo Write a relative path: the Report... -> notes.md
- Follow-up: note: conductor question 2 solo-report check with a relative path... -> notes.md
- Follow-up: note: conductor question 3 block-role-write hook... -> notes.md
- Follow-up: note: docs/work/0759-solo-report-path-one/handoff.md Outcome says case... -> notes.md
