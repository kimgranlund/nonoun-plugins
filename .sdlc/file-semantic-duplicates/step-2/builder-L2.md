<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/skills/file/SKILL.md: step 3.1 now says the dry run lists each open ticket as `open T-NNNN <title> [<slug>]`. Step 3.2 marks follow-ups as `likely duplicate of T-NNNN` using the T-0047 vs T-0002 example. Steps 3.3 and 3.5 leave those out and `--skip` their indices, and step 3.6 reports them with the matching id.
- plugins/sdlc-lite/scripts/check.py: added docstring item 7 and a check that fails, naming `skills/file/SKILL.md`, when that file lacks `likely duplicate` or `open T-NNNN`.
- .claude/agents/sdlc-lite-author.md: the sync sentence now covers the dry run's `open T-NNNN` listing and the /file likely-duplicate step.

## Checks
- Criterion 1 (grep for both strings in SKILL.md): passed.
- Criterion 2 (check.py on a temp copy: ok first; after the sed it exits nonzero and names `skills/file/SKILL.md`): passed.
- Criterion 3 (grep for `likely duplicate` in sdlc-lite-author.md): passed.
- `bash plugins/sdlc-lite/scripts/check.sh`: rc=0. All selftests pass, and shellcheck and plugin validate are ok.

## Notes
None
