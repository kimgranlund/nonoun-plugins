<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/check.py`: added the conflict-marker guard behavior probe after the merge-step lint block, and updated docstring item 6.
- `CLAUDE.md`: changed the last sentence of the "A merge is a standard builder step" bullet so it names the conflict-marker guard run against a throwaway repo.

## Checks
- `plugins/sdlc-lite/scripts/check.sh`: exit 0. The real templates pass all three probe cases.
- Negative control with the old 192054c templates (whole-tree form): check.py output contains "conflict-marker guard" (grep exit 0).
- Negative control with an inverted guard (`|| git grep`): the output contains "conflict-marker guard" (grep exit 0).
- `grep -q "conflict-marker guard" CLAUDE.md`: exit 0.
- `sed -n 6,14p plugins/sdlc-lite/scripts/check.py | grep -q "conflict-marker guard"`: exit 0.

## Notes
- The probe runs its three cases in order. It resets main to the pre-merge commit (HEAD^1 after case 1) before case 2 and again before case 3.
- If a git command fails while setting up the probe repo, check.py records a `conflict-marker guard: probe setup failed` error.
- `.claude/agents/sdlc-lite-author.md` is unchanged. Nothing was committed.
