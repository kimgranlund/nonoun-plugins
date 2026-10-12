<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout50/g/plugins/sdlc-lite/scripts/verify_scope.py`: tests-gate class in `scope(root, base, handoff=None, report=None, need_report=False)`, new `--report FILE` CLI option, module docstring, selftest cases `tests-gate ok: ` (4) and `tests-gate red: ` (11).
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout50/g/plugins/sdlc-lite/scripts/tickets.py`: `docs_waiver(d)` returns `(base, klass)`, new `solo_report(d)`, the skip line carries the class, `import json` added at module top, `vs_root` gains a `lane` argument, five `(tests-gate)` selftest expects.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout50/g/.sdlc/config`: appended `tests_gate: pilot`.

## Checks
`SDLC_BASE_SHA` was empty in the shell, so every run below had `export SDLC_BASE_SHA=a3e2cd9b273ade52a66978f8e1938ad8e7fae948` (the brief's base) first.
- `f=plugins/sdlc-lite/scripts/verify_scope.py; python3 "$f" selftest && for l in "tests-gate: level" "tests-gate: lane" "tests-gate: criteria" "tests-gate: red-control" "tests-gate: report" "tests-gate: shared-name" "tests-gate: size" "tests-gate: protected-path" "verifier requested by"; do grep -qF "$l" "$f" || exit 1; done` exit 0 (`verify_scope.py selftest: ok`)
- `f=plugins/sdlc-lite/scripts/verify_scope.py; grep -qF "tests-gate ok: " "$f" && grep -qF "tests-gate red: pilot off" "$f" && test "$(grep -c "tests-gate red: " "$f")" -ge 10` exit 0
- `out=$(python3 plugins/sdlc-lite/scripts/verify_scope.py "$SDLC_BASE_SHA" --handoff .sdlc/0496-tests-gate-pilot/handoff.md); printf "%s\n" "$out" | grep -qF "tests-gate: level"` exit 0 (printed `tests-gate: level: size is L3, not L2`)
- `grep -qxF "tests_gate: pilot" .sdlc/config` exit 0
- `f=plugins/sdlc-lite/scripts/tickets.py; grep -qF "(tests-gate)" "$f" && grep -qF "reason: tests-gate diff against" "$f" && python3 "$f" selftest` exit 0 (`tickets selftest: PASS`)
- `python3 plugins/sdlc-lite/scripts/redck.py selftest` exit 0 (`redck selftest: PASS`)
- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vxF -e plugins/sdlc-lite/scripts/verify_scope.py -e plugins/sdlc-lite/scripts/tickets.py)" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc")"` exit 0. It ran before the `tickets.py` selftest; `git status --short` after that selftest showed the same three modified files and no untracked path outside `.sdlc/`.
- `git diff --check` exit 0 (not a criterion).

## Notes
- A verifier that runs criteria 3 and 7 with `SDLC_BASE_SHA` unset gets a usage exit 2 on criterion 3, not `tests-gate: level`.
- The step handoff has no `(red)` criterion, so no `redck.py record` was run and there is no red-checkpoint record for this attempt.
- Reach of the close integration: `skip_missing` asks for a verifier only per `step-<n>/` dir, and the `tickets.py` docstring says a solo ticket has no steps. `docs_waiver` is therefore consulted, and the `tests-gate` skip line written, only for a solo-lane ticket that has a step dir. The `(tests-gate)` selftest fixture is lane solo with `step-1/builder-L1.md` for that reason. A real solo ticket with no step dir closes today without a verifier result and without the new line. The planner should decide whether the pilot needs the line on that path.
- Two readings of the handoff, both in the direction of keeping the verifier:
  - shared-name: a removed token counts as present on a `+` line only as a whole token (no adjacent word character or `-`). A rename `helper` to `helper2` therefore still searches `helper`. The search itself is `git grep -F -l -e <token>`, substring as specified.
  - shared-name: untracked files add no `+` lines, since the handoff names only the `git diff -U0` output.
- `protected-path` matches the sensitive words as substrings of any path component, so `auth` also matches `author`.
- Until step 2 lands, `agents/solo.md` treats only `docs-only` as a skip. Solo's own `verify_scope.py` call can now print `tests-gate` or `tests-gate: <label>: ...` in place of the first non-docs path when the pilot flag is on and `--handoff` is given.
- `docs_waiver` has no caller outside `tickets.py`; its three uses there are updated.
- The `verify_scope.py` selftest has three cases beyond the handoff list: legacy size `M`, a solo call without a report, and a CLI exit 1 case for a tests-gate reason.
- No throwaway worktree was created. Nothing is committed.
