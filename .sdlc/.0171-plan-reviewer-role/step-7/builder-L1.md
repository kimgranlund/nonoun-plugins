<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/run.sh`: replaced the two-line Codex comment with a three-line comment covering both the verifier and the plan-reviewer. No code changed.

## Checks
- `grep -qF "a verifier, or a plan-reviewer, whose model equals" plugins/sdlc-lite/scripts/run.sh` passed.
- `! grep -qF "# Codex: a verifier whose model equals the build's switches" plugins/sdlc-lite/scripts/run.sh` passed.
- `bash -n plugins/sdlc-lite/scripts/run.sh` passed.
- `python3 plugins/sdlc-lite/scripts/check.py` passed ("ok: 19 role levels, 9 agents checked").

## Notes
None
