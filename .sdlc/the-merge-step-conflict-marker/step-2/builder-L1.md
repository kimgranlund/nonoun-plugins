<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/agents/planner.md: added the limitation paragraph after the "Criterion 1 above still applies" paragraph in `## Merge steps`.
- plugins/sdlc-lite/skills/handoff-format/SKILL.md: added the same limitation paragraph after the merge-step fenced block in `### Merge step`.
- CLAUDE.md: added a clause after the diff-tree clause in the merge-step decision.
- .claude/agents/sdlc-lite-author.md: the hazard line now lists the seven probe cases and says a kept marker passes by design.

## Checks
- `grep -q "textually identical to a parent line"` passes on all four files.
- `grep -q "aligned kept marker" .claude/agents/sdlc-lite-author.md` passes.
- Both merge-step block diff guards (planner.md and SKILL.md against HEAD) showed no difference.
- The em-dash grep over the four files found none.
- `bash plugins/sdlc-lite/scripts/check.sh` finished with every selftest, shellcheck and plugin validate green. I read only the tail of the output.

## Notes
- `check.py` already showed a diff in the tree before this step. I did not touch it. It is presumably step 1's probe change.
