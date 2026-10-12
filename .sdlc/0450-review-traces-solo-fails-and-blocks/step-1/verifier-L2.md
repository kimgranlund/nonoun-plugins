<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- #1 (red) exactly one `*-solo-fails-and-blocks.md` in docs/reports: pass. Evidence: ran the span on the built tree, exit 0. `step-1/red-checkpoint.jsonl` records the pre-edit control for this span as `"result":"red","exit":1` and a post-build audit `status ok`. No `process-deviations.md` exists in the artifacts dir. The check bites: with no report, `grep -c` prints 0 and `-eq 1` fails.
- #2 five required `##` headings, whole-line match: pass. Evidence: ran the span, exit 0. The report at `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout37/m/docs/reports/2026-10-11-solo-fails-and-blocks.md` holds all five. The `ls` inside `$()` exits nonzero when the report is absent, so the check goes red with no report.
- #3 pointer check (at least 10 verifier, at least 5 builder, all resolve): pass. Evidence: ran the python span, exit 0, and printed 27 verifier and 11 builder pointers. `os.path.exists` runs on every pointer, so a nonexistent path would fail the `assert not bad`.
- #4 `propose a ticket` appears at most 3 times: pass. Evidence: python span exit 0, count 3. Offsets are 10397, 12550 and 14269, which are the three `Status: propose a ticket.` lines of ranked changes 1 to 3. The phrase appears nowhere else.
- #5 T-0412, T-0413, T-0438, T-0439, T-0441, T-0448 all present: pass. Evidence: ran the span, exit 0. All six appear under `## Already covered`.
- #6 K-005 and "89 of 123": pass. Evidence: ran the span, exit 0. The line after the title cites `docs/kpi/005-solo-first-pass-rate.md` and the baseline report. `ls docs/kpi` confirms 005 exists in this tree (T-0449 landed), so the builder's note that the handoff's "no file yet" is stale is correct.
- #7 category words (criterion defect, builder gap, environment, verifier over-reach, plan defect): pass. Evidence: ran the span, exit 0. All five appear in `## Classified counts`.
- #8 an `agents/(builder|verifier|planner|solo).md` path: pass. Evidence: ran the span, exit 0. The report names `plugins/sdlc-lite/agents/solo.md` and `planner.md`.
- #9 no trailing whitespace: pass. Evidence: ran the span, exit 0. Em dash count in the report is 0 (`grep -c '—'`). The report is 198 lines, under 400.
- #10 the verifier opens at least 5 pointers and reruns `sample.py`: pass. Evidence, pointers: I opened nine files and compared each with the cause the report assigns.
  - Ranked changes 1 and 2 (the dependent and criterion-span causes):
    - `~/Projects/maison/ui-kit-maison/.sdlc/tickets/.0274-component-switchgroup/verifier-L2.md`: row 3 fail, `lib.mjs:282` rejects `maison/switch` that is not in `dependencies`. Matches.
    - `~/Projects/nonoun/sdlc-lite/.sdlc/.0378-red-checkpoint-builder/verifier-L2.md`: criterion 2 fails, exit 1, because of the `control: ` label prefix. Matches.
    - `~/Projects/nonoun/ultimate-tokens/.sdlc/peer-luminosity-diagnose/verifier-L2.md`: `npm test` fails the citation gate on 3 stale lines (42, 145, 170). Matches.
    - `~/Projects/nonoun/sdlc-lite/.sdlc/.0356-verifier-routing-by-level/verifier-L3.md`: T0356-6 `plan defect`, `wc -l` pads its count on Darwin and `grep -qx 4` never matches. Matches.
    - `~/Projects/nonoun/sdlc-lite/.sdlc/.0398-fanout-stale-verifier-result/verifier-L2.md`: `plan defect`, the selftest prints only misses, so no output can hold ok lines. Matches.
  - Ranked changes 3 and 4:
    - `~/Projects/maison/ui-kit-maison/.sdlc/tickets/.0319-component-avatar/verifier-L2.md`: `plan defect`, rows 7 to 12 cannot pass in a lane build. Matches.
    - `~/Projects/nonoun/agent-ui/.sdlc/skills-em-dash-1/verifier-L2.md`: 31 lone-comma table cells, fences, and drifted descriptions. Matches.
  - Ranked change 5, builder blocked notes:
    - `~/Projects/nonoun/ultimate-tokens/.sdlc/native-dom-charts/step-2/builder-L3.md`: the scope excludes `scripts/bundle.mjs` that the gate runs. Matches "scope left out".
    - `~/Projects/maison/ui-kit-maison/.sdlc/tickets/.0152-manifest-driven-renderers/step-3.superseded-1/builder-L3.md`: criterion 1 cannot pass while the Do says controllers move verbatim. Matches "criterion contradicts the Do".
    - `~/Projects/nonoun/agent-ui/.sdlc/response-type-selection/step-10/builder-L2.md`: red criterion already green at base. Matches.
    - `~/Projects/nonoun/ultimate-tokens/.sdlc/geometry-compound-insets/step-4.superseded-1/builder-L3.md`: the criterion is stale against the step base. Matches.
    - `~/Projects/maison/ui-kit-maison/.sdlc/tickets/.0307-native-element-discovery-contracts/step-1/builder-L3.md`: `plan defect`, the allowed scope cannot represent native roots. Matches "scope left out".
  - Evidence, rerun: `python3 .sdlc/0450-review-traces-solo-fails-and-blocks/sample.py` prints "solo tickets 166, verified 123, first-round non-pass 34, of which later passed or closed 34" and "builder blocked notes 39 ... read sample 20". Per-repo counts are maison 29/15, agent-ui 2/1, ultimate-tokens 8/4, sdlc-lite 0/0. All of these match `## Sample`. 34 equals the baseline's 123 minus 89.
  - Planner rule claims: `planner.md` line 44 (a sub-bullet of rule 11) names `specgate.py red` refusing a `(red)` span that is already green. Rule 14 is the final `gates green` step. `## Contract dependents` exists at line 51. `solo.md` Loop step 2 (line 14) runs `specgate.py red` as the report says.
- #11 (guard) `docs_check.py`: pass. Evidence: ran the span, exit 0. This is a gate and it is green, so no base run was needed.
- #12 (guard) scope: pass. Evidence: ran the span with `SDLC_BASE_SHA=41cdd954...`, exit 0. Outside `.sdlc`, the tracked diff is empty and the only untracked file is `docs/reports/2026-10-11-solo-fails-and-blocks.md`.

Steelman pass on the draft concerns:
- Concern: the report's read of each verifier file is "fail lines only", so the 34-way classification may be shallow. The report discloses this under `## Unverified`. I read nine files in the same way and all matched, so I dropped the concern.
- Concern: the handoff says 173 notes and "no K-005 file", but the tree shows 174 and a K-005 file. The report states both numbers and the reason (an unwindowed count and one later note). It also cites the kpi file. I dropped this concern; a changed baseline is reported, not an error.
- Concern: ranked change 1 and 2 ordering is by count (7 vs 6), consistent with the stated rule. Dropped.

## Out of scope changes
None. `git status` shows only the report under `docs/reports/` plus files under `.sdlc/0450-.../` (sample.py, sample.txt, scratch/, step-1 run records). The ` M skips.md` change was already modified before the build, per the builder's note. It is under `.sdlc`, which the scope guard allows.

## For the next attempt
None
