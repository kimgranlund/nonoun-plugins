<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/hooks/block-publish.sh`: after masking, a new INTERP regex looks for an interpreter command word with its inline-code flag and exits 1 so the hook falls back to scanning the raw command. The words are python and its versioned forms, node, perl and ruby, path-qualified forms included; other options may come before the flag, and flags count inside short-option clusters. The header comment now names the "interpreter inline code" rule.
- `plugins/sdlc-lite/scripts/hook-selftest.sh`: the `allows python3 -c string` fixture is replaced, and it becomes the `blocks python3 -c` fixture. Added blocking fixtures for `/usr/bin/python3 -c`, `node -e`, `node --eval`, `perl -e` and `ruby -e`, plus pass fixtures for a python3 script run, an interpreter with no publish phrase, and an interpreter word inside a quoted mention. The header comment is extended.
- `CLAUDE.md`: the block-publish.sh bullet now describes the interpreter inline-code raw scan.

## Checks
- All 11 blocking criteria (python3 -c, /usr/bin/python3 -u -c, `cd x && python -c`, node -e/--eval/-p/--print, perl -e/-E/-ne, ruby -e): each exits 2. Extra probe `python3 -Sc` also exits 2.
- Guards pass (exit 0): the script run, the commit-message mention, the grep mention, the interpreter code with SDLC_ROLE unset, and `python3 -c "print(1)"`. Extra probe `ruby -E utf-8 x.rb '...'` also exits 0.
- The 8 selftest-label greps, the `! grep` for the removed fixture, the header grep and the CLAUDE.md grep all pass.
- Em-dash diff guard: no added lines contain an em dash.
- `bash plugins/sdlc-lite/scripts/hook-selftest.sh`: hook selftest: PASS.
- `plugins/sdlc-lite/scripts/check.sh`: rc=0, all sections ok.

## Notes
- `.claude/agents/sdlc-lite-author.md` is unchanged, as the handoff said.
- A known limit: an option that takes its value as a separate word before the inline-code flag (for example `python3 -X dev -c`) stops the match, and that command keeps the masked scan.
