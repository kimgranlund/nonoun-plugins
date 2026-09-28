<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/skills/level-rubric/SKILL.md: added the recurring-finding rule to the "Bump one level" line. It sends a recurring finding to a planner L3 replan, with no bump and no count toward one, and says the test fires only on a recurrence.
- plugins/sdlc-lite/skills/chain/SKILL.md: item 4 now checks whether a second fail is a recurring finding before bumping. If it is, /chain writes a `recurring finding:` entry to `## Plan review` and takes the 4.2 replan path. Item 2 now treats a repeated block after a replan as a recurring finding.
- plugins/sdlc-lite/agents/planner.md: added rule 6 under "Criteria that can pass". A replan must land a concrete change, and commentary alone is not allowed.
- plugins/sdlc-lite/agents/conductor.md: extended the `- Levels follow` line: a recurring finding means a planner L3 replan, never a level bump.
- plugins/sdlc-lite/skills/handoff-format/SKILL.md: the `## Plan review` description now includes `recurring finding:` entries.
- CLAUDE.md: added one sentence to the plan-defect decision bullet.
- .claude/agents/sdlc-lite-author.md: added one clause to the plan-defect route bullet.

## Checks
All run from `plugins/sdlc-lite`.
- All six `grep` criteria for `recurring finding` (level-rubric, chain item 4, planner numbered rule, conductor `- Levels follow` line, handoff-format, `../../CLAUDE.md`): pass.
- `git diff --quiet HEAD -- scripts/run.sh`: pass.
- `! git diff HEAD -- skills/level-rubric/SKILL.md ../../CLAUDE.md | grep -qE '^[-+]\|'`: pass.
- `scripts/check.sh`: exit 0.

## Notes
- The agreement criterion (the four named files agree) is a reading check. It is left for the verifier.
- The `plan defect:` sentences and the fenced `merge-step` block were not edited.
