## Task goal
Plan defects stop fewer lanes.

## Step 2: Route `swap` in /chain and the conductor, and repair the records
level: L3
### Do
Prose only; every file below already carries the plan-defect route, so add the swap next to it.
- `plugins/sdlc-lite/skills/chain/SKILL.md`, section 4: add `swap` to the action list in the first paragraph: run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py swap .sdlc/<task>/step-<n>`; exit 0 -> append one line `swap applied: step <n>: <its stdout line>` to the task handoff's `## Plan review` (create it if missing, keep earlier entries) and run the builder at the level `next` printed (a rebuild: no `## Previous attempt`, never a bump, never counted toward "a second fail"); exit 1 -> append its stderr to `## Plan review` and take the 4.2 replan path. In item 4, amend the plan-defect exception so it takes the 4.2 path unless `steps.py next` prints `swap`. Add an item 8 under "For each step" stating the swap rule, including that a swap comes only from the verifier (a builder's `plan defect:` note always replans: whoever writes the work never sets its check) and that a second swap on the same step replans.
- `plugins/sdlc-lite/agents/conductor.md`, the escalation bullet under "How you run roles": `swap` -> `steps.py swap`, then the builder at the printed level; a swap refusal is a plan defect and goes to a planner L3 replan; never a bump.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: in the step handoff section, state that `steps.py swap` is the one other writer of a step handoff (it rewrites one criterion line from the verifier's `swap old:`/`swap new:` pair, never by hand); in `## Plan review`, add the `swap applied:` line and a swap refusal as entries; in the `## Previous attempt` paragraph, say a swapped plan defect rebuilds without one.
- `plugins/sdlc-lite/skills/level-rubric/SKILL.md`, the bump paragraph of the builder section: a verifier fail tagged `plan defect:` goes to replan, or to a criterion swap and a rebuild at the same level when `steps.py swap` accepts the verifier's proposal; neither counts toward a bump. The planner L3 row stays.
- `CLAUDE.md`: the `scripts/steps.py` bullet gains the `swap` subcommand (its preconditions, the span run, the tree check, the refusal, the already-applied exit) and `swap` at the end of the `next` action list (`... `inherited`, `swap`)`), and says `/chain` step 4 runs `swap` when `next` prints it. The Decisions bullet "A plan defect goes to a replan, never a rebuild" is retitled and amended: a verifier plan defect with a `swap old:`/`swap new:` pair that `steps.py swap` accepts rewrites that one criterion and rebuilds at the same level, with no bump and no `## Previous attempt`; a refused swap replans; a builder never proposes a swap.
- `.claude/agents/sdlc-lite-author.md`: the Plan-defect route line names the swap route and `steps.py swap` among the places kept in sync.
- `plugins/sdlc-lite/scripts/check.py`: add `'steps.py swap': ('agents/conductor.md', 'skills/chain/SKILL.md', 'skills/handoff-format/SKILL.md', 'skills/level-rubric/SKILL.md', 'scripts/steps.py')` to `PLAN_DEFECT_DOCS`.
### Acceptance criteria
- `grep -q "steps.py swap" plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -q "swap applied:" plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -q "steps.py swap" plugins/sdlc-lite/agents/conductor.md`
- `grep -q "steps.py swap" plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- `grep -q "steps.py swap" plugins/sdlc-lite/skills/level-rubric/SKILL.md`
- `grep -q "steps.py swap" CLAUDE.md`
- `grep -q "inherited., .swap" CLAUDE.md`
- `grep -q "steps.py swap" .claude/agents/sdlc-lite-author.md`
- `grep -q "steps.py swap" plugins/sdlc-lite/scripts/check.py`
- `t=$(mktemp -d) && cp -R plugins/sdlc-lite "$t/p" && cp CLAUDE.md "$t/p/CLAUDE.md" && perl -pi -e "s/steps.py swap/xx/g" "$t/p/skills/chain/SKILL.md" && python3 plugins/sdlc-lite/scripts/check.py "$t/p" 2>&1 | grep -q "skills/chain/SKILL.md: plan-defect route missing \"steps.py swap\""` (run from the repo root; proves the guard bites)
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`
- Observable: in `plugins/sdlc-lite/skills/chain/SKILL.md`, section 4's first paragraph lists `swap` among the actions, item 4's plan-defect exception names `steps.py next` printing `swap`, and an item 8 states that a swap comes only from the verifier and that a second swap on the same step replans.
