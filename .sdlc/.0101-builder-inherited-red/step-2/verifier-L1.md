<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `grep -q 'want_rc 0 builder L2 .*inherited red: ' plugins/sdlc-lite/scripts/run-selftest.sh`: pass. Evidence: in this tree it exits `c1=0`. In a throwaway worktree at HEAD it exits `base_c1=1`, so the check can fail. The line is at run-selftest.sh:159, and the bare `want_rc 3 builder L2 $'## Status\ninherited red'` case is at :160.
- `grep -q "builder) sect=Status; allowed='done|blocked|inherited red" plugins/sdlc-lite/scripts/run.sh`: pass. Evidence: in this tree it exits `c2=0`, and at HEAD it exits `base_c2=1`. run.sh:223 reads `builder) sect=Status; allowed='done|blocked|inherited red: .+' ;;`. The header comment at run.sh:18 now names `(done|blocked|inherited red: <tests>)`, as the Do asks.
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh`: pass. Evidence: it prints "run selftest: PASS" and exits 0. For a negative control I ran the new run-selftest.sh against the HEAD run.sh in the throwaway worktree. It went red with `FAIL: builder result '## Status\ninherited red: test_a': exit 3, want 0 (run.sh: builder result lacks ## Status (done|blocked)...)`, which shows the new case fails without the run.sh change. The existing `want_rc 3 ... maybe` case still passes, so `maybe` is still rejected.
- (guard) `shellcheck --severity=warning plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/run-selftest.sh`: pass. Evidence: exit 0 with no output.

## Out of scope changes
None from this step. `git diff --stat` lists 4 files. `run.sh` and `run-selftest.sh` are this step's files. `plugins/sdlc-lite/scripts/steps.py` belongs to step 1 of the same task; its handoff is `.sdlc/0101-builder-inherited-red/step-1/handoff.md`, and `step-1/verifier-L1.md` shows a pass. `.sdlc/0101-builder-inherited-red/handoff.md` changed only in its Intent and Constraints sections, which is the task's clarify output and not code (checked with `git diff` on that file).

## For the next attempt
None
