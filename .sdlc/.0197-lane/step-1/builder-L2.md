<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/scripts/steps.py: added `review_required(plan, task_dir)` in the review section. `review_action` and `lean_warnings` now call it instead of carrying their own copies of the conditions. Added the new `(r) review_required ...` selftest case right after the `(r)` review cases.

## Checks
- `out=$(python3 plugins/sdlc-lite/scripts/steps.py selftest) && printf "%s\n" "$out" | grep -qF "ok: (r) review_required returns the unresolved items and every reason review prints, in order"`: pass. The selftest exits 0, prints `steps selftest: PASS`, and every line is `ok:`.
- inspect check on `review_action` (contains `review_required(`, no `builder L4 or L5`): exit 0.
- inspect check on `lean_warnings` (contains `review_required(`, no `Merge `): exit 0.
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`: PASS.
- (guard) no em dash in steps.py: exit 0.
- (guard) scope check with `SDLC_BASE_SHA=0209ceb3...`: exit 0. The only changed file is steps.py.
- `git diff --check`: clean.

## Notes
The byte-identical requirement for `review_action` output is covered by the new selftest. It checks the exact reason line from the handoff, and all the existing `(r)` and `(lean)` cases still pass unchanged.
