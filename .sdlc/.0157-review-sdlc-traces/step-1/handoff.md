## Task goal
A skill plus scripts/traces.py reads a project's sdlc run traces and reports inefficiencies and bugs caused by sdlc-lite, each with evidence and a proposed fix ticket.

## Step 1: Row schema, entry script, and selftest runner
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Create the package `plugins/sdlc-lite/scripts/traces/` (with `__init__.py`) and the thin entry `plugins/sdlc-lite/scripts/traces.py`. The host python3 is 3.9.6: no `match` statements, no `X | Y` type unions, no parenthesized context managers. The entry inserts its own folder at the front of `sys.path` and calls `traces.cli.main(sys.argv[1:])`; a package dir wins over a same-named module (verified on this host), so `import traces` inside the entry resolves to the package (keep `__init__.py`). Import the sibling scripts the way `board.py` and `fanout.py` do (`import steps`, `import order`, `import tickets` from the scripts folder) and never re-implement what they export.

`traces/table.py`: `ROW_FIELDS`, in this order: attempt_id, ticket, task_dir, step, superseded, role, level, attempt_k, status, verdict, plan_defect, turns, cost_usd, secs, tool_calls, denials, rate_limits, exit_code, sources. `join(dir_rel, attempts, runs, results, ticket=None)` returns one row dict per attempt for one handoff dir from already parsed records (the readers of steps 2 to 5 produce them; this step takes plain dicts): an attempt record is the `*.attempt.json` dict plus `path`; a run record is the `runs.jsonl` dict plus `index` (its line number) and `path`; a result record is `{name, status, verdict, plan_defect, ...}` for one result file (name without `.md`). Rules: a run record joins the attempt with the same `attempt_id`; a run record with no `attempt_id` but with `file` joins the attempt whose `name` plus `.md` equals `file`; a run record that joins nothing becomes its own row with `attempt_id` = `legacy:<dir_rel>/<file>`, or `legacy:<dir_rel>/runs.jsonl#<index>` when it has no `file`, `status` `completed`, `exit_code` None; a result record joins the row whose `name` matches; `step` is the integer n of a `step-<n>` or `step-<n>.superseded-<k>` dir name (None for a task-level dir) and `superseded` is True for the latter; `attempt_k` is the k in `<role>-L<n>-<k>` (1 when absent); `secs` is `duration_ms / 1000` from the run record, else `finished_at` minus `started_at` from the attempt record; `sources` lists every file path that fed the row, relative to the analyzed repo. Every row holds every field of `ROW_FIELDS` (None when unknown).

`traces/selftest.py`: a registry of named cases `<family>: <detail>`; `run(family=None)` runs every case, or only the cases whose family (the text before the first colon) equals `family`, prints `ok: <name>` per passing case and `skip: <name>: <why>` for a case that cannot run on this host, then `traces selftest: PASS` (exit 0), or the misses and `traces selftest: FAIL` on stderr (exit 1); with no matching case it prints `traces selftest: no selftest case matches <family>` on stderr and exits 1. Each case builds its fixtures in a `tempfile` dir and never writes into the repo. `traces/cli.py`: `main(argv)` with only the `selftest [-k FAMILY]` subcommand for now (step 16 adds the rest); an unknown subcommand prints usage and exits 2.

Register the `join` cases: an attempt joins its run record by attempt_id; a legacy record joins by result name in the same dir; an orphan record gets `legacy:<relpath>`; every row has every field of ROW_FIELDS; `step`, `superseded`, and `attempt_k` come from names. Add `__pycache__/` to the root `.gitignore` so a bytecode dir never shows as an untracked file in scope checks.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k join`
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k join | grep -q '^ok: join: '`
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k nonesuch 2>&1 | grep -q 'no selftest case matches'`
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k nonesuch 2>/dev/null; test $? -eq 1`
- `test -f plugins/sdlc-lite/scripts/traces/__init__.py`
- `python3 -c "import sys; sys.path.insert(0, 'plugins/sdlc-lite/scripts'); import traces.table as t; assert list(t.ROW_FIELDS) == ['attempt_id', 'ticket', 'task_dir', 'step', 'superseded', 'role', 'level', 'attempt_k', 'status', 'verdict', 'plan_defect', 'turns', 'cost_usd', 'secs', 'tool_calls', 'denials', 'rate_limits', 'exit_code', 'sources']"`
- `grep -qxF '__pycache__/' .gitignore`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore)$')"`
