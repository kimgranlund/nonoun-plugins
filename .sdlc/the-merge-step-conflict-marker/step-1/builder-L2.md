<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/check.py`: added two probe cases after the kept-conflict case. The first is a both-sides legit lane line, which must pass. The second is an aligned kept marker, a known miss the guard must pass. Also updated the probe comment and docstring item 6 to name all seven cases and to explain the aligned-marker miss.

## Checks
- `python3 plugins/sdlc-lite/scripts/check.py`: exit 0, "ok: 18 role levels, 8 agents checked"
- Widened-guard copy, `grep -q "aligned kept marker flagged"`: exit 0
- Widened-guard copy, `grep -q "both-sides legit lane line flagged"`: exit 0
- `grep -qF 'grep -qE "^\+\+(<<<<<<<|>>>>>>>)( |$)"' plugins/sdlc-lite/agents/planner.md`: exit 0
- `! grep -n '—' plugins/sdlc-lite/scripts/check.py`: exit 0, no matches
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0, with all selftests, shellcheck and plugin validate ok

## Notes
None
