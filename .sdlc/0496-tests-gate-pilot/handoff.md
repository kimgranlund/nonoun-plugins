---
id: T-0496
title: "Pilot: solo L2 closes on green criteria with observed-red controls; verifier by exception"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A solo L2 ticket whose acceptance criteria are all mechanical and each carry an observed-red control closes on green criteria with no independent verifier; the verifier runs by exception. A measured pilot over the next 20 qualifying tickets decides whether it stays.

## Intent
- Do: extend `plugins/sdlc-lite/scripts/verify_scope.py` (the T-0429 docs-only skip) with a second skip class, `tests-gate`, printed with exit 0 when ALL hold: ticket level is L2 and the lane is solo; every acceptance criterion is a command span (no prose-only criterion); every `(red)` criterion has a pre-edit control record in `red-checkpoint.jsonl` with phase `pre-edit` (not `retrospective`); the solo report lists each span with exit 0 (the Run-verbatim rule, T-0471); the diff touches no shared name (a `git grep` of each added, renamed or removed contract id, schema key, selftest label or command line finds no dependent outside the diff); the diff is at most 8 files and 300 changed lines; no path under `agents/`, `hooks/`, `adapters/`, `levels.json`, `models.json`, `run.sh`, `dispatch.py`, `results.py`, `gate_lock.py` or security-sensitive code; the handoff has no `verifier: L1..L3` line. Any other case prints the first unmet condition and exits 1 (verifier still needed). Add the class to `agents/solo.md` `## Verification` as one affirmative line and to the lane report (`lanes.py`, `solo_stats.py` print `gate: tests-only` or `gate: verifier`). Record every skip in the ticket close note.
- Pilot guard: the skip is on by default only when `.sdlc/config` has `tests_gate: pilot`; this repo sets it. Measure with `solo_stats.py`: K-005 first-pass rate and rework after close (a reopened ticket, or a follow-up ticket citing a closed one within 7 days) for pilot tickets versus the 89 of 123 (72 percent) baseline, plus verifier dollars and minutes not spent. Revert rule, written in the ticket: if K-005 for the pilot tickets falls below 72 percent, or any pilot ticket is reopened for a defect a verifier would have caught, set `tests_gate: off` and report.
- Non-goals: any change for L1 (solo L1 already runs no verifier), L3 and above, chain tickets, merge steps, or model and effort rows; removing the verifier role; the second-round rule.
- Done when: `verify_scope.py selftest` has a positive case (a qualifying L2 diff prints `tests-gate`, exit 0) and an observed-red negative control for each of the nine conditions (each makes it exit 1 naming that condition); `solo_stats.py selftest` prints the gate field; `claude_roles.py generate --check`, `codex_roles.py generate --check`, `check.py` and `prompt_lint.py` exit 0 with `solo.md` prohibitions not above its current count; `.sdlc/config` here gets `tests_gate: pilot`.

## Context
Origin: maintainer thinking 2026-10-12 that independent verification adds ceremony and token burn on small tasks, where a few designed tests could guarantee the outcome. Evidence: verifiers are 7.5 percent of spend against planning 55 percent (`docs/reports/2026-10-12-industry-alternatives-review.md`); of 34 first-round verifier non-passes, 22 were builder gaps, 9 criterion defects the builder could not catch, 0 verifier over-reach, and 13 of the 34 were reachable by the Search-dependents and Run-verbatim rules (`docs/reports/2026-10-11-solo-fails-and-blocks.md`, T-0471); 4 builder gaps were found only by the verifier's own probe (144 minutes, the costliest). Ceremony audit: `docs/reports/2026-10-12-ceremony-audit.md`. The criterion-defect share is why the controls are required: a builder's test can be wrong, and a check that cannot fail is the defect class this system exists to stop. Pillars: cost and performance up, quality guarded by the revert rule.

## Constraints
No model or effort change. The skip never applies when a criterion lacks an observed-red control. One writer on `solo.md`. Depends on T-0471 (merged) and benefits from T-0473 and T-0486 (red checkpoint on resumed work); a `retrospective` control disqualifies a ticket, which is the safe direction.
