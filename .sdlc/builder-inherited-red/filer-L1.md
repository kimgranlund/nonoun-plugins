<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0101: Builder reports inherited red when a gate is already red at the pre-build HEAD

## PR body
### Summary
A gate that was already red before the build started is now reported as `inherited red: <tests>`. It is no longer reported as a build failure or a plan defect. `steps.py next` prints a new action, `inherited`, for it. That action is never counted as a fail, a rebuild, a bump, or a replan, and it goes to the conductor. Interactively the conductor asks the user (fix main first, rebuild once main is green, or stop). Unattended, it stops the task and reports the inherited tests. It never waives the gate.

### Changes
- `scripts/steps.py`: `next` reads a builder Status starting with `inherited red:` (case-insensitive) as `inherited`. The new branch sits after the statusless check and before `blocked`. A bare `inherited red` with no colon still counts as statusless, so it maps to `rebuild` or `stop` as before. `done` and `blocked` parse as before. Inherited builders are also left out of the builder list that verifiers pair with, so they cannot add to a fail count. Four `next inherited:` selftest cases cover a lone inherited result, an inherited result then a done result, done then a verifier fail then inherited, and the bare no-colon form.
- `scripts/run.sh` and `run-selftest.sh`: the builder Status check accepts `inherited red: <tests>` and still rejects `maybe` and a bare `inherited red`. Two selftest cases added.
- `scripts/board.py`: an inherited red step renders as 🔴 `inherited red · builder <level>, ask the user`, and `--summary` counts it in the 🔴 total. One selftest case added.
- `agents/builder.md`: new rule 8, the pre-build check. Before reporting a gate failure, the builder runs the same command at the committed HEAD in `$SDLC_TMP_WORKTREES/base` (`HEAD^1` on a merge step). It applies to gate criteria only, not to criteria for the step's new behavior, which are red at base by design. The same failures at base give `inherited red: <tests>`. Different failures, or a green base, are an ordinary failure. The `plan defect:` wording no longer covers findings that predate the build, and the output-format Status line now reads `done | blocked | inherited red: <tests>`.
- `skills/chain/SKILL.md` and `agents/conductor.md`: the routing above is added to the step 4 action list, to a new numbered item 7 under "For each step", and to the conductor's escalation bullet.
- `CLAUDE.md` and `.claude/agents/sdlc-lite-author.md`: the action list, the Status mapping, the `board.py` and `run.sh` behavior, and a new "Inherited-red route" invariant.
- `scripts/check.py`: new `INHERITED_RED_DOCS` guard. The phrase `inherited red` must appear in builder.md, conductor.md, chain SKILL.md, steps.py, board.py, and run.sh. Each miss reports `<rel>: inherited-red route missing "inherited red"`.

Not changed: the verifier, `fanout.py`, levels and models.

### Verification
All four steps have a verifier verdict of pass.
- Step 1 (steps.py): the `next` command prints `inherited` on the new input. In a throwaway worktree at HEAD the same input gave `rebuild L2`. `steps.py selftest` passes.
- Step 2 (run.sh): `run-selftest.sh` passes. Run against the HEAD `run.sh`, the new case fails with exit 3, so it bites. `shellcheck --severity=warning` is clean.
- Step 3 (board.py): a `step_row` check returns 🔴 with an `inherited red` status. At HEAD it returned 🟡 `built` and exit 1. `board.py selftest` passes.
- Step 4 (docs and guard): the greps for the phrase in builder.md, chain SKILL.md, conductor.md, CLAUDE.md, and the author agent all pass, and `findings that predate this build` is gone from builder.md. Blanking `inherited red` in a copy of conductor.md makes `check.py` report the new error. An unmodified copy reports none. `scripts/check.sh` exits 0, with the steps, order, fanout, run, hook, and live-probe selftests, shellcheck, and plugin validate all ok.

## Changelog entry
- Builder: a gate already red at the pre-build HEAD is reported as `inherited red: <tests>`. `steps.py next` prints `inherited`, `run.sh` accepts the Status, and `board.py` shows 🔴 `inherited red`. `/chain` and the conductor ask the user (interactive) or stop and report the tests (unattended). It is never a fail, rebuild, bump, or replan. `check.py` guards the wording across the docs and scripts.

## Follow-ups
- Verifier fail on a gate that is already red at the pre-build HEAD still routes as an ordinary fail; T-0101 left the verifier unchanged, so decide whether it should route to `inherited` too.
- `fanout.py` treats a lane that ends on an `inherited red` builder like any other non-merged outcome; decide whether lane reports should name the inherited tests so the cause is visible.
