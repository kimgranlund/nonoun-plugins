<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- Blocked step-2 fixture (line 1 is `$t/step-2`, line 2 is `replan`): pass. Evidence: ran as written, rc 0. Output was `<t>/step-2`, `replan`, `reason: newest builder builder-L2.md is blocked ...`, `read: .../step-2/builder-L2.md`.
- All-passed fixture prints `done` on line 1: pass. Evidence: ran as written, rc 0.
- Superseded dir plus step-10 fixture (`step-2`, then `build L2`): pass. Evidence: ran as written, rc 0.
- Empty task dir gives rc 1 and `^steps resume: `: pass. Evidence: rc 0 from the whole check. stderr was `steps resume: <t> has no step-<n>/ dirs; run steps.py split <t> first`.
- `selftest | grep -q '^ok: resume'`: pass. Evidence: exit 0. There are 7 `ok: resume ...` lines. At `$SDLC_BASE_SHA` in a throwaway worktree, `grep -c '^ok: resume'` gave 0. So the check goes red without the change.
- (guard) `steps.py selftest >/dev/null`: pass. Evidence: exit 0 on the built tree. It was also exit 0 at base, so the gate is green both before and after.
- `grep -qE '^  resume ' steps.py`: pass. Evidence: exit 0. Diff line 121 is `  resume    pick the step ...`, and the Usage line has `resume <task dir>`.
- `grep -qF 'steps.py resume' chain/SKILL.md`: pass. Evidence: exit 0. The section 4 diff shows the rule.
- `grep -qF 'run_lifecycle.py recover' chain/SKILL.md`: pass. Evidence: exit 0.
- `allowed-tools` line names `scripts/run_lifecycle.py`: pass. Evidence: exit 0. The diff shows `Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/run_lifecycle.py:*)` added.
- `grep -qF 'resume <task dir>' docs/references/sdlc-internals.md`: pass. Evidence: exit 0. The `steps.py` entry has the new clause and the extended closing sentence.
- (guard) scope diff: pass. Evidence: the command returned 0. Only `steps.py`, `chain/SKILL.md` and `sdlc-internals.md` changed outside `.sdlc`.
- Runtime behavior beyond the fixtures: pass. Evidence:
  - At base, `steps.py resume <dir>` gave an argparse `invalid choice: 'resume'` error with rc 2, so the new behavior is red without the change.
  - `resume_action` in `steps.py` uses `STEP_DIR_RE.fullmatch` and sorts by integer n. It reads no file times and writes nothing; the selftest asserts the snapshot is unchanged.
  - The recover step names `run_lifecycle.py recover`, which exists at `scripts/run_lifecycle.py:54`. `handoff-format/run-operations.md` also exists.
  - `git diff --check` was clean. `scripts/check-packaging.py` printed PASS.

Steelman: I drafted a fail on "the selftest cases could be vacuous". The builder would answer that the fixtures use real `next_action`, and I confirmed the base run has 0 resume cases. The check bites. Dropped.

## Out of scope changes
None. The `.sdlc/0150-resume-from-blocked-step/` artifacts are excluded by the scope guard and are runner-owned.

## For the next attempt
None
