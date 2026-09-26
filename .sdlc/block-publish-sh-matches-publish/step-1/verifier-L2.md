<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- The 5 allowed cases exit 0 (heredoc body, `sed`, `python3 -c`, `git commit -m`, `grep`): pass. Evidence: I built each command with `printf` and `jq -n --arg` and ran it with `SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-publish.sh`. All five exited 0.
- Guard cases exit 2 (plain push, `cd x && git push`, `bash -c`, `sh -c`, `bash <<EOF`, `echo "$(...)"`, `eval`, `gh api -X POST`, `npm publish`, `cat <<EOF | sh`, `ssh host "..."`, `xargs`, `ls | (git push)`): pass. Evidence: each of the 13 exited 2. A backtick substitution inside double quotes exited 2, and so did unterminated double-quote, single-quote and heredoc cases (fail closed).
- Guard: `git push` with `SDLC_ROLE` unset: pass. Evidence: `env -u SDLC_ROLE` run exited 0.
- `run "$pub"` count is at least 20: pass. Evidence: `bash -c 'test "$(grep -c ...)" -ge 20'` gave rc=0, count 22. Under this session's zsh, `grep` is a wrapper that returns 0 for that pattern, so the count only holds under bash. The builder flagged this and it holds up.
- The new selftest fails against the base hook: pass. Evidence: I copied the HEAD hook and the new selftest into a temp dir. The run printed `hook selftest: FAIL: block-publish allows heredoc body: exit 2, want 0`, exit 1. The check can go red. The variable that bites is the allowed-direction masking cases, which the base hook blocks.
- CLAUDE.md line contains `heredoc`: pass. Evidence: `grep -n 'hooks/block-publish.sh' CLAUDE.md | grep -qi heredoc` gave rc=0. The diff shows the extended Layout bullet.
- Guard `hook-selftest.sh`: pass. Evidence: it printed `hook selftest: PASS`.
- Guard `shellcheck` on both files: pass. Evidence: no output, exit 0.
- Guard `check.sh`: pass. Evidence: exit 0, ending `ok: shellcheck` and `ok: plugin validate`. It also ran the tickets, board, steps, fanout, run and hook selftests.
- Observable: diff stat is scoped and no commit was made: pass. Evidence: `git status` shows `M` only on `CLAUDE.md`, `block-publish.sh`, `hook-selftest.sh` and the ticket `handoff.md`, plus untracked `.sdlc/` artifacts. HEAD is still `d787377`. The `handoff.md` change is planner output under `.sdlc/`, so it is not a project-file change.
- Extra adversarial probes I ran, all correct:
  - Exit 2 for a push after a quoted string and `;`, after a heredoc terminator, after a comment, after an `x=1` prefix, after `git commit && …`, and inside an unquoted heredoc `$(...)`.
  - Exit 2 for an escaped quote before a push, and for `$(echo "x"; git push)`.
  - Exit 0 for text that is genuinely inside quotes or a heredoc body, which is correct.

## Out of scope changes
None. `.sdlc/block-publish-sh-matches-publish/handoff.md` is modified, but the step allows `.sdlc/` artifacts. Its diff is the Goal, Intent and Constraints text, so it is planner output and not the builder's work. `.claude/agents/sdlc-lite-author.md` is unchanged, as instructed.

## For the next attempt
None
