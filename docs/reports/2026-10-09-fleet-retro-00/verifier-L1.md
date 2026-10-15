<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
fail

## Criteria
- Sample row 1 holds (unmetered runs): pass. Evidence: `fleet_detect.evidence_value(fp,'runs.unmetered')` printed ui-kit-maison 122, agent-ui 14, gen-ui-kit 1, ultimate-tokens 15, sdlc-lite 11; all five match the expected values.
- Sample row 7 holds (unfilled template reached a verifier): pass. Evidence: grep -niE 'template|placeholder' matched both `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0329-example-preview-hygiene/verifier-L2.md:6` and `0331-form-adapter-test-hardening/verifier-L2.md:6`. The row cites 3 tickets but names only 2.
- Rubric row 1, Sub-agent runs carry no cost row: pass. Evidence: G1 to G5 pass (fingerprint paths; no dispatch.py commit addresses it, and `git log` shows no `unpriced` line in dispatch.py; collector counts; dispatch.py and helper scripts; K-001 `docs/kpi/001-runs-without-cost-row.md` has a runnable `measure:`). C1 0 (spend unmeasured), C2 2, C3 2, C4 1, C5 2 = 7.
- Rubric row 2, Full lane 77 percent of spend: fail. Evidence: G5 fails. Prevention reads "not designed yet, needs /review-traces", so no check that fails today and passes once fixed can be stated. G1 to G4 pass (full 359.2117 / 392.6278 = 91 percent of repo spend, not 77; the stated 77 percent is not what the collector gives, and the cost cell is $359.21 of $392.63). Note the 77 percent title does not match the collector values.
- Rubric row 3, steps.py widen refuses a deny-path guard: fail. Evidence: G1 to G5 pass (steps.py:2925 still carries the refusal on 0.22.1, and T-0365 8aa62b25 shipped in v0.22.0 before the evidence). Score 5: C1 0 (minutes unmeasured), C2 0, C3 2, C4 2, C5 1. Below 7.
- Rubric row 4, redck placeholder misread: fail. Evidence: G1 to G5 pass (PLACEHOLDER_RE at steps.py:390 unchanged since 2026-10-07; [U] with sourced builder notes). Score 6: C1 0, C2 1 (four steps, one repo), C3 2, C4 2, C5 1. Below 7.
- Rubric row 5, T-0040 step 2 plan defects: fail. Evidence: G3 fails. "about 1 hour" has no source, and the only pointer is a builder Notes section. Score 0.
- Rubric row 6, Template rows 7 to 12 fail every lane: fail. Evidence: G3 fails. "2 to 3 hours across 11 lanes (maison's estimate)" is an estimate with no collector, command or log source. Score 0.
- Rubric row 7, Unfilled template reached a verifier: fail. Evidence: G2 fails. T-0399 09f53a09 (dispatch.py prepare refuses an unfilled handoff template) was committed 2026-10-08 22:07, after the 0329 verifier-L2.md written 2026-10-08 21:28; the row itself says it was fixed on main. Score 0.
- Rubric row 8, Mailbox lease expiry: fail. Evidence: G2 fails. T-0396 6c34ad8c and T-0397 e9e331ae (commits 2026-10-08) address the symptom, and the row says it was fixed. Score 0.
- Rubric row 9, Interrupted runs 12: fail. Evidence: G1 to G5 pass (runs.interrupted.count = 12 reproduced; dispatch.py prepare/record are the mechanism). Score 6: C1 0 (a count of runs, no cost or minutes), C2 1, C3 1, C4 2, C5 2. Below 7. Also dispatch.py:90 already writes a `.limit` file for a failed record with 429 or session-limit text, so "no limit-aware path" is only partly true.
- Rubric row 10, Verifier base sha was the build commit: fail. Evidence: G2 fails. T-0381 shipped in 0.22.1 and the evidence is from 0.22.0; the row says so. Score 0.
- Rubric row 11, size_m_criteria T-0332: fail. Evidence: G4 fails. The cause is "a mega-wave ticket was kept as one ticket", a project cause; the prevention is "none". Value reproduced: tickets.items[170] criteria = 26. Score 0.
- Rubric row 12, Lane helper pinned a version path: fail. Evidence: G2 fails. T-0401 939b66c7 (merged on main after 0.22.1) is the fix and the row says so. Score 0.
- The planted claim holds: fail, as the control intends. Evidence: `evidence_value(agent-ui.json,'processes.chromium.count')` = 49, not 999, so the command exited 1. The check discriminates; the planted claim is wrong.

## Out of scope changes
None. Only a read-only check; no project files changed (git status shows only the untracked retro files).

## For the next attempt
Rows 2 to 12 belong under `## Not actionable` with the failed gate or score above (2 G5, 3 score 5, 4 score 6, 5 G3, 6 G3, 7 G2, 8 G2, 9 score 6, 10 G2, 11 G4, 12 G2); only row 1 stays actionable (7 of 10). Fix row 2's title: it says 77 percent, but the collector gives 359.2117 of 392.6278 (91 percent). Row 7 cites 2 of its 3 tickets. The planted claim (999 chromium processes) is wrong against the collector's 49 and must not enter the report.
