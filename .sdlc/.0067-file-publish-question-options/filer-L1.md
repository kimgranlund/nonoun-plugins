<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0067: Keep the /file publish question within AskUserQuestion's 4-option limit

## PR body
### Summary
During the T-0047 run, the `/file` step 4 publish question failed twice with `Invalid tool parameters`. The first call had 5 options and the second had 1. The skill now names at most 4 options on that question, and a check.py guard fails if that limit goes away.

### Changes
- `plugins/sdlc-lite/skills/file/SKILL.md`: step 4 now asks one multiSelect `AskUserQuestion` with "at most 4 options": commit, push, PR, and changelog edit. The GitHub-issues item is no longer in that list. If the user wants follow-ups published as issues, a separate second question asks about them, and it must have at least 2 options. The rest of step 4 is unchanged, including the `hooks/block-publish.sh` note, the numbered-mode folder note, and "Never publish on your own".
- `plugins/sdlc-lite/scripts/check.py`: a new guard sits next to the existing `/file` word check. It fails when SKILL.md lacks "at most 4 options", or when step 4's option list still names issues or says "optional item".

### Verification
The verifier (L1) passed every criterion.
- The `grep` checks for "at most 4 options" pass in SKILL.md and in check.py (check.py:168).
- `python3 scripts/check.py` exits 0 with the fix. In a throwaway worktree at HEAD with the new check.py copied in, it exits 1 with two FAIL lines on `skills/file/SKILL.md`: the missing phrase, and issues listed among the publish options. So the guard fails on the old text and passes on the fix.
- Guard: `block-publish.sh` and "Never publish on your own" are still in SKILL.md.
- Guard: `scripts/check.sh` exits 0 on this tree, with all selftests, shellcheck, and plugin validate ok. Diffed against a HEAD run, the only differences are the two new guard lines.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Fixed: `/file` step 4 now asks its publish question with at most 4 options (commit, push, PR, changelog edit), so `AskUserQuestion` accepts it on the first call. GitHub issues for follow-ups are offered in a separate question. `check.py` enforces the limit. (T-0067)

## Follow-ups
- `/file` step 3.3 follow-ups multiSelect can exceed AskUserQuestion's 4-option limit when a filer file lists more than 4 follow-ups; cap or batch it and add a check.py guard.
