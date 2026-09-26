<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/agents/builder.md: added rules 6 (formatters, `--fix` linters, and code generators touch only the files this step changed) and 7 (stop only the PIDs you started, never kill by name pattern).
- plugins/sdlc-lite/scripts/check.py: new builder scope guard (`builder_scope_missing`) that fails when either phrase is missing, with a negative control per phrase that reports `check.py: builder scope guard negative control not flagged`.
- CLAUDE.md: new `hooks/block-pattern-kill.sh` Layout bullet after the block-background bullet, and the check.sh command line now names the hook in the hook-selftest list.
- .claude/agents/sdlc-lite-author.md: the check.sh line names the hook in the hook selftest list, and a new Hazards bullet covers the hook and both builder rules.

## Checks
- All seven `grep -q` criteria: passed.
- `python3 plugins/sdlc-lite/scripts/check.py "$PWD/plugins/sdlc-lite"`: exit 0 ("ok: 18 role levels, 8 agents checked").
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0. Run, hook, and hook-live-probe selftests passed, and so did shellcheck and plugin validate.
- Bite test: I copied the plugin plus CLAUDE.md into `$SDLC_TMP_WORKTREES/bite`, deleted the phrase `PIDs you started` from its builder.md, and ran that copy's check.py. It exited 1 with `FAIL agents/builder.md: builder scope rule missing "PIDs you started"`. I removed the copy afterwards.

## Notes
- The live `block-pattern-kill.sh` hook blocked one of my commands: a python heredoc whose text contained `pkill`. It fails closed on heredocs, as designed, so I made the edits with the Edit tool instead.
- I saved the check.sh output to `/tmp/cs.out`. It is a log file only; no worktree was created there.
