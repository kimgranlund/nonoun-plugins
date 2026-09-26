<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/steps.py`: `next_action` no longer raises on a builder result with no `done`/`blocked` Status. One such result gives `rebuild L<level>`, and two or more in a row (newest first) give `stop`. A new helper `build_status_or_none` supports this. Statusless builders are left out when pairing a verifier with its builder, so they never change fail counts. The docstring's `next` rules and Errors line are updated. In the selftest, the old error case is replaced with `rebuild L2`, and cases are added for `stop` and for `verify L1`.

## Checks
- Criterion 1 (a statusless builder gives `rebuild L2`): exit 0
- Criterion 2 (two statusless builders give `stop`): exit 0
- Criterion 3, guard (a statusless builder then a done builder gives `verify L1`): exit 0
- Criterion 4, guard (`python3 plugins/sdlc-lite/scripts/steps.py selftest`): PASS, exit 0
- Criterion 5 (`! grep -q "next error: a builder with no done/blocked Status" ...`): exit 0

## Notes
Once `next_action` has handled a statusless newest builder, it filters the builders list down to results with a Status before pairing verifiers with builders. Without that, a statusless builder that sits between a done builder and a verifier would be picked as the verifier's paired builder.
