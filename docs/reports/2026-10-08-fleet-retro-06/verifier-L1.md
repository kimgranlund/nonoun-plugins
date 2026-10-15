<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
fail

## Criteria
- Sample row 1 (ultimate-tokens planner runs and spend): pass. Evidence: evidence_value on runs.by_ticket["geometry-maison-ladder"].planner = 6; runs.by_role.planner.cost_usd = 67.841 (within 0.01 of 67.84).
- Sample row 7 (gen-ui-kit unmetered): pass. Evidence: runs.unmetered = 33.
- Sample row 12 (maison idle agents): pass. Evidence: grep -cF of the quoted heading in ui-kit-maison/.sdlc/fleet-retro-2026-10-08.md returns 1.
- Rubric row 1 (planner 6 plan runs): pass, 7 of 10. Gates G1 to G5 pass (planner_results_per_ticket rule, steps.py and agents/planner.md named, no commit since the window addresses plan-review notes). C1 2 (67.84 of 236.71 is 29 percent), C2 0, C3 1, C4 2, C5 2.
- Rubric row 2 (verifier spend top line): fail at G2. Evidence: the row itself says the routing was changed by T-0356; `git log` shows cf3f5b84 "Merge vroute-vroute: T-0356 verifier routing by level" on 2026-10-07 17:56, after the evidence. The Repo column also says ultimate-tokens while the evidence is sdlc-lite.json (44.822) and ui-kit-maison.json (6.1518).
- Rubric row 3 (plan defects found at verify): fail on score, 4 of 10. Gates pass. C1 1, C2 1, C3 1, C4 1, C5 0 (no named detect rule or command).
- Rubric row 4 (steps.py widen): fail on score, 6 of 10. Gates pass. C1 0 (20 minutes, no share measured), C2 2 (two repos), C3 1, C4 2, C5 1.
- Rubric row 5 (prepare Base sha): fail on score, 4 of 10. Gates pass (dispatch.py:504 builds the Base sha line; no commit addresses it). C1 0, C2 1, C3 1, C4 2, C5 0.
- Rubric row 6 (fanout.py prep): fail at G3. Cost "hours of one-off scripts across about 30 lanes" is an "about" with no source.
- Rubric row 7 (solo lanes no cost row): fail at G2. The row itself cites T-0355 shipped in 0.21.3; `git log` shows 60085401 on 2026-10-07 15:38 "dispatch.py record refuses a solo_run.py dispatch file ... no cost rows".
- Rubric row 8 (replan cap): fail on score, 3 of 10. Gates pass. C1 0, C2 0, C3 1, C4 2, C5 0.
- Rubric row 9 (prepare blocks on caller pid attempt): fail at G2. `git log` shows 764c5436 (2026-10-07 05:56, in v0.21.1) "dispatch.py prepare recovers or names a stale attempt ... instead of blocking the next prepare".
- Rubric row 10 (final messages not in result file): fail at G3. Cost "about 1 minute per role, 30+ roles" is an estimate. (Also the fix, --transcript, shipped in T-0343 in v0.21.2.)
- Rubric row 11 (stray worktree warnings): fail on score, 3 of 10. Gates pass (dispatch.py strays at :578, no addressing commit). C1 0, C2 0, C3 2, C4 1, C5 0.
- Rubric row 12 (idle sub-agents): fail on score, 3 of 10. Gates pass. C1 0, C2 0, C3 1, C4 2, C5 0.
- Rubric row 13 (plugin version mid-session): fail at G2. solo_run.py:84 and :100 now refuse with "want L1, L2, or L3" and accept deprecated aliases (T-0342, 59a3697c), which is the row's own prevention.
- Rubric row 14 (mechanical solo misses): fail on score, 3 of 10. Gates pass (agents/solo.md has no em-dash or negative-control text). C1 0, C2 0, C3 1, C4 2, C5 0.
- Rubric row 15 (gate failures after push): fail at G4. The mechanism is "project CI" and the prevention is "none in sdlc-lite".
- Rubric row 16 (Chromium over 30 processes): fail at G4. The mechanism is "Project Playwright shards, not a plugin file" and the prevention is "none: project cause". Observed processes.chromium.count = 41 for agent-ui, ui-kit-maison and sdlc-lite; "over 6 GB" and "all five" are not backed by the cited paths.
- Planted claim holds (agent-ui processes.chromium.count == 999): fail, as planted. Evidence: evidence_value returns 41, not 999, so the command exits 1. The control bites: the wrong claim is caught.

## Out of scope changes
None. `git status` shows only the untracked verify directory.

## For the next attempt
Only row 1 clears the rubric. Move rows 2, 6, 7, 9, 10, 13, 15 and 16 to `## Not actionable` with the gate named above (2: G2, 6: G3, 7: G2, 9: G2, 10: G3, 13: G2, 15: G4, 16: G4). Rows 3, 4, 5, 8, 11, 12 and 14 pass the gates but score under 7, so they also go to `## Not actionable` with their scores (4, 6, 4, 3, 3, 3, 3). Row 2's Repo column should name sdlc-lite and ui-kit-maison, not ultimate-tokens. Row 16's "over 6 GB" and "all five" need a cited source if the row is kept. Do not file anything except row 1.
