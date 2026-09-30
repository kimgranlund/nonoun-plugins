## Task goal
A skill plus scripts/traces.py reads a project's sdlc run traces and reports inefficiencies and bugs caused by sdlc-lite, each with evidence and a proposed fix ticket.

## Step 9: Bench baseline reader
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add `traces/sources/bench.py`: `baseline(bench_dir)` returns {median_cost_per_passed_step, steps (the list of (result dir, step n, cost) that counted), hidden ({result dir: the `hidden_check:` value of `grade.md`, or None})} over `<bench_dir>/results/*/step-<n>/` (never a `.superseded-` dir): a step counts when its newest verifier (`order.newest`) has verdict pass (`steps.verdict_or_none`); its cost is the sum of `cost_usd` over that step dir's runs.jsonl; the median is None when no step counts or the results dir is missing. `default_bench_dir()` follows `scripts/bench-dir.sh`: `$SDLC_BENCH_DIR`, else `<git toplevel>/bench` when it exists, else the plugin's own `bench/`. Register the `bench` cases: two fixture result dirs with passed steps costing 1.0, 3.0, and 8.0 and one failed step costing 50.0 give median 3.0 and three counted steps; a missing results dir gives None.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k bench`
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k bench | grep -q '^ok: bench: '`
- `test -f plugins/sdlc-lite/scripts/traces/sources/bench.py`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore)$')"`
