## Task goal
The bug is fixed and a test that failed before the fix passes after it.

## Step 1: Exclude the closing ticket from the duplicate set, with a selftest
level: L2
### Do
In `plugins/sdlc-lite/scripts/tickets.py`, function `cmd_close`, build the `known` list (about line 615) from the tickets other than the one being closed. Skip the entry whose id equals `pid`, or whose folder equals the closing ticket's folder name. Update the docstring or help text that says a follow-up is compared against "an existing ticket" so it says "any other ticket".

In `selftest()`, add a case next to (s) (about line 1303). Its label starts `(s2)`. The fixture is a ticket whose slug is `alpha`, with a filer file whose Follow-ups are two bullets that both begin with the words "Alpha" (for example `- Alpha guard still flags a line on the lane` and `- Alpha guard empty input branch was missed`). It expects three things:
- `close alpha --dry-run` marks neither bullet as a duplicate.
- A real close files two new tickets, and the second slug gets a `-2` suffix when the first five slug words collide.
- `run(root, 'check')` returns 0.

Write the case first and confirm it fails with the fix reverted. Then apply the fix and confirm it passes.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0 (green now as a guard; it must stay green after the change).
- `grep -c "(s2)" plugins/sdlc-lite/scripts/tickets.py` prints 1 or more (it is red now: prints 0).
- The verifier reverts only the `known` change in a `git worktree add <tmp> HEAD` copy, runs `python3 plugins/sdlc-lite/scripts/tickets.py selftest` there, and sees it fail on the `(s2)` case. With the fix in place it passes.
- `plugins/sdlc-lite/scripts/check.sh` shows no new findings versus the same command run in a `git worktree add <tmp> HEAD` copy of the base commit.
