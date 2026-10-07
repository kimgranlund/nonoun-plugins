<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0155: Tag fanout lane and gate log lines with a per-run id

## PR body
### Summary
Every fanout lane and gate log line now carries the id of the fanout run that wrote it. After a resume, a line left by an earlier stopped run no longer reads as a new failure.

The ticket said to use `SDLC_ATTEMPT_ID`. This change does not, and the plan gives the reason. `run_lifecycle.py` sets that variable only for a `run.sh` role process, and a fanout run is not a role attempt. If a builder or verifier ran `fanout.py selftest`, it would inherit one id. Two fanout runs would then share it, and a resumed run could not be told apart. Fanout instead mints its own id, `fanout-<12 hex>`, on every non-dry run. This is the ticket's "separate identifier for fanout lines that have no role attempt". Role attempt ids in `*.attempt.json` and `runs.jsonl` are untouched.

### Changes
- `plugins/sdlc-lite/scripts/fanout.py`:
  - Each non-dry run mints `ctx['run_id']`. It never reads `SDLC_ATTEMPT_ID`.
  - `say()` prints `[<run_id>] [<lane>] <id> <event>`. It also appends the same line to `<lanes-dir>/logs/fanout.log`, which is append-only, so earlier runs' lines survive a resume.
  - A new `run_logged` helper writes the driver log and each gate log line by line as `[<run_id>] <line>`. File names and the overwrite mode are unchanged.
  - `FANOUT_RUN_ID` is exported to the driver and gate environments.
  - `report.md` gains a `- Run:` line.
  - Selftest case 9 (`resume case`) is added, and the module docstring is updated.
- `docs/references/sdlc-internals.md`: the fanout entry now states the prefix, `logs/fanout.log`, `FANOUT_RUN_ID`, and why fanout mints its own id.
- `plugins/sdlc-lite/skills/fanout/SKILL.md` is unchanged. It does not describe the line or log format.

### How each step was verified
The verifier's verdict was pass. It ran every criterion independently.
- The resume probe from the plan exited 0. `logs/fanout.log` held run A `fanout-a3c7344f336d` with `driver failed rc=3` and run B `fanout-72f8e278fa44` with `merged`. The base code has no `FANOUT_RUN_ID`, so the probe cannot pass there.
- The greps for `resume case` and `FANOUT_RUN_ID` in `fanout.py` and for `logs/fanout.log` and `FANOUT_RUN_ID` in `sdlc-internals.md` all passed.
- Negative control: with a constant id, `fanout.py selftest` failed on `resume case: the two runs have distinct ids`. The builder ran it, and the verifier reproduced it on a copy of the scripts. With the uuid restored, selftest passes.
- The scope guard passed: only `fanout.py` and `sdlc-internals.md` changed.
- `fanout.py selftest` printed PASS.
- `check.py` printed `ok: 18 role levels, 8 agents checked`.
- `check.sh` printed `ok: plugin validate` and skipped shellcheck because it is not installed. The verifier lost the exit status to a zsh pipe. The output shows no failure and the builder reports rc=0.
- `check-packaging.py` printed PASS.
- `git diff --check` was clean.

Not run: shellcheck (not installed). No live host run was made.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Fanout lane and gate log lines now start with a per-run `[fanout-<id>]` prefix, and `logs/fanout.log` keeps every run's lines. A resumed run's lines are distinguishable from those of the earlier stopped run. `FANOUT_RUN_ID` is exported to drivers and gates, and `report.md` records the run id.

## Follow-ups
- decide: The ticket says to use `SDLC_ATTEMPT_ID`, but fanout mints its own `fanout-<hex>` id, so T-0157's join by attempt id needs a rule for how fanout run ids relate to role attempt ids.
- note: Lane and gate log files are still overwritten on resume, and only `logs/fanout.log` keeps history. T-0156 owns per-attempt gate logs and may rename the `gate-<lane>-<id>-<k>.log` path the probe reads.
- note: Driver and gate log lines now carry a `[<run_id>] ` prefix that T-0157's trace ingest must strip. Nothing in the repo parses lane logs today.
