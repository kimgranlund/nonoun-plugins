# Verify T-0307 and T-0310 on the released tree

Verify the two criteria sets below against the current tree. Read-only; write one verdict covering both, listing each failed criterion by id.

## Acceptance criteria

T-0307 (plugins/sdlc-lite/skills/fleet-retro/interview.md):
- A1: the file exists, is under 60 lines, has no em dashes; `python3 plugins/sdlc-lite/scripts/check.py` (or the check.sh skill-folder check) finds the skill folder valid.
- A2: it asks first for plugin version path, claude version, time and load snapshot; then at most 5 questions; answer format is one row per finding (symptom, evidence, mechanism, cost, [V]/[U], prevention), ranked by cost, at most 7 rows, written to `.sdlc/fleet-retro-<date>.md` (max 80 lines), one-line reply with path and top three; includes the rule measure only, start no new work, never edit another repo.
- A3: it states counts and costs come from the collector, not the conductor.
- A4: each finding in the three existing root-cause reports fits one row of the answer format (see fixtures.md/rubric.md in the skill folder); any that do not are listed.

T-0310 (.sdlc/fleet.json, plugins/sdlc-lite/scripts/fleet_config.py, schema doc under docs/specs/sdlc-lite/):
- B1: `python3 plugins/sdlc-lite/scripts/fleet_config.py selftest` passes.
- B2: an excluded repo is absent from `show --active` and present in `show` (run it and observe).
- B3: a malformed file exits 1 naming the line and never silently drops a repo (try a temp copy; do not edit the real file).
- B4: `fleet_config.py` has show, add, exclude, include, selftest; fleet.json entries have path, name, conductor, optional gh repo, status with reason and date; seed repos active/excluded as the ticket T-0310 states (gen-ui-kit path was later corrected, ultimate-tokens added: acceptable).
- B5: `check.py` and `tickets.py --root .sdlc check` pass.
