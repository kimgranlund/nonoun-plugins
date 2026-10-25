---
id: T-0777
title: "land overlap ignores lanes already landed and removed"
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
`fanout.py land` reports overlap only against lanes still open; a host lane that already landed and whose worktree was removed is not listed.

## Intent
- Do: reproduce first (a selftest case built from the observation), then the smallest fix in `plugins/sdlc-lite/scripts/fanout.py` and its docs.
- Non-goals: other rehearsal findings.
- Done when: the criteria pass.

## Context
Observed: the T-0003 land report listed the T-0001 lane (worktree already removed) and a false overlap: `Overlap: agent-a0c9e143dcc776478 and agent-a098b45af8ca1f151: calc/__init__.py, tests/test_calc.py`.

Evidence: the second 0.36 release rehearsal 2026-10-25 (sdlc-lite b7c64749) in /Users/kimgranlund/Projects/nonoun/live036b (state kept, read-only); report /Users/kimgranlund/Projects/nonoun/live036b-run/report.md, log /Users/kimgranlund/Projects/nonoun/live036b-run/log.md.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A `fanout.py` selftest case reproduces the observation and passes; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
- Cause: `fanout.py land` reports every ticket in the lanes dir's land journal, so a lane landed earlier whose host worktree was removed still got a table row, a Lane line and an Overlap pair.
- Fix: `lanes.landed_and_gone` (the T-0762 HOST-GONE test, now one helper that `lanes.evaluate` also uses) and `cmd_land` skips a prior journal entry whose recorded worktree is gone and whose branch is an ancestor of the integration branch. Docs: fanout.py land section, lanes.py API line; the HOST-GONE mutant needle follows the renamed line.
- Red first: case 23 "land gone lane (T-0777)" failed before the fix with `FAIL: case 23 land gone lane (T-0777): landed branches whose worktrees are gone are not listed and are no overlap, got rc=0 ... - Overlap: `agent-g1` and `agent-g2`: `shared.txt``; its control (worktrees still standing, rows and overlap kept) passed both before and after.
- Checks: `fanout.py selftest` via gate_lock exit 0 (PASS), `lanes.py selftest` exit 0 (HOST-GONE mutant ok), `check.py` exit 0, `check-packaging.py` exit 0, `git diff --check aec100f3` exit 0.

## Outcome

2026-10-24 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: aec100f3cfb1
- Changed: see commits
- Commits: beec660 T-0777: land report ignores lanes already landed and removed
- Check: 1 A `fanout.py` selftest case reproduces the observation and passes; with the change reverted it fa...: pass
- Check: 2 The fanout selftest through gate_lock exits 0, `check.py` exits 0, `check-packaging.py` passes, a...: pass
- Follow-up: note: plugins/sdlc-lite/scripts/lanes.py:737 evaluate now calls the... -> notes.md
- Follow-up: note: The added not Pathpath.is_dir in landed_and_gone does nothing extra... -> notes.md
- Follow-up: note: python3 plugins/sdlc-lite/scripts/dispatch.py selftest on this lane... -> notes.md
