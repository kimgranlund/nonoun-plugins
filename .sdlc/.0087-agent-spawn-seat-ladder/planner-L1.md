<!-- role=planner level=L1 model=sonnet effort=medium -->
## Goal
Add an "Agent-tool spawns" seat ladder to level-rubric and a pointer line in conductor.md, so in-session spawns outside run.sh always state a fixed `model`.

## Step 1: Add seat ladder section and conductor pointer
level: L2
### Do
In `plugins/sdlc-lite/skills/level-rubric/SKILL.md`, append a section headed `## Agent-tool spawns (outside run.sh)`. Write it as prose and a bullet list, not a table. `scripts/check.py` parses level-table rows in this file, and a table would risk a false level-sync failure. The section must cover these points:
- It applies to any in-session Agent-tool spawn that has no run.sh role: `general-purpose`, `Explore`, `Plan`, or any spawn naming no agent file.
- Every such spawn states `model` explicitly, because an unset `model` inherits the session's top model.
- The seat ladder by class:
  - Mechanical or gather-only work uses `haiku`.
  - Search, review, and routine coding use `sonnet`, the default.
  - Judgment-heavy synthesis uses `opus`.
- A plain Agent spawn cannot set effort.
- A `context: fork` or `subagent_type: "fork"` spawn always prices at the parent model, so it is never a step-down.
- Work that has a run.sh role goes through run.sh, not the Agent tool.
- One evidence line: 62 inherited general-purpose builders cost $7.13 each, against $1.82 for an L3 run.sh builder.

In `plugins/sdlc-lite/agents/conductor.md`, add one bullet under "How you run roles", after the levels bullet. It says: every Agent-tool spawn outside run.sh states `model` per the "Agent-tool spawns" section of the level-rubric skill.

Use no em dashes in either file. Change nothing else. Leave the CLAUDE.md `skills/level-rubric` layout line and `.claude/agents/sdlc-lite-author.md` as they are unless they describe level-rubric contents this section makes stale. They currently describe only the level tables, so they should not need edits.

### Acceptance criteria
- `grep -q '^## Agent-tool spawns' skills/level-rubric/SKILL.md`, run from `plugins/sdlc-lite`. Red now: the section is missing.
- `grep -c 'haiku' skills/level-rubric/SKILL.md` prints at least 1, and the section also names `sonnet`, `opus`, `fork`, `effort`, `7.13`, and `1.82`. Each is checked with `grep -q` inside the section. Red now: none of these terms are in the file.
- `grep -q 'Agent-tool spawn' agents/conductor.md && grep -q 'level-rubric' agents/conductor.md`, run from `plugins/sdlc-lite`. Red now: the conductor has no such line.
- `! grep -q '—' skills/level-rubric/SKILL.md agents/conductor.md`, run from `plugins/sdlc-lite`. (guard) Green now: neither file has an em dash.
- `scripts/check.sh` passes, run from `plugins/sdlc-lite`, with the expected `claude plugin validate` warning about CLAUDE.md. (guard) The level-table sync between level-rubric, run.sh, and CLAUDE.md still agrees.
- `git diff --name-only` lists only `plugins/sdlc-lite/skills/level-rubric/SKILL.md`, `plugins/sdlc-lite/agents/conductor.md`, and optionally `CLAUDE.md` and `.claude/agents/sdlc-lite-author.md`. It lists no `scripts/` file.

## Risks
- A table or a `| L1 |` style row in the new section could trip the `check.py` level-table parser. The Do says to use bullets.
- The two optional stale-record files might need a small edit if the builder judges their level-rubric description stale. The builder should record that decision in its notes.
