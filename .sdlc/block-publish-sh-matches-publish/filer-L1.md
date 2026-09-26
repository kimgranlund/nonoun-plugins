<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0077: block-publish.sh ignores publish phrases inside heredoc bodies and quoted strings

## PR body
### Summary
Inside a role run, `hooks/block-publish.sh` used to match publish phrases anywhere in a Bash command. That included heredoc bodies written to a file and quoted arguments to `sed`, `python3 -c` or `git commit -m`. In T-0065 this blocked a builder's plain edit and forced a temp-script workaround. The hook now matches against a masked copy of the command. Real publishes stay blocked, including publishes handed to a shell or evaluator. When the hook can't tell, it fails closed and scans the raw text.

### Changes
- `plugins/sdlc-lite/hooks/block-publish.sh`: a small `python3` masker, embedded in the hook, removes these before the pattern runs:
  - heredoc bodies (`<<WORD`, `<<'WORD'`, `<<"WORD"`, `<<-WORD`)
  - single-quoted and `$'...'` contents
  - double-quoted contents
  - comments

  Some text stays scannable:
  - A double-quoted string that holds `$(...)` or backticks is kept as raw text.
  - An unquoted heredoc body that holds `$(...)` or backticks also stays scannable. This goes beyond the plan: bash runs those substitutions.

  The hook falls back to a raw scan when:
  - python3 is missing or the masker errors
  - a quote, heredoc or `$(` is unterminated
  - `((` appears (also beyond the plan: arithmetic `<<` could be misread as a heredoc)
  - a shell or evaluator appears as a command word: `bash`, `sh`, `zsh`, `dash`, `ksh`, `eval`, `xargs`, `ssh`, `source`, `.`, `env`

  The `SDLC_ROLE` early exit, the `jq` extraction, the publish pattern and the exit contract (0 allow, 2 block) are unchanged.
- `plugins/sdlc-lite/scripts/hook-selftest.sh`: a `pj` JSON helper built on `jq -n --arg`, plus 5 allowed and 15 blocked cases (22 `run "$pub"` cases in total). Every publish phrase is built with `printf`.
- `CLAUDE.md`: the Layout bullet for the hook now describes the masking and the raw-scan fallback.

### Verification
Step 1 was built at L3 and verified at L2. Verdict: **pass**.
- **Allowed cases exit 0:**
  - a heredoc body with a push
  - `sed -i 's/x/git push/'`
  - `python3 -c 'print("gh pr create")'`
  - `git commit -m "doc: never git push"`
  - `grep -n "npm publish"`
- **Blocked cases exit 2:**
  - plain push and `cd x && git push`
  - `bash -c`, `sh -c`, `bash <<EOF`, `cat <<EOF | sh`
  - `echo "$(git push)"` and a backtick substitution
  - `eval`, `ssh host "..."`, `xargs`, `ls | (git push ...)`
  - `gh api -X POST`, `npm publish`
  - unterminated double quote, single quote and heredoc
- **Hook outside a role run:** with `SDLC_ROLE` unset, it still allows.
- **The new cases catch the old behavior:** the new selftest fails against the HEAD hook (`block-publish allows heredoc body: exit 2, want 0`).
- **Repo checks:** `hook-selftest.sh` PASS, `shellcheck` clean on both files, `scripts/check.sh` exit 0.
- **Extra probes by the verifier, all correct:** a push after a quoted string, a heredoc terminator, a comment, an `x=1` prefix or `&&`; an escaped quote; `$(echo "x"; git push)`; the hook run with python3 missing.
- **Scope:** the diff touches only the three target files plus `.sdlc/` artifacts. No commit was made.

### Known trade-offs
- `python3 -c 'import os; os.system("git push")'` and `node -e` were blocked before, only as a side effect. They are now allowed. The ticket's threat model (accidents, not an adversary) accepts this.
- A command containing `env`, `xargs`, `ssh` or `.` as a word still scans raw, so `env FOO=1 git commit -m "never git push"` stays blocked. This is fail closed on purpose.
- The `grep -c 'run "$pub"'` criterion only counts correctly under bash or `command grep`. The zsh `grep` wrapper (ugrep) reads the `$` as an anchor.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- `block-publish.sh` no longer blocks role-run commands that only write or quote a publish phrase (heredoc bodies, quoted arguments, comments). Real publishes stay blocked, including publishes fed to `bash`, `sh`, `eval`, `xargs` or `ssh`, or run inside a `$(...)`/backtick substitution. The hook fails closed to a raw scan when it can't parse the command. (T-0077)

## Follow-ups
- block-publish.sh no longer blocks a publish run from an interpreter one-liner such as `python3 -c 'os.system("git push")'` or `node -e`, which it blocked before T-0077 only as a side effect. Decide whether to add interpreter words to the raw-scan fallback.
