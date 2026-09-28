<!-- role=builder level=L2 model=opus effort=low -->
## Status
blocked

## Changes
None kept. `plugins/sdlc-lite/scripts/tickets.py` is back at its post-step-2 state: the numbered-mode code is intact and `grep -c numbered` gives 53. My step-3 attempt is saved for reference in `.sdlc/0016-ticket-numbered-folders/step-3/attempt.txt`. It is the full diff against the index, so it also contains steps 1-2.

## Checks
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` with the step-3 rule added: FAIL. My new cases passed (the mismatch mutation fired, the matching `0001-alpha` passed, plain slugs got no prefix error). Two existing step-1/2 cases then failed:
  - `plain mode still takes a digit-led slug as-is`: in plain mode, `new feature 0007-gamma` gets id T-0003, so the new rule rejects it.
  - `(i) plain close keeps bare slugs`: in plain mode, the follow-up `- 0042 fix the parser` becomes folder `0042-fix-the-parser` with id T-0005, so close fails.
- `scripts/check.sh`: failed on the same two cases; the board selftest, shellcheck and plugin validate passed.
- After backing out step 3: `tickets.py selftest` PASS.

## Notes
- The step conflicts with the task's own constraints. The task says the prefix check runs "always, in both modes", and also says plain-slug `new` and `close` stay "byte-for-byte the same". Steps 1-2 locked in plain behavior that makes a `NNNN-` folder whose id does not match, and the new rule rejects exactly that. The step says "no special-casing needed", but that doesn't hold, so I stopped rather than choose a fix. A replan needs to pick one of these:
  - (a) In plain mode, `new` refuses a slug that starts with `NNNN-` unless the digits match the id it assigns, and `close` strips or rewrites a leading `NNNN` in follow-up slugs. The two step-2 selftests change to match.
  - (b) Enforce the prefix only in numbered mode, which drops the "always" decision.
  - (c) Keep plain mode as it is and accept that plain `new`/`close` can write a folder that `check` rejects. I don't recommend this.
- Process slip: I backed out my edit with `git checkout` on the file, which also wiped the unstaged step-1/2 work. I restored it right away by re-applying the saved diff without my step-3 hunks, and the selftest passes. Before steps 4+ build, the verifier should confirm the step-1/2 diff is intact: 184 lines changed in tickets.py.
