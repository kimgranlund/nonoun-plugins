---
id: T-0613
title: "steps.py lint flags another repo's verifier file as the step's own result"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-17
claimed_by: sdlc-lite-author 2026-10-17
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`steps.py lint` no longer reports "reads this step's own verifier result" for a criterion that cites a verifier file in another repository (an absolute path outside this repo), and a test that failed before the fix passes after it; the T-0415 own-result case still fails.

## Repro
1. Write a step handoff whose criterion is `` `test -s /Users/kimgranlund/Projects/nonoun/agent-ui/.sdlc/runtime/tasks/0247-validate-payload-persona-ids/verifier-L1.md` ``.
2. `python3 plugins/sdlc-lite/scripts/steps.py lint <handoff>`.

## Expected
`steps lint: ok` (the file belongs to another repo's ticket, not this step).

## Actual
`acceptance criterion reads this step's own verifier result, so it can pass only after the verifier passes` and exit 1; renaming to `verifier-L1.attempt.json` fails the same way.

## Context
Found writing the 2026-10-17 fleet retro verify handoff (`.sdlc/runtime/tasks/fleet-retro-2026-10-17/verify/handoff.md`); worked around with a `runs.jsonl` count. Rule text is `plugins/sdlc-lite/scripts/steps.py` lines 148 to 155 (T-0415): any span holding `verifier-L<digit>` with no other `step-<m>/` folder matches. Guess: exempt absolute paths outside the repo root, as the T-0536 rule already does.

## Constraints
The failing test lands before or with the fix, never after.

## Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0 and includes a new case: a criterion citing an absolute verifier-result path outside the repository lints ok.
- The existing T-0415 own-result cases still report the finding (same selftest).
- (red) The new case fails on the base commit (revert the fix, run the selftest, observe exit 1, restore).
- `python3 plugins/sdlc-lite/scripts/plan_check.py selftest` exits 0.

## Outcome

2026-10-17 · lane: solo L1 · verdict: closed by reason (delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full; verifier notes: note: plugins/sdlc-lite/scripts/plan_check.py:958 `clarify_foreign` resolves the repo root from the process cwd (`git rev-parse --show-toplevel` with no `-C`), not from the clarified file's folder. It also ignores the main checkout of a linked worktree, which steps.py `repo_roots` does count. So running clarify from another directory, or on an absolute path into the main checkout from a lane, can classify a path differently. | note: plugins/sdlc-lite/scripts/steps.py:7061 the in-repo control predicts the next fixture dir name with `tmp / f"o-repo{count[0] + 1}"`. This works today but is coupled to `o_repo`'s counter. | note: .sdlc/0613-lint-foreign-verifier-result/skips.md:5 the working tree has a duplicated `lane: solo` line that is not in the review sha.) · verifier: verifier-L2 (opus) · base: beb81bd34449
- Changed: see commits
- Commits: a6a08d9 T-0613: steps.py lint flags another repo's verifier file as the step's own result
- Check: 1 `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0 and includes a new case: a criterio...: pass
- Check: 2 The existing T-0415 own-result cases still report the finding (same selftest): pass
- Check: 3 (red) The new case fails on the base commit: pass
- Check: 4 `python3 plugins/sdlc-lite/scripts/plan_check.py selftest` exits 0: pass
