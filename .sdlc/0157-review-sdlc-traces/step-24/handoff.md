# Task: review-sdlc-traces (T-0157), loose ends

Context: read `.sdlc/0157-review-sdlc-traces/handoff.md` for the goal. Steps 1 to 23 built `plugins/sdlc-lite/scripts/traces.py` and the `plugins/sdlc-lite/scripts/traces/` package; all passed.

## Step 24: Loose ends
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
- Ingest misses `runs.jsonl` files in non-step subfolders of a task dir (for example `.sdlc/.0106-extend-claude-agents-sdlc-lite/verify/runs.jsonl` and `.sdlc/.0016-ticket-numbered-folders/old-step-3/runs.jsonl`), so their lines map to no row. Make `plugins/sdlc-lite/scripts/traces/ingest.py` also read any other subdirectory of a task dir that holds a `runs.jsonl` (its rows keep step None unless the name is a step dir), and add a selftest case named `nested-runs` in `plugins/sdlc-lite/scripts/traces/selftest.py` that builds a fixture task dir with `verify/runs.jsonl` and asserts its line becomes a row.
- `traces.py detect` prints a Python traceback when `<out>/events.jsonl` or `aux.json` is missing. Make `plugins/sdlc-lite/scripts/traces/cli.py` print one line to stderr naming the missing file and telling the user to run `traces.py ingest` first, and exit 2.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k nested-runs | grep -q '^ok: nested-runs'`
- `d=$(mktemp -d); python3 plugins/sdlc-lite/scripts/traces.py detect --out "$d" > "$d/o" 2>&1; rc=$?; test "$rc" -eq 2 && ! grep -q Traceback "$d/o" && grep -q ingest "$d/o"`
- (guard) `python3 plugins/sdlc-lite/scripts/traces.py selftest`
