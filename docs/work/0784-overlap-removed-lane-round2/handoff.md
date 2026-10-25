---
id: T-0784
title: "land overlap ignores a removed lane from an earlier round"
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
A land in a second sub-agent round lists no lane that landed in an earlier round and whose worktree was removed, and reports no overlap with it.

## Intent
- Do: reproduce first with a selftest case built from the observation, then the smallest fix in `plugins/sdlc-lite/scripts/fanout.py` and its docs.
- Non-goals: other findings.
- Done when: the criteria pass.

## Context
Observed: after round 1 landed T-0001 (host lane `agent-a3ec2829004940e86`), settle closed the integration tree and the `git worktree remove` line was run; round 2 opened a new `fanout/rehearsal` from main. The T-0002 and T-0003 land reports still listed `Lane agent-a3ec2829004940e86: .../.claude/worktrees/agent-a3ec2829004940e86` and `Overlap: agent-a3ec2829004940e86 and agent-ae3c036bc2b44058b: calc/__init__.py, tests/test_calc.py`. T-0777 added `lanes.landed_and_gone` (worktree gone and branch an ancestor of the integration branch) to skip such entries; find why it did not apply here (the land journal entry, the recorded worktree path, the new integration branch, or the branch still existing) and fix it, with a case built from this two-round shape.

Evidence: the fourth 0.36 rehearsal 2026-10-25 (sdlc-lite 7d8acebe) in /Users/kimgranlund/Projects/nonoun/live036d (state kept, read-only); report /Users/kimgranlund/Projects/nonoun/live036d-run/report.md, log /Users/kimgranlund/Projects/nonoun/live036d-run/log.md, lanes dir /Users/kimgranlund/Projects/nonoun/live036d.worktrees.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A `fanout.py` selftest case reproduces the observation and passes; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.
