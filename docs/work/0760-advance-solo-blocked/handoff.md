---
id: T-0760
title: "dispatch.py advance does not route a blocked solo as done"
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
`dispatch.py advance` on a solo whose report or final line says `blocked` records it as blocked and prepares no verifier, instead of routing it as `solo L2 done`.

## Intent
- Do: reproduce first (a selftest case built from the observation below), then make the smallest fix in `plugins/sdlc-lite/scripts/dispatch.py` and its docs.
- Non-goals: the other rehearsal findings (each has its own ticket).
- Done when: the criteria pass.

## Context
Observed: T-0003's solo ended `solo blocked ...` (a plan defect in its criterion 2) and advance printed `solo L2 done` and prepared a verifier.

Evidence: the 0.36 release rehearsal 2026-10-24 (sdlc-lite 8f98f1f1, Claude Code 2.1.309, `fanout.py prep`/`land`/`settle` with `isolation: worktree` sub-agents) in the throwaway repo /Users/kimgranlund/Projects/nonoun/live036 (state kept); report /Users/kimgranlund/Projects/nonoun/live036-run/report.md, step log /Users/kimgranlund/Projects/nonoun/live036-run/log.md, the conductor transcript under ~/.claude/projects/-Users-kimgranlund-Projects-nonoun-live036/.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A `dispatch.py` selftest case: advance on a solo dispatch whose report says `blocked` prints blocked and prepares no verifier; with the change reverted it fails (state the FAIL line).
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
`dispatch.py advance` on a solo dispatch now reads the solo's report file (the dispatch's `result`): a first non-empty line starting `blocked` (or `solo blocked`) prints `stop: blocked <report>: <line>; ...`, exit 0, and prepares no verifier or close line (`solo_blocked`, `advance_solo`; usage text in the file header updated). The final stdin message is not consulted, since record already writes the report file from the transcript.
- Selftest cases `T-0760 advance on a L2 / L1 solo dispatch whose report says blocked ...` pass. Negative control (fix disabled): `FAIL: T-0760 advance on a L2 solo dispatch whose report says blocked prints stop: blocked and prepares no verifier` and the same for L1.
- `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/dispatch.py selftest` exit 0; `check.py` exit 0; `check-packaging.py` exit 0; `git diff --check 12f046a9` exit 0.
- Not done: a one-line note in `skills/fanout/SKILL.md` (it is at the 18,000 character limit); the dispatch.py header carries the behavior.
