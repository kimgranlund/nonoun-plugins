<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/skills/checking-rules/SKILL.md: new file. A trimmed port of harness checking-rules, reworded for a verifier checking a builder's step.
- plugins/sdlc-lite/agents/verifier.md: added `checking-rules` to `skills:` and one sentence to the "A criterion with no evidence fails." paragraph.
- CLAUDE.md: the "Agent skills" bullet now lists both verifier skills.
- plugins/sdlc-lite/.claude-plugin/plugin.json: version bumped from 0.8.3 to 0.8.4.

## Checks
All run from `plugins/sdlc-lite/`:
- The dry-run system prompt file contains both `# Skill: checks-that-bite` and `# Skill: checking-rules`: pass
- `name: checking-rules` line: pass
- No banned words: pass
- No em dash: pass
- No bold inline labels: pass
- Steelman, evidentiary symmetry, runtime over claim, and the three section headings are all present: pass
- No "invariant's unit" or "soft size budget": pass
- verifier.md has the skill line and at least 2 mentions: pass
- CLAUDE.md verifier line matches the required pattern: pass
- Version is 0.8.4: pass
- (guard) verifier.md still has exactly its four output headings: pass
- (guard) `git diff --quiet` on run.sh, level-rubric, checks-that-bite and sdlc-lite-author.md: pass
- (guard) `scripts/check.sh`: exit 0
- The criterion that needs a reviewer to read the file is left for the verifier.

## Notes
- `.sdlc/0084-port-checking-rules/handoff.md` already had changes before this build. I did not touch it.
- Nothing was committed.
