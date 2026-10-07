<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0195: Runner: verifier family rule for a task-dir verifier

## PR body
### Summary
The verifier model-family rule only read builder results in the verifier's own handoff directory. A verifier launched at the task directory found none, so the rule never fired. A Sonnet-built step could then be verified by Sonnet. This change makes the rule fire for a task-dir verifier on Claude (`run.sh`) and on Codex (`codex_roles.resolve`).

The rule is now:
- The handoff directory's own newest builder result still wins, as before.
- If it has none, the rule reads the newest builder result from the highest-numbered live `step-<n>/` child that holds one.
- `step-<n>.superseded-<k>/` directories are ignored.
- Step order is numeric, so `step-10` beats `step-2`.

Model and effort defaults are unchanged. There is no version bump, tag, push or publish.

### Changes
- `plugins/sdlc-lite/scripts/run.sh`: a fallback in the verifier family block, plus the header "Family rules" paragraph.
- `plugins/sdlc-lite/scripts/run-selftest.sh`: a new task-dir block with 8 cases, plus a `# Task dir:` header paragraph.
- `plugins/sdlc-lite/scripts/codex_roles.py`: `resolve` applies the same step-dir fallback for a verifier. It carries a comment naming `run.sh` as its Claude twin.
- `plugins/sdlc-lite/scripts/codex-selftest.py`: new `test_verifier_task_dir_reads_newest_live_step_builder` with 5 sub-cases.
- `docs/references/sdlc-internals.md` and `docs/references/codex-role-execution.md`: guidance updated for the new rule.
- `docs/reports/runner-family-task-dir-live-run.md`, `docs/reports/runner-family-task-dir-live-run/` and one `docs/README.md` index line: the live-run report and its evidence.

### How each step was verified
Each step passed an independent verifier.

- Step 1 (Claude rule and selftest), verifier L2: pass.
  - A superseded Opus build is ignored, so a Sonnet verifier is moved to Opus.
  - `step-10` beats `step-2`.
  - A builder in the task dir itself still wins.
  - A verifier at a step dir does not read other steps.
  - The new selftest, run against the pre-change plugin tree, exits non-zero with `FAIL: task dir: `.
  - `run-selftest.sh` passes.
- Step 2 (Codex `resolve`), verifier L1: pass.
  - A task-dir argument now names the alternate model; before, `shared` was false with no builder.
  - Superseded dirs and numeric order behave as designed.
  - The Codex dry run prints `--model gpt-6.1-sol --effort low`.
  - The new test fails on the base code and passes on the built tree.
  - The full `codex-selftest.py` passes (23 tests).
- Step 3 (live run and report), verifier L1: pass.
  - The live run on a throwaway project ran the builder on Sonnet and the verifier on Opus (`claude` 2.1.286).
  - The negative control comes from the pre-fix commit 171e13b. The first attempt used the step-2 checkpoint, which already held the fix, so that control did not discriminate. It was replaced, and no live role was rerun.
  - Dry run at 171e13b prints `--model sonnet`. Dry run on the fixed `run.sh` prints `--model opus`.
  - The report records the `run.sh` blob e5308edf and the pre-fix blob dc34865e, and has `Result: pass`.
  - The `docs/README.md` change is exactly one added line.
- Step 4 (full gates), verifier L1: pass. `bash plugins/sdlc-lite/scripts/check.sh`, `python3 scripts/check-packaging.py` and `tickets.py --root .sdlc check` passed. The whole-task `git diff --check` and em-dash check against 171e13b passed, and the scope guard was clean.

Not run:
- The step-4 verifier did not re-run `check.sh` as a whole. It ran each command separately.
- The shellcheck pass inside `check.sh` was skipped because shellcheck is not installed on this host.

### Not checked
- No live Codex run was done. The Codex path is covered by `codex-selftest.py` and the `run.sh` Codex dry run only. The handoff asked for a live run on the Claude path only.

## Changelog entry
- sdlc-lite: the verifier model-family rule now fires for a verifier launched at the task directory. When the handoff dir holds no builder result, it reads the newest builder result from the highest-numbered live `step-<n>/` and skips `step-<n>.superseded-<k>/`. A Sonnet or Fable build is therefore verified on Opus on both Claude (`run.sh`) and Codex (`codex_roles.resolve`).

## Follow-ups
- decide: `steps.py split --only` has a 300 s default guard timeout, but `check.sh` took 417 s on this host. Nothing in the chain skill or the agents says to pass `--guard-timeout` (grep of `plugins/sdlc-lite/skills` and `plugins/sdlc-lite/agents` for `guard-timeout` printed nothing). Plans with a `check.sh` guard criterion hit the plan-defect refusal. The plan reviewer's step-4 finding in this task was this case.
- note: shellcheck is not installed on this host, so the shellcheck pass in `check.sh` was skipped and `run.sh` and `run-selftest.sh` were not shellchecked.
- note: the first step-3 attempt's throwaway temp dir `/var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/tmp.PDQbvWuqBm` still exists outside the repo. The builder's cleanup was denied by permissions.
