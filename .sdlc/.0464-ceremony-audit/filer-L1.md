<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None. The verifier passed step 1 on all 12 criteria. No `process-deviations.md` exists, and `red-checkpoint.jsonl` records the pre-edit control as red (exit 1). The report calls its filer-warning findings inferences and lists them under `## Unverified`, including the 547 minutes lost, which is an upper bound.

## PR title
T-0464: Audit ceremony versus defects caught; rank cuts toward resolve-and-ship

## PR body
## Summary
This is a read-only spike. It adds a dated report that ranks SDLC Lite ceremony sites by measured cost and by recorded catches. It proposes 3 tickets, under the cap of 5. It edits no skill, agent, script or ticket, and it changes no model or effort.

Findings:
- **Filer-warning close refusal.** 8 distinct tickets were refused for open filer warnings in fanout waves f50 to f59. 6 of them are closed in this tree, and all 6 were cleared with `--ack-warnings`. T-0458 and T-0460 are still open.
- **Retrospective red-checkpoint.** It has no recorded catch across 10 entries [U].
- **Plan-reviewer.** It caught a replan in 7 of 24 runs, so it stays.
- **Inherited red stops.** There were 2 stops and 2 real catches, so they stay.
- **Second verifier round.** There were 14 rounds with 1 catch, so it stays.

Corrections to the handoff's claims:
- "9 of 11 filers" was counted per file. Per ticket it is 6 of 7 tickets with a filer since T-0431.
- "About 6 lane stalls" is 8 distinct tickets refused for open filer warnings.

## Changes
- Adds `docs/reports/2026-10-12-ceremony-audit.md` (135 lines, `doc-type: report`).
- Adds the evidence folder `docs/reports/2026-10-12-ceremony-audit/`:
  - `count.py` produces every count the report cites.
  - `counts.txt` holds its captured output.
  - `fleet-collect.txt` is a trimmed `fleet_collect.py` summary.
- Proposed tickets, marked `[propose a ticket]` in the report:
  1. Stop a retrospective red-checkpoint on a later step of a shared tree from blocking close, when the step verifier recorded its own red control.
  2. Make `steps.py lint` stop refusing test-fixture paths in criteria.
  3. Trial solo L3 with one independent verifier for L3 tickets that have no merge step and no cross-cutting scope.

## Verification
- **Independent verifier (L2): pass.** It reran three sampled counts and got the report's numbers:
  - First case: 11 filer files in this tree, 20, 12 and 8 in the three other repos, and 8 refused tickets.
  - Per-site: plan-reviewer verdicts of 17 pass and 7 replan.
  - Prompt lint: 72 P-6 info rows, and loop, re-verify and re-run counts of 36, 9 and 55.
- **Evidence folder.** A rerun of `count.py` diffed identical to `counts.txt`.
- **Docs gate.** `docs_check.py` exits 0 with 0 errors and 26 warnings, and none name the report.
- **Negative control.** The builder appended a span naming a nonexistent ticket folder, and `docs_check.py` raised `error S-6` against the report.
- **Other criteria.** All six required headings are present, there are no em dashes, and the scope guard shows only the report and its sibling folder changed outside `.sdlc`.

## Changelog entry
- Added `docs/reports/2026-10-12-ceremony-audit.md`, a ranked audit of SDLC Lite ceremony against defects caught. It corrects the filer-warning stall count and proposes 3 changes. No behavior change.

## Follow-ups
- decide: Open the follow-up ticket for the retrospective red-checkpoint close block (change 1 in `docs/reports/2026-10-12-ceremony-audit.md`). It cost 6 manual acks, and its measure is acks per wave dropping from 6 to at most 1.
- note: Changes 2 and 3 (fixture-path lint refusals and the solo L3 trial) are proposed in the report but not ticketed, since only one follow-up ticket per task is allowed.
- note: The `skips.md` close refusal (T-0450, T-0462) is watched in the report with no ticket proposed until a second wave shows it.
- note: Minutes lost per refusal, questions that did not change the output, and cost for the other three repos are not measured. They are listed under `## Unverified` in `docs/reports/2026-10-12-ceremony-audit.md`.
