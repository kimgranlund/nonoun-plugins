<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/skills/chain/SKILL.md: added item 9, "Scope widening", covering the `steps.py widen` command, what to do on exit 0 and exit 1, and why. Item 2 now names item 9 as its one exception.
- plugins/sdlc-lite/agents/conductor.md: the escalation bullet now includes the `steps.py widen` route.
- plugins/sdlc-lite/skills/handoff-format/SKILL.md: `## Plan review` now lists the `scope widened:` and `scope decision:` entries. Added the step handoff's `## Scope widened` section, which `steps.py widen` writes.
- plugins/sdlc-lite/skills/level-rubric/SKILL.md: the bump paragraph now says a block resolved by `steps.py widen` never counts toward a bump.
- plugins/sdlc-lite/agents/planner.md: rule 9 now handles a `scope decision:` entry. It applies at replan time only; the plan-time scope-guard rules are unchanged.
- plugins/sdlc-lite/scripts/check.py: added the `'steps.py widen'` entry to `PLAN_DEFECT_DOCS`.
- plugins/sdlc-lite/adapters/codex/agents/sdlc-conductor-l1.toml, sdlc-planner-l1/l2/l3.toml: regenerated with `codex_roles.py generate`, not edited by hand.

## Checks
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`: generated.
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: passed, exit 0 (guard).
- `grep -qF 'steps.py widen'` on conductor.md, chain/SKILL.md, handoff-format/SKILL.md and level-rubric/SKILL.md: all exit 0.
- `grep -qF 'scope decision:'` on planner.md and chain/SKILL.md: both exit 0.
- `grep -qF "'steps.py widen'" plugins/sdlc-lite/scripts/check.py`: exit 0.
- `python3 plugins/sdlc-lite/scripts/check.py`: passed ("ok: 18 role levels, 8 agents checked").
- `git diff --check`: clean.

## Notes
The work tree also has changes this step did not make, left untouched: `scripts/steps.py`, `docs/references/sdlc-internals.md` and the task handoff. They appear to be step 1's work.
