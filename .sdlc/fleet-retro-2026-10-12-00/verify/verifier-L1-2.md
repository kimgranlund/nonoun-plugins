<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
fail

## Criteria
- #1 Sample row 1 quoted text in interview: pass. Evidence: grep -qF 'verdicts fail on criteria that name no owner' on the maison interview, rc=0. The finding's own commands (`deferred: owner` in 0468-attachment/verifier-L2-2.md, `deferred: integration` in 0474-task-row/verifier-L2-2.md) each match 1 line.
- #2 Sample row 6 quoted text in interview: pass. Evidence: grep -qF 'Fanout cannot run here: handoffs are uncommitted and .sdlc is gitignored' on the maison interview, rc=0.
- #3 Sample row 12 refusal reproduces: pass. Evidence: `steps.py lint .sdlc/fleet-retro-2026-10-12-00/verify/handoff.refused.md` prints "acceptance criterion reads this step's own verifier result ..." and exits 1 (rc=1 confirmed).
- #4 Rubric row 1, Deferred owner fail: fail. Evidence: G1 pass, G2 pass (T-0408 added the deferred verdict earlier; nothing since fixes the symptom), G3 fails: cost is "maison's estimate" of 25 to 40 minutes per extra verify, and "2 of 5" is maison's own count. Score 0, first failed gate G3.
- #5 Rubric row 2, Unmetered maison: fail. Evidence: G1 pass (ui-kit-maison.json runs.unmetered = 166, of runs.total = 203, reproduced with fleet_detect.evidence_value). G2 fails: the row says T-0446 (aad0c3b2, dispatch.py record finds the transcript) prices new runs and only older runs show it. Score 0, first failed gate G2.
- #6 Rubric row 3, Planner results per ticket: fail. Evidence: G1 pass, G2 pass, G3 pass (runs.by_ticket["tickets/0463-wave7b-source-recut"].planner = 6 reproduced). G4 fails: the mechanism is "maison's reading, unchecked", a project cause with no named plugin file or rule. Score 0, first failed gate G4.
- #7 Rubric row 4, Gate lock queue: fail. Evidence: G1 pass (quoted text present, count 1), G2 pass (T-0456 is still proposed, gate_lock.py unchanged for this symptom). G3 fails: "about 1 hour on one wave 7b gate (maison's estimate)". Score 0, first failed gate G3.
- #8 Rubric row 5, record no result: fail. Evidence: G1 pass (quoted text present). G2 fails: the row states T-0412 and T-0446 fixed it and the recoveries pre-date maison's reload (git log shows aad0c3b2 T-0446 on dispatch.py). Score 0, first failed gate G2.
- #9 Rubric row 6, Fanout cannot run: fail. Evidence: G1 pass, G2 pass (fanout.py commits since 2026-10-05 do not address uncommitted handoffs). G3 fails: cost "maison hand-runs lanes ..., unmeasured". Score 0, first failed gate G3.
- #10 Rubric row 7, size_m_criteria: fail. Evidence: G1 pass, G2 pass, G3 pass (tickets.items[152].criteria = 32 reproduced). G4 fails: cause is "a large wave ticket kept as one ticket", a project cause; prevention itself says "none; a size rule is a design question" (also fails G5). Score 0, first failed gate G4.
- #11 Rubric row 8, Lane gate checks: fail. Evidence: G1 pass (quoted text present), G2 pass. G3 fails: "one fix cycle, about 40 minutes (maison's estimate)". G4 would also fail (the project's lane-gate.sh). Score 0, first failed gate G3.
- #12 Rubric row 9, Wave 7b plan cycles: fail. Evidence: G1 pass (quoted text present), G2 pass, G3 passes on the sourced $75.63 over 78 runs from maison's collector. G4 fails: mechanism is "source lanes were not self-consistent ... (maison's reading)", a project cause; row is [U]. Score 0, first failed gate G4.
- #13 Rubric row 10, Chromium load: fail. Evidence: G1 pass (processes.chromium.count = 48 reproduced), G2 pass, G3 pass (count from collector). G4 fails: "the project's Playwright shards; the plugin only schedules them", the same verdict as the Chromium calibration row in rubric.md. Score 0, first failed gate G4.
- #14 Rubric row 11, Solo plus lane gate: fail. Evidence: G1 pass (quoted text present), G2 pass. G3 fails: "solo about $0.51 and 5 minutes a run (maison's estimate)". The row is also a keep with no defect, so G5 would fail too. Score 0, first failed gate G3.
- #15 Rubric row 12, steps lint foreign verifier path: fail. Evidence: G1 pass (command reproduces, rc=1), G2 pass (T-0457 f57fcc0b is the only steps.py commit in the window and it adds the refusal rather than fixing it). G3 fails: cost is "one handoff rewrite, minutes", unmeasured. Score 0, first failed gate G3.
- #16 Planted claim (runs.total = 999 in sdlc-lite.json): fail. Evidence: the python3 -I command prints 99 and exits rc=1. The claim is wrong by design, so the control bites: the check discriminates and rejects the planted value.

## Out of scope changes
None. Read-only run; no worktree created, no project file touched.

## For the next attempt
No build defect. The report's three samples reproduce (#1 to #3) and the planted claim is caught (#16, the intended red control). Criteria #4 to #15 are the actionability grading and all twelve rows fail a gate, as above (G2: rows 2 and 5; G3: rows 1, 4, 6, 8, 11, 12; G4: rows 3, 7, 9, 10). Move all twelve into `## Not actionable` with those gates, file nothing, and do not treat #16 as a report defect. If the handoff meant criteria #4 to #15 to be graded rather than required to pass, read the table above as the grade.
