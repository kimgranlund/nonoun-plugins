<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- #1 verify_scope.py selftest plus the nine label greps: pass. Evidence: ran with SDLC_BASE_SHA=a3e2cd9b; `verify_scope.py selftest: ok`, rc=0, no label missing. Negative controls: in a copy of scripts under the tmp prefix I mutated the protected-path, size, shared-name, lane, red-control phase, report, pilot-off and criteria checks one at a time; each mutation made the selftest fail naming the matching `tests-gate red: ...` case (8 of 8 went red). The copy was removed afterwards.
- #2 `tests-gate ok: `, `tests-gate red: pilot off` present and at least 10 `tests-gate red: ` lines: pass. Evidence: both greps succeed; `grep -c "tests-gate red: "` gives 11.
- #3 the CLI against the base with the task handoff prints `tests-gate: level`: pass. Evidence: output `tests-gate: level: size is L3, not L2`, grep rc=0. The handoff front matter holds size L3, so the output is correct. The check needs SDLC_BASE_SHA set; it was set here.
- #4 `tests_gate: pilot` line in .sdlc/config: pass. Evidence: `grep -qxF` rc=0; `git diff .sdlc/config` shows the single appended line.
- #5 tickets.py `(tests-gate)` and `reason: tests-gate diff against` strings plus `tickets.py selftest`: pass. Evidence: both greps succeed and `tickets selftest: PASS`. The (tests-gate) cases assert a qualifying ticket closes with the skip line, pilot off keeps the verifier, and a report missing one exit line keeps the verifier. The legacy (docs-only) cases still pass, so the docs path is unchanged.
- #6 `redck.py selftest`: pass. Evidence: `redck selftest: PASS`, rc=0.
- #7 (guard) no changed file outside .sdlc other than the two scripts, no untracked file outside .sdlc: pass. Evidence: the command gave rc=0; `git status --short` shows only .sdlc/config, tickets.py and verify_scope.py modified, and untracked paths only under .sdlc/. It is a gate; it is green on the built tree, so no pre-build run was needed.

Builder claims checked: the "no (red) criterion in the step handoff, so no red-checkpoint record" note is true, because the handoff has no `(red)` line and no process-deviations.md exists. The `verify_scope.py` diff matches the settled interface: the evaluation order, the exact labels, the `--report` CLI option, `scope(root, base, handoff=None, report=None, need_report=False)`, and the local `redck`, `results` and `steps` imports.

Steelman pass: drafted the fail "solo ticket with no step dir never reaches docs_waiver, so the pilot never writes the skip line". The builder's rebuttal holds. The handoff's Do specifies only the docs_waiver generalization and the two existing call sites, none of the acceptance criteria covers the no-step-dir path, and the builder flagged it for the planner. Dropped as a finding for this step.

## Out of scope changes
None. The diff holds only `.sdlc/config`, `plugins/sdlc-lite/scripts/tickets.py` and `plugins/sdlc-lite/scripts/verify_scope.py`, all named in the handoff Targets. Other untracked files are task records under .sdlc/.

## For the next attempt
None. For the planner (not a defect in this step): `tickets.py close` consults `docs_waiver`, and so writes the tests-gate skip line, only for a solo ticket that has a `step-<n>/` dir (see the builder note). Decide in step 2 or a follow-up whether the pilot needs the line on a solo ticket with no step dir.
