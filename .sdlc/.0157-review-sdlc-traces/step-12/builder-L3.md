<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/traces/detectors/__init__.py`: new package with a docstring for the detector contract and family list.
- `plugins/sdlc-lite/scripts/traces/detectors/thresholds.py`: new. Holds the single `THRESHOLDS` dict (replan counts, bump distance, the exit-3 code, a `severity` table per finding kind) and `merged(overrides)`.
- `plugins/sdlc-lite/scripts/traces/detectors/escalation.py`: new. `detect(rows, aux, thresholds=None)` runs the ten detectors, and every finding is built with `findings.make`.
- `plugins/sdlc-lite/scripts/traces/selftest.py`: adds the `escalation` family: 10 `fires` cases, 10 `quiet on control` cases (each control is the same fixture with the defect flag off), and 2 extra cases (plan-defect rule grouping plus a verifier plan defect; dead vs live `owner_pid`).

## Checks
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k escalation`: exit 0, 22 `ok:` lines, PASS.
- AC2 loop over the 10 detector names (`fires` and `quiet on control`): exit 0.
- `test -f .../thresholds.py && test -f .../escalation.py`: exit 0.
- (guard) scope command with `$SDLC_BASE_SHA`=7334f49: exit 0.
- `python3 plugins/sdlc-lite/scripts/traces.py selftest` (whole suite): exit 0, 51 `ok:` lines, PASS.
- Negative controls (throwaway in-process mutations, nothing written):
  - With every detector replaced by a no-op, all 10 `fires` cases plus both extra cases fail.
  - With every detector's output doubled, all 10 "want 1 finding" checks fail.
  - Setting `exit_code_missing_section` to 0 makes `exit-3-result quiet on control` fail.
- Corpus smoke run (ingest of this repo into a mktemp out dir, then `escalation.detect`): 861 rows, 29 findings (14 plan-defect-refusal, 13 replan-loop, 2 attempt-without-run-row). All four step-17 targets are present: `.0109` handoff, `.0134` step-1 verifier-L1, `.0113` step-2.superseded-1/builder-L2.md, and the `.0162` step-6 attempt id. This live builder's running attempt (owner pid alive) was not flagged.
- `git diff --check`, plus a trailing-whitespace grep over the untracked plugin files: clean.

## Notes
- **Status field:** a row's `status` is the attempt lifecycle status (running, completed, failed), and `table.join` never copies a builder's result Status into the row. So `statusless-builder` and the "blocked" test in `wrong-resume-order` read the builder Status from the result file named in the row's `sources`, through `steps.build_status_or_none`. `statusless-builder` and `no-verdict-verifier` fire only when a result file exists, so a running or crashed attempt with no output is not flagged. The module docstring states this.
- **Raw reads:** besides the task `handoff.md` and result files, the detectors open `.attempt.json` files named in `sources` (for `started_at`, `finished_at`, `owner_pid`) and list row dirs for `.running` markers. Result ordering goes through `order.ordered`, `order.newest` and `order.counts_after`. The repo root comes from `aux["repo"]`.
- **Choices the handoff left open:**
  - A Plan review "entry" is a bullet, or a paragraph together with its fenced blocks.
  - An entry that names several lint rules is counted under each rule, with one finding per (handoff, rule) group.
  - `wrong-resume-order` gives one finding per (blocked step n, later step m), using the earliest later attempt.
  - Replans are counted as max(planner rows - 1, superseded dirs).
  - Severities live in `THRESHOLDS['severity']`.
  - When a `.running` marker's role-level has no attempt record, the detector skips it.
