<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- #1 selftest exits 0 with a positive fixture and a just-short negative control per rule: pass. Evidence: `python3 plugins/sdlc-lite/scripts/fleet_doctor.py selftest` exits 0 and prints "fleet_doctor selftest: ok". It shows 7 positives firing exactly once, 7 `negative control: silent` lines, 9 new `boundary:` lines (BOUNDARY at fleet_doctor.py:580), the collect checks, and the resolve refusals (pid in no finding, reused pid, name outside DAEMONS, daemon with no finding). Mutation re-check: I copied `plugins/sdlc-lite/scripts/` to a scratch dir under the tmp prefix, applied one edit at a time to `fleet_doctor.py`, and ran selftest. All 7 mutations the prior attempt found surviving are now KILLED, each with a named FAIL line: drop `k['cpu'] < 1.0` (FAIL "stdin-wait reader at 5% CPU"); drop the stdin age conjunct (FAIL "reader aged 4 min"); drop `ta` (FAIL "transcript write 10 min ago"); drop `ca` (FAIL "child change 10 min ago"); drop the runaway CPU conjunct (FAIL "79% CPU"); heavy-peer `>=` replaced by `True` (FAIL "49% CPU"); drop `MIN_TICKET_S` (FAIL "500 s ticket"). Also killed: slow-check `>` to `>=`, overloaded `>` to `>=`, replan share compare removed. Threshold-constant mutations in DEFAULTS were killed for stdin_wait_min 5 to 3, stall_min 20 to 8, runaway_cpu 80 to 70, heavy_cpu 50 to 40, check_factor 2 to 1.5, load_factor 1.5 to 1.2, and MIN_TICKET_S 600 to 300. The unmutated tree is green, so the checks go red only on the mutations. Steelman of a possible fail: the replan_share default 0.4 to 0.3 survives (negative is 0.30, a strict `>`). I dropped it as a fail because the handoff and the prior verdict named the seven listed mutations, the replan negative (900/3000) is observed silent, and the share compare itself is killed. It goes under Notes.
- #2 `test "$(... selftest | grep -c 'negative control: silent')" -eq 7`: pass. Evidence: exit 0. The boundary lines say `boundary: ... is silent`, so they do not inflate the count; it stays at 7.
- #3 live-probe: pass. Evidence: `bash .sdlc/0552-fleet-doctor-skill/live-probe.sh` exits 0. Output: `1. stdin-wait  pid 59973 \`cat\` idle 0m ...`, `pid 59972 is in no finding; nothing killed`, `killed pid 59973 (stdin-wait, SIGTERM)`, `found=0 refused_sibling=2 reader_gone=1 writer_alive=1`. Rerun to confirm the exit code: 0.
- #4 `check.py`: pass. Evidence: exit 0, `ok: 20 role levels, 10 agents, 23 generated definitions checked`.
- #5 `check-packaging.py`: pass. Evidence: exit 0, `PASS: catalog parity, identity, skill routes, hook isolation and context links`.
- #6 `prompt_lint.py`: pass. Evidence: exit 0, `prompt_lint: 76 files, 0 errors, 9 warnings`.
- #7 no tracked file outside `.sdlc` changed: pass. Evidence: `test -z "$(git diff --name-only HEAD -- . ':(exclude).sdlc')"` exit 0. `git status` shows only `.sdlc/0552-*` files plus untracked `plugins/sdlc-lite/scripts/fleet_doctor.py` and `plugins/sdlc-lite/skills/fleet-doctor/`.
- #8 no em dash in the new files: pass. Evidence: the `chr(0x2014)` check exits 0.

## Out of scope changes
None. `.sdlc/0552-fleet-doctor-skill/handoff.md` gained its acceptance criteria and is inside `.sdlc`. `redck.py deviations` printed no process deviation.

## For the next attempt
None

## Notes
- plugins/sdlc-lite/scripts/fleet_doctor.py:580 BOUNDARY: note: no fixture sits between the replan-cost default 0.4 and the existing negative's 0.30 share, so lowering `replan_share` to 0.3 leaves selftest green; a 0.39-share fixture would close it. Dropping the `role.get('age_s', 0) > lim` conjunct from stalled also leaves selftest green (the rule's text names only the two quiet clocks).
- plugins/sdlc-lite/scripts/fleet_doctor.py:resolve_kill: note: `slow-check` is accepted for `--kill` but no slow-check resolution offers a kill; harmless, carried from the prior attempt.
- plugins/sdlc-lite/scripts/fleet_doctor.py:detect stdin-wait: decide: a bare `cat` at under 1% CPU at the end of a slow producer pipe has the same signature as an idle stdin reader; the approval step limits the harm. Carried from the prior attempt.
