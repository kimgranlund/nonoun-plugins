<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/scripts/check.py: added `'gates green': ('agents/planner.md',)` to `PLAN_DEFECT_DOCS`. Docstring item 5 now names the planner's "gates green" rule.
- plugins/sdlc-lite/agents/planner.md: added rule 14, using the proposed text, under `## Criteria that can pass`. The merge-step block is untouched.
- CLAUDE.md: added a clause to the plan-defect decision. It says whole-suite gate guards go on one final `gates green` step, and that check.py guards the phrase.

## Checks
- `grep -qF 'gates green' plugins/sdlc-lite/agents/planner.md`: exit 0
- `grep -qF 'gates green' CLAUDE.md`: exit 0
- `grep -qF "'gates green'" plugins/sdlc-lite/scripts/check.py`: exit 0
- Negative control: I copied the plugin to a temp dir, stripped the phrase from planner.md, and ran check.py there. Its output contained `gates green`, so the check flags the missing phrase: exit 0
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`: printed `ok: 18 role levels, 8 agents checked`, exit 0
- (guard) `git diff --quiet HEAD -- plugins/sdlc-lite/skills/handoff-format/SKILL.md`: exit 0

## Notes
None
