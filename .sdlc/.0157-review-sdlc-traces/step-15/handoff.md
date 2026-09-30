## Task goal
A skill plus scripts/traces.py reads a project's sdlc run traces and reports inefficiencies and bugs caused by sdlc-lite, each with evidence and a proposed fix ticket.

## Step 15: Cost and transcript detectors
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add `traces/detectors/cost.py` with `detect(rows, aux, thresholds)` returning `(findings, notes)`:
- `cost-over-baseline`: per verifier-passed step, the sum of `cost_usd` over its rows divided by `aux.baseline.median_cost_per_passed_step`; fires at a ratio of at least the threshold (default 2.0) with the ratio and the step's attempt ids in the evidence; cause `skills/level-rubric/SKILL.md`; with a None baseline it emits no finding and the note `cost-over-baseline: no baseline`.
- `many-builder-attempts`: builder rows per step at or above the threshold (default 3); evidence the attempt ids; cause `skills/level-rubric/SKILL.md`.
- `polling-loop`: a transcript with at least the threshold (default 5) Bash calls whose whitespace-collapsed command is identical, or matches `^(sleep|kill -0|ls .*\.running|test -e .*\.running)`; evidence the attempt id, the call count, the seconds between the first and last such call from their timestamps, and `load` = the load1 value of an optional load series (a JSON list of [iso timestamp, load1] pairs given to ingest as `--load-series`, stored in aux) nearest the first call, else the string `unknown`; cause `agents/conductor.md`.
- `background-denial`: transcript denials whose stderr names `run_in_background`, `Agent`, or `Monitor`; evidence the attempt id and count; cause `hooks/block-background.sh`.
- `rate-limit`: `rate_limits` of at least 1; evidence the attempt id and count; layer host, cause file None.
Register the `cost` cases: a passed step costing 3x a fixture baseline fires cost-over-baseline with ratio 3.0; a transcript with 6 identical `sleep 30` calls fires polling-loop with call count 6 and `load` `unknown`; the same transcript with a load series carries the series value; a None baseline yields the `no baseline` note and no finding; a step with 3 builder rows fires many-builder-attempts; negative controls fire none; printed as `ok: cost: <detector> fires` and `ok: cost: <detector> quiet on control`.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k cost`
- `for d in cost-over-baseline many-builder-attempts polling-loop background-denial rate-limit; do python3 plugins/sdlc-lite/scripts/traces.py selftest -k cost | grep -qF "ok: cost: $d fires" || exit 1; python3 plugins/sdlc-lite/scripts/traces.py selftest -k cost | grep -qF "ok: cost: $d quiet on control" || exit 1; done`
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k cost | grep -qF 'no baseline'`
- `test -f plugins/sdlc-lite/scripts/traces/detectors/cost.py`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore)$')"`
