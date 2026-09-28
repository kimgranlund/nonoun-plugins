<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/agents/builder.md: added rule 9. It says to run gates, tests, and long commands in the foreground with the Bash timeout at 600000 or more, never to use `run_in_background` or Monitor, and to "never end the turn while background work runs".
- plugins/sdlc-lite/agents/verifier.md: added the same rule as the new rule 5. The old rule 5 ("Your only output is the verdict") is now rule 6.
- plugins/sdlc-lite/scripts/check.py: new check that both files contain the phrase. When it is missing, the error names the file.

## Checks
- `grep -qF 'never end the turn while background work runs' plugins/sdlc-lite/agents/builder.md`: exit 0
- `grep -qF 'never end the turn while background work runs' plugins/sdlc-lite/agents/verifier.md`: exit 0
- Negative control: a temp copy with the phrase removed from verifier.md. Check.py exits nonzero, so the criterion passes (exit 0). Output: `FAIL agents/verifier.md: foreground rule missing "never end the turn while background work runs"`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: `ok: 18 role levels, 8 agents checked`, exit 0

## Notes
None
