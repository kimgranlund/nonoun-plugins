## Task goal
Check the findings of docs/reports/fleet-retro-2026-10-06.md: reproduce the sampled [V] rows from their evidence, apply plugins/sdlc-lite/skills/fleet-retro/rubric.md to every row, and confirm a planted false claim fails. Run from the repository root; never edit a file.

## Step 1: Verify the fleet retro report
level: L1
### Read first
- plugins/sdlc-lite/skills/fleet-retro/rubric.md
- docs/reports/fleet-retro-2026-10-06.md
### Do
Nothing to build. Run each criterion and report pass or fail with the evidence. For a rubric criterion, read the row's evidence yourself (open the files and fingerprint paths it names; use `git log` and `git tag --contains` for G2), score G1 to G5 then C1 to C5 as `rubric.md` defines, and write the gate results and the five scores in the evidence. Report a row that fails a gate or scores under 7 as fail; that is a finding about the row, not a defect in the check.
### Acceptance criteria
- Sample, row 1: `python3 -I -c "import sys,json; sys.path.insert(0,'plugins/sdlc-lite/scripts'); import fleet_detect as d; fp=json.load(open('.sdlc/fleet-retro-2026-10-06/agent-ui.json')); v=d.evidence_value(fp,'plan_review_share'); c=d.evidence_value(fp,'runs.by_role[\"planner\"].cost_usd + runs.by_role[\"plan-reviewer\"].cost_usd'); sys.exit(0 if abs(v-0.5546)<0.0005 and abs(c-436.44)<0.01 else 1)"`
- Sample, row 6: `grep -qF '| block-disk-scan.sh | before | 0.35 | 1.60 | 8.93 | over 25 | over 25 |' docs/reports/hook-perf.md`
- Control, planted [V] claim "agent-ui has 250 deduped runs" (evidence `agent-ui.json :: runs.total`): `python3 -I -c "import sys,json; sys.path.insert(0,'plugins/sdlc-lite/scripts'); import fleet_detect as d; fp=json.load(open('.sdlc/fleet-retro-2026-10-06/agent-ui.json')); sys.exit(0 if d.evidence_value(fp,'runs.total')==250 else 1)"`
- Rubric, row 1 (`grep '^| 1 |' docs/reports/fleet-retro-2026-10-06.md`) passes every gate of rubric.md and scores at least 7 of 10.
- Rubric, row 2 (`grep '^| 2 |' docs/reports/fleet-retro-2026-10-06.md`) passes every gate of rubric.md and scores at least 7 of 10.
- Rubric, row 3 (`grep '^| 3 |' docs/reports/fleet-retro-2026-10-06.md`) passes every gate of rubric.md and scores at least 7 of 10.
- Rubric, row 4 (`grep '^| 4 |' docs/reports/fleet-retro-2026-10-06.md`) passes every gate of rubric.md and scores at least 7 of 10.
- Rubric, row 5 (`grep '^| 5 |' docs/reports/fleet-retro-2026-10-06.md`) passes every gate of rubric.md and scores at least 7 of 10.
- Rubric, row 6 (`grep '^| 6 |' docs/reports/fleet-retro-2026-10-06.md`) passes every gate of rubric.md and scores at least 7 of 10.
