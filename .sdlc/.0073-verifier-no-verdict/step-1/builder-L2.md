<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/steps.py`: added the `verdict_or_none` helper. `next_action` now returns `reverify` for one no-verdict verifier and `stop` for two or more in a row after the same build. The fail count skips no-verdict results. The docstring rules are updated. The selftest drops the old error case and adds five new cases: reverify, stop, rebuild, done, and reverify-not-bump.

## Checks
- AC1 (`reverify L1`, and the reason names `verifier-L1.md`): exit 0
- AC2 (two no-verdict verifiers give `stop`): exit 0
- AC3 (no-verdict, then a fail, gives `rebuild L2`): exit 0
- AC4 (the old error string is gone): exit 0
- AC5 (`reverify` appears in `steps.py`): exit 0
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`: PASS

## Notes
- The new `reverify` action is not yet handled in `/chain` or the conductor docs. This step did not cover them, so they are left for a later step.
- `verdict_or_none` catches every exception.
