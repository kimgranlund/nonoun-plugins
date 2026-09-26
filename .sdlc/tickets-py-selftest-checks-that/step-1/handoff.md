## Task goal
`tickets.py selftest` proves that the `close --dry-run` `expect <digest>` line is unchanged by other-worktree `open ... (worktree <name>)` lines when follow-ups are present, so the digest guarantee (it covers only the ordered follow-ups) is tested beyond the empty-follow-ups case. Done when the new selftest case passes and fails against a mutant that folds open lines into the digest.

## Step 1: Add the follow-ups-present digest case to the worktree dry-run selftest
level: L2
### Do
In `plugins/sdlc-lite/scripts/tickets.py`, inside `selftest()`, add one case right after the existing `worktree dry-run:` expect. It sits at the end of the `git`-guarded block that builds the `dr` repo and its `wtdr` worktree, where `gamma` is an open ticket living only in `wtdr`.

- Write a filer file for `delta` in `d_root` with two Follow-ups bullets, using the existing `filer('filer-L1.md', 'None', '- A\n- B', slug='delta')(d_root)` helper. Check the helper's argument format at its definition and match it.
- Snapshot `d_root` and `dw_root`, then run `run(d_root, 'close', ('delta',), dry_run=True)`.
- Assert all of the following:
  - `rc == 0`.
  - The output contains an `open T-0004 Gamma [gamma] (worktree wtdr)` line. The id may differ, so build the expected line from the fixture, or match `(worktree wtdr)`.
  - The last line equals `'expect ' + follow_digest([<the two bullet texts>])`.
  - Neither tree changed.
- Give the case a label starting `worktree dry-run with follow-ups:` so it can be found by grep.

Do not change `cmd_close` or any output. The change is test-only.

### Acceptance criteria
- `grep -c "worktree dry-run with follow-ups" plugins/sdlc-lite/scripts/tickets.py` prints at least 1 (red now: the case does not exist).
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0 and prints `tickets selftest: PASS`.
- Mutant check: copy `tickets.py` to a temp dir and change `[f'expect {digest}']` in the dry-run return to fold the open lines into the digest, for example `[f'expect {follow_digest(items + opens + other_opens)}']`. Running `selftest` on the copy exits 1, and stderr names the `worktree dry-run with follow-ups` case among the misses.
- `git diff HEAD --stat -- plugins/sdlc-lite/scripts` lists only `tickets.py`, and `git diff HEAD -U0 -- plugins/sdlc-lite/scripts/tickets.py` shows no removed lines outside `selftest()`.
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py check` exits 0. This is green now and must stay green.
- `plugins/sdlc-lite/scripts/check.sh` shows no new failures versus the same command run in a `git worktree add <tmp> HEAD` copy.
