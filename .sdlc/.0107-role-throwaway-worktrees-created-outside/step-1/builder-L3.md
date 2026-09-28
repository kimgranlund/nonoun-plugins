<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/hooks/block-stray-worktree.sh`: new executable PreToolUse(Bash) hook. Inside a role run it checks every `git [global opts] worktree add` and denies (exit 2) when:
  - the command uses `-b`, `-B`, or `--orphan`
  - `SDLC_TMP_WORKTREES` is unset or empty
  - the path is not strictly under the prefix, or it has a `..` segment
  - the path cannot be resolved (it holds `$`, a glob, or a leading `~`)
  - the path is relative and comes after a `cd` or `pushd`
  - there is neither `--detach`/`-d` nor a commit-ish

  The deny message names the role and gives the allowed form. On a heredoc, a shell or evaluator word, an unterminated quote, or a python3 or parser failure it scans the raw text and denies any `git ... worktree add`.
- `plugins/sdlc-lite/hooks/hooks.json`: added the hook as the fourth command in the `Bash` matcher group.
- `plugins/sdlc-lite/scripts/hook-selftest.sh`: updated the header comment and added a `block-stray-worktree` section with all the handoff's deny and allow cases, including checks that stderr names the role and the `--detach` form. `run()` now also unsets `SDLC_TMP_WORKTREES`, so the caller's value never leaks into a test.
- `plugins/sdlc-lite/scripts/check.sh`: the header comment now names `block-stray-worktree.sh` in the list of hooks the selftest covers.

## Checks
- `test -x plugins/sdlc-lite/hooks/block-stray-worktree.sh`: rc 0.
- The handoff's six printf fixture criteria all hold:

  | Command | Env | Expected | Got |
  |---|---|---|---|
  | `/tmp/x HEAD` | builder + prefix | 2 | 2 |
  | `-b tmpbr` | builder + prefix | 2 | 2 |
  | `--detach "$SDLC_TMP_WORKTREES/x" HEAD` | builder + prefix | 0 | 0 |
  | `/tmp/x HEAD` | role and prefix unset | 0 | 0 |
  | `bash -c` wrapper | builder + prefix | 2 | 2 |
  | `--detach /r/x HEAD` | conductor, prefix unset | 2 | 2 |

- `jq -e '... any(test("block-stray-worktree"))' plugins/sdlc-lite/hooks/hooks.json`: true, rc 0.
- `grep -q block-stray-worktree plugins/sdlc-lite/scripts/hook-selftest.sh`: rc 0.
- `grep -q block-stray-worktree plugins/sdlc-lite/scripts/check.sh`: rc 0.
- `shellcheck --severity=warning plugins/sdlc-lite/hooks/block-stray-worktree.sh`: rc 0.
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`: `hook selftest: PASS`, rc 0.
- Negative control: made a throwaway worktree at `$SDLC_TMP_WORKTREES/negctl`, copied in the four changed files, and put `exit 0` right after the `SDLC_ROLE` line. Its `hook-selftest.sh` printed `hook selftest: FAIL: block-stray-worktree denies /tmp/x: exit 0, want 2` (rc 1). The worktree was removed afterwards and `git worktree list` shows no `negctl`.
- Extra sanity run, not a criterion: `bash plugins/sdlc-lite/scripts/check.sh` returned rc 0. All selftests passed, and shellcheck and `claude plugin validate` were ok.
- Also tried by hand, all behaving as intended:
  - Denied: `echo "$(git worktree add /tmp/x HEAD)"`, `cd /tmp && git worktree add --detach x HEAD`, `--detach $(mktemp -d)`, the bare prefix as the path, `-fb`, `sh -c`, a heredoc, an unterminated quote.
  - Allowed: a relative `.worktrees/tmp/builder-1/x HEAD^1 2>&1 | tail -1` with cwd `/r`, `git worktree list`, `bash -c "git worktree list"`, a mention in a commit message.

## Notes
- The first raw-scan regex (modelled on block-pattern-kill's `${word}git${wend}.*${word}...`) could not match when only one space separates `git` from `worktree`. I used `${word}git[^[:alnum:]_-](.*[^[:alnum:]_-])?worktree[[:space:]]+add${wend}` instead. The same regex shape in `block-pattern-kill.sh` has the same weakness for adjacent words (for example `kill` directly followed by one space and `ps`). I left that out of scope.
- The hook uses a small Python tokenizer instead of block-pattern-kill's masker. The masker drops a quoted non-plain word like `"$SDLC_TMP_WORKTREES/x"`, and the hook needs that path token. Any occurrence of the word `git` followed by `worktree add` is checked, not only one in command position. So an unquoted `echo git worktree add /tmp/x` is denied, which errs on the safe side.
- Known gap, not in the spec: `git worktree add --detach`-less `<path> <name>`, where `<name>` exists only as a remote branch, can make git create a local tracking branch. The hook treats `<name>` as a commit-ish and allows it. Git aliases (for example `git wt add`) are not caught either.
- Step 2 (CLAUDE.md, sdlc-lite-author.md, builder.md, verifier.md) was not touched.
