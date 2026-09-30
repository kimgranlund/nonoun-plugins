## Task goal
A skill plus scripts/traces.py reads a project's sdlc run traces and reports inefficiencies and bugs caused by sdlc-lite, each with evidence and a proposed fix ticket.

## Step 3: Run-row reader
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add `traces/sources/runs.py`: `read(dir)` returns the good JSON object lines of `<dir>/runs.jsonl` through `order.records(dir)` (each dict plus `index` and `path`) and `skipped`, the count of lines that are not JSON objects (count them yourself; `order.records` drops them silently); a missing file gives no records and 0 skipped. Fields kept per record: ts, role, level, model, effort, file, attempt_id, backend, cost_usd, duration_ms, turns, stray_worktrees, stray_branches, routing_reason (lists default to empty, the rest to None). Register the `runs` cases: a legacy row with neither attempt_id nor file, a row with both, and a malformed line read as two records and one skipped line; a missing runs.jsonl reads as no records.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k runs`
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k runs | grep -q '^ok: runs: '`
- `test -f plugins/sdlc-lite/scripts/traces/sources/runs.py`
- `grep -q 'order.records' plugins/sdlc-lite/scripts/traces/sources/runs.py`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore)$')"`
