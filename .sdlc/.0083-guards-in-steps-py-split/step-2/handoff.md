## Task goal
`steps.py split --only N` refuses, with a `plan defect:` last line, when running a step's `(guard)` criteria changed the git work tree (tracked or untracked files), so a side-effecting guard is caught by code, not only by the planner prompt. The selftest proves the refusal fires and that a guard which changes nothing still passes.

## Step 2: Keep docs and check.py in step with the new refusal
level: L2
### Do
Describe the new refusal with the exact phrase `changed the work tree` in each of these places:
- `CLAUDE.md`:
  - Layout `scripts/steps.py` bullet: `--only N` also refuses when its guards changed the work tree, tracked or untracked, versus before they ran, and names the paths. Outside git there is no check. A tree already dirty before is fine.
  - Decisions "A plan defect goes to a replan" bullet: a guard that changed the work tree is a plan defect, and the `split --only` guard run is a code gate for it.
  - Systems line naming the three code gates.
- `.claude/agents/sdlc-lite-author.md`: the Plan-defect route bullet.
- `plugins/sdlc-lite/skills/chain/SKILL.md`: section 3 and 4.2 text on `--only N`, i.e. a red guard or a guard that changed the work tree.
- `plugins/sdlc-lite/agents/planner.md`: rule 1 under "Criteria that can pass". Add one sentence saying `steps.py split --only N` runs every `(guard)` and refuses one that changed the work tree, so a guard must be side-effect free. Do not touch the `merge-step` block.

In `plugins/sdlc-lite/scripts/check.py`, add a `PLAN_DEFECT_DOCS` entry `'changed the work tree': ('agents/planner.md', 'skills/chain/SKILL.md', 'scripts/steps.py')`. That way check.py fails if the phrase drops out of any of those files.
### Acceptance criteria
- `grep -q "changed the work tree" CLAUDE.md`
- `grep -q "changed the work tree" .claude/agents/sdlc-lite-author.md`
- `grep -q "changed the work tree" plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -q "changed the work tree" plugins/sdlc-lite/agents/planner.md`
- `grep -q "'changed the work tree'" plugins/sdlc-lite/scripts/check.py`
- (guard) `plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest | tail -n1 | grep -qx 'steps selftest: PASS'`
- (guard) `test -z "$(git status --porcelain --untracked-files=all -- plugins/sdlc-lite/skills/handoff-format)"`. This shows the merge-step template copy was not touched, and check.sh's identity check on the planner.md copy covers the other side.
