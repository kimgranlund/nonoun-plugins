## Task goal
Check the fleet retro report `docs/reports/2026-10-12-fleet-retro-12.md`: reproduce two sampled [V] rows, grade every row against the actionability rubric, and run one planted control whose claim is false.

## Step 1: Verify the fleet retro report
level: L1

### Acceptance criteria
- Sample row 1 holds (quoted text in the interview): `grep -qF 'Full gate timed out inside check:gen-ui-harness' /Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/fleet-retro-2026-10-12-12.md`
- Sample row 6 holds (quoted text in the interview): `grep -qF 'skips.md close check blocks close for roles that ran' /Users/kimgranlund/Projects/nonoun/agent-ui/.sdlc/fleet-retro-2026-10-12-12.md`
- Rubric row 1, 7b full gate timeout: in `docs/reports/2026-10-12-fleet-retro-12.md` the row passes every gate of `plugins/sdlc-lite/skills/fleet-retro/rubric.md` (G1 to G5, in order, naming the first gate it fails) and scores at least 7 of 10.
- Rubric row 2, Gate lock admitted too much: in `docs/reports/2026-10-12-fleet-retro-12.md` the row passes every gate of `plugins/sdlc-lite/skills/fleet-retro/rubric.md` (G1 to G5, in order, naming the first gate it fails) and scores at least 7 of 10.
- Rubric row 3, Chromium load: in `docs/reports/2026-10-12-fleet-retro-12.md` the row passes every gate of `plugins/sdlc-lite/skills/fleet-retro/rubric.md` (G1 to G5, in order, naming the first gate it fails) and scores at least 7 of 10.
- Rubric row 4, Shared generated files conflict: in `docs/reports/2026-10-12-fleet-retro-12.md` the row passes every gate of `plugins/sdlc-lite/skills/fleet-retro/rubric.md` (G1 to G5, in order, naming the first gate it fails) and scores at least 7 of 10.
- Rubric row 5, Plan criterion cannot pass: in `docs/reports/2026-10-12-fleet-retro-12.md` the row passes every gate of `plugins/sdlc-lite/skills/fleet-retro/rubric.md` (G1 to G5, in order, naming the first gate it fails) and scores at least 7 of 10.
- Rubric row 6, skips.md close check: in `docs/reports/2026-10-12-fleet-retro-12.md` the row passes every gate of `plugins/sdlc-lite/skills/fleet-retro/rubric.md` (G1 to G5, in order, naming the first gate it fails) and scores at least 7 of 10.
- Rubric row 7, Em-dash verifier nit: in `docs/reports/2026-10-12-fleet-retro-12.md` the row passes every gate of `plugins/sdlc-lite/skills/fleet-retro/rubric.md` (G1 to G5, in order, naming the first gate it fails) and scores at least 7 of 10.
- Rubric row 8, Derived-file freshness: in `docs/reports/2026-10-12-fleet-retro-12.md` the row passes every gate of `plugins/sdlc-lite/skills/fleet-retro/rubric.md` (G1 to G5, in order, naming the first gate it fails) and scores at least 7 of 10.
- Rubric row 9, PR number collisions: in `docs/reports/2026-10-12-fleet-retro-12.md` the row passes every gate of `plugins/sdlc-lite/skills/fleet-retro/rubric.md` (G1 to G5, in order, naming the first gate it fails) and scores at least 7 of 10.
- Rubric row 10, Stale-history criteria: in `docs/reports/2026-10-12-fleet-retro-12.md` the row passes every gate of `plugins/sdlc-lite/skills/fleet-retro/rubric.md` (G1 to G5, in order, naming the first gate it fails) and scores at least 7 of 10.
- The planted claim holds: `grep -qF 'Gate lock capacity was never changed' /Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/fleet-retro-2026-10-12-12.md`
