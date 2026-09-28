<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/chain/SKILL.md`: section 4 action list gains `swap`, which runs `steps.py swap`. On exit 0 it appends a `swap applied:` line to `## Plan review` and rebuilds at the printed level. On exit 1 it appends stderr and takes the 4.2 replan path. Item 4's plan-defect exception now says "unless `steps.py next` prints `swap`". New item 8 states the swap rule: the verifier is the only source, a builder's `plan defect:` note always replans, and there is one swap per step, so a second one replans.
- `plugins/sdlc-lite/agents/conductor.md`: the escalation bullet adds the route: `swap` goes to `steps.py swap`, then the builder at the printed level with no `## Previous attempt`. A refused swap is a plan defect and gets a planner L3 replan. A swap is never a bump.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: the step handoff section names `steps.py swap` as the only other writer. `## Plan review` lists the `swap applied:` line and a swap refusal as entries. The `## Previous attempt` paragraph says a swapped plan defect rebuilds without one.
- `plugins/sdlc-lite/skills/level-rubric/SKILL.md`: the bump paragraph now reads: a verifier `plan defect:` fail goes to a replan, or to a swap plus a rebuild at the same level when `steps.py swap` accepts it. Neither counts toward a bump. The planner L3 row is unchanged.
- `CLAUDE.md`: the `scripts/steps.py` bullet documents the `swap` subcommand: preconditions, the span run, the tree check, the refusal line, and the already-applied exit. The `next` action list ends `inherited`, `swap`, and `/chain` step 4 runs `steps.py swap` when `next` prints it. The Decisions bullet is retitled and gains the swap exception. Its code-gates sentence names `steps.py swap`.
- `.claude/agents/sdlc-lite-author.md`: the Plan-defect route line names the swap route and lists `steps.py swap` among the places kept in sync.
- `plugins/sdlc-lite/scripts/check.py`: `PLAN_DEFECT_DOCS` gains `'steps.py swap'` for the conductor, chain, handoff-format, level-rubric, and steps.py. The docstring's item 5 now mentions it.

## Checks
- `grep -q "steps.py swap" plugins/sdlc-lite/skills/chain/SKILL.md`: PASS
- `grep -q "swap applied:" plugins/sdlc-lite/skills/chain/SKILL.md`: PASS
- `grep -q "steps.py swap" plugins/sdlc-lite/agents/conductor.md`: PASS
- `grep -q "steps.py swap" plugins/sdlc-lite/skills/handoff-format/SKILL.md`: PASS
- `grep -q "steps.py swap" plugins/sdlc-lite/skills/level-rubric/SKILL.md`: PASS
- `grep -q "steps.py swap" CLAUDE.md`: PASS
- `grep -q "inherited., .swap" CLAUDE.md`: PASS
- `grep -q "steps.py swap" .claude/agents/sdlc-lite-author.md`: PASS
- `grep -q "steps.py swap" plugins/sdlc-lite/scripts/check.py`: PASS
- Guard-bites probe (copy the plugin, strip "steps.py swap" from the chain skill, run check.py and grep for the `plan-defect route missing "steps.py swap"` error): PASS
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: exit 0, "ok: 18 role levels, 8 agents checked"
- Observable: section 4's first paragraph lists `swap`, item 4's exception names `steps.py next` printing `swap`, and item 8 states the verifier-only origin and the second-swap replan. Checked by reading the edited file.

## Notes
- Step 1's changes to `steps.py`, `verifier.md`, and `check.py` are uncommitted in the tree, and this step builds on them. Nothing was committed.
- The check.py docstring edit goes beyond the Do. I made it so item 5 does not go stale.
- Item 4 used to say a plan-defect fail "never rebuilds". It now says "never rebuilds as a fail", because a swap does rebuild, at the same level with no `## Previous attempt`.
- CLAUDE.md's sentence "The planner runs each criterion once before writing it (...)" is unchanged, so step 3 can extend it.
