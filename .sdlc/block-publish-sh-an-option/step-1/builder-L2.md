<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/hooks/block-publish.sh: I added a per-interpreter `VALOPTS` list of options that take a separate value word, plus an `opts(name)` builder. These replace the single `OPTS` regex. I also extended the header comment, which now cites `python3 -X dev -c`, `node --require x -e` and `perl -I lib -e`.
- plugins/sdlc-lite/scripts/hook-selftest.sh: added 5 blocked fixtures (`python3 -X dev -c`, `python3 -W ignore -c`, `node --require x -e`, `perl -I lib -e`, `ruby -I lib -e`) and 2 allowed fixtures (`python3 -X dev scripts/check.py`, `python3 scripts/check.py -c`).
- CLAUDE.md: the block-publish.sh bullet now says value-taking options before the inline-code flag still count, citing `python3 -X dev -c`.

## Checks
- The 5 blocked-case criteria each exited 2 (pass).
- The 2 allowed guard criteria each exited 0 (pass).
- Extra probes: `python3 -Xdev -c` exited 2, `node --require=x -e` exited 2, and `ruby -E utf-8 x.rb 'git push'` exited 0.
- All 4 grep criteria passed (`-X dev` and `--require` in selftest, `-X dev` in the hook, `-X dev` on the CLAUDE.md block-publish line).
- `bash plugins/sdlc-lite/scripts/hook-selftest.sh`: exit 0, PASS.
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0; all selftests, shellcheck and plugin validate passed.

## Notes
- The node list covers the options the handoff names plus more `--flag value` options taken from Node's option set. I did not run `node --help` to confirm the list; the list is easy to extend.
- A value-taking option's value can be any word, so `python3 -W scripts/x.py -c ...` would be scanned raw. That is the conservative direction, since it blocks rather than allows.
- `.claude/agents/sdlc-lite-author.md` is unchanged, as the handoff instructs.
