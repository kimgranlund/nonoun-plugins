## Task goal
A skill plus scripts/traces.py reads a project's sdlc run traces and reports inefficiencies and bugs caused by sdlc-lite, each with evidence and a proposed fix ticket.

## Step 2: Attempt reader
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Add `plugins/sdlc-lite/scripts/traces/sources/__init__.py` and `traces/sources/attempts.py`: `read(dir)` returns one record per `*.attempt.json` in `dir` (the parsed dict plus `path` and `marker`, True when `<role>-<level>.running` exists next to it), sorted by name; a file that is not a JSON object is skipped and named in a `problems` list the function also returns. Register the `attempts` cases: a fixture dir with completed, failed, interrupted, and running records yields one record each with its status and exit code (None for running); a record with no runs.jsonl row still yields a row through `table.join` with an empty run list; the running record with a marker next to it reports `marker` True and the others False.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k attempts`
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k attempts | grep -q '^ok: attempts: '`
- `test -f plugins/sdlc-lite/scripts/traces/sources/attempts.py`
- (guard) scope: `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ':(exclude).sdlc'; git ls-files --others --exclude-standard -- . ':(exclude).sdlc'; } | grep -vE '^(plugins/sdlc-lite/scripts/traces/.*)$')"`
