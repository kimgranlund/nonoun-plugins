<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
fail

## Criteria
- Sample, row 1: pass. Ran the command: `plan_review_share` = 0.5546 and the planner plus plan-reviewer cost = 436.4375, exit 0. The cost sum matches the report's $436.44.
- Sample, row 6: pass. `grep -nF` matched `docs/reports/hook-perf.md:18`, `| block-disk-scan.sh | before | 0.35 | 1.60 | 8.93 | over 25 | over 25 |`, exit 0.
- Control, planted claim "250 deduped runs": pass, because the check rejects the false claim. `evidence_value(fp,'runs.total')` printed 193 and the command exited 1. The check can go red and is not vacuous. The command exits nonzero by design, so I read "pass" as "claim rejected".
- Rubric, row 1: fail. The row fails G2 (Current), so its score is 0.
  - G1 passes: `agent-ui.json :: plan_review_share`, plus the agent-ui report at section 4, which I opened.
  - G2 fails. `agent-ui.json` has `window.since` = None and `until` = 2026-10-06T14:06:53Z, so it covers runs from before the fix. T-0294 `48e25a3a` (2026-10-06 07:19, "Plan review only for L4 and L5 steps", tag v0.20.11) is exactly the row's prevention.
  - `rubric.md` Calibration line 38 scores this same finding G2 fail until it is re-collected with `--since`. T-0315 owns that re-collection.
  - G3 to G5 and C1 to C5 were not scored, because the rubric stops at the first failed gate.
- Rubric, row 2: fail. The row fails G2, so its score is 0.
  - G1 passes: `ui-kit-maison.json :: runs.by_ticket[...]`. I confirmed the counts: 0105 has 20, first-wave-components 11, 0012 has 8, 0106 has 7, .0037 has 6.
  - G2 fails. The prevention, `steps.py lint` naming the exact heading, shipped as T-0295 `9456b377` (2026-10-06 07:21, `steps.py`, tag v0.20.11). The evidence is from 2026-10-04, and the maison fingerprint has `window.since` = None.
  - Even past G2 the row would score low: its cost is unmeasured (the 2 hours is the maison report's own figure) and four of the five tickets are undiagnosed.
- Rubric, row 3: fail. The row fails G4 (Plugin cause), so its score is 0.
  - G1 passes: `ui-kit-maison.json :: runs.interrupted.count`. I confirmed 16 interrupted and `limit_markers.count` 0.
  - G4 fails. The maison report lines 24 and 25 give the causes as "a role dies with its parent shell" (session exit) and a session or usage limit. Both are host or session causes, and no sdlc-lite file is named.
  - G3 is also weak: the cost is unmeasured and the other interrupted attempts are undiagnosed.
- Rubric, row 4: fail. The row fails G4, so its score is 0.
  - G1 passes: `agent-ui.json :: processes.chromium.count` = 59 and `rss_mb` = 14258.8. `ui-kit-maison.json :: processes.chromium.count` = 57.
  - G4 fails. The mechanism is "Browser shards of several lanes' Playwright runs, which are the projects' tests". This is the same ruling as the Chromium row in `rubric.md` Calibration line 39 (G4 fails; T-0292 owns the plugin half). The cost is also unmeasured.
- Rubric, row 5: fail. The row fails G2, so its score is 0.
  - G1 passes: `agent-ui.json :: runs.by_ticket["no-barrels"].planner`. The collector gives 6 against the report's claim of 12, and the row discloses that mismatch.
  - G2 fails. T-0297 `3a75c8b3` (2026-10-06 07:25, "Planner guard dry-run; split inherits earlier widenings", tag v0.20.11) addresses the row's causes (guards diff against the base commit, `split --only` on a red guard) and its prevention. The window `since` is None.
  - The row's own measured count (6) contradicts the 12 that its mechanism text rests on. The cost is unmeasured, and the specgate and ADR-ordering causes are not plugin rules.
- Rubric, row 6: fail. The row fails G2, so its score is 0.
  - G1 passes: the `hook-perf.md` timings table (sample criterion 2 confirmed its row). `processes.hooks.count` is 0.
  - G2 fails. T-0291 `42721341` (2026-10-06 07:04, hooks linear on long commands, tag v0.20.11) already fixed the symptom. The row's own Mechanism column says "T-0291 replaced them", and the evidence predates the fix.
  - The calibration's "pass at 24ef333" was scored before T-0291. After T-0291 the row is an outcome check that reads `moved`, not a new finding.

## Out of scope changes
None. `git status` shows only the step's untracked `.sdlc/fleet-retro-2026-10-06/` folder, the report, and the fleet-retro skill files. Its modified files belong to T-0308 work. I edited nothing.

## For the next attempt
The 6 findings are not actionable and all go under `## Not actionable`. None should be filed.
- Rows 1, 2, 5 and 6 each fail G2. Their evidence predates T-0294, T-0295, T-0297 and T-0291, all in v0.20.11. Re-collect with `--since 2026-10-06T14:20Z` (after T-0297) so the window starts after those fixes, then re-score. The T-0315 re-measure already exists for row 1.
- Rows 3 and 4 fail G4. The causes are the host or session (parent-shell kill, usage limit) and the projects' Playwright shards. The plugin half of row 4 is already T-0292.
- Row 1 is fully fixed and rows 2, 5 and 6 are partly fixed. After a re-collect, any surviving symptom comes back as a new row with its own cost number, a named sdlc-lite file or rule, and a command that fails today.
- Fill `## Verification` and `## Not actionable` in `docs/reports/fleet-retro-2026-10-06.md` with these results.
- The sample and control checks hold, so the collector values are correct. The defect is in which rows were put forward, not in the numbers.
