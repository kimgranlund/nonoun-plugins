<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
fail

## Criteria
- Sample row 1 (full lane cost): pass. Evidence: both handoff commands exit 0; `evidence_value` gives ultimate-tokens `runs.by_lane.full.cost_usd` 153.9916 and agent-ui 61.5497. 153.9916 / 159.3075 = 96.7 percent, matching the row.
- Sample row 6 (batched verifier covered one step): fail. Evidence: the grep exits 0 (2 hits), but the check is vacuous. `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0346-gap-buildout-wave-plan/step-3/verifier-L3.md` line 1 reads "Batched verification of T-0346 Wave 1 steps 1 to 4" and has result sections for Steps 1, 2, 3 and 4. The file does not cover "step 3 only" or "one of four lanes", so the report's symptom is contradicted by its own evidence. `grep step 3` could not have gone red for this claim.
- Sample row 12 (gen-ui-kit unmetered): pass. Evidence: `evidence_value(gen-ui-kit.json, 'runs.unmetered')` = 56, exit 0.
- Rubric row 1, Full lane share of spend: fail at G5. G1 to G4 pass (fingerprint paths, collector numbers, `steps.py lane`). Prevention reads "no check can be named before it reports", so no check is stated that fails today and passes once fixed. Score 0.
- Rubric row 2, Host restarts orphan sub-agents: pass. G1 to G5 pass: the fingerprint path resolves (5 interrupted attempts, `stall_attempts`), no commit since the evidence addresses `prepare` or recovery (`git log --since=2026-10-09 -- dispatch.py` shows T-0402, T-0412, T-0415 only), `dispatch.py prepare` is the mechanism, and K-002 (`docs/kpi/002-restart-recovery-minutes.md`) exists. Score about 8 of 10: C1 1 (hours are maison's estimate), C2 2, C3 1, C4 2, C5 2. Caveat: the 5 interrupted attempts in the fingerprint are verifiers on closed dotted tickets, while the `prepare` refusal itself rests on the agent-ui interview.
- Rubric row 3, Stale primary checkout as Tree and Base sha: fail on score. G1 to G5 pass (`step-2/builder-L3.md` and `step-4/builder-L3.md` both mention a stale lane; the selftest in T-0413 is named). Score about 5 of 10: C1 0 (3 blocked builders, about 10 minutes, an estimate), C2 1 (only maison evidence is cited), C3 1, C4 2, C5 1 (a selftest, no rule or KPI). Below 7.
- Rubric row 4, Scope list missed a guarded test: fail at G5. The prevention is the spike T-0416 and states no check that fails today. The pointers resolve in ultimate-tokens, but the agent-ui pointer is `.sdlc/.../step-4/builder-L4.md`, an ellipsis path. The file is actually at `agent-ui/.claude/worktrees/wave-rts/.sdlc/response-type-selection/step-4/builder-L4.md`. Score 0.
- Rubric row 5, widen edits the handoff after redck: fail at G1. The evidence path `.sdlc/.../step-4/process-deviations.md` has an ellipsis and sits in a worktree, not in agent-ui's `.sdlc`. The file that exists holds only a `red-checkpoint: missing` line. The text "stale input ... handoff changed while builder ran" is in none of the step-4 files (grep returns nothing). A reader cannot open the evidence without asking. Score 0.
- Rubric row 6, Batched verifier checked one of four lanes: fail at G3. The symptom is contradicted (see sample row 6): the verifier did cover steps 1 to 4. The cost is an estimate ("about 10 minutes"). Score 0.
- Rubric row 7, record before the result file: fail at G2. `git log` shows c5152d76 "T-0412: record leaves the attempt running when no result exists yet" (2026-10-09). The row itself says "fixed by T-0412". Score 0.
- Rubric row 8, Prune cron stopped waiting agents: fail at G3. The cost "about 40 minutes (its estimate)" is a guess, and the row admits it does not show that `dispatch.py prune` stopped any agent. Score 0.
- Rubric row 9, Whole-ticket verifiers 43 to 56 minutes: fail at G5. The prevention is the spike T-0417, a measurement, not a check that fails today. Score 0.
- Rubric row 10, size_m_criteria 32 criteria: fail at G5. Prevention is "none; a size rule is a design question". The count is real: `ui-kit-maison.json` `tickets.items[151]` is T-0332 with `criteria` 32, but the cost is "unmeasured". Score 0.
- Rubric row 11, ADR number collision: fail at G4. The row says the numbering is the project's ADR convention and that nothing in this plugin owns it. Score 0.
- Rubric row 12, gen-ui-kit unpriced runs: fail at G2. T-0402 (6a99c887, 2026-10-09) already addresses the symptom, and the row says 0.22.2 prints `unpriced:`. The remaining fix is the repo adopting it, not a plugin defect. Score 0.
- The planted claim holds: fail, as the control intends. `evidence_value(agent-ui.json, 'runs.unmetered')` is 0, not 999, and the command exits 1. The check can go red.

## Out of scope changes
None. `git status` shows only the untracked verify dir and `docs/reports/2026-10-09-fleet-retro-12.md`. No project file was edited.

## For the next attempt
Fix the report, not the plugin. Findings 6, 7 and 12 should move to `## Not actionable`: row 6's symptom is false, row 7 failed G2, and row 12 failed G2. Findings 1, 4, 9 and 10 fail G5 and need a stated check before they can be filed. Finding 8 fails G3, 11 fails G4, 5 fails G1 and 3 scores about 5.

Only finding 2 passes. Fill `## Not actionable` with the gate or score for each row above. Replace the ellipsis pointers in rows 4 and 5 with real paths. Re-read the step-3 verifier file before restating finding 6. The sample-row-6 criterion (`grep -qiE 'step 3'`) cannot go red for "covered one step". Its replacement should assert the count of steps the file covers.
