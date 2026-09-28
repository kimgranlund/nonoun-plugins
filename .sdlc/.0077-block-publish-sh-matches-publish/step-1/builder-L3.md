<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/hooks/block-publish.sh`: an embedded `python3` masker, run through `python3 -c`, builds the masked copy. It removes heredoc bodies (`<<WORD`, `<<'WORD'`, `<<"WORD"`, `<<-WORD`), single-quoted and `$'...'` contents, double-quoted contents, and comments. A double-quoted string that holds a `$(...)` or backtick substitution is kept as raw text. The hook falls back to scanning the raw command when python3 is missing, the masker errors, a quote, heredoc or `$(` is unterminated, `((` appears, or one of the spec's shell or evaluator words appears as a command word. The early exit, the `jq` extraction, the pattern and the exit contract are unchanged. The header comment is updated.
- `plugins/sdlc-lite/scripts/hook-selftest.sh`: added a `pj` JSON helper built on `jq -n --arg c`. Added 5 allowed and 15 blocked `run "$pub"` cases (22 total), with every publish phrase built by `printf`. Header comment updated.
- `CLAUDE.md`: the Layout bullet for `hooks/block-publish.sh` now says the hook matches after masking heredoc bodies, quoted string contents and comments, and scans the raw text when a shell or evaluator is present or parsing fails.

## Checks
- Ran all 25 acceptance-criterion commands with `bash -c` from the worktree root: all exit 0. That covers the 5 allowed cases, the 13 blocked guards plus the xargs, subshell and no-role guards, the `run "$pub"` count (22), the check that the new selftest fails against the HEAD hook, the CLAUDE.md `heredoc` grep, `hook-selftest.sh` (PASS), `shellcheck` on both files (clean), and `check.sh` (exit 0).
- Ran my own extra cases, all as expected:
  - Blocked: an unquoted heredoc body containing `$(git <push>)`; a publish after a heredoc terminator; nested quotes inside `$(...)` inside double quotes; `/bin/sh -c`; a comment containing an apostrophe; `$'a\'b'` followed by a publish line; the hook run with no python3 on PATH (exit 2, raw scan).
  - Allowed: the same `$(...)` body under a quoted `<<"EOF"`; a `<<-EOF` body.
- Observable: `git diff --stat HEAD` shows only the three target files plus `.sdlc/` artifacts. HEAD is still `d787377`; no commit made.

## Notes
- One addition beyond the spec: an unquoted heredoc body (`<<EOF`) that holds a `$(...)` or backtick substitution stays scannable, the same rule the spec gives for double quotes. Bash runs those substitutions, and removing them would have let a real publish through. Quoted heredocs are removed completely.
- One more fail-closed rule beyond the spec: a command containing `((` scans raw, because `x<<2` inside `$(( ))` would otherwise be read as a heredoc.
- The criterion ``test "$(grep -c 'run "$pub"' ...)" -ge 20`` passes under bash and `command grep` (count 22). It fails in this session's zsh, where `grep` is a wrapper around ugrep that reads the `$` in the middle of the pattern as an anchor (count 0). The verifier should run the criteria with bash or `command grep`.
- Known gaps, not fixed because they are out of scope: a publish run through a variable used as the command (`c="git <push>"; $c`), through `python3 -c 'os.system(...)'`, or through other interpreters (`fish`, `su -c`, `git -c alias`) is not detected. These were not detected before this change either.
- `.sdlc/0077-block-publish-sh-matches-publish/handoff.md` was already modified before this build; I did not touch it.
