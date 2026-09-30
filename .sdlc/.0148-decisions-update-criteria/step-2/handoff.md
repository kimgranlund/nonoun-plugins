## Task goal
A conductor decision that widens a step's scope edits the scope guard the criteria read, so the next builder does not block on the old guard.

## Step 2: Document the widen route in the conductor, /chain, and role contracts
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Document the route. Each doc names `steps.py widen` literally.

- **`plugins/sdlc-lite/skills/chain/SKILL.md`**:
  - Add item 9, "Scope widening". Trigger: a builder blocked only because a file it needs sits outside the step's scope criterion, when the conductor decides the file serves the task goal. Interactive runs confirm through AskUserQuestion. The decision is never recorded as prose alone.
  - Command: run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py widen .sdlc/<task>/step-<n> <path>...`.
  - On exit 0: append `scope widened: step <n>: <its stdout line>` to the task handoff's `## Plan review`. Then run the builder at the blocked builder's level. That run is not a bump and gets no `## Previous attempt`. The widened block does not count toward the rubric's blocked-builder bump.
  - On exit 1: append a `scope decision: step <n>: <paths>` line and the stderr to `## Plan review`, then take the 4.2 replan path.
  - State why: the conductor names only paths and the script rewrites the check, so "never edit the criterion by hand" and "whoever writes the work never sets its check" both hold.
  - Reference item 9 from item 2 (builder blocked) as its one exception.
- **`plugins/sdlc-lite/agents/conductor.md`**: add the same route to the escalation bullet.
- **`plugins/sdlc-lite/skills/handoff-format/SKILL.md`**:
  - Add the `scope widened:` and `scope decision:` entries to `## Plan review`.
  - Add the step handoff's `## Scope widened` section, which `steps.py widen` writes.
- **`plugins/sdlc-lite/skills/level-rubric/SKILL.md`**: in the bump paragraph, a block resolved by `steps.py widen` never counts toward a bump.
- **`plugins/sdlc-lite/agents/planner.md`** rule 9: a `scope decision:` entry in `## Plan review` names paths the conductor allowed for that step. The replan widens that step's scope criterion to hold them. This is replan-time only. Do not change the plan-time scope-guard rules.
- **`plugins/sdlc-lite/scripts/check.py`**: add a `PLAN_DEFECT_DOCS` entry `'steps.py widen': ('agents/conductor.md', 'skills/chain/SKILL.md', 'skills/handoff-format/SKILL.md', 'skills/level-rubric/SKILL.md', 'scripts/steps.py')`.
- **Codex agents**: then run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` to regenerate them. Never hand-edit the TOML files.
### Acceptance criteria
- `grep -qF 'steps.py widen' plugins/sdlc-lite/agents/conductor.md`
- `grep -qF 'steps.py widen' plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -qF 'steps.py widen' plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- `grep -qF 'steps.py widen' plugins/sdlc-lite/skills/level-rubric/SKILL.md`
- `grep -qF 'scope decision:' plugins/sdlc-lite/agents/planner.md`
- `grep -qF 'scope decision:' plugins/sdlc-lite/skills/chain/SKILL.md`
- `grep -qF "'steps.py widen'" plugins/sdlc-lite/scripts/check.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
