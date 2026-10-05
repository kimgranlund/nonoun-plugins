# Solo cost capture live run

Recorded: 2026-10-05. Live run for ticket T-0225: a real headless solo session, started through `scripts/solo_run.py`, wrote one `role solo` record to the ticket's `runs.jsonl` whose cost matches the session's own result event, and `budget.py` and the board counted it. One arm, one machine, Claude Code only.

## Environment

- `claude --version`: `2.1.289 (Claude Code)` ([`claude-version.txt`](solo-cost-live-run/claude-version.txt)).
- Model, from the result event's `modelUsage` ([`raw-result.json`](solo-cost-live-run/raw-result.json)): `claude-sonnet-5-5`. Effort `low` comes from the launch flag the wrapper passes for tier S, and the record says the same (`"effort":"low"`).
- Plugin: this worktree's `plugins/sdlc-lite` at the T-0225 step commit (`b6cf1a5` plus the `--raw-out` option added after it, which the run used). Not a released version.
- macOS, one throwaway Git project from `mktemp -d` outside this repository. The run's start and end times are in [`start.txt`](solo-cost-live-run/start.txt) and [`end.txt`](solo-cost-live-run/end.txt): 18 seconds.
- Nested-session variables (`CLAUDECODE`, `CLAUDE_CODE_*`, `CLAUDE_PLUGIN_ROOT`, and the other session ids) were removed with `env -u` before the launch, because this run was itself started from a Claude Code session. `SDLC_HEADLESS=1` and the 3600000 ms Bash timeouts were set, as `fanout.py` and the bench set them.

## Method

Fixture ([`fixture/`](solo-cost-live-run/fixture)): a project with `util.py` (one function, `whisper`), `tests/test_util.py` (one test), and a size S ticket `.sdlc/shout/handoff.md` with `budget_usd: 5` that asks for `shout(s)` returning the text in upper case followed by `!`, plus one test. A hidden check ([`fixture/hidden_check.py`](solo-cost-live-run/fixture/hidden_check.py), 3 cases) sat outside the project and no prompt named it.

Command, from the project root:

```
python3 <plugin>/scripts/solo_run.py run --task-dir .sdlc/shout --tier S --brief "<typed brief>" \
  --cwd <project> --timeout 900 --raw-out ../raw-result.json
```

The wrapper started `SDLC_ROLE=solo claude -p --plugin-dir <plugin> --agent sdlc-lite:solo --model sonnet --effort low --dangerously-skip-permissions --output-format json -- <brief>`.

## Result

| Check | Evidence | Outcome |
| --- | --- | --- |
| Session | [`report.txt`](solo-cost-live-run/report.txt), [`rc.txt`](solo-cost-live-run/rc.txt) | exit 0; the agent reported the change and its test run |
| Hidden check | [`hidden-check.txt`](solo-cost-live-run/hidden-check.txt) | `hidden_check: 3/3 passed` |
| Change | [`solo-session.patch`](solo-cost-live-run/solo-session.patch) | `util.py` and `tests/test_util.py` only (trailing whitespace on blank context lines stripped so `git diff --check` is clean) |
| Record written | [`runs.jsonl`](solo-cost-live-run/runs.jsonl) | one line: `role` `solo`, `level` `L1`, `model` `sonnet`, `effort` `low`, `backend` `claude`, an `attempt_id` |
| Cost matches the result event | `raw-result.json` against `runs.jsonl` | `total_cost_usd` 0.1315212 equals `cost_usd` 0.1315212 |
| Usage, turns, duration copied | same two files | `output_tokens` 1163, `turns` 9, `duration_ms` 14996 on both sides |
| Budget counts it | [`budget-status.txt`](solo-cost-live-run/budget-status.txt) | `spend: 0.13`, `budget: 5`, `percent: 2`, `state: ok`, `unmetered_runs: 0` |
| Board counts it | [`board.txt`](solo-cost-live-run/board.txt) | Budget column `$0.13/$5 2%` |

`footprint.py` on the ticket folder counted `role_runs solo L1: 1` (not saved as a file; the command is `footprint.py .sdlc/shout`).

The selftest ([`solo_run.py selftest`](../../plugins/sdlc-lite/scripts/solo_run.py), part of `check.sh`) covers the paths this live run does not: a result with no `total_cost_usd` records `cost_usd` null with `cost_reason` and the budget reports the run as unmetered (never zero); a crash with no result event still writes a record; an `is_error` result exits 1; Codex records null with `codex reports no cost`; refusals write nothing; and two solo runs of 8.5 dollars each on a 10 dollar budget go from `warn` at 85 percent to `over`. Three mutants each made it fail: a missing cost recorded as zero, no record written on a crash, and a wrong tier effort.

## Limits

- The first branch verifier found that the wrapper reused an inherited `SDLC_ATTEMPT_ID`, which made `budget.py` skip a second solo record as a duplicate and undercount spend (two 3.25 runs metered 3.25). The wrapper now always mints its own attempt id and ignores an inherited routing reason; the selftest runs with both variables set and has a negative control. The live run above ran before that fix with no inherited id, so it did not exercise the path.
- One run, tier S, Claude Code. No tier M or L run, and no Codex run: `codex_exec.py` reports no cost, so a Codex solo records `cost_usd` null by design.
- Fanout's solo driver still starts the raw command, so fanout solo lanes are not metered yet. The conductor path is metered only when the conductor uses the wrapper; `agents/solo.md` now names it as the start path, and the raw command stays as an unmetered fallback.
- The verifier, if any, is a separate `run.sh verifier` run with its own record. The solo's own session cost covers the solo only.
- The budget meter still covers Claude roles only; a Codex solo counts as an unmetered run.
- `check.py` guard 25 ties `solo_run.py` TIERS to `agents/solo.md` and `fanout.py`; the guard number may be renumbered at merge if other work has taken 25.
- Evidence is from the wrapper's own output plus the result event it saved with `--raw-out`; nothing else was captured from the session.
