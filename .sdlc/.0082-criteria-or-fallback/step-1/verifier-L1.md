<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `d=$(mktemp -d) && ... ! python3 steps.py lint ...`: pass. Evidence: ran verbatim, lint printed the `joins two checks with ||` finding plus `plan defect: replan this step (/chain 3)` and exited nonzero, so `! lint` succeeded (`rc-as-bool=0`).
- `... lint ... 2>&1 | grep -q "plan defect"`: pass. Evidence: ran verbatim, `rc=0`.
- `... split "$d" && test ! -e "$d/step-1"` (with `! split`): pass. Evidence: ran verbatim, split refused with the same plan-defect message (`rc-as-bool=0`), and `test ! -e "$d/step-1"` succeeded (`test-rc=0`).
- (guard) three-span lint (quoted `||`, `test $# -eq 0 ||`, `&&`) all pass: pass. Evidence: ran verbatim, output `steps lint: ok`, `rc=0`.
- (guard) `steps.py selftest`: pass. Evidence: ran `python3 plugins/sdlc-lite/scripts/steps.py selftest`, ended `steps selftest: PASS`, `rc=0`.
- `selftest` prints new `ok:` lines for the `||` refusal and for allowed forms: pass. Evidence: `grep -n "(k2)" /tmp/selftest_out.txt` shows three new lines — two for the refusal (split, lint) and one for the allowed forms (quoted `||`, `test $# -eq 0 ||`, `&&`).
- (guard) `plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: ran full `check.sh`, output ends `ok: shellcheck` / `ok: plugin validate`, `rc=0`, all selftests (`steps selftest: PASS`, `order selftest: PASS`, `fanout selftest: PASS`, `run selftest: PASS`, `hook selftest: PASS`) present.

Negative control (checks-that-bite): built a throwaway detached worktree at HEAD (pre-change `12c0c9f`) and reran criterion 1's lint command there — it printed `steps lint: ok` and exited 0 (no refusal), proving the `||`-refusal check is red without the fix and green with it. Worktree removed afterward (`git worktree remove --force`).

## Out of scope changes
`git status --short` shows only `plugins/sdlc-lite/scripts/steps.py` modified (matches the step's scope) plus untracked planner/step artifacts (`planner-L2.md`, `step-2/handoff.md`, `runs.jsonl`) that are pre-existing plan/task scaffolding for a later step, not code changes. Checked: `.sdlc/0082-criteria-or-fallback/step-2/` holds only an unbuilt `handoff.md` (no builder/verifier output), so it is planning artifact, not this step's work spilling out of scope. None.

## For the next attempt
None.
