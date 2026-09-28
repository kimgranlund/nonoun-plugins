## Task goal
A gate that main already made red is reported as inherited, not as a build failure or a plan defect.

## Step 2: run.sh accepts an inherited red builder Status
level: L1
### Do
- In `plugins/sdlc-lite/scripts/run.sh`, change the builder case to `allowed='done|blocked|inherited red: .+'`. The existing `^($allowed)$` match on the lowercased value then accepts `inherited red: <tests>`. It still rejects `maybe`, and it rejects a bare `inherited red`.
- Update the header comment line `builder ## Status (done|blocked)` to name the new value.
- In `plugins/sdlc-lite/scripts/run-selftest.sh`, next to the existing builder `want_rc` cases, add two cases:
  - `want_rc 0 builder L2 $'## Status\ninherited red: test_a'`
  - `want_rc 3 builder L2 $'## Status\ninherited red'`
### Acceptance criteria
- `grep -q 'want_rc 0 builder L2 .*inherited red: ' plugins/sdlc-lite/scripts/run-selftest.sh`
- `grep -q "builder) sect=Status; allowed='done|blocked|inherited red" plugins/sdlc-lite/scripts/run.sh`
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh`
- (guard) `shellcheck --severity=warning plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/run-selftest.sh`
