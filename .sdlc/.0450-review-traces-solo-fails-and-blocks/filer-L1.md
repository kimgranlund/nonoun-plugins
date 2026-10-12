<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None. The step 1 verifier (verifier-L2) passed all 12 criteria, and no `process-deviations.md` exists in the artifacts dir or `step-1`. The handoff's `## Plan review` section records earlier planning refusals (a count-over-a-changing-set criterion, then `steps.py lint` rejecting `sample.py` and `.sdlc/tickets/` paths). The step 1 build ran after those, so they are history, not a failed or unverified step.

## PR title
T-0450: Run review-traces on solo first-round fails and builder blocked notes; rank agent file changes

## PR body
Summary
- T-0450 is a spike. It adds one dated report, `docs/reports/2026-10-11-solo-fails-and-blocks.md`, and changes no agent file, script or ticket.
- The report sorts the 34 first-round verifier non-passes on solo tickets (2026-10-08 to 2026-10-11, ui-kit-maison, agent-ui, ultimate-tokens, sdlc-lite) by root cause. Of the 34, 22 are builder gaps, 9 criterion defects, 2 environment, 1 other and 0 verifier over-reach.
- It reads 20 of the 39 builder blocked notes in the window. Most are the designed outcome, and the plan defects they name are already covered.
- It ranks 5 changes. Three are marked "propose a ticket", all in `plugins/sdlc-lite/agents/solo.md`:
  - Search contract dependents and sibling sites before the change (7 tickets).
  - Run every acceptance criterion verbatim before `verify: needed` (6 tickets).
  - Mark lane-unsatisfiable criteria with an owner (4 tickets).
- The report also lists what is already covered (T-0412, T-0413, T-0438, T-0439, T-0441, T-0448) and what is unverified.

Changes
- New: `docs/reports/2026-10-11-solo-fails-and-blocks.md`.
- New under `.sdlc/0450-review-traces-solo-fails-and-blocks/`:
  - `sample.py`, the rerunnable sampler.
  - `sample.txt`, its output.
  - `scratch/`, the stdout of each traces run and fleet_collect run.
  - `step-1/` run records.

How verified
- The verifier ran all 12 criteria and all passed:
  - one report exists, with the five required headings;
  - 27 verifier and 11 builder pointers, all resolving;
  - 3 "propose a ticket" lines;
  - the six prior tickets, K-005, "89 of 123", the category words and an agents path are present;
  - no trailing whitespace;
  - `docs_check.py` is green;
  - no changes outside `.sdlc` except the report.
- The red control for criterion 1 was recorded in `step-1/red-checkpoint.jsonl` before the first edit.
- The verifier opened 9 evidence pointers and found each matches the cause the report gives it.
- The verifier reran `sample.py` and got 166 solo tickets, 123 verified, 34 non-passes, and 39 blocked notes with 20 read.
- The verifier also checked the planner-rule claims about `planner.md` and `solo.md` against those files.
- Unverified, as the report states:
  - Stages 2 to 4 of review-traces ran inside the builder, not as separate dispatches.
  - Classifications are one reader's judgment from the fail lines.
  - The K-005 movements are upper bounds, not observed effects.
  - Minutes and dollars are floors, because only sdlc-lite is priced.

## Changelog entry
- Added `docs/reports/2026-10-11-solo-fails-and-blocks.md`: the 34 solo first-round verifier non-passes and the builder blocked notes since 2026-10-08, classified and ranked into 5 agent file changes, 3 of them proposed as tickets, with a rerunnable sampler.

## Follow-ups
- decide: Whether to file a ticket for the top-ranked change, `solo.md` search contract dependents and sibling sites before the change (7 tickets, K-005 up to 96 of 123 [U]). The other two "propose a ticket" changes (verbatim criterion run before `verify: needed`, and an owner for lane-unsatisfiable criteria) are in the same report. Only one becomes a ticket per task.
- note: The handoff said K-005 had no file and counted 173 blocked notes (55 plan defect). `docs/kpi/005-solo-first-pass-rate.md` exists now, and the on-disk count is 174 (56), so the report cites both counts.
- note: The three planning refusals in the handoff's `## Plan review` came from `steps.py lint` and `dispatch.py prepare`. Lint rejects a `.sdlc/` path a step is told to create, and it rejects a foreign-repo `.sdlc/tickets/` path. Both are logged there with the unblock.
- note: Ranked change 3 would not move K-005, because a held criterion still gives verdict `fail`. The report says to measure `plan defect:` against `deferred:` in `## For the next attempt` instead.
