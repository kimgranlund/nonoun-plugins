<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
fail

## Criteria
- #1 Sample row 1 (lost minutes): pass. Evidence: `evidence_value(fp,'runs.interrupted.lost_min_total')` printed 1364.7, rc=0. The two attempt files (T-0431, T-0432 verifier-L3) hold status `interrupted` while `verifier-L3.md` holds `## Verdict pass`, and d7bea393 touched many `*.attempt.json`, so the row's mechanism is real.
- #2 Sample row 6 (quoted text): pass. Evidence: `grep -cF 'Dispatch base sha and solo worktrees start from the stale primary checkout' .../ui-kit-maison/.sdlc/fleet-retro-2026-10-11-12.md` printed 1, rc=0. The quoted text for rows 4, 5, 7, 8, 9, 12 also each count 1.
- #3 Sample row 11 (chromium): pass. Evidence: `evidence_value(fp,'processes.chromium.count')` printed 57, rc=0.
- #4 Rubric row 1, K-002 false interrupts: pass. Evidence: G1 fingerprint path; G2 no commit on `fleet_collect.py` or `dispatch.py recover` addresses it since the window (`git log` shows only T-0411, T-0438, T-0439, none for this); G3 collector value; G4 `dispatch.py recover`, `fleet_collect.py`; G5 K-002 / selftest. Score C1 1 (phantom minutes, no real loss), C2 1, C3 2, C4 2, C5 2 = 8 of 10.
- #5 Rubric row 2, Unmetered maison: fail. Evidence: gates pass (G1 fingerprint, G2 no pricing fix since 0.22.1, G3 collector, G4 `dispatch.py record`, G5 K-001), but the score is C1 0 (unmeasured; $69.15 is a floor), C2 2, C3 1, C4 1 (prevention is "adopt 0.22.4, pass --transcript", a consumer action; no plugin change is built, row 3 carries it), C5 2 = 6 of 10, under 7. It duplicates row 3's mechanism.
- #6 Rubric row 3, Unmetered sdlc-lite: pass. Evidence: gates G1 to G5 pass (`runs.unmetered` = 9 confirmed, `dispatch.py record` named, selftest case). Score C1 0, C2 2 (maison and this repo), C3 2, C4 2, C5 2 (K-001) = 8 of 10.
- #7 Rubric row 4, Lane source at integration: fail. Evidence: first failed gate G3. Cost "about 1.5 hours plus 3 planner runs (maison's estimate)" has no collector, command or log source. G4 would also fail (the row says "none in the plugin").
- #8 Rubric row 5, record closes attempt: fail. Evidence: first failed gate G2. T-0412 (c5152d76, 2026-10-09, released in v0.22.3) makes `record` leave the attempt running; the commit predates the row's window (2026-10-11). The row itself says it is fixed.
- #9 Rubric row 6, Stale base: fail. Evidence: first failed gate G2. T-0413 (f0af4d24, 2026-10-10, v0.22.3) added `prepare --tree`, before the window. G3 would also fail (estimate).
- #10 Rubric row 7, Lint cited paths: fail. Evidence: first failed gate G3. "about 10 minutes (maison's estimate)" has no measured source. G1 and G2 pass (no `steps.py lint` commit addresses it; only T-0430 circular-glob).
- #11 Rubric row 8, Lane defects unread: fail. Evidence: first failed gate G3 (estimate "about 45 minutes (maison's estimate)"). G4 would also fail (Codex lane owner is not a plugin cause; the row says "none in the plugin").
- #12 Rubric row 9, Monitor expiry: fail. Evidence: first failed gate G2. `messages.py watch` (T-0396/T-0397, e9e331ae, 2026-10-08) shipped in v0.22.2, before the window; the row says maison had not adopted it. G3 would also fail ("9 turns" is a re-arm count from interview).
- #13 Rubric row 10, size_m_criteria: fail. Evidence: first failed gate G4. G1 to G3 pass (`ui-kit-maison.json` `tickets.items[152]` = T-0332, criteria 32). The mechanism is a project choice ("a large wave ticket kept as one ticket") and the row's prevention is "none; a size rule is a design question".
- #14 Rubric row 11, Chromium load: fail. Evidence: first failed gate G4. Mechanism "the project's Playwright shards; the plugin only schedules them". `rubric.md` Calibration scores the same Chromium finding G4 fail, 0.
- #15 Rubric row 12, Researchers parallel: fail. Evidence: first failed gate G4. The mechanism ("independent read-only studies ran in parallel") names no sdlc-lite file, rule, script or role; the prevention "keep" is not a check that fails today (G5 fails too). It is also [U] with the saving unmeasured.
- #16 The planted claim holds: fail. Evidence: `evidence_value(fp,'runs.total')` printed 17, not 999, rc=1. The control is wrong as intended and the check bites.

## Out of scope changes
None. The working tree shows only the untracked task folder and the report, both from before this run.

## For the next attempt
Control caught: the planted claim (runs.total = 999) is false, the collector says 17. Only rows 1 and 3 are actionable; `## Not actionable` in `docs/reports/2026-10-11-fleet-retro-12.md` still reads "Filled by the step 5 verifier" and should be filled with: row 2 (score 6, duplicate of row 3), row 4 (G3), row 5 (G2), row 6 (G2), row 7 (G3), row 8 (G3), row 9 (G2), row 10 (G4), row 11 (G4), row 12 (G4). The sampled rows 1, 6 and 11 reproduce, so no row is wrong; row 6 and 11 are still not actionable by the rubric. File only rows 1 and 3.
