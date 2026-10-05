repo: /Users/kimgranlund/Projects/nonoun/sdlc-lite
base: 433125d
solution: 7b7096e
level: L2
tests_from: (external) tests/footprint.py
test_paths: []
setup: true
check: python3 /tmp/bench-sl/tests/footprint.py

## Goal
Add `plugins/sdlc-lite/scripts/footprint.py` (Python 3, standard library only) that measures how much a ticket or task folder wrote under `.sdlc/`, and can gate on it.

`python3 plugins/sdlc-lite/scripts/footprint.py <ticket dir>` prints exactly these `key: value` lines, one per line, in this order, derived from the directory at run time (never fixed numbers), and exits 0:

```
ticket: <basename of the dir>
files: <number of regular files under the dir, recursive>
bytes: <total size in bytes of those files>
md_bytes: <total size in bytes of the files whose name ends in .md>
steps: <number of immediate subdirectories named step-<N> where N is digits>
planner_bytes: <total size in bytes of the files named planner-L*.md directly in the dir>
role_runs: <total number of non-empty lines in every runs.jsonl at any depth under the dir>
```

followed by one line per distinct role and level found in those runs.jsonl lines, each line a JSON object with string fields `role` and `level`: `role_runs <role> <level>: <count>`, sorted by role then level.

`python3 plugins/sdlc-lite/scripts/footprint.py check <ticket dir> --max-files N --max-bytes N` exits 0 and prints `ok` when files <= N and bytes <= M hold (the two values given by --max-files and --max-bytes). When a limit is exceeded it exits 1 and prints a message on stdout or stderr that names the exceeded option, `--max-files` or `--max-bytes`, and does not name an option that was not exceeded. A missing directory exits non-zero.

The script is read-only: it never creates, changes, or deletes anything under the ticket dir.

Also add a `selftest` subcommand (`footprint.py selftest`) that builds fixture ticket directories (a fix-lane one and a chained one) in a temp dir, asserts exact counts, includes a negative control fixture where one extra file makes `check --max-files` fail, and exits 0 when everything holds. Wire the selftest into `plugins/sdlc-lite/scripts/check.sh` next to the other selftests, and add a short entry for the script in `docs/maintenance/sdlc-internals.md`.

## Context
Size M. Part of measuring the cost of the SDLC loop: a ticket's footprint is the files and bytes its roles wrote. Do not change model or effort defaults. Do not commit, push, or publish.

## Constraints
Follow the repository guidance in AGENTS.md and plugins/sdlc-lite/AGENTS.md. No em dashes in anything you write. Keep one authoritative location for each fact.
