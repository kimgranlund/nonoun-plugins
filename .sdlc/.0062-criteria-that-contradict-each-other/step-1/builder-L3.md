<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/steps.py`: I split span extraction into `line_spans`, which both `command_spans` and the new `guard_spans` call, so both paths see the same spans. Added `is_guard_line`, `guard_skipped` (skips `HEAD^1` and `<placeholder>` spans), `guard_cwd` (git toplevel of the task dir, else the task dir) and `run_guard`. `run_guard` runs `bash -c --` with stdin from DEVNULL and `start_new_session=True`, and on timeout kills the whole process group with `os.killpg`. Added `run_guards`, which raises `Fail` with one line per red guard, an indented tail of its output, and a last line `plan defect: step <n> red guard: <span>; replan this step (/chain 3)`. `split` calls `run_guards` only when `--only` is given, after the lint, missing-step and superseded checks and before any write. Added `--guard-timeout SECONDS` (default 300; it refuses a value that is not finite or not above 0). Updated the usage docstring and added seven `(n)` selftest cases.

## Checks
- AC1 (red guard refuses, `plan defect:` last line holds the span, no `step-1`): exit 0.
- AC2 (`sleep 30` with `--guard-timeout 1` refuses, `plan defect:` last line, no `step-1`): exit 0.
- AC3 (`split --help` shows `--guard-timeout`): exit 0.
- AC4 (`selftest` has at least 6 `ok: (n)` lines): exit 0. It prints 7.
- AC5 (docstring contains `red guard`, `guard-timeout`, `HEAD^1`, `placeholder`): exit 0.
- AC6 guard (full `split` and `lint` run nothing: marker absent, the red guard does not refuse): exit 0.
- AC7 guard (`--only` with a green guard plus a `HEAD^1` guard and a `<placeholder>` guard writes the handoff): exit 0.
- AC8 guard (`python3 plugins/sdlc-lite/scripts/steps.py selftest`): PASS, exit 0.
- AC9 guard (`plugins/sdlc-lite/scripts/check.sh`): exit 0. Every selftest passed, plus shellcheck and plugin validate.
- Extra (a pipeline guard `sleep 30 | cat` with `--guard-timeout 1`): refused after 1s, so the process-group kill works.
- Negative control 1 (guard call disabled): the red, green and timeout `(n)` cases failed. After restoring, PASS.
- Negative control 2 (skip rule disabled): the `HEAD^1` and placeholder `(n)` cases failed. After restoring, PASS.

## Notes
- When several guards are red, all of them run and the one `plan defect:` last line names each as `step <n> red guard: <span>`, joined by `; `.
- The existing `PLAN_DEFECT` constant for the lint refusal is unchanged.
- The `.sdlc/0062-criteria-that-contradict-each-other/handoff.md` change in `git status` was already there before this run. I did not touch it.
- The doc updates (CLAUDE.md, the author agent, `/chain`, check.py) belong to step 2 and were not made here.
