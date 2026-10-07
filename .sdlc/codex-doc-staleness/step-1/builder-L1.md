<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `docs/references/codex-role-execution.md`: replaced the "current alternate pairs" sentence and reworded the smoke-test "predates" sentence.
- `plugins/sdlc-lite/HARNESS-NOTES.md`: rewrote the agent-count clause on line 19.
- `docs/reports/release-0.19.0.md`: added the scout-move line after the existing correction line.

## Checks
- The four `grep -qF` criteria and the `! grep -qF` criterion all passed.
- `python3 plugins/sdlc-lite/scripts/check.py`: "ok: 18 role levels, 8 agents checked".

## Notes
None
