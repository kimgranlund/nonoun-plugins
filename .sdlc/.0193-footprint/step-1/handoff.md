## Task goal
Add scripts/footprint.py that measures a ticket's footprint and can gate on it.

## Step 1: footprint.py with measure, check, and selftest
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Create `plugins/sdlc-lite/scripts/footprint.py` (new, stdlib only, `#!/usr/bin/env python3`). Follow the shape of `plugins/sdlc-lite/scripts/order.py`: a module docstring with a usage block, a `selftest()` that prints `ok: <name>` per held check and, at the end, either `footprint selftest: PASS` (exit 0) or `footprint selftest: FAIL` with the misses on stderr (exit 1), and `main(argv)` returning the exit code, with `sys.exit(main(sys.argv[1:]))`.

Depends on: none.

Settled interface. These definitions reproduce the design's Baseline table. I checked this with shell on the four closed folders: `find -type f` counts and sizes, plus `runs.jsonl` line counts grouped by role and level.
- `footprint.py <ticket dir>` prints exactly these `key: value` lines in this order, values as plain integers with no thousands separators:
  - `ticket: <basename of dir>`
  - `files: N`: every regular file under the dir, recursive (`os.walk`, `followlinks=False`).
  - `bytes: N`: sum of those files' sizes.
  - `md_bytes: N`: the same sum, over names ending `.md`.
  - `steps: N`: immediate subdirectories whose name fully matches `^step-\d+$`. Superseded dirs such as `step-2.superseded-1` do not count. That naming exists under `.sdlc/`, seen with `find .sdlc -maxdepth 2 -name 'step-*'`.
  - `planner_bytes: N`: sum of sizes of files directly in the dir whose name fully matches `^planner-L\d+(-\d+)?\.md$`.
  - `role_runs: N`: the count of non-blank lines across every `runs.jsonl` anywhere under the dir.
  - One line per (role, level) group, `role_runs <role> <level>: N`, sorted by role then level. A non-blank line that is not a JSON object holding string `role` and `level` counts in the group `unknown ?`.
- `footprint.py check <ticket dir> [--max-files N] [--max-bytes N]`:
  - `--max-bytes` compares against `bytes` (all files).
  - At least one limit is required. Pass neither, give a dir that does not exist, or give bad args, and it exits 2 with a usage message on stderr.
  - For each exceeded limit (value strictly greater than the limit) it prints one stderr line naming the flag, e.g. `footprint: files 9 exceeds --max-files 8`, and the command exits 1.
  - Otherwise it prints `ok` and exits 0.
- `footprint.py selftest` covers the following.
  - It builds fixture ticket dirs in a `tempfile.TemporaryDirectory()`:
    - A fix-lane dir: `handoff.md` plus `step-1/` holding `handoff.md`, `base-sha`, `builder-L1.md`, `builder-L1.attempt.json`, `verifier-L1.md`, `verifier-L1.attempt.json`, and a 2-line `runs.jsonl` (builder L1, verifier L1). That is 8 files, the same shape as `.sdlc/.0188-tighten-idle-note`.
    - A chained dir: top-level `handoff.md`, `planner-L2.md`, `planner-L3-2.md`, `plan-reviewer-L1.md`, and a `runs.jsonl` with 3 lines, one of them malformed so it lands in `unknown ?`. It also has `step-1/` and `step-2/`, each with builder and verifier results and a `runs.jsonl`, plus a `step-2.superseded-1/` dir.
  - It asserts exact `files`, `bytes`, `md_bytes`, `steps` (2 for the chained dir; the superseded dir is excluded), `planner_bytes`, `role_runs`, and each per-group count, all computed from the bytes the fixture itself wrote.
  - It asserts that `check` exits 0 on the fix-lane dir with `--max-files 8`.
  - The negative control: copy the fix-lane dir, add one extra file, and assert that `check --max-files 8` exits 1 with stderr naming `--max-files`. Name this check with the prefix `negative control` so it prints `ok: negative control: extra file fails check --max-files`.
  - It asserts that `check` with no limit exits 2.
  - It asserts that measuring writes nothing. Snapshot each fixture tree's (path, size) list before and after, and compare.
- Read-only: the script never opens a file for writing under the measured dir. Counts come only from the directory at run time; no fixed numbers live in the script.

Focused checks: the selftest, then the four closed ticket folders below.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/footprint.py selftest`
- `python3 plugins/sdlc-lite/scripts/footprint.py selftest | grep -q '^ok: negative control'`
- `out=$(python3 plugins/sdlc-lite/scripts/footprint.py .sdlc/.0181-messages-wait) && for l in 'files: 51' 'bytes: 214502' 'md_bytes: 185323' 'steps: 5' 'role_runs: 15' 'planner_bytes: 105542' 'role_runs planner L3: 2' 'role_runs plan-reviewer L1: 2'; do printf '%s\n' "$out" | grep -qxF "$l" || exit 1; done`
- `out=$(python3 plugins/sdlc-lite/scripts/footprint.py .sdlc/.0175-ticket-root-router) && for l in 'files: 69' 'bytes: 224330' 'md_bytes: 187209' 'steps: 8' 'role_runs: 21' 'planner_bytes: 68213' 'role_runs filer L1: 1' 'role_runs builder L3: 5'; do printf '%s\n' "$out" | grep -qxF "$l" || exit 1; done`
- `out=$(python3 plugins/sdlc-lite/scripts/footprint.py .sdlc/.0188-tighten-idle-note) && for l in 'files: 8' 'bytes: 8010' 'md_bytes: 4521' 'steps: 1' 'role_runs: 2' 'role_runs builder L1: 1' 'role_runs verifier L1: 1'; do printf '%s\n' "$out" | grep -qxF "$l" || exit 1; done`
- `out=$(python3 plugins/sdlc-lite/scripts/footprint.py .sdlc/.0164-fix-skill-lints-task-folder) && for l in 'files: 8' 'bytes: 10050' 'md_bytes: 6586' 'steps: 1' 'role_runs: 2' 'role_runs builder L2: 1' 'role_runs verifier L1: 1'; do printf '%s\n' "$out" | grep -qxF "$l" || exit 1; done`
- `python3 plugins/sdlc-lite/scripts/footprint.py check .sdlc/.0188-tighten-idle-note --max-files 8 --max-bytes 8010`
- `err=$(python3 plugins/sdlc-lite/scripts/footprint.py check .sdlc/.0188-tighten-idle-note --max-files 7 2>&1 >/dev/null); rc=$?; test "$rc" -eq 1 && printf '%s\n' "$err" | grep -qF -- '--max-files'`
- `err=$(python3 plugins/sdlc-lite/scripts/footprint.py check .sdlc/.0188-tighten-idle-note --max-bytes 8009 2>&1 >/dev/null); rc=$?; test "$rc" -eq 1 && printf '%s\n' "$err" | grep -qF -- '--max-bytes'`
- `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF plugins/sdlc-lite/scripts/footprint.py)"`
- `git diff --quiet "$SDLC_BASE_SHA" -- .sdlc/.0181-messages-wait .sdlc/.0175-ticket-root-router .sdlc/.0188-tighten-idle-note .sdlc/.0164-fix-skill-lints-task-folder`
