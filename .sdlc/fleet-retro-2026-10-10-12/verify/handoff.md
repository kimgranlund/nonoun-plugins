## Task goal
Check the fleet retro report `docs/reports/2026-10-10-fleet-retro-12.md`: reproduce two sampled [V] rows, grade every row against the actionability rubric, and run one planted control whose claim is wrong. Read-only: run checks, change nothing.

## Step 1: Verify the fleet retro report
level: L1

### Acceptance criteria
- Sample row 1 holds (evidence files exist): `test -s /Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0378-integration-wave-3/step-2/builder-L4.md` and `test -s /Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0378-integration-wave-3/evidence/phase-b/full-check.failed.txt`
- Sample row 7 holds (criteria count): `python3 -I -c "import sys,json;sys.path.insert(0,'plugins/sdlc-lite/scripts');import fleet_detect as f;fp=json.load(open('.sdlc/fleet-retro-2026-10-10-12/ui-kit-maison.json'));v=f.evidence_value(fp,'tickets.items[152].criteria');sys.exit(0 if v==32 else 1)"`
- Rubric row 1, Cross-lane red after a green step 1: in `docs/reports/2026-10-10-fleet-retro-12.md` the row passes every gate of `plugins/sdlc-lite/skills/fleet-retro/rubric.md` (G1 to G5, in order, naming the first gate that fails) and scores at least 7 of 10 on C1 to C5; report the score or the failed gate.
- Rubric row 2, record flags a deviation after every widen: in `docs/reports/2026-10-10-fleet-retro-12.md` the row passes every gate of `plugins/sdlc-lite/skills/fleet-retro/rubric.md` (G1 to G5, in order, naming the first gate that fails) and scores at least 7 of 10 on C1 to C5; report the score or the failed gate.
- Rubric row 3, review says replan after a corrected plan: in `docs/reports/2026-10-10-fleet-retro-12.md` the row passes every gate of `plugins/sdlc-lite/skills/fleet-retro/rubric.md` (G1 to G5, in order, naming the first gate that fails) and scores at least 7 of 10 on C1 to C5; report the score or the failed gate.
- Rubric row 4, Mailbox Monitor expiry: in `docs/reports/2026-10-10-fleet-retro-12.md` the row passes every gate of `plugins/sdlc-lite/skills/fleet-retro/rubric.md` (G1 to G5, in order, naming the first gate that fails) and scores at least 7 of 10 on C1 to C5; report the score or the failed gate.
- Rubric row 5, Stop hook re-fire: in `docs/reports/2026-10-10-fleet-retro-12.md` the row passes every gate of `plugins/sdlc-lite/skills/fleet-retro/rubric.md` (G1 to G5, in order, naming the first gate that fails) and scores at least 7 of 10 on C1 to C5; report the score or the failed gate.
- Rubric row 6, Truncated role reports: in `docs/reports/2026-10-10-fleet-retro-12.md` the row passes every gate of `plugins/sdlc-lite/skills/fleet-retro/rubric.md` (G1 to G5, in order, naming the first gate that fails) and scores at least 7 of 10 on C1 to C5; report the score or the failed gate.
- Rubric row 7, size_m_criteria 32 criteria: in `docs/reports/2026-10-10-fleet-retro-12.md` the row passes every gate of `plugins/sdlc-lite/skills/fleet-retro/rubric.md` (G1 to G5, in order, naming the first gate that fails) and scores at least 7 of 10 on C1 to C5; report the score or the failed gate.
- The planted claim holds: `python3 -I -c "import sys,json;sys.path.insert(0,'plugins/sdlc-lite/scripts');import fleet_detect as f;fp=json.load(open('.sdlc/fleet-retro-2026-10-10-12/ui-kit-maison.json'));v=f.evidence_value(fp,'runs.total');sys.exit(0 if v==999 else 1)"`
