<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
None

## Checks
- `plugins/sdlc-lite/scripts/check.sh` from git toplevel: exit 0, all ok including "fanout selftest: PASS", "shellcheck", "plugin validate"
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: exit 0, printed `fanout selftest: PASS`

## Notes
Both gates were already green with step 1's uncommitted changes in the tree; no fixes were needed.
