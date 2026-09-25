<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/tickets.py`: in `cmd_close`, the `known` list now leaves out the ticket being closed (matched by id `pid` or by folder `slug`). The module help and the `cmd_close` docstring now say "any other ticket". Added selftest case `(s2)` next to `(s)`.

## Checks
- Wrote `(s2)` before the fix and ran `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: FAIL on both `(s2)` expectations. The dry run marked both bullets `duplicate of T-0001 (alpha)`, and the close filed 0 tickets.
- After the fix, `python3 plugins/sdlc-lite/scripts/tickets.py selftest`: PASS.
- `grep -c "(s2)" plugins/sdlc-lite/scripts/tickets.py`: 3.
- `plugins/sdlc-lite/scripts/check.sh`: exit 0. The same command in a `git worktree add` copy of HEAD also exits 0, and the two outputs are identical, so there are no new findings. The temp worktree was removed.

## Notes
- The fixture bullets differ from the handoff's examples. `- Alpha guard still flags a line on the lane` and `- Alpha guard empty input branch was missed` would not fail before the fix, because neither matches alpha's title (`Alpha | one`, which normalizes to `alpha one`) or its slug base `alpha`. Their five-word slugs also differ, so there would be no `-2`. So `(s2)` uses `- Alpha one` and `- Alpha one.` instead. Both start with "Alpha", both matched the closing ticket by title before the fix, and they share the slug `alpha-one`, so the second is filed as `alpha-one-2`.
- CLAUDE.md still says follow-ups are skipped when they "exactly duplicate an existing ticket". That wording is now slightly imprecise. I left it alone because it is outside this step's scope.
