## Task goal
A gate that main already made red is reported as inherited, not as a build failure or a plan defect.

## Step 1: steps.py next maps an inherited red builder to `inherited`
level: L2
### Do
In `plugins/sdlc-lite/scripts/steps.py`:
- Teach the builder Status parser to accept a third value. A first non-blank line under `## Status` that starts with `inherited red:` (case-insensitive) is the status `inherited`. `done` and `blocked` parse exactly as before. A bare `inherited red` with no colon stays statusless, which keeps the current `rebuild` / `stop` handling.
- `build_status_or_none` returns `inherited` for such a line, so it breaks a run of statusless builders like any real status does.
- In `next_action`, add a check right after the statusless branch and before the `blocked` check: when the newest builder's status is `inherited`, return `('inherited', None, '<name> reports inherited red (gate already red at the pre-build HEAD); ask the conductor, not a fail, rebuild, bump, or replan', read)`.
  - An older inherited builder followed by a `done` builder follows the normal path (verify).
  - An inherited builder is never a counted fail and never a bump.
- Update the module docstring's `next` rules. Add the line `newest builder Status inherited red: <tests> -> inherited` and say it is never counted as a fail, a bump, a rebuild, or a replan.
- Add selftest cases whose names start with `next inherited:`:
  - (a) newest builder `## Status\ninherited red: test_a` → `inherited`.
  - (b) inherited builder then a `done` builder → `verify L1`.
  - (c) a `done` builder, a verifier FAIL, then an inherited builder → `inherited`, not `rebuild` or `bump`.
  - (d) `## Status\ninherited red` with no colon → `rebuild L2`.
### Acceptance criteria
- `d=$(mktemp -d) && printf '## Status\ninherited red: test_a\n' > "$d/builder-L2.md" && out=$(python3 plugins/sdlc-lite/scripts/steps.py next "$d") && test "$(printf '%s\n' "$out" | head -1)" = inherited` (run from the repo root; the `&&` chain also requires exit 0)
- `grep -q "next inherited: " plugins/sdlc-lite/scripts/steps.py`
- `grep -q 'inherited red:' plugins/sdlc-lite/scripts/steps.py`
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`
