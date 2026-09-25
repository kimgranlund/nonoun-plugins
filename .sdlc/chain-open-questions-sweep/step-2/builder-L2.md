<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/skills/chain/SKILL.md`: added `AskUserQuestion` to `allowed-tools`. Added a `## 6. Close out` section between `## 5. File` and `## Report`. It runs the /open-questions flow, asks one AskUserQuestion round when interactive, lists open items as plain lines in the final report when unattended, and drops items already asked in /file's round.
- `plugins/sdlc-lite/agents/conductor.md`: added a route line under `## Route every ask` that sends "anything still open", loose-ends and close-out asks to `/sdlc-lite:open-questions`.
- `CLAUDE.md`: added `/open-questions` to the Understand skills list on line 33, noting that /chain runs it as its close-out, and added harness find-open-questions to the provenance list.

## Checks
- awk close-out criterion: exit 0
- `grep -q '^allowed-tools:.*AskUserQuestion' plugins/sdlc-lite/skills/chain/SKILL.md`: exit 0
- `grep -q '/sdlc-lite:open-questions' plugins/sdlc-lite/agents/conductor.md`: exit 0
- `grep -q '/open-questions' CLAUDE.md`: exit 0
- No em dash in the added lines (the `test -z` git diff check): exit 0
- `plugins/sdlc-lite/scripts/check.sh`: exit 0. All selftests passed, shellcheck ok, plugin validate ok.

## Notes
`git diff --stat` also shows changes to `.sdlc/chain-open-questions-sweep/handoff.md`. I did not make those changes; they were already in the tree before this step.
