<!-- role=builder level=L1 model=sonnet effort=low -->
handoff.md and other artifacts are pre-existing from planning; only tickets.py is mine to report as changed.

## Status
done

## Changes
plugins/sdlc-lite/scripts/tickets.py: `cmd_close` cleanup regex now strips paired emphasis underscores first (`_word_`, `__word__`) via a word-boundary-aware pattern, then removes remaining markdown chars without `_` in the class, so underscores inside a word (e.g. `follow_up_title`) survive; added an `underscore_item` bullet to the `good` selftest fixture and a new `expect(...)` asserting the filed title contains `follow_up_title` and not `followuptitle`; bumped fixture-dependent counts (4 follow-ups instead of 3, 6 tickets instead of 5) in existing assertions.

## Checks
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest` — PASS (exit 0)
- Manual regex check: `follow_up_title` bullet cleans to contain `follow_up_title` (not `followuptitle`); `_emphasized_`/`__bold__` still strip to `emphasized`/`bold` — both correct
- Revert-only test: manually reverted just the `cmd_close` regex fix (keeping the new selftest assertion) → selftest FAILs on exactly the new assertion; restored fix → selftest PASSes
- `plugins/sdlc-lite/scripts/check.sh` — exit 0 (tickets selftest, board selftest, shellcheck, plugin validate all pass)

## Notes
None
