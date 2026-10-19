---
id: T-0442
title: "Replay A/B of builder overlays on the five bench tasks"
type: spike           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0441]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-11
router: .sdlc/AGENTS.md  # how to claim and close this ticket
budget_usd: 15
---

## Question
Do the builder L1 and L5 overlays improve cost, first-pass rate, blocked rate or verifier minutes on a fixed task set?

## Question
Do the builder L1 and L5 overlays improve cost, first-pass rate, blocked rate or verifier minutes on a fixed task set, or should the idea be dropped?

## Goal
A dated report with a keep, extend or drop verdict backed by priced runs.

## Intent
- Do: run the architect's replay A/B (Approach "Proof" paragraph): the five bench tasks under `plugins/sdlc-lite/bench/tasks/`, one step handoff each at the task's base in a throwaway worktree, with and without the overlay, two repetitions, `dispatch.py prepare builder <level>` and `record --transcript` so each row is priced, graded by the hidden `check:` command, one verifier per arm; record `.sdlc/evals/0005-builder-overlays.md` and `docs/reports/<date>-builder-overlay-ab.md`. Fix the bench task repo paths (`/Users/kimba/...`) for this machine first. Apply the design's drop rules.
- Non-goals: changing overlays during the run; extending to other roles.
- Done when: the report states the verdict and numbers, and whether the result is a null at this sample size.

## Context
Design: `.sdlc/.0440-per-tier-agent-prompts/architect-L1.md` (Proof, drop rules, Risks). Depends on T-0441. Cost budget: $15 total (set by the maintainer 2026-10-11, `budget_usd: 15`); stop at it and report what was run.

## Constraints
No model or effort change. Report unverified anything not run. One ticket, one lane.

## Closed

2026-10-11: warnings acknowledged: red controls for steps 2 and 3 recorded after the edit on a shared base; all three step verifiers passed; hidden_check and minutes columns are recorded claims (the arm clones were removed by record); L5 pairs and one L1 pair skipped at the budget stop, so the L5 overlay is unverified and the L1 drop rests on a rule that cannot be met with zero baseline blocks

> - process deviation: red-checkpoint: retrospective: attempt b33ab99a006f4456a7ca879d572314fb, handoff sha256 c1ca5ba3346a, 6 of 6 (red) criteria without a pre-edit red control. This is step 2 (the report and eval). The six criteria were the verdict-line grep, the table header, A/B row parity, Spend versus the table sum, the not-run names plus `## Raw rows`, and the eval file grep. The builder says `redck.py record` stored them as retrospective because step 1's bench task edits were already in the tree. Step 2's verifier passed, but a passing verdict does not clear this deviation. The verifier did run its own negative controls on criteria 3 and 4.
> - process deviation: red-checkpoint: retrospective: attempt bd2dabf0dec34569929d2a1f3369c3a1, handoff sha256 2081aabcfaac, 1 of 1 (red) criteria without a pre-edit red control. This is step 3 (the Loose ends step that fixed the stale Method sentence). The builder says redck found 4 source paths already different from the base, so the control stored as retrospective. The verifier passed the step and ran its own control: a fixture with the old sentence restored exited 1. A passing verdict does not clear this deviation.
> - All three steps passed (step 1 verifier-L1: pass, step 2 verifier-L2: pass, step 3 verifier-L1: pass). These parts of the result are unverified:
>   - The report's `hidden_check` column (subagent-tool-names 4 of 4 pass, figma-stale-skip-report 4 of 4 fail) and the builder and verifier minutes are claims. The verifier could not re-observe grading, because `dispatch.py record` had already removed the arm and cell clones under `.worktrees/tmp/0442-s2-builder-L3/`.
>   - Step 3 corrected the Method sentence. It now says the clones and evidence folder were removed with the tmp prefix, so the hidden_check and minutes columns stand as recorded claims.
>   - `command-modal-footer` L1 rep 2 and all six L5 pairs were skipped at the budget stop (7.94 spent of the 10 the runs allowed; the ticket's `budget_usd` is 15). The L5 overlay is therefore `unverified`.
>   - `button-geometry-model` and `svelte-icon-component` were not run. Their repos are not on this machine and their base shas are not on GitHub.
>   - The step-1 builder did not run the python file-scope guard. The verifier ran it and it passed.
