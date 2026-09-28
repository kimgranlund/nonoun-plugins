<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/hooks/block-pattern-kill.sh`: widened the cheap exit so a command holding `kill` together with `ps`, or with an assignment and a `$`, goes on to the full scan. Added two strict patterns. The first is `ps` piped to `xargs kill`, alongside the existing `pgrep` form. The second is `kill $(ps ...)` and its backtick form. Added a `held_kill` check: it pulls the names from `NAME=<pkill|killall|kill>` assignments (a path to one of those also counts), then blocks when `$NAME` or `${NAME}` is used as a command. The masker now keeps a double-quoted `"$VAR"` or `"${VAR}"`, so `k=kill; "$k" x` is caught too. Added matching loose raw-text patterns. Updated the header's Blocked and Allowed lists, the masking note, and the `block()` message, which still contains `PID` and the role.
- `plugins/sdlc-lite/scripts/hook-selftest.sh`: added 5 block fixtures (two `ps | ... | xargs kill` forms, one with `-9`; `kill $(ps ...)`; `p=<pkill>; $p x`; `k=<killall>; ${k} node`) and 4 allow fixtures (`kill %1`, `kill $(cat pidfile)`, `echo $! | xargs kill`, `cmd=ls; $cmd -la`). Updated the header comment.
- `CLAUDE.md`: the `hooks/block-pattern-kill.sh` Layout line now names the ps-fed forms, the variable-held kill word, and the new allowed forms.
- `.claude/agents/sdlc-lite-author.md`: the matching hazard line now names the ps-fed forms and the variable-held kill word.

## Checks
- Ran all 24 command criteria in a loop with `bash -c "<criterion>"`: every one exited 0. That covers:
  - the 5 block criteria (each ends in `test $? -eq 2`)
  - the 7 hook guards (6 allowed commands under `SDLC_ROLE=builder`, plus the pkill fixture with `SDLC_ROLE` unset)
  - `bash plugins/sdlc-lite/scripts/hook-selftest.sh`
  - `plugins/sdlc-lite/scripts/check.sh`
  - the 10 grep and head criteria
- Fed each of the 24 criterion strings to the hook as a verifier's own Bash command (`SDLC_ROLE=verifier`): all exited 0, so the hook blocks none of them.
- Ran extra probes through the hook:
  - Blocked (exit 2): `k=killall; "$k" node`, `p=/usr/bin/pkill;$p x`, and a `bash -c '...'` form of both new patterns (the raw-text scan).
  - Allowed (exit 0): `pid=$!; kill "$pid"; ps aux`.
- `shellcheck` on both changed scripts: clean. The first version drew an info-level SC2013; I rewrote the loop as `while read`, then reran all of the checks above and they stayed green.
- Observable `git diff --stat HEAD -- plugins/sdlc-lite/hooks/`: only `block-pattern-kill.sh` changed.

## Notes
- `.sdlc/0111-pattern-kill-hook-misses-forms/handoff.md` was already modified before this step started; I did not change it.
- Assigning plain `kill` to a variable and running it (`k=kill; $k 1234`) is also blocked, as the handoff specifies, even when the arguments are PIDs.
- The name check does not look at order, so `$k x; k=kill` is blocked too. That is a harmless false positive.
- A kill word assigned through a substitution (`p=$(command -v pkill); $p x`) is not caught. It was out of scope.
- Heredoc edits in a role run hit the hook's fail-closed raw scan whenever the heredoc body mentions these words, so I used the Edit tool for those edits.
