<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0150: Add `steps.py resume` so a resumed /chain restarts at the blocked step

## PR body
### Summary
A resumed /chain could go to the newest step that had work instead of the blocked one. `steps.py next` looks at one step directory and never chooses between steps. No script or skill text said which step a resumed chain starts from. At plan time, a task with step-1 passed, step-2 blocked and step-3 done printed `done`, `replan` and `verify L1`, so "newest step with work" picked step-3. gen-ui worked around this with a local `stepn.sh`.

This adds a read-only `steps.py resume <task dir>`. It picks the lowest-numbered non-superseded step whose `next` action is not `done`. The /chain skill now uses it and never starts from the newest or highest step directory.

### Changes
- `plugins/sdlc-lite/scripts/steps.py`:
  - New `resume <task dir>` subcommand.
  - Candidates are direct children matching `step-\d+`, sorted by integer, so step-2 comes before step-10. `step-<n>.superseded-<k>` dirs are ignored.
  - It prints the chosen step path, then the same action, `reason:` and `read:` lines as `next`.
  - When every step passed, it prints `done` and `reason: every step-<n>/ passed`.
  - A missing task dir, a task dir with no steps, or a `Fail` from `next` prints a `steps resume: ` line on stderr and exits 1.
  - It writes nothing and never reads file times.
  - Also added: a docstring entry, a Usage line, an argparse subparser, and 7 selftest cases whose names start with `resume`.
- `plugins/sdlc-lite/skills/chain/SKILL.md`:
  - New resume rule at the start of section 4: check for stale attempts and run `run_lifecycle.py recover` when explicit recovery is required, inspect the step, then run `steps.py resume`. A `replan` takes the 4.2 path.
  - `Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/run_lifecycle.py:*)` added to `allowed-tools`.
- `docs/references/sdlc-internals.md`: the `steps.py` entry documents `resume <task dir>`, and its closing sentence says /chain runs `resume` when it resumes a task.

### How each was verified
Both steps have a verifier verdict of pass.
- Step 1 (verifier L2): all 12 acceptance criteria were run as written and passed.
  - Fixtures: a blocked step-2 is chosen over a done step-3 (prints the step-2 path, then `replan`). An all-passed task prints `done`. A superseded dir is ignored and step-2 is chosen before step-10 (`build L2`). An empty task dir exits 1 with `steps resume:`.
  - Failing before the fix: at the base SHA in a throwaway worktree, `selftest | grep -c '^ok: resume'` printed 0, and `steps.py resume` failed with an argparse invalid-choice error (rc 2).
  - Negative control: the builder ran the selftest with `resume_action` patched to sort newest-first. It failed on the blocked-step case and the step-10 case.
  - Scope: the scope guard shows only the three files above changed outside `.sdlc`.
- Step 2 (gates, verifier L1): the builder changed nothing because all gates were already green. The verifier re-ran them and all exited 0.
  - `bash plugins/sdlc-lite/scripts/check.sh`
  - `python3 scripts/check-packaging.py`
  - `codex_roles.py generate --check`
  - `git diff --check` against the base SHA
  - the `^ok: resume` selftest check, which the verifier also saw fail at base

Not verified:
- No live resumed /chain run was done. The SKILL.md rule is conductor prose, and the checks cover the script and the contracts only.
- shellcheck is not installed on the host, so that part of `check.sh` was skipped.

## Changelog entry
- Added `steps.py resume <task dir>`. A resumed /chain now restarts at the lowest-numbered unfinished step, such as a blocked one, instead of the newest step. The /chain skill and the SDLC internals doc describe the new step.

## Follow-ups
- decide: The ticket's Repro and Actual were placeholders, and gen-ui's lane logs and `stepn.sh` were never available. If gen-ui's conductor picked the right step dir and `next` misread it, this fix does not cover that case. Someone should compare against the gen-ui evidence.
- note: The resume rule in the chain skill (including running `run_lifecycle.py recover` first) is prose. No automated check proves a conductor follows it before `resume`.
- note: shellcheck is not installed on the host, so `check.sh` skipped that part and it stayed unverified.
