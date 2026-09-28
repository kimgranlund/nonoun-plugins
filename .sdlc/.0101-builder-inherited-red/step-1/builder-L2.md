<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/steps.py`:
  - `build_status_or_none` now returns `inherited` when the first line under `## Status` starts with `inherited red:` (case-insensitive).
  - `next_action` has a new `inherited` branch after the statusless check and before the `blocked` check.
  - The module docstring's `next` rules include the new line.
  - Four `next inherited:` selftest cases were added.

## Checks
- `d=$(mktemp -d) && printf '## Status\ninherited red: test_a\n' > "$d/builder-L2.md" && out=$(python3 plugins/sdlc-lite/scripts/steps.py next "$d") && test "$(printf '%s\n' "$out" | head -1)" = inherited`: exit 0
- `grep -q "next inherited: " plugins/sdlc-lite/scripts/steps.py`: exit 0
- `grep -q 'inherited red:' plugins/sdlc-lite/scripts/steps.py`: exit 0
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: exit 0, "steps selftest: PASS". All four `next inherited:` cases printed ok: (a) inherited, (b) verify L1, (c) inherited, (d) rebuild L2.

## Notes
The handoff did not ask for this, but it follows from its "never a counted fail" rule: the list of builders that verifiers pair with now holds only `done` and `blocked` results. An inherited builder is never used as a verifier's paired builder, so it can never add to a fail count.
