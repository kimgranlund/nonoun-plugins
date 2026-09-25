<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0087: Seat ladder for conductor Agent-tool spawns outside run.sh, in level-rubric

## PR body
### Summary
When the conductor spawns an agent with the Agent tool instead of run.sh and leaves `model` unset, the spawn inherits the session's top model. One peer project spawned 62 general-purpose builders this way. They cost $7.13 each, against $1.82 for an L3 run.sh builder. This PR adds a seat ladder to the level-rubric skill so every such spawn states its `model`, and adds a pointer to it in the conductor.

### Changes
- `plugins/sdlc-lite/skills/level-rubric/SKILL.md`: new section `## Agent-tool spawns (outside run.sh)`, written as prose and bullets with no table so the `check.py` level-table parser is not affected. It covers:
  - Scope: `general-purpose`, `Explore`, `Plan`, and any spawn that names no agent file.
  - `model` is always stated, because an unset spawn inherits the top model.
  - Seat ladder: `haiku` for mechanical or gather-only work, `sonnet` (the default) for search, review, and routine coding, `opus` for judgment-heavy synthesis.
  - A plain Agent spawn cannot set effort.
  - A `context: fork` or `subagent_type: "fork"` spawn always prices at the parent model, so it is never a step-down.
  - Work that has a run.sh role goes through run.sh.
  - The $7.13 vs $1.82 evidence line.
- `plugins/sdlc-lite/agents/conductor.md`: one bullet under "How you run roles", after the levels bullet: every Agent-tool spawn outside run.sh states `model` per the level-rubric "Agent-tool spawns" section.
- `CLAUDE.md` and `.claude/agents/sdlc-lite-author.md` are unchanged. They describe only the level tables, which this PR leaves alone.

### Verification
There was one step. The builder ran at L2 and the verifier at L1. Verdict: pass.
- The section heading exists. The diff shows it as a new line, so the check was red before the change.
- `haiku`, `sonnet`, `opus`, `fork`, `effort`, `7.13`, and `1.82` each matched a `grep -q` limited to the new section, and every match is on an added line.
- The conductor has the new bullet and it points to level-rubric.
- Neither file contains an em dash.
- `scripts/check.sh` exited 0 in the builder run. The verifier ran it too and saw the order, fanout, run, and hook selftests pass, plus shellcheck and plugin validate. It read only the last 15 lines of output, and nothing there showed a failure.
- `git diff --name-only` shows only the two plugin files plus the task's own `.sdlc` handoff. No `scripts/` file changed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- level-rubric has a new "Agent-tool spawns" seat ladder, and the conductor points to it. Every in-session Agent-tool spawn outside run.sh now states `model` explicitly (`haiku` for mechanical or gather-only work, `sonnet` by default, `opus` for judgment-heavy synthesis) instead of inheriting the session's top model. (T-0087)

## Follow-ups
None
