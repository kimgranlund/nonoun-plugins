<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/level-rubric/SKILL.md`: added a new section, `## Agent-tool spawns (outside run.sh)`. It is written as prose plus a bullet list, with no table.
- `plugins/sdlc-lite/agents/conductor.md`: added one bullet under "How you run roles", right after the levels bullet. It points to the rubric's "Agent-tool spawns" section.

## Checks
- `grep -q '^## Agent-tool spawns' skills/level-rubric/SKILL.md`: pass.
- Each of `haiku`, `sonnet`, `opus`, `fork`, `effort`, `7.13` and `1.82` was checked with `grep -q` inside the new section only: all found.
- `grep -q 'Agent-tool spawn' agents/conductor.md && grep -q 'level-rubric' agents/conductor.md`: pass.
- `! grep -q '—'` on both files: pass.
- `scripts/check.sh`: exit 0. The fanout, run and hook selftests passed, shellcheck passed, and plugin validate passed.
- `git diff --name-only`: shows the two plugin files above plus `.sdlc/0087-agent-spawn-seat-ladder/handoff.md`. No `scripts/` file is listed.

## Notes
The diff also lists `.sdlc/0087-agent-spawn-seat-ladder/handoff.md`. I did not touch that file; it was already changed before this step, probably by the planner or chain writing to it. `CLAUDE.md` and `.claude/agents/sdlc-lite-author.md` did not need edits.
