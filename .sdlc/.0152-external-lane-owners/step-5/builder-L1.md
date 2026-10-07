<!-- role=builder level=L1 model=sonnet effort=low -->
Line 121 is now longer than the neighbouring wrapped lines, but the text is correct.

## Status
done

## Changes
- `plugins/sdlc-lite/scripts/fanout.py`: docstring line 121 reworded for the external lane's Commit cell.
- `docs/references/sdlc-internals.md`: the matching sentence reworded the same way.

## Checks
- Both greps for `merged nothing new` and the negated greps for the old wording passed (the `ok` line, plus grep output at line 121). The `fanout.py` grep also matched a selftest string at line 1418. That string was already there.
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest` printed PASS.
- `git diff --check -- plugins docs` was clean.

## Notes
None
