<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/agents/builder.md: rule 6 now has a sentence naming `hooks/block-repo-format.sh`. The phrase "files this step changed" is kept.
- plugins/sdlc-lite/scripts/check.sh: added `block-repo-format.sh` to the header comment's hook-selftest list.
- CLAUDE.md: added the hook to the Check everything `hook-selftest.sh` list, and added a new Layout bullet for `hooks/block-repo-format.sh`.
- .claude/agents/sdlc-lite-author.md: added the hook to the hook-selftest list in After-every-change item 1, and added one Hazards line.

## Checks
- The 8 non-guard acceptance greps, chained with `&&`: all passed (printed ALLOK).
- `git diff | grep -c '^+.*—'`: 0, so the added lines have no em dashes.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: rc=0. All selftests passed; shellcheck ok; plugin validate ok.

## Notes
- The fixtures sentence in the `block-background.sh` bullet in CLAUDE.md names no other hooks, so the conditional item 3c needed no edit.
- Step 1's files (the hook, hooks.json, hook-selftest.sh) were already in the tree before this step, uncommitted, and are left as they were.
- Nothing was committed.
