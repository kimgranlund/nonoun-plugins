<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0111: Block ps-fed kills and variable-held kill words in block-pattern-kill hook

## PR body
### Summary
Inside a role run, `hooks/block-pattern-kill.sh` now also blocks two pattern-kill forms that used to pass. The first is a `ps` listing piped through filters into `xargs kill`, or fed to `kill $(ps ...)`. The second is a kill word held in a shell variable and then run (`p=pkill; $p x`). Killing a saved PID is still allowed.

### Changes
- `plugins/sdlc-lite/hooks/block-pattern-kill.sh`:
  - The cheap exit now lets through commands that hold `kill` with `ps`, or an assignment with a `$` expansion.
  - Two new strict patterns cover `ps ... | xargs kill` and `kill $(ps ...)` (backtick form too).
  - A new `held_kill` check collects names from `NAME=<pkill|killall|kill>` assignments (a path to one of those counts) and blocks when `$NAME` or `${NAME}` is used as a command.
  - The masker keeps a double-quoted `"$VAR"`, so `k=kill; "$k" x` is caught.
  - The loose raw-text scan has matching patterns.
  - The header comment and the `block()` message are updated. The message still names the PID and the role.
- `plugins/sdlc-lite/scripts/hook-selftest.sh`: 5 new block fixtures (both `ps` pipelines including `-9`, `kill $(ps ...)`, `p=pkill; $p x`, `k=killall; ${k} node`) and 4 new allow fixtures (`kill %1`, `kill $(cat pidfile)`, `echo $! | xargs kill`, `cmd=ls; $cmd -la`). Header comment updated.
- `CLAUDE.md` and `.claude/agents/sdlc-lite-author.md`: the hook's line now names the ps-fed forms and the variable-held kill word.
- `block-publish.sh` and `block-background.sh` are untouched.

### How each was verified
- Verifier L2 (Sonnet high) returned pass, with no out-of-scope changes.
- The 5 block criteria exit 2 under `SDLC_ROLE=builder`. For three of them the verifier also ran the same command at HEAD in a throwaway worktree and got exit 0, so the checks are red before the change.
- The 6 allowed forms (`kill $(cat pidfile)`, `kill $pid`, `kill %1`, `echo $! | xargs kill`, `cmd=ls; $cmd -la`, `pid=$!; kill "$pid"`) exit 0. `p=pkill; $p x` exits 0 with `SDLC_ROLE` unset.
- `bash plugins/sdlc-lite/scripts/hook-selftest.sh` prints `hook selftest: PASS`.
- `plugins/sdlc-lite/scripts/check.sh` exits 0, including shellcheck and plugin validate.
- The builder also fed all 24 criterion commands to the hook as a verifier's own Bash calls, and none was blocked. It ran extra probes: `k=killall; "$k" node`, `p=/usr/bin/pkill;$p x`, and `bash -c '...'` forms were blocked, and `pid=$!; kill "$pid"; ps aux` was allowed.
- Grep checks confirm the new fixtures, the header comment, and the CLAUDE.md and author-agent lines. `git diff --stat HEAD` shows only `block-pattern-kill.sh` changed under `hooks/`.

Known limits (from the builder notes):
- `p=$(command -v pkill); $p x` is not caught (out of scope).
- The variable check ignores order, so `$k x; k=kill` is also blocked.
- `k=kill; $k 1234` is blocked even with PID arguments, as the handoff specifies.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `block-pattern-kill.sh` now also blocks `ps` output piped into `xargs kill`, `kill $(ps ...)`, and a kill word held in a shell variable (`p=pkill; $p x`) inside role runs. Killing a saved PID (`kill $pid`, `kill %1`, `kill $(cat pidfile)`, `echo $! | xargs kill`) is still allowed.

## Follow-ups
- Pattern-kill hook does not catch a kill word assigned through a substitution (`p=$(command -v pkill); $p x`), so it still passes inside role runs.
