<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
- process deviation: red-checkpoint: retrospective: attempt b33ab99a006f4456a7ca879d572314fb, handoff sha256 c1ca5ba3346a, 6 of 6 (red) criteria without a pre-edit red control. This is step 2 (the report and eval). The six criteria were the verdict-line grep, the table header, A/B row parity, Spend versus the table sum, the not-run names plus `## Raw rows`, and the eval file grep. The builder says `redck.py record` stored them as retrospective because step 1's bench task edits were already in the tree. Step 2's verifier passed, but a passing verdict does not clear this deviation. The verifier did run its own negative controls on criteria 3 and 4.
- Both steps passed (step 1 verifier-L1: pass, step 2 verifier-L2: pass). These parts of the result are unverified:
  - The report's `hidden_check` column (subagent-tool-names 4 of 4 pass, figma-stale-skip-report 4 of 4 fail) and the builder and verifier minutes are claims. The verifier could not re-observe grading, because `dispatch.py record` had already removed the arm and cell clones under `.worktrees/tmp/0442-s2-builder-L3/`.
  - The report's Method says "The clones are kept there". That is now false, for the same reason.
  - `command-modal-footer` L1 rep 2 and all six L5 pairs were skipped at the budget stop (7.94 spent of the 10 the runs allowed; the ticket's `budget_usd` is 15). The L5 overlay is therefore `unverified`.
  - `button-geometry-model` and `svelte-icon-component` were not run. Their repos are not on this machine and their base shas are not on GitHub.
  - The step-1 builder did not run the python file-scope guard. The verifier ran it and it passed.

## PR title
T-0442: Replay A/B of builder overlays on the five bench tasks

## PR body
Summary
- Runs the architect's replay A/B for the builder L1 and L5 `## At this level` overlays, with and without, on the bench tasks that run on this machine. The result is priced rows, a dated report and an eval record.
- Verdict: drop. The L1 overlay is a drop and the L5 overlay is unverified. "Null at this sample size" is `no` under the handoff's literal rule. The report says this does not mean an effect was found.
- The L1 drop comes only from the blocked-rate rule. No builder blocked in either arm (0 of 5 each), so arm B can never be "below" arm A.
- Everything else matched or moved within noise:
  - First pass was identical per task.
  - Builder cost was +3.3 percent (arm A 1.856, arm B 1.917), under the 10 percent threshold.
  - There was no hidden-check regression.
  - Minutes moved both ways.
- Spend is 7.94 USD, and the table sums to 7.92. Arm B passed 3 of 5.

Changes
- `plugins/sdlc-lite/bench/tasks/subagent-tool-names.md`, `figma-stale-skip-report.md` and `command-modal-footer.md`: the `repo:` line now points at `/Users/kimgranlund/Projects/nonoun/<name>` (`agent-ui`, `ultimate-tokens`, `agent-ui`). Nothing else in those files changed.
- `docs/reports/2026-10-11-builder-overlay-ab.md`: the new report. It holds the verdict lines, the per-run table, rule outcomes, Method, the not-run section, Limits and 20 raw rows.
- `.sdlc/evals/0005-builder-overlays.md`: the new eval, written by `evals.py add`.
- `.sdlc/0442-builder-overlay-ab/`: the plan, step handoffs, builder and verifier records and run records.
- No overlay, agent, adapter or script changed.

How each was verified
- Step 1:
  - The `cat-file` check for `base`, `solution` and `tests_from` passes in all three tasks.
  - Each `repo:` line matches the expected path.
  - The two unchanged tasks and `README.md` are untouched.
  - Only `repo:` lines differ, only the three task files changed outside `.sdlc`, and `git diff --check` passes.
  - The verifier ran negative controls in a shared clone for each guard, and each control failed as intended.
- Step 2:
  - The verdict lines, the exact table header, A=5 and B=5 rows, Spend versus the table (7.94 against 7.92) and the not-run names plus `## Raw rows` all pass.
  - The eval file matches the table (pass_rate 3/5, cost 7.94).
  - The scope guard, `evals.py check`, `check.py` and `check-packaging.py` pass, and `git diff --check` passes.
  - The verifier recomputed the 20 raw rows (sum 7.9374) and the budget skips, and confirmed the arms differ only by the `## At this level` section.
  - Negative controls bit on criteria 3 and 4.
- 20 builder and verifier runs went through `dispatch.py prepare`, headless `claude -p` and `dispatch.py record --transcript`. All 20 produced priced rows.
- Arms and cells were `git clone --shared` copies, not worktrees, because the stray-worktree hook blocked `git worktree add`. The Method records this.
- Not verified: see Warnings.

## Changelog entry
- Added a replay A/B of the builder L1 and L5 overlays (`docs/reports/2026-10-11-builder-overlay-ab.md`, eval `0005-builder-overlays`). Verdict: drop; the L5 overlay is unverified because of the budget stop. The three runnable bench tasks now point at this machine's repos.

## Follow-ups
- fix-now: Correct the stale line in the Method of `docs/reports/2026-10-11-builder-overlay-ab.md` ("The clones are kept there"). `dispatch.py record` removed the arm and cell clones.
- decide: The "Null at this sample size" rule returns `no` whenever the four L1 rule outcomes agree across reps and L5 has no reps. This is a different meaning from "no visible effect at this cost", which is what the data shows. Choose whether to repair the rule before the verdict is relied on.
- decide: The L5 overlay is unverified (six pairs skipped at the 10 USD run stop of the 15 USD ticket budget, estimated at about 8 USD). Choose whether to fund an L5-only run or leave it as drop-by-default.
- note: `figma-stale-skip-report` failed the hidden `staleskipnotice` gate in all four runs in both arms, and the 2026-09-27 archived run also failed it. The task is probably uninformative for this comparison.
- note: `button-geometry-model.md` and `svelte-icon-component.md` still carry `/Users/kimba/...` repo paths. Their repos are not on this machine, so those two tasks cannot run here.
