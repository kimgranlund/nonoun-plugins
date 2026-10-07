<!-- role=planner level=L3 model=fable effort=xhigh -->
## Goal
A `review-traces` skill and `scripts/traces.py` read a project's sdlc run traces into one attempt table, run deterministic detectors over it with no model call, and drive the diagnose, verify, propose, and file stages so each confirmed sdlc-lite finding becomes a ticket only after user approval.

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

## Step 2: Attempt reader
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add `plugins/sdlc-lite/scripts/traces/sources/__init__.py` and `traces/sources/attempts.py`: `read(dir)` returns one record per `*.attempt.json` in `dir` (the parsed dict plus `path` and `marker`, True when `<role>-<level>.running` exists next to it), sorted by name; a file that is not a JSON object is skipped and named in a `problems` list the function also returns. Register the `attempts` cases: a fixture dir with completed, failed, interrupted, and running records yields one record each with its status and exit code (None for running); a record with no runs.jsonl row still yields a row through `table.join` with an empty run list; the running record with a marker next to it reports `marker` True and the others False.

The superseded attempt's `sources/__init__.py`, `sources/attempts.py`, and its three `attempts:` selftest cases are still in the tree, uncommitted: check them against this Do, fix any gap, and report done. The scope guard below allows every file steps 1 and 2 touch, because builders never commit and `$SDLC_BASE_SHA` stays the chain base, so the guard of each step sees the uncommitted files of every earlier step; the same holds for every later step's guard.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k attempts`
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k attempts | grep -q '^ok: attempts: '`
- `test -f plugins/sdlc-lite/scripts/traces/sources/attempts.py`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore)$')"`

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

## Step 4: Result reader
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add `traces/sources/results.py`: `read(dir)` returns one record per `<role>-L*.md` file in `dir`: name (without `.md`), role, level (from the name), model and effort from the first-line `<!-- role=... model=... effort=... -->` header (None when absent), `status` = `steps.build_status_or_none(path)` for a builder, `verdict` = `steps.verdict_or_none(path)` for a verifier, `plan_defect` = `steps.is_plan_defect(path)`, `swap` = `steps.swap_pair(path) is not None`, `next_note` = the first non-blank line under the For the next attempt section (a verifier) or the Notes section (a builder), `changes` = the code-span texts under the Changes section. Every section read goes through `steps.section(path, '<heading name>')` with the bare heading name; the file's text never holds the strings `## Status` or `## Verdict`, not even in a comment, so it cannot grow its own parsing of them. Register the `results` cases: builder done, blocked, `inherited red: x`, and statusless fixtures give done, blocked, inherited, and None; verifier pass, fail, and no-verdict fixtures give pass, fail, and None; a fail whose For the next attempt starts `plan defect:` gives plan_defect True; and on the same fixtures laid out as step dirs, `steps.next_action` derives the matching action (rebuild for statusless, reverify for no verdict, replan for blocked and plan defect, inherited for inherited red), so the reader classifies exactly as `steps.py next` does.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k results`
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k results | grep -q '^ok: results: '`
- `grep -q 'build_status_or_none' plugins/sdlc-lite/scripts/traces/sources/results.py && grep -q 'verdict_or_none' plugins/sdlc-lite/scripts/traces/sources/results.py && grep -q 'is_plan_defect' plugins/sdlc-lite/scripts/traces/sources/results.py && ! grep -qE "## (Status|Verdict)" plugins/sdlc-lite/scripts/traces/sources/results.py`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore)$')"`

## Step 5: Transcript reader
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add `traces/sources/transcripts.py`: `read(log_path)` parses a stream-json `.log` leniently (lines that are not JSON objects are skipped): `tool_calls` = the count of `tool_use` blocks in `assistant` events, `bash_calls` = a list of (event `timestamp`, `input.command`) for `Bash` tool_use blocks, `tool_errors` = the count of `tool_result` blocks with `is_error` true, `denials` = a list of {hook_name, stderr} from `system` events with subtype `hook_response` and `exit_code` 2, `rate_limits` = the count of `rate_limit_event` events, `result` = {total_cost_usd, duration_ms, num_turns} from the last `result` event. A missing path returns a record with every field None and raises nothing. Register the `transcripts` cases: a fixture log with 5 Bash tool_use blocks, one `hook_response` with exit_code 2 whose stderr names run_in_background, one `rate_limit_event`, and prose lines mixed in yields tool_calls 5, one denial, rate_limits 1; a missing path yields None fields.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k transcripts`
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k transcripts | grep -q '^ok: transcripts: '`
- `test -f plugins/sdlc-lite/scripts/traces/sources/transcripts.py`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore)$')"`

## Step 6: Fanout reader
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add `traces/sources/fanout.py`: `read(lanes_dir)` returns lanes-dir facts in both layouts (`scripts/fanout.py` documents them; the pre-T-0155 layout has no run-id prefixes, `gate-<lane>-<id>-<k>.log` names, and no fanout.log): `report` (the `| Lane | Ticket | Outcome | Commit |` rows of `report.md`, the `- Run:` id or None, the gate commands, the integration worktree path, the external lane branches), `fanout_log` entries (path, line number, run_id, lane, ticket, event) from `logs/fanout.log` when present, `driver_logs` (lane, ticket, path, line count, the run ids seen), and `gate_logs` (lane, ticket, k, attempt n or None for the legacy name, path, run ids seen, rc when a fanout.log or report line records `rc=<n>` for that gate). A line's run id is its `[fanout-<12 hex>] ` prefix, None without one. Register the `fanout` cases: a legacy fixture (no prefixes, `gate-alpha-T-0001-1.log`, no fanout.log, report.md without a Run line, outcome `red: ... rc=1`) and a prefixed fixture (`fanout.log`, `gate-alpha-T-0001-1-a1.log` and `-a2.log`, a `- Run:` line) both yield lane outcomes, gate attempts with rc, and per-line run ids (None for legacy, the id for prefixed).
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k fanout`
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k fanout | grep -q '^ok: fanout: '`
- `test -f plugins/sdlc-lite/scripts/traces/sources/fanout.py`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore)$')"`

## Step 7: Git reader
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add `traces/sources/git.py`: `read(repo, integration=None, limit=2000)` collects read-only facts through `git -C <repo>` subprocesses and never writes: `worktrees` from `git worktree list --porcelain` (path, branch, and `nested` True when the path holds `.worktrees/` twice or lies under `.worktrees/tmp/`), `branches` from `git for-each-ref --format=%(refname:short) refs/heads`, `tracked_runtime` = `git ls-files` paths ending in `.log`, `.running`, `.run.lock`, or `.board-state.json`, `resets` = the `reset: moving to` entries of `git reflog show HEAD` run in `integration` when given (else in `repo`), and `commits` = (sha, subject) for subjects matching `Merge <lane>: <id>`, `close <id>`, or `wip(<id>): <outcome>` from `git log --format=%H%x09%s -n <limit>`; a repo that is not a git work tree gives empty lists and a `problems` entry. Register the `git` cases on a throwaway repo (built in a temp dir; the nested `.worktrees/x/.worktrees/tmp/builder-1` worktree is made with `git worktree add --detach` from Python and removed in `finally`; the hook sees only the Bash tool text, and the throwaway repo is invisible to this repo's worktree list): a tracked `foo.log`, a `reset: moving to` reflog entry, and a `wip(T-0001): driver failed rc=3` commit each yield their fact, and after the read `git status --porcelain` output and the reflog line count equal their values before it.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k git`
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k git | grep -q '^ok: git: '`
- `test -f plugins/sdlc-lite/scripts/traces/sources/git.py`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore)$')"`

## Step 8: Ticket reader
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add `traces/sources/tickets.py` (inside the package; a plain `import tickets` there still names the scripts-folder module, since implicit relative imports do not exist): `read(root)` returns `by_slug` = {slug: (id, status)} from `tickets.load(root)` (which includes closed `.NNNN-<slug>` folders), `problems` = `tickets.problems(ts, tickets.config_numbered(root))`, `external` = `tickets.external_branches(root)`, and `notes` = True when `<root>/notes.md` exists. Register the `tickets` cases: a root with `0001-a` (T-0001, ready), `.0002-b` (T-0002, done), and `0003-c` reusing T-0001 yields slug to id and status for all three folders and exactly one problem line holding `duplicate id T-0001`; a root without a config gives `external` empty.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k tickets`
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k tickets | grep -q '^ok: tickets: '`
- `grep -q 'tickets.load' plugins/sdlc-lite/scripts/traces/sources/tickets.py && grep -q 'tickets.problems' plugins/sdlc-lite/scripts/traces/sources/tickets.py`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore)$')"`

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

## Step 10: Store, cursor, and the ingest walk
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add `traces/store.py`: `out_dir(repo, out=None)` = `out` when given, else `<cwd>/.sdlc/runtime/traces/<repo-key>/` where repo-key is `<basename of repo>-<first 8 hex of sha256 of its absolute path>`; `write_events(out, rows)` writes `events.jsonl` with rows sorted by (task_dir, step or -1, attempt name) and keys in `ROW_FIELDS` order, so an unchanged corpus gives byte-identical output; `write_aux(out, aux)` writes `aux.json` (lanes, gates, git facts, tickets, baseline, `repo` as an absolute path); `cursor.json` maps each source key (a handoff dir, a lanes dir) to its fingerprint (the sorted names with size and mtime_ns of the files in it, digested with sha256) and the rows it produced; a key whose fingerprint is unchanged is served from the cursor without opening its files; a module-level `READS` counter counts source files actually opened so the selftest can assert it. Add `traces/ingest.py`: `run(repo, lanes_dirs=(), out=None, bench_dir=None)` walks `<repo>/.sdlc/` task dirs (including `.NNNN-<slug>` closed folders; skipping `_templates`, `runtime`, and plain files) and each `step-<n>` and `step-<n>.superseded-<k>` dir under them, calls the readers of steps 2 to 5 per dir (the transcript reader on each `<name>.log` next to a result), `table.join` with the ticket id from the task dir's `handoff.md` front matter via `tickets.parse`, then the fanout reader on every given lanes dir plus each `<repo>/.worktrees/*/` that holds a `report.md` or a `logs/` dir, the git reader (integration = the report's worktree when it exists), the ticket reader on `<repo>/.sdlc`, and the bench reader on `bench_dir` or the default; it writes events.jsonl, aux.json, and cursor.json and returns the out dir. Register the `store` cases: two ingests of an unchanged throwaway corpus (a temp git repo with two task dirs holding attempt, runs, and result files) give byte-identical events.jsonl and the second opens 0 source files (READS); appending one attempt record to one dir re-reads only that dir (READS equals that dir's file count); with `out` outside the throwaway repo, its `git status --porcelain` is empty after the ingest; with no `out`, the out dir lies under `<cwd>/.sdlc/runtime/traces/` (run with cwd set to a temp dir).
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k store`
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k store | grep -q '^ok: store: '`
- `test -f plugins/sdlc-lite/scripts/traces/store.py && test -f plugins/sdlc-lite/scripts/traces/ingest.py`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore)$')"`

## Step 11: Findings writer, stable ids, and clusters
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add `traces/findings.py`: `make(detector, family, severity, layer, cause_file, cause_rule, evidence, summary)` returns a finding dict with `id` = the first 12 hex of sha256 over the detector name plus the sorted evidence keys and values, `detector`, `family`, `severity` (3 high, 2 medium, 1 low), `layer` (one of sdlc-lite, project, host, task-text, unknown), `cause_hint` {file (a plugin-relative path or None), rule}, `evidence` (a list of {path, line} or {attempt_id} entries, each allowed extra keys), `summary`; `write(out, findings, now)` merges into `<out>/findings.jsonl`: an id already present keeps its `first_seen` and gets `last_seen` = now, a new id gets both = now, an id absent from this run is kept with `stale` True; `clusters(out, max_n)` groups the non-stale findings by `cause_hint.file`, ranks clusters by highest severity then finding count, caps the list at `max_n`, writes `<out>/clusters.json`, and returns the list. Register the `findings` cases: writing the same three synthetic findings twice keeps every id and changes only `last_seen`; a finding missing from the second run is marked stale; `clusters(out, 2)` on findings over three cause files returns the two highest-severity clusters.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k findings`
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k findings | grep -q '^ok: findings: '`
- `test -f plugins/sdlc-lite/scripts/traces/findings.py`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore)$')"`

## Step 12: Escalation detectors
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add `traces/detectors/__init__.py`, `traces/detectors/thresholds.py` (one dict `THRESHOLDS`; every detector reads its numbers there), and `traces/detectors/escalation.py` with `detect(rows, aux, thresholds)` over the persisted rows, reading raw files only where a row's `sources` names them (the task `handoff.md` and the result files). Detectors, each building findings with `findings.make`:
- `replan-loop`: a task dir with two or more planner rows, or any `superseded` row; evidence: each superseded dir's newest builder or verifier result path (`order.newest`) and the planner attempt ids; severity 3 at two or more replans, else 2; cause `agents/planner.md`.
- `recurring-finding`: a `recurring finding:` line under `## Plan review` in the task handoff; evidence the path and line; cause `agents/planner.md`.
- `unchanged-verdict-bump`: in one step, a verifier fail after a build at level n, a builder at level n+1, then a verifier fail whose `next_note` (lowercased, whitespace collapsed) equals the earlier fail's; evidence both verifier paths; cause `skills/level-rubric/SKILL.md`.
- `plan-defect-refusal`: each `## Plan review` entry holding `plan defect`, grouped by the steps.py lint rule its text names (`compares a count over a changing set`, `pins a commit sha`, `joins two checks with ||`, `clean porcelain status`, `clean whole-tree diff`, `does not parse`, `Read first lists a path`, else `other`), evidence the handoff path and line, cause `scripts/steps.py` with the rule name; and each builder or verifier row with `plan_defect` True, evidence the result path, cause `agents/planner.md`.
- `wrong-resume-order`: a step n whose newest builder is blocked while a higher step m holds a builder attempt whose `started_at` is later than that blocked attempt's `finished_at`; evidence both attempt ids; cause `skills/chain/SKILL.md`.
- `exit-3-result`: an attempt with `exit_code` 3; evidence the attempt id; cause `agents/<role>.md`.
- `statusless-builder` and `no-verdict-verifier`: a builder row with status None, or a verifier row with verdict None; evidence the result path; cause `agents/builder.md` or `agents/verifier.md`.
- `attempt-without-run-row`: an attempt record with an `attempt_id` whose status is not running and that no run record joined; evidence the attempt id and its status; severity 3 for failed, 2 otherwise; cause `scripts/run.sh`.
- `stale-running-marker`: a `.running` marker whose attempt record is not `running`, or a `running` record whose `owner_pid` is not alive on this host (`os.kill(pid, 0)`, errors caught); evidence the marker path or attempt id; cause `scripts/run_lifecycle.py`.
Register the `escalation` cases: for each detector name above, one positive fixture that fires exactly one finding of that detector holding a `path` plus `line` or an `attempt_id` evidence entry and a `cause_hint.file`, printed as `ok: escalation: <detector> fires`, and a paired negative control (the same fixture minus the defect) that fires none, printed as `ok: escalation: <detector> quiet on control`.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k escalation`
- `for d in replan-loop recurring-finding unchanged-verdict-bump plan-defect-refusal wrong-resume-order exit-3-result statusless-builder no-verdict-verifier attempt-without-run-row stale-running-marker; do python3 plugins/sdlc-lite/scripts/traces.py selftest -k escalation | grep -qF "ok: escalation: $d fires" || exit 1; python3 plugins/sdlc-lite/scripts/traces.py selftest -k escalation | grep -qF "ok: escalation: $d quiet on control" || exit 1; done`
- `test -f plugins/sdlc-lite/scripts/traces/detectors/thresholds.py && test -f plugins/sdlc-lite/scripts/traces/detectors/escalation.py`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore)$')"`

## Step 13: Plan-quality detectors
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add `traces/detectors/plan.py` with `detect(rows, aux, thresholds)`, `traces/rerun.py`, and a `rerun_criteria=False` flag on `ingest.run`:
- `criteria-never-red` (only with the flag): during ingest, `rerun.run(repo, rows)` takes each step dir whose newest verifier passed and that holds a `base-sha` file, the non-guard command spans of its `handoff.md` (`steps.command_spans` minus `steps.guard_spans`, skipping spans `steps.guard_skipped` flags), and runs each with `bash -c` from a detached throwaway worktree of the analyzed repo at that base-sha (under `$SDLC_TMP_WORKTREES/traces-rerun-<pid>` when that variable is set, else under a `tempfile.mkdtemp()` dir outside the repo; `git worktree remove --force` and `git worktree prune` in `finally`), with `SDLC_BASE_SHA` set to the base-sha and a per-span timeout from thresholds (default 60 s), and stores the outcomes in aux.json under `criteria_reruns`; the detector turns each span that exited 0 at base (it never went red) into a finding with evidence the step handoff path and criterion line; cause `agents/planner.md`. Without the flag aux has no `criteria_reruns` and the detector is quiet.
- `contract-dependents`: a verifier fail row in step m whose `next_note` names a path (a code span, or a token holding `/`) that an earlier step's (n < m) done builder `changes` lists; evidence both result paths; cause `agents/planner.md`.
- `scope-prose`: two or more blocked builder rows on one step whose `next_note` names the same path, with no `scope widened:` line under `## Plan review` in the task handoff and no `## Scope widened` section in the step handoff; evidence both builder paths; cause `skills/chain/SKILL.md`.
Register the `plan` cases on a throwaway git repo: a passed step whose criterion is `test -f README.md` with README.md present at base-sha fires `criteria-never-red` only when the flag is set, and `git worktree list` after the run equals the list before it; a criterion `test -f added.txt` for a file the build added is quiet; a later fail note citing a path an earlier step's `## Changes` listed fires `contract-dependents`; two scope-blocked builders naming one path with no `scope widened:` line fire `scope-prose`; each negative control fires none; printed as `ok: plan: <detector> fires` and `ok: plan: <detector> quiet on control`.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k plan`
- `for d in criteria-never-red contract-dependents scope-prose; do python3 plugins/sdlc-lite/scripts/traces.py selftest -k plan | grep -qF "ok: plan: $d fires" || exit 1; python3 plugins/sdlc-lite/scripts/traces.py selftest -k plan | grep -qF "ok: plan: $d quiet on control" || exit 1; done`
- `test -f plugins/sdlc-lite/scripts/traces/detectors/plan.py && test -f plugins/sdlc-lite/scripts/traces/rerun.py`
- `grep -q 'rerun_criteria' plugins/sdlc-lite/scripts/traces/ingest.py`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore)$')"`

## Step 14: Hygiene detectors
level: L3
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add `traces/detectors/hygiene.py` with `detect(rows, aux, thresholds)` over the git, lanes, and ticket facts in aux:
- `stray-worktree`: a worktree with `nested` True or under `.worktrees/tmp/`; evidence the path; cause `scripts/run.sh`.
- `tracked-runtime-file`: each `tracked_runtime` path; cause `skills/handoff-format/SKILL.md`.
- `integration-reset`: a `reset: moving to` reflog entry paired with a lost-edit signal in the lanes facts (a `red: ... rc=` outcome, an `integration dirty` outcome, or a `wip(` commit); evidence the reflog line and the lane line; cause `scripts/fanout.py`; when report.md names an integration worktree that no longer exists, one severity-1 `reflog-gone` finding instead.
- `stale-log-lines`: a driver or gate log whose lines carry two or more distinct run ids (severity 2), or no run id at all (legacy, severity 1); evidence the log path and, for mixed ids, the first line of the second id; cause `scripts/fanout.py`.
- `overwritten-gate-log`: a legacy `gate-<lane>-<id>-<k>.log` name with no `-a<n>`; severity 1; evidence the path; cause `scripts/fanout.py`.
- `ticket-id-collision`: each `duplicate id` problem line; evidence the ticket root and the line; cause `scripts/tickets.py`.
- `unregistered-external-branch`: a report.md external lane branch absent from the registered `external` names, and a registered name with no local branch; evidence the report or config path; cause `scripts/tickets.py`.
Register the `hygiene` cases: the step 7 throwaway repo and the step 6 legacy lanes fixture fire one finding per defect with the file or worktree path as evidence; a clean throwaway repo and the prefixed lanes fixture fire none; printed as `ok: hygiene: <detector> fires` and `ok: hygiene: <detector> quiet on control`.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k hygiene`
- `for d in stray-worktree tracked-runtime-file integration-reset stale-log-lines overwritten-gate-log ticket-id-collision unregistered-external-branch; do python3 plugins/sdlc-lite/scripts/traces.py selftest -k hygiene | grep -qF "ok: hygiene: $d fires" || exit 1; python3 plugins/sdlc-lite/scripts/traces.py selftest -k hygiene | grep -qF "ok: hygiene: $d quiet on control" || exit 1; done`
- `test -f plugins/sdlc-lite/scripts/traces/detectors/hygiene.py`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore)$')"`

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

## Step 16: CLI: ingest, detect, clusters
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Extend `traces/cli.py`: `ingest <repo> [--lanes-dir DIR]... [--out DIR] [--bench-dir DIR] [--rerun-criteria] [--load-series PATH]` runs `ingest.run` and prints the events.jsonl path; `detect [--repo REPO] [--out DIR]` reads `<out>/events.jsonl` and `aux.json`, runs the four detector families, writes findings through `findings.write`, prints each note and then the findings.jsonl path; `clusters --max N [--repo REPO] [--out DIR]` prints `findings.clusters(out, N)` as JSON; `detect` and `clusters` resolve the out dir exactly as ingest does (`REPO` defaults to `.`). Stages 1 and 2 spawn no `claude` or `codex` process, so a run under a PATH whose `claude` and `codex` exit 99 still exits 0. Add `.sdlc/runtime/` to the root `.gitignore`. Update the module docstring of `traces.py` with the four subcommands.
### Acceptance criteria
- `d=$(mktemp -d) && python3 plugins/sdlc-lite/scripts/traces.py ingest . --out "$d/out" | grep -q 'events.jsonl' && python3 plugins/sdlc-lite/scripts/traces.py detect --out "$d/out" | grep -q 'findings.jsonl' && python3 plugins/sdlc-lite/scripts/traces.py clusters --max 2 --out "$d/out" > "$d/clusters.txt" && test -s "$d/out/events.jsonl" && test -f "$d/out/aux.json" && test -f "$d/out/cursor.json" && test -f "$d/out/findings.jsonl"`
- `d=$(mktemp -d) && printf '#!/bin/sh\nexit 99\n' > "$d/claude" && cp "$d/claude" "$d/codex" && chmod +x "$d/claude" "$d/codex" && PATH="$d:$PATH" python3 plugins/sdlc-lite/scripts/traces.py ingest . --out "$d/out" && PATH="$d:$PATH" python3 plugins/sdlc-lite/scripts/traces.py detect --out "$d/out"`
- `grep -qxF '.sdlc/runtime/' .gitignore`
- `grep -q 'clusters' plugins/sdlc-lite/scripts/traces.py`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore)$')"`

## Step 17: Selftest suite, corpus regression, check.sh wiring
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add the `corpus` family to `traces/selftest.py`: it prints `skip: corpus: <why>` when `<git toplevel>/.sdlc/.0109-make-the-fixed-count-lint` is absent; otherwise it runs `ingest.run(toplevel, out=<temp dir>)` and the detectors and asserts that every `*.attempt.json` under `<toplevel>/.sdlc/` (walking the dot folders too) is named in some row's `sources`, that every runs.jsonl line that parses as an object maps to exactly one row, and that the findings hold `plan-defect-refusal` with evidence path `.sdlc/.0109-make-the-fixed-count-lint/handoff.md`, `plan-defect-refusal` with evidence path `.sdlc/.0134-mirror-the-extended-planner-rules/step-1/verifier-L1.md`, `replan-loop` with evidence path `.sdlc/.0113-close-rename-breaks-refs/step-2.superseded-1/builder-L2.md`, and `attempt-without-run-row` with the attempt id recorded in `.sdlc/.0162-entry-files-in-step-handoffs/step-6/builder-L2.attempt.json` (status failed, no runs.jsonl row); when `<toplevel>/.worktrees/fanout-night/logs` exists it also asserts `overwritten-gate-log` for `gate-steps-T-0148-1.log`, else prints a `skip:` line for that part. The whole suite (no `-k`) prints one `ok:` line per detector positive and one per negative control from steps 12 to 15 plus the reader, join, store, and findings cases; the whole suite is a guard here because it already passes and must keep passing, so fix any case an earlier step broke. Wire `python3 "$root/scripts/traces.py" selftest || fail=1` into `plugins/sdlc-lite/scripts/check.sh` after the onboard selftest line and name the traces selftest in its header comment.
### Acceptance criteria
- (guard) `python3 plugins/sdlc-lite/scripts/traces.py selftest`
- `python3 plugins/sdlc-lite/scripts/traces.py selftest | grep -q '^ok: corpus: '`
- `grep -qF 'traces.py' plugins/sdlc-lite/scripts/check.sh`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore|plugins/sdlc-lite/scripts/check\.sh)$')"`

## Step 18: review-traces skill: ingest, detect, and diagnose stages
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Create `plugins/sdlc-lite/skills/review-traces/SKILL.md` in the shape of `skills/dig/SKILL.md`: frontmatter (`name: review-traces`; `description:` one sentence saying it reviews a project's sdlc run traces for waste and bugs caused by sdlc-lite with no model call in the ingest and detect stages, then diagnoses, verifies, proposes, and files each confirmed finding as a ticket after approval; `argument-hint: "<repo> [--lanes-dir DIR]... [--max N]"`; `allowed-tools:` Bash for `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/traces.py`, `${CLAUDE_PLUGIN_ROOT}/scripts/run.sh`, `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py`, and `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py`, plus Read, Write, Grep, Glob, AskUserQuestion), the Codex host line every skill carries (it names `../sdlc-lite/SKILL.md`), the `SDLC_ROUTING_REASON` line, and a review task dir `.sdlc/<review task>/` created from the arguments per handoff-format. Sections: `## 1. Ingest and detect` (run `traces.py ingest <repo> [--lanes-dir DIR]...`, then `traces.py detect`, then `traces.py clusters --max N` with N from `--max`, default 5; these spend no model call), and `## 2. Diagnose` (per cluster write `.sdlc/<review task>/cluster-<k>/handoff.md` from the fenced ```cluster-question template with `## Goal`, `## Context` listing the cluster's finding ids, summaries, and evidence paths, `## Question` asking for the cause layer (sdlc-lite, project, host, task text) and the plugin file or rule at fault, and the sentence `Read only the evidence paths listed above; nothing else.`; run `${CLAUDE_PLUGIN_ROOT}/scripts/run.sh archaeologist L1` on it, or `scout L1` when the question is where a rule lives; read the result's `## Summary` for the layer and file; keep only findings whose layer is sdlc-lite for stage 3, the rest go to the stage 5 report). Leave placeholders for sections 3 to 5, which steps 19 to 21 fill.
### Acceptance criteria
- `head -1 plugins/sdlc-lite/skills/review-traces/SKILL.md | grep -qx -- '---'`
- `grep -q '^name: review-traces$' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- `grep -qF '../sdlc-lite/SKILL.md' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- `grep -qF 'archaeologist L1' plugins/sdlc-lite/skills/review-traces/SKILL.md && grep -qF 'scout L1' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- `grep -qF 'clusters --max' plugins/sdlc-lite/skills/review-traces/SKILL.md && grep -qF 'traces.py ingest' plugins/sdlc-lite/skills/review-traces/SKILL.md && grep -qF 'traces.py detect' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- ````awk '/^```cluster-question$/{f=1;next} /^```$/{f=0} f' plugins/sdlc-lite/skills/review-traces/SKILL.md | grep -q '^## Question$'````
- ````awk '/^```cluster-question$/{f=1;next} /^```$/{f=0} f' plugins/sdlc-lite/skills/review-traces/SKILL.md | grep -qF 'Read only the evidence paths listed above; nothing else.'````
- `grep -qF 'SDLC_ROUTING_REASON' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore|plugins/sdlc-lite/scripts/check\.sh|plugins/sdlc-lite/skills/review-traces/.*)$')"`

## Step 19: review-traces skill: verify stage
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Fill `## 3. Verify` in `plugins/sdlc-lite/skills/review-traces/SKILL.md`: per finding kept by stage 2, write `.sdlc/<review task>/finding-<id>/handoff.md` from the fenced ```finding-step template, a step handoff per handoff-format: `## Task goal` (the review goal), `## Step 1: Reproduce finding <id>`, `level: L1`, `### Do` saying there is nothing to build, this step only reproduces the finding from its evidence, and `### Acceptance criteria` with one line per evidence entry rendered as a runnable check (`<evidence command>` in the template): a `{path, line}` entry becomes `sed -n '<line>p' <path> | grep -qF '<quoted text>'`, an `{attempt_id}` entry becomes `grep -q '<attempt_id>' <attempt.json path>`; lint it with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/steps.py lint <that handoff>`, then run `${CLAUDE_PLUGIN_ROOT}/scripts/run.sh verifier L1` on it. A `fail` verdict drops the finding from the propose list; `pass` keeps it; no verdict reruns the verifier once, then drops. State that a finding whose evidence cannot be rendered as commands is dropped before any run.
### Acceptance criteria
- `grep -qF 'verifier L1' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- `grep -qF 'steps.py lint' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- `grep -qF 'drops the finding from the propose list' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- ````d=$(mktemp -d) && mkdir "$d/t" && awk '/^```finding-step$/{f=1;next} /^```$/{f=0} f' plugins/sdlc-lite/skills/review-traces/SKILL.md | sed -e 's#<evidence command>#test -f README.md#' > "$d/t/planner-L1.md" && grep -q '^## Step 1: ' "$d/t/planner-L1.md" && grep -q '^level: L1$' "$d/t/planner-L1.md" && python3 plugins/sdlc-lite/scripts/steps.py lint "$d/t/planner-L1.md"````
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore|plugins/sdlc-lite/scripts/check\.sh|plugins/sdlc-lite/skills/review-traces/.*)$')"`

## Step 20: review-traces skill: propose stage
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Fill `## 4. Propose` in `plugins/sdlc-lite/skills/review-traces/SKILL.md`: write `.sdlc/<review task>/propose/handoff.md` from the fenced ```propose-handoff template: `## Goal` (one ticket draft per confirmed sdlc-lite finding), `## Context` listing per finding its id, detector, summary, evidence paths, the diagnose result path, and the verify result path, and per ticket the required lines `Repro:` (steps from the evidence), `Expected:`, `Actual:` (quoted verbatim from the finding summary and evidence), and `Red check:` (one command that fails today and passes once the defect is fixed: a `traces.py selftest` case, a script selftest case, or a fixture), and `## Constraints` (drafts only, one `## Step` per ticket at level L1, no code, no filing). Run `${CLAUDE_PLUGIN_ROOT}/scripts/run.sh planner L2` on it once; each `## Step` of the result is one draft: its title is the ticket title, its Do the ticket body, its acceptance criteria the red check.
### Acceptance criteria
- `grep -qF 'planner L2' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- ````awk '/^```propose-handoff$/{f=1;next} /^```$/{f=0} f' plugins/sdlc-lite/skills/review-traces/SKILL.md | grep -q '^Repro:' && awk '/^```propose-handoff$/{f=1;next} /^```$/{f=0} f' plugins/sdlc-lite/skills/review-traces/SKILL.md | grep -q '^Expected:' && awk '/^```propose-handoff$/{f=1;next} /^```$/{f=0} f' plugins/sdlc-lite/skills/review-traces/SKILL.md | grep -q '^Actual:' && awk '/^```propose-handoff$/{f=1;next} /^```$/{f=0} f' plugins/sdlc-lite/skills/review-traces/SKILL.md | grep -q '^Red check:'````
- `grep -qF 'quoted verbatim' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore|plugins/sdlc-lite/scripts/check\.sh|plugins/sdlc-lite/skills/review-traces/.*)$')"`

## Step 21: review-traces skill: file stage and the model-call cap
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Fill `## 5. File` and a closing `## Report` in `plugins/sdlc-lite/skills/review-traces/SKILL.md`: one AskUserQuestion round over the drafts, at most 4 options per question (batch the drafts four at a time, recommendation first); each approved draft is filed with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/tickets.py new bug <slug> "<title>"` (numbered mode follows `<root>/config`) and its `handoff.md` body gets the draft's Repro, Expected, Actual, Context (evidence paths, diagnose and verify result paths), and Constraints (the red check lands before or with the fix); findings whose layer is not sdlc-lite go to `.sdlc/<review task>/report.md` (one section per finding: layer, evidence, diagnose summary) and are never filed; a session with no person present (`SDLC_HEADLESS=1`, a fanout lane, or `claude -p`) writes every draft to `report.md` and files nothing. State the model-call cap: at most `clusters + findings + 1` role runs per review (one archaeologist or scout per cluster, one verifier per finding, one planner), bounded by `--max N`; the ingest and detect stages spend none. The `## Report` lists the findings path, the clusters, the drafts filed with their ticket ids, and the report.md path.
### Acceptance criteria
- `grep -qF 'AskUserQuestion' plugins/sdlc-lite/skills/review-traces/SKILL.md && grep -qF 'at most 4 options' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- `grep -qF 'tickets.py new bug' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- `grep -qF 'report.md' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- `grep -qF 'files nothing' plugins/sdlc-lite/skills/review-traces/SKILL.md && grep -qF 'SDLC_HEADLESS' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- `grep -qF 'clusters + findings + 1' plugins/sdlc-lite/skills/review-traces/SKILL.md`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore|plugins/sdlc-lite/scripts/check\.sh|plugins/sdlc-lite/skills/review-traces/.*)$')"`

## Step 22: Integration: conductor route, Codex adapter, ignore guidance, internals doc
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
- `plugins/sdlc-lite/agents/conductor.md`: under `## Route every ask`, add the line: review a project's sdlc run traces for waste and bugs caused by sdlc-lite → `/sdlc-lite:review-traces`.
- `plugins/sdlc-lite/skills/sdlc-lite/SKILL.md`: add the table row `| Review sdlc run traces for sdlc-lite waste and bugs | review-traces |`.
- `plugins/sdlc-lite/skills/handoff-format/SKILL.md`: add `.sdlc/runtime/` to the Layout block (traces analysis outputs and cursor written by `traces.py`, never committed) and to the ignore snippet for projects that commit the trail.
- `docs/references/sdlc-internals.md`: add a `## \`scripts/traces.py\`` entry (the four subcommands, the out dir and cursor under `.sdlc/runtime/traces/<repo-key>/`, the detector families and thresholds table, the model-free stages 1 and 2, the selftest and its corpus case, the `--rerun-criteria` opt-in and its worktree rule) and name `/review-traces` in the Launcher skills paragraph.
- The conductor is a generated Codex agent (`conductor` is a key of `adapters/codex/models.json`): run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate` so `plugins/sdlc-lite/adapters/codex/agents/sdlc-conductor-l1.toml` carries the route and `generate --check` stays green.
### Acceptance criteria
- `grep -qF 'review-traces' plugins/sdlc-lite/agents/conductor.md`
- `grep -qF 'review-traces' plugins/sdlc-lite/skills/sdlc-lite/SKILL.md`
- `grep -qF 'review-traces' plugins/sdlc-lite/adapters/codex/agents/sdlc-conductor-l1.toml`
- `grep -qF 'sdlc/runtime' plugins/sdlc-lite/skills/handoff-format/SKILL.md`
- `grep -qF 'scripts/traces.py' docs/references/sdlc-internals.md && grep -qF 'review-traces' docs/references/sdlc-internals.md`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces\.py|plugins/sdlc-lite/scripts/traces/.*|\.gitignore|plugins/sdlc-lite/scripts/check\.sh|plugins/sdlc-lite/skills/review-traces/.*|plugins/sdlc-lite/agents/conductor\.md|plugins/sdlc-lite/skills/sdlc-lite/SKILL\.md|plugins/sdlc-lite/adapters/codex/agents/sdlc-conductor-l1\.toml|plugins/sdlc-lite/skills/handoff-format/SKILL\.md|docs/maintenance/sdlc-internals\.md)$')"`

## Step 23: Gates green
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Run every gate below from the repository root and fix any red that steps 1 to 22 introduced (a `traces.py selftest` failure inside check.sh, a skill without its Codex route, a stale generated Codex agent, whitespace errors). A gate red at the build-start HEAD for a reason outside this task is reported as Status `inherited red: <tests>`. shellcheck is not installed on this host, so check.sh prints `skip: shellcheck not installed`; that is not a red. All three gates were green at replan time (check.sh takes about two minutes here).
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'`

## Risks
- Builders never commit, so `$SDLC_BASE_SHA` stays the chain base for every step and each scope guard sees the uncommitted files of every earlier step. Every guard from step 2 on therefore allows the union of the files steps 1 to n touch (the form `steps.py widen` recognizes, so a conductor scope decision can still extend it). The guard still refuses a file outside the task (it went red on a stray `steps.py` line at replan time), but it no longer proves which of two earlier steps edited a shared file such as `.gitignore`; the verifier's own diff reading covers that.
- Step 2's non-guard criteria are green on the current tree because the blocked attempt's reader and cases were kept, as the handoff's Plan review records; the rebuild confirms them against the Do instead of writing them again. Step 17's whole-suite run is a guard for the same reason: it passes today and must keep passing.
- The done-condition names the gen-ui-system-svelte-lite traces of 2026-09-28 and the batch-3 scratchpad; neither is on this machine (the architect searched). The plan proves every detector on synthetic fixtures and on this repo's own trail (step 17); the live check on the gen-ui traces is the user's to supply, and the T-0148, T-0149, and T-0153 shapes were found by a person reading lane prose, so the deterministic detectors may name them only as advisories.
- The manifest's edges point from the detector leaves to `findings`, while their own why text says findings.py owns the record shape the detectors fill; the plan builds `findings` (step 11) before the detectors (steps 12 to 15), as the architect's risk note asks.
- Twenty-three serial steps for a size L ticket. If the run must be split, steps 1 to 17 are stages 1 and 2 (with the check.sh wiring) and steps 18 to 23 are stages 3 to 6.
- The handoff asks for scout or archaeologist at L2; run.sh defines only L1 for both, and adding a level is a user decision on models, so the skill uses L1.
- `--rerun-criteria` executes plan criteria from the analyzed repo in a throwaway worktree; a criterion with side effects could write there, and `git worktree add` writes `.git/worktrees` metadata into the analyzed repo until the `finally` removes it. It is opt-in, never on by default, and the selftests run it only on throwaway repos.
- The lane-log corpus (`.worktrees/fanout-night/logs`) lives only in the main checkout, so the corpus case skips its lane assertions in a lane worktree; the fanout and hygiene fixtures cover both layouts.
- The host python3 is 3.9.6; a builder writing 3.10+ syntax breaks every later step. Each Do says so. Python writes `traces/__pycache__/` on import; step 1's `.gitignore` line keeps it out of the scope guards.
- `steps.py`, `order.py`, and `tickets.py` are imported as modules; a later change to their exported names breaks the readers, which is the intended coupling (one reading of the rules) and shows up in the traces selftest inside check.sh.
