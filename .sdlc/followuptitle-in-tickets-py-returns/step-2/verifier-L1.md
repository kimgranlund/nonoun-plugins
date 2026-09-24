<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- A bullet with `` `follow_up_title` `` cleans to text that still contains `follow_up_title`: pass. Evidence: I ran the new cleanup (the two regexes copied word for word from tickets.py lines 362-363) in `python3`. It turned `` '`follow_up_title` in tickets.py' `` into `'follow_up_title in tickets.py'`. The old regex gave `'followuptitle in tickets.py'`, so this check does tell the two apart. The selftest also runs the real `close` command, and the filed titles include `'followuptitle in tickets.py returns a mangled title with...'` only when the fix is reverted (see the third criterion).
- `_emphasized_` and `__bold__` still lose their surrounding underscores: pass. Evidence: the same run turned `'_emphasized_ word'` into `'emphasized word'`, `'__bold__ word'` into `'bold word'`, and `'x _a_ y'` into `'x a y'`.
- The selftest fails when only the regex fix is reverted and passes with the fix in place: pass. Evidence: I made a throwaway worktree at HEAD, copied in the current tickets.py, and put back only the old line `plain = ' '.join(re.sub(r'[`*_\[\]()]', '', item).split())`. Running `python3 plugins/sdlc-lite/scripts/tickets.py selftest` there printed `tickets selftest: FAIL, these did not bite: - (a) underscore inside a word survives cleanup (not mangled to followuptitle): [... 'followuptitle in tickets.py returns a mangled title with...']` and exited with rc=1. It failed on the new assertion only. In the real tree it exits 0 (next criterion). I removed the worktree afterwards.
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` exits 0: pass. Evidence: it printed `tickets selftest: PASS` and exited with rc=0. The Step 1 assertion (empty first sentence) is in the suite that passed.
- `plugins/sdlc-lite/scripts/check.sh` exits 0 from the repo root: pass. Evidence: rc=0, with output `selftest: PASS`, `tickets selftest: PASS`, `board selftest: PASS`, `ok: shellcheck`, `ok: plugin validate`.

## Out of scope changes
None from this step. `git diff` also shows `.sdlc/followuptitle-in-tickets-py-returns/handoff.md`, where the Goal and Constraints were filled in during the earlier clarify step. It shows the `follow_up_title` change in tickets.py (lines 315-316) and its selftest assertion too, both from Step 1. The only changes Step 2 made are to the `cmd_close` cleanup and to selftest: the new fixture bullet, the new assertion, and the counts raised from 3 to 4 follow-ups and from 5 to 6 tickets.

## For the next attempt
None
