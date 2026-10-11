## Task goal
Check the fleet retro report `docs/reports/2026-10-11-fleet-retro-00.md`: reproduce two sampled [V] rows, grade every row against the actionability rubric, and run one planted control whose claim is wrong. Read-only: run checks, change nothing.

## Step 1: Verify the fleet retro report
level: L1

### Acceptance criteria
- Sample row 1 holds (unmetered count): `python3 -I -c "import sys,json;sys.path.insert(0,'plugins/sdlc-lite/scripts');import fleet_detect as f;fp=json.load(open('.sdlc/fleet-retro-2026-10-11-00/ui-kit-maison.json'));v=f.evidence_value(fp,'runs.unmetered');sys.exit(0 if v==160 else 1)"`
- Sample row 7 holds (quoted text in the interview): `grep -qF 'first-ever browser run of lane source' /Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/fleet-retro-2026-10-11-00.md`
- Rubric row 1, Unmetered runs in maison: in `docs/reports/2026-10-11-fleet-retro-00.md` the row passes every gate of `plugins/sdlc-lite/skills/fleet-retro/rubric.md` (G1 to G5, in order, naming the first gate that fails) and scores at least 7 of 10 on C1 to C5; report the score or the failed gate.
- Rubric row 2, Unmetered runs in sdlc-lite: in `docs/reports/2026-10-11-fleet-retro-00.md` the row passes every gate of `plugins/sdlc-lite/skills/fleet-retro/rubric.md` (G1 to G5, in order, naming the first gate that fails) and scores at least 7 of 10 on C1 to C5; report the score or the failed gate.
- Rubric row 3, record gives no result: in `docs/reports/2026-10-11-fleet-retro-00.md` the row passes every gate of `plugins/sdlc-lite/skills/fleet-retro/rubric.md` (G1 to G5, in order, naming the first gate that fails) and scores at least 7 of 10 on C1 to C5; report the score or the failed gate.
- Rubric row 4, Unquoted variable under zsh: in `docs/reports/2026-10-11-fleet-retro-00.md` the row passes every gate of `plugins/sdlc-lite/skills/fleet-retro/rubric.md` (G1 to G5, in order, naming the first gate that fails) and scores at least 7 of 10 on C1 to C5; report the score or the failed gate.
- Rubric row 5, Red-checkpoint hash: in `docs/reports/2026-10-11-fleet-retro-00.md` the row passes every gate of `plugins/sdlc-lite/skills/fleet-retro/rubric.md` (G1 to G5, in order, naming the first gate that fails) and scores at least 7 of 10 on C1 to C5; report the score or the failed gate.
- Rubric row 6, Monitor expiry: in `docs/reports/2026-10-11-fleet-retro-00.md` the row passes every gate of `plugins/sdlc-lite/skills/fleet-retro/rubric.md` (G1 to G5, in order, naming the first gate that fails) and scores at least 7 of 10 on C1 to C5; report the score or the failed gate.
- Rubric row 7, Lane source never browser-run: in `docs/reports/2026-10-11-fleet-retro-00.md` the row passes every gate of `plugins/sdlc-lite/skills/fleet-retro/rubric.md` (G1 to G5, in order, naming the first gate that fails) and scores at least 7 of 10 on C1 to C5; report the score or the failed gate.
- Rubric row 8, size_m_criteria 32 criteria: in `docs/reports/2026-10-11-fleet-retro-00.md` the row passes every gate of `plugins/sdlc-lite/skills/fleet-retro/rubric.md` (G1 to G5, in order, naming the first gate that fails) and scores at least 7 of 10 on C1 to C5; report the score or the failed gate.
- Rubric row 9, Stop hook re-fire: in `docs/reports/2026-10-11-fleet-retro-00.md` the row passes every gate of `plugins/sdlc-lite/skills/fleet-retro/rubric.md` (G1 to G5, in order, naming the first gate that fails) and scores at least 7 of 10 on C1 to C5; report the score or the failed gate.
- The planted claim holds: `python3 -I -c "import sys,json;sys.path.insert(0,'plugins/sdlc-lite/scripts');import fleet_detect as f;fp=json.load(open('.sdlc/fleet-retro-2026-10-11-00/ui-kit-maison.json'));v=f.evidence_value(fp,'runs.total');sys.exit(0 if v==999 else 1)"`
