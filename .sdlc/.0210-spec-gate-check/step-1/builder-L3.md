<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/steps.py`: added `GUARD_TIMEOUT_RE`, `DEFAULT_GUARD_TIMEOUT`, `guard_timeout_in`, `plan_guard_timeout(plan)` and `step_guard_timeout(block)`. `split`/`cmd_split` now take `guard_timeout=None`, and each step resolves its timeout in this order: explicit flag, then the step's line, then the plan's line, then 300. `run_guards` takes a `{n: seconds}` dict and the red line format is unchanged. `--guard-timeout` defaults to None and an explicit value is still checked. Help text and the module docstring are updated, and there are three new `(guard timeout)` selftest cases.
- `plugins/sdlc-lite/scripts/specgate.py` (new, executable): `check` and `selftest`. It uses `import steps` and calls only steps.py's parser functions. It reports the three finding kinds, the skip and missing-target exits, the 11 labelled selftest cases, and the verbatim T-0183 and T-0195 replay fixtures.
- `plugins/sdlc-lite/scripts/run.sh`: added the plan-reviewer spec gate just before the `run_lifecycle.py` exec. It skips when `SDLC_LIFECYCLE_CHILD=1`, runs on dry runs too, and respects `SDLC_SPECGATE=off`. The run line gets `specgate: "off"` only for plan-reviewer with the gate off. The header gains the exit-2 note, a Spec gate paragraph and the env note.
- `plugins/sdlc-lite/scripts/run-selftest.sh`: added spec gate cases with `spec gate: <reason>` failures and a header paragraph. The cases cover: a dry run refused with exit 2, a real run refused with no stub call, no runs.jsonl, no .running and no attempt record, a plan with a timeout line passing silently, an off run exiting 0 with `"specgate":"off"`, and a planner run line with no specgate key.
- `plugins/sdlc-lite/scripts/check.sh`: added the `specgate.py selftest` line after footprint and named specgate.py in the header list.

## Checks
- All 12 acceptance criteria, each span run verbatim under `bash -c` with `SDLC_BASE_SHA` from step-1/base-sha: all 12 exit 0, including both `(guard)` criteria.
- `python3 plugins/sdlc-lite/scripts/specgate.py selftest`: all 11 labels ok, `specgate selftest: PASS`.
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: `steps selftest: PASS`, including the three `(guard timeout)` labels. Rerun after loosening the timing bound: PASS.
- `specgate.py check` on real plans:
  - 0195 planner-L3-2.md: exit 1, step 4 slow guard.
  - 0184 planner-L2.md: exit 1, step 7 slow guard only.
  - 0197 planner-L3.md: exit 1, step 3 slow guard only.
- `bash plugins/sdlc-lite/scripts/run-selftest.sh`: `run selftest: PASS`.
- Negative control: I ran run-selftest.sh against a temp copy of the plugin with the gate condition replaced by `if false`. It failed with `run selftest: FAIL: spec gate: dry run on a check.sh guard with no guard timeout line exited 0, want 2`.
- `python3 plugins/sdlc-lite/scripts/codex-selftest.py`: passed, as part of guard criterion 12.
- `bash plugins/sdlc-lite/scripts/check.sh`: rc 0. Every selftest prints PASS, `ok: plugin validate`, `skip: shellcheck not installed`.
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: ok.
- `git diff --check`: clean. No em dash in the diff or in specgate.py.
- `steps.py split --help`: the new `--guard-timeout` help renders cleanly.
- `specgate.py check .sdlc/0210-spec-gate-check`: `specgate: ok: .../planner-L2.md`, exit 0.

## Notes
- The handoff's T-0183 line numbers are off by one: line 341 is the `### Acceptance criteria` heading. I copied each step's full criteria block instead: step 2 lines 281-288, step 3 lines 342-346, step 7 line 538. The replay asserts exactly two `duplicate span` findings at step 3, both naming step 2, plus one `slow guard` at step 7.
- On this macOS host `timeout` is not on PATH, so steps.py's existing span check does not treat a span starting with the bare word `timeout` as a command. Neither `split` nor `specgate` sees it. The `timeout N` prefix in the regex therefore only applies inside a span that already counts as a command (for example `cd . && timeout 900 bash scripts/check.sh`). This is existing steps.py behavior and outside this step.
- Two docs still describe the split guard default as 300 with no mention of the `guard timeout:` line: `docs/maintenance/sdlc-internals.md:47` and `docs/lean-sdlc/cost-control.md:41`. Criterion 11's scope guard forbids editing docs in this step, so step 2 or a follow-up needs to fix them.
- If a plan has more than one `guard timeout:` line outside its step blocks, the first positive one wins. A value of 0 or less is skipped.
- When `specgate.py check` exits 0, run.sh prints nothing, including skip lines. This keeps the existing plan-reviewer dry-run and codex-selftest outputs unchanged.
- shellcheck is not installed on this host, so it did not run.
