<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/skills/file/SKILL.md: step 4 now asks one multiSelect AskUserQuestion with "at most 4 options" (commit, push, PR, changelog edit). The GitHub-issues item is out of that list. Follow-ups get a separate second question with at least 2 options, asked only when the user wants them published. The rest of step 4 is unchanged.
- plugins/sdlc-lite/scripts/check.py: new guard after the `/file` word check. It fails when SKILL.md lacks "at most 4 options", or when step 4's option list names issues or still says "optional item".

## Checks
- `grep -q "at most 4 options" skills/file/SKILL.md`: pass
- `grep -q "at most 4 options" scripts/check.py`: pass
- `python3 scripts/check.py`: exit 0. Against HEAD's pre-fix SKILL.md it exits 1 with two FAIL lines naming skills/file/SKILL.md (missing phrase, and issues listed among the publish options).
- (guard) block-publish.sh and "Never publish on your own" greps: pass
- (guard) `scripts/check.sh` in a `git worktree add /tmp/fpq-base HEAD` copy and in this tree: both exit 0, and `diff` of the two outputs is empty. The temp worktree has been removed.

## Notes
None
