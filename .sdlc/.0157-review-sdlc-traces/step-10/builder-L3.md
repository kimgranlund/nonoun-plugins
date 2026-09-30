<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/traces/store.py` (new): `out_dir` and `repo_key`, `write_events` (rows in a fixed sort order, keys in `ROW_FIELDS` order), `write_aux`, cursor load and write, `fingerprint` (uses only stat, over names, sizes and mtime_ns), the `reading()` context that tracks opens, and the `READS` counter.
- `plugins/sdlc-lite/scripts/traces/ingest.py` (new): `run(repo, lanes_dirs=(), out=None, bench_dir=None)` walks task dirs and step dirs, uses the cursor for unchanged dirs, reads lanes dirs, the git, ticket and bench facts, and writes events.jsonl, aux.json and cursor.json.
- `plugins/sdlc-lite/scripts/traces/selftest.py`: added the `store` family (4 cases) and a `_store_repo` fixture (a throwaway git repo with an open task dir and a closed `.0002-b` task dir; `_templates` is present and must be skipped).
- `plugins/sdlc-lite/scripts/traces/__init__.py`: the module list in the docstring now names sources, store and ingest.

## Checks
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k store`: exit 0, 4 `ok: store:` lines, PASS.
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k store | grep -q '^ok: store: '`: exit 0.
- `test -f .../traces/store.py && test -f .../traces/ingest.py`: exit 0.
- Scope guard (the `git diff --name-only "$SDLC_BASE_SHA"` / `ls-files --others` command): exit 0.
- `python3 plugins/sdlc-lite/scripts/traces.py selftest` (full suite): exit 0, PASS.
- `git diff --check`: exit 0.
- Negative controls, run by monkeypatching in-process with no file edits:
  - With `load_cursor` returning `{}`: the unchanged case fails with "second ingest READS 15, want 0" and the append case fails with "READS 16, want 6".
  - With `reading()` counting nothing: both cases fail with READS 0.
- Ad hoc: changing only the task `handoff.md` ticket id makes the untouched step dir's rows pick up the new id on the next ingest (READS 7).
- Real repo, ingested twice with `out` in a temp dir: 857 rows, first READS 1640, second READS 1 (this step's live `builder-L3.log` was changing), about 1 s. `git status` showed nothing new outside `.sdlc/0157`.

## Notes
- `READS` counts real opens: an audit hook sees each `open` event under the source dir being read, and only paths that exist as files count, so a failed open of a missing `runs.jsonl` is not a read. It resets to 0 at the start of each `ingest.run`. The git, ticket and bench readers run on every ingest and are not counted. The ticket reader opens every `handoff.md` through `tickets.load`.
- Row `sources` and legacy attempt ids are repo-relative (`.sdlc/<task>/step-<n>/...`). `aux.repo` is the absolute root for joining them.
- Transcript counts go on the result record before the join: `tool_calls`, `denials` as a count, and `rate_limits`. The `.log` path is appended to that row's `sources`, so step 15 can re-read `bash_calls` and the denial stderr from it.
- The cursor serves a step dir only when its fingerprint and the task's ticket id are both unchanged.
- For a lanes dir, the fingerprint covers its top-level files plus `logs/*`.
- `aux.gates` is the flat list of every lanes dir's `gate_logs`, each tagged with `lanes_dir`.
- `.sdlc/runtime/` is not ignored in this repo yet. Step 22 plans the ignore snippet, and this step made no `.gitignore` change.
