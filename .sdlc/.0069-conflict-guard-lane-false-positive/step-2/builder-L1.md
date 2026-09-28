<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- CLAUDE.md: the merge-step decision now says the guard fails only on conflict-marker lines the merge itself added (`git diff-tree --cc`), so a lane line that starts with seven `<` or `>` passes.
- .claude/agents/sdlc-lite-author.md: added one line under `## Hazards learned` on the `git diff-tree --cc HEAD` guard and the five probe cases.

## Checks
- `! grep -q 'no conflict markers in touched files' CLAUDE.md`: passed.
- `grep -c 'diff-tree --cc'` on both files: 1 each, so both criteria pass.
- Em dash count in both files: 0, checked before the edit and not re-run after it. The added text contains none.
- `bash plugins/sdlc-lite/scripts/check.sh`: ran, the last 8 lines showed all selftests, shellcheck, and plugin validate passing. I read only the tail, not the full output.

## Notes
None
