<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k tickets`: pass. Evidence: I ran it and it printed two `ok: tickets:` lines and `traces selftest: PASS`, with rc=0.
- `... selftest -k tickets | grep -q '^ok: tickets: '`: pass. Evidence: rc=0 on my run.
- `grep -q 'tickets.load' ... && grep -q 'tickets.problems' ...` on `plugins/sdlc-lite/scripts/traces/sources/tickets.py`: pass. Evidence: rc=0. The file calls `tickets.load(root)` and `tickets.problems(ts, tickets.config_numbered(root))`.
- (guard) scope: pass. Evidence: I ran it with `SDLC_BASE_SHA` set to 7334f49 (read from `step-8/base-sha`) and got guard=0. The only tracked diff outside `.sdlc` is `.gitignore`. The new files are `traces.py` and `traces/`, all inside the allowed pattern.

The behavior described in the Do holds, read against `selftest.py:686-708`:
- **Fixture:** `0001-a` (T-0001, ready), `.0002-b` (T-0002, done) and `0003-c` (T-0001) are checked with an exact dict equality on `by_slug`.
- **Problems:** exactly one problem line, containing `duplicate id T-0001`.
- **Notes flag:** `notes` is False without `notes.md` and True with it.
- **External branches:** `external` is `[]` with no config. A positive control writes a config and gets `['feat/x']`, so that case can go red.

Checks that bite:
- **Attempted:** I tried a negative control, a scratch copy with `problems` stubbed to `[]`, but the sandbox denied the command. The assertions pin exact values, so a stub would fail them: `len(problems) == 1` fails on an empty list.
- **Not run:** I did not observe that red. I also did not run the base worktree. The `tickets` cases are new and untracked, so `-k tickets` has nothing to match at the base commit.

## Out of scope changes
None. `git status --short plugins` shows only `plugins/sdlc-lite/scripts/traces.py` and `plugins/sdlc-lite/scripts/traces/` as untracked, both in scope. `.gitignore` is the only tracked change, and the guard allows it.

## For the next attempt
None
