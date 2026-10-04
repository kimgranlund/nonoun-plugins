<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- AC1 (superseded opus ignored, step-1 sonnet gives `--model opus --effort medium`): pass. I ran the criterion verbatim and got rc=0. It bites: the same fixture on the `$SDLC_BASE_SHA` copy of run.sh prints `--model sonnet --effort medium`.
- AC2 (`step-10` sonnet beats `step-2` opus, verifier L2 gives `--model opus --effort high`): pass. Verbatim run rc=0. The base copy prints `--model sonnet --effort high`, so it bites.
- AC3 (guard, a builder in the task dir wins over `step-1`, so verifier L1 stays sonnet medium): pass. Verbatim run rc=0.
- AC4 (guard, a verifier at `step-2/handoff.md` with no build ignores `step-1`'s sonnet build, so it stays sonnet medium): pass. Verbatim run rc=0.
- AC5 (the new selftest run against the base-SHA plugin tree must fail with `FAIL: task dir: `): pass. Verbatim run rc=0, so the selftest exits non-zero on the pre-change run.sh and prints the `run selftest: FAIL: task dir: ` line.
- AC6 (guard, `bash plugins/sdlc-lite/scripts/run-selftest.sh`): pass. The output ends with `run selftest: PASS`. I did not run this gate at base, because it is green on the built tree.
- AC7 (run.sh header holds `step-<n>.superseded-<k>`): pass. Verbatim run rc=0. The diff shows the sentence at run.sh header lines 26-29.
- AC8 (selftest header has a line starting `# Task dir: `): pass. Verbatim run rc=0. The diff shows it at run-selftest.sh line 16.
- AC9 (the `scripts/run.sh` entry in sdlc-internals.md holds `step-<n>.superseded-<k>`): pass. Verbatim run rc=0. The diff replaces the Fable-never-verifies-Fable phrase with the specified text.
- AC10 (scope: only the three allowed files changed, no untracked files outside `.sdlc`): pass. Verbatim run rc=0. `git status` shows only run.sh, run-selftest.sh and sdlc-internals.md modified, plus untracked files under `.sdlc/`.
- Diff read of run.sh against the handoff constraints: pass.
  - The code sits inside the `{ ... }` group.
  - It uses `[[ -d ]]` and the `^step-[0-9]+$` regex.
  - The `order.py` call is guarded with `|| true` and the comparison uses `10#`.
  - The `codex_roles.resolve` comment is present.
  - There are no bash 4 features.
  - The new selftest block sits after the T-0108 skill-file check and before the plan-reviewer block, and its cases 1-8 match the handoff.
- `git diff --check`: pass. rc=0.

## Out of scope changes
None. `git diff --name-only` lists only the three allowed files. The untracked entries under `.sdlc/0195-runner-family-task-dir/step-1/` are run artifacts, which the criterion's `.sdlc` exclusion allows.

I checked one concern before filing. The run.sh header says `codex_roles.py resolve` applies the same rule on Codex, which is not true until step 2 lands. The handoff mandates that wording and says step 2 mirrors the rule, so I dropped it as a finding.

## For the next attempt
None
