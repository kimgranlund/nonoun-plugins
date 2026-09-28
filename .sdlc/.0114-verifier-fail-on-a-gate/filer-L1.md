<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0114: Route a verifier "inherited red" verdict to `inherited`, not a rebuild or replan

## PR body
### Summary
A gate that was already red at the pre-build HEAD now counts as inherited whether the builder or the verifier finds it. A verifier that finds one reports `## Verdict` as `inherited red: <tests>`. That verdict routes to `inherited`. It is never a rebuild, a level bump, a replan, or a reverify. T-0101 did this for the builder only. The verifier used to send "findings that predate the build" to `plan defect:`, which triggers a planner L3 replan. Any other red gate became an ordinary fail, which meant a rebuild and then a bump.

`pass`, `fail`, and the builder's inherited-red path parse and route as before.

### Changes
Step 1, scripts:
- `steps.py`: `verdict_or_none` returns `inherited` when the first line under `## Verdict` starts with `inherited red:` (any case). `next_action` returns `inherited` for a newest verifier that counts after the build.
  - An inherited verdict never counts as a fail.
  - It breaks a run of consecutive no-verdict results.
  - A bare `inherited red` with no colon stays a no-verdict and maps to `reverify`.
  - Docstring rules updated, five selftest cases added.
- `board.py`: `step_row` renders 🔴 `inherited red · builder <L> · verifier <L>, ask the user`. The no-verdict loop treats `inherited red:` as a verdict. Docstring updated, selftest case added.
- `run.sh`: the verifier's required Verdict value is now `pass|fail|inherited red: .+`, and the header comment is updated.
- `run-selftest.sh`: a case where `inherited red: test_a` exits 0, and a case where a bare `inherited red` exits 3.

Step 2, docs and guards:
- `agents/verifier.md`:
  - New procedure item: before failing a gate criterion, run it at the pre-build HEAD (`HEAD^1` on a merge step).
  - The verdict is `inherited red: <tests>` only when every failing criterion is an inherited gate.
  - The "predate the build" clause is removed from `plan defect`.
  - The Verdict line is now `pass | fail | inherited red: <tests>`.
- `skills/chain/SKILL.md` (step 4 and rule 7), `agents/conductor.md`, `CLAUDE.md`, and `.claude/agents/sdlc-lite-author.md` name the verifier verdict and its routing.
- `check.py`: `agents/verifier.md` is added to `INHERITED_RED_DOCS`, so the guard fails if the doc loses the phrase.
- `skills/handoff-format/SKILL.md` lists no Verdict values, so it is unchanged.

### How each step was verified
Step 1 (builder L3, verifier L2 on Sonnet high): pass.
- The verifier ran the criteria verbatim.
- It confirmed the new checks go red on HEAD: the same fixture printed `reverify L1` in `steps.py next`, and `board.py` gave 🟡 `no verdict`.
- It copied the changed `run-selftest.sh` onto HEAD's `run.sh`, which failed with exit 3 where 0 was wanted.
- The steps.py, board.py, and run-selftest.sh selftests and `scripts/check.sh` passed.

Step 2 (builder L2, verifier L1): pass.
- The grep criteria for each doc passed.
- A mutation probe on a temp copy of `verifier.md` (`inherited red` replaced by `INHERITED`) made the `check.py` guard print `agents/verifier.md: inherited-red`.
- The old "predate" clause was confirmed removed from the plan-defect line.
- `scripts/check.sh` passed as a guard (all selftests, shellcheck, and `claude plugin validate`).
- The step 2 verifier did not read the CLAUDE.md, conductor.md, chain, or author-file diffs beyond the grep criteria.

## Changelog entry
- Verifier: a gate already red at the pre-build HEAD is now reported as `inherited red: <tests>` and routes to `inherited` (no rebuild, bump, replan, or reverify). `steps.py next`, `board.py`, and `run.sh` accept it, and `check.py` guards the docs. The "findings that predate the build" clause no longer maps to `plan defect:`.

## Follow-ups
- fanout.py `inherited_red()` reads the tests from the newest builder's `## Status`, so a verifier-inherited step reports `inherited red: step-<n>: done` and names the wrong tests; read them from the verifier Verdict when that is newer.
