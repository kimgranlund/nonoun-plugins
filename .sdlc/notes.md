# Notes

`tickets.py close` appends follow-ups that did not become tickets.

## T-0105: Find out why the T-0072 background hook did not stop the run in... (2026-09-26)

- note: the Monitor tool name in the `PreToolUse` payload is assumed to be exactly `"Monitor"` (matching the hooks.json matcher and block-background.sh's check); no live probe covers it, same as the planner's Risks and the T-0076 non-goal it inherits.
- note: step 7's builder accidentally ran `git checkout` on `run.sh` mid-mutation-test, discarding its uncommitted steps 1-6 changes, and restored it from a manual `/tmp` backup taken before the mutation; the verifier independently confirmed the restore was exact (matching diff stats and intact heading-pick and timeout-floor lines), but the near-loss is worth knowing about if this pattern recurs.
