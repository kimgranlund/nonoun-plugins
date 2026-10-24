---
id: T-0761
title: "settle without --forward leaves main where it is"
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
`fanout.py settle <integration>` without `--forward` never moves main, as the fanout skill documents (`--forward` is the flag that brings the integration branch into main); or the docs say exactly when plain settle moves main.

## Intent
- Do: reproduce first (a selftest case built from the observation below), then make the smallest fix in `plugins/sdlc-lite/scripts/fanout.py` and its docs.
- Non-goals: the other rehearsal findings (each has its own ticket).
- Done when: the criteria pass.

## Context
Observed: `settle fanout/rehearsal` (no --forward) printed `settled: fanout/rehearsal is in main`, and the reflog shows `26b7276 main@{0}: merge fanout/rehearsal: Fast-forward`. First reproduce and find whether this is intended (read `fanout.py settle` and the skill's settle text); state the finding in the Outcome.

Evidence: the 0.36 release rehearsal 2026-10-24 (sdlc-lite 8f98f1f1, Claude Code 2.1.309, `fanout.py prep`/`land`/`settle` with `isolation: worktree` sub-agents) in the throwaway repo /Users/kimgranlund/Projects/nonoun/live036 (state kept); report /Users/kimgranlund/Projects/nonoun/live036-run/report.md, step log /Users/kimgranlund/Projects/nonoun/live036-run/log.md, the conductor transcript under ~/.claude/projects/-Users-kimgranlund-Projects-nonoun-live036/.

## Constraints
The failing test lands before or with the fix.

## Acceptance criteria
1. A `fanout.py` selftest case pins the documented behavior of plain settle on main; with the change reverted it fails (state the FAIL line); if the behavior was intended, the case pins it and the skill text says so.
2. `python3 plugins/sdlc-lite/scripts/gate_lock.py run --need compute_units=1 --nice -- python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0, `check.py` exits 0, `check-packaging.py` passes, and `git diff --check <base sha>` exits 0.

## Outcome
Finding: intended. `cmd_settle` (docstring, case 28 `fanout/ff`, and `references/main.md` for the light gate path) always fast-forwards the current branch when the integration branch is a fast-forward of it; `--forward` only adds the diverged case (merge main in, regenerate, run `--gate`) and its refusals. The skill text implied otherwise, so it was the docs that were wrong, not the code.
Change: new selftest case `T-0761 plain settle` in `fanout.py` (no --forward, no --gate, main moves to the integration tip); settle section of the `fanout.py` docstring states the rule; `skills/fanout/SKILL.md` `--forward` row now says without it `settle` only fast-forwards (17,973 of 18,000 chars); `skills/fanout/references/main.md` gains "What plain settle does" (to leave main alone: do not settle, or `--catch-up`).
Negative control: with the ff block made conditional on `a.forward`, the selftest FAILs, first on `T-0761 plain settle: no --forward and no --gate, a fast-forward integration branch still moves main from 95873e7 to its tip 786449a, got rc=1 main=95873e7 ...` (plus cases 28, T-0565, T-0489, T-0481). Reverted.
Checks: fanout selftest exit 0 (PASS), check.py exit 0, check-packaging.py exit 0, `git diff --check c6d6b586` exit 0.

## Outcome

2026-10-24 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full) · verifier: verifier-L2 (opus) · base: c6d6b5867416
- Changed: see commits
- Commits: 0838656 T-0761: plain settle fast-forwards main by design; pin it and say so in the docs
- Check: 1 A `fanout.py` selftest case pins the documented behavior of plain settle on main; with the change...: pass
- Check: 2 selftest via gate_lock exits 0, `check.py` exits 0, `check-packaging.py` passes, `git diff --chec...: pass
- Follow-up: note: plugins/sdlc-lite/scripts/fanout.py:125 says "--forward only adds... -> notes.md
- Follow-up: note: the new T-0761 case overlaps case 28's fanout/ff assertion both... -> notes.md
