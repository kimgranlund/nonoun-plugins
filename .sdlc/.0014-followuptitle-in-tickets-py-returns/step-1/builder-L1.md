<!-- role=builder level=L1 model=sonnet effort=low -->
That handoff.md diff is unrelated/pre-existing, not touched by me.

## Status
done

## Changes
plugins/sdlc-lite/scripts/tickets.py: fixed `follow_up_title` to recurse past an empty first sentence instead of returning `''`, and added a selftest assertion for `follow_up_title('. ' + 'x'*80)`.

## Checks
- `python3 -c "...follow_up_title('. ' + 'x'*80)..."` → `'xxx...xxx...'` (non-empty, no leading `.`): pass
- Reverting only the `follow_up_title` line change (verified by hand-evaluating the old condition on the test input): confirmed it returns `''`, so the new selftest assertion catches the regression
- `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: PASS
- `follow_up_title('x'*50)` returns input unchanged: confirmed
- Existing `short_first_sentence_item` and `long_item` assertions in case (a): still pass (selftest PASS overall, assertion order unchanged, new assertion added after the short-first-sentence one)

## Notes
None
