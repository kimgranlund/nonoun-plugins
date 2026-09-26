<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0097: block-publish.sh raw-scans interpreter inline code

## PR body
## Summary
Since T-0077, `hooks/block-publish.sh` no longer blocked a publish command run through an interpreter one-liner such as `python3 -c 'os.system("git push")'` or `node -e`. Before T-0077 it blocked these only as a side effect. This change extends the existing fail-closed raw-scan rule, which already covers shell and evaluator words, to interpreter inline code. A plain `python3 script.py` keeps the masked scan, and quoted mentions still pass.

## Changes
- `plugins/sdlc-lite/hooks/block-publish.sh`:
  - After masking, a new regex looks for an interpreter command word with an inline-code flag. If it finds one, the hook scans the raw command.
  - The words are python and its versioned forms, node, perl and ruby, including path-qualified forms like `/usr/bin/python3`.
  - The flags are python `-c`, node `-e`/`-p`/`--eval`/`--print`, and perl `-e`/`-E`. Ruby `-e` counts, but ruby `-E` is the encoding flag and does not.
  - Other options may come before the flag, and the flag counts inside short-option clusters such as `perl -ne` and `python3 -Sc`.
  - The header comment names the rule.
- `plugins/sdlc-lite/scripts/hook-selftest.sh`:
  - Added blocking fixtures for `python3 -c`, `/usr/bin/python3 -c`, `node -e`, `node --eval`, `perl -e` and `ruby -e`.
  - Added pass fixtures for a python3 script run, an interpreter with no publish phrase, and an interpreter word inside a quoted mention.
  - The header comment is extended.
- `CLAUDE.md`: the `hooks/block-publish.sh` bullet describes the new rule.
- Deliberate exception to "existing fixtures keep their outcomes": the fixture `allows python3 -c string` (`python3 -c 'print("gh pr create")'`, expected pass) contradicts the ticket's decision, because no static check can tell `print(...)` from `os.system(...)`. It became the `blocks python3 -c` fixture. Every other fixture keeps its outcome.
- `.claude/agents/sdlc-lite-author.md` is unchanged. It does not describe the evaluator list.

## Verification
The verifier (L1) passed the step.
- Blocking commands returned exit 2 under `SDLC_ROLE=builder`:
  - `python3 -c`, `/usr/bin/python3 -u -c`, `cd x && python -c`
  - node `-e`, `--eval`, `-p`, `--print`
  - perl `-e`, `-E`, `-ne`
  - ruby `-e`
  - `python3 -Sc` (extra probe)
- Guards returned exit 0:
  - a python3 script run with a publish phrase argument
  - a commit message mentioning `python3 -c`
  - a grep mention
  - interpreter code with `SDLC_ROLE` unset
  - `python3 -c "print(1)"`
  - `ruby -E utf-8 x.rb '...'`
- Negative control: at HEAD in a throwaway worktree, the `python3 -c` case returned exit 0, so the check can go red.
- The selftest label greps and the header and CLAUDE.md greps pass. No em dashes appear in added lines.
- `bash plugins/sdlc-lite/scripts/hook-selftest.sh` printed `hook selftest: PASS`, and `plugins/sdlc-lite/scripts/check.sh` passed with all sections ok, including shellcheck and plugin validate.

## Changelog entry
- `hooks/block-publish.sh` again blocks publish commands run through interpreter inline code (python `-c`, node `-e`/`-p`/`--eval`/`--print`, perl `-e`/`-E`, ruby `-e`, path-qualified too) inside a role run by scanning the raw command. Plain script runs and quoted mentions still pass. The hook selftest and CLAUDE.md are updated.

## Follow-ups
- block-publish.sh: an option that takes a separate value word before the inline-code flag (for example `python3 -X dev -c '...git push...'`) stops the interpreter match, so that command keeps the masked scan and a publish call can slip through
