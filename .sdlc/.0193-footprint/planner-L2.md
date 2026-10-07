<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Add `plugins/sdlc-lite/scripts/footprint.py`, which measures a ticket folder's footprint (files, bytes, `.md` bytes, steps, planner bytes, role runs by role and level) and gates on it with `check --max-files/--max-bytes`, with a fixture selftest wired into `check.sh`, a reference entry in the internals doc, and the design's Baseline table reproduced for T-0188, T-0164, T-0181, and T-0175.

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

## Step 2: Wire into check.sh, document, record baseline, gates green
level: L1
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Depends on: step 1.
- In `plugins/sdlc-lite/scripts/check.sh`:
  - Add the line `python3 "$root/scripts/footprint.py" selftest || fail=1` directly after the `messages.py` selftest line.
  - Add `footprint.py` to the selftest list in the header comment (the `# Plugin checks: ... messages.py selftests` line).
- In `docs/references/sdlc-internals.md`, add a `## \`scripts/footprint.py\`` entry directly after the `## \`scripts/order.py\`` entry. Keep it to 2 to 4 sentences:
  - what it measures (files, bytes, `.md` bytes, steps as `step-<n>` dirs with superseded dirs excluded, planner bytes, and role runs from every `runs.jsonl` by role and level);
  - that `check --max-files N --max-bytes N` exits 1 and names the exceeded limit;
  - that it is read-only on ticket folders;
  - that `check.sh` runs its selftest.
  The doc must name `--max-files`. Do not copy the Baseline table; `docs/lean-sdlc/design.md` stays its one home.
- Run `python3 plugins/sdlc-lite/scripts/footprint.py <dir>` for `.sdlc/.0188-tighten-idle-note`, `.sdlc/.0164-fix-skill-lints-task-folder`, `.sdlc/.0181-messages-wait`, and `.sdlc/.0175-ticket-root-router`. Paste the four outputs verbatim into this step's builder result, with one line stating that they match the design's Baseline table (`docs/lean-sdlc/design.md` "Baseline (measured 2026-10-03)").
- This is the gates green step. Run every gate below. If step 1 introduced any red, fix it inside `footprint.py`. Change no model or effort defaults, and make no version bump.
### Acceptance criteria
- `grep -qF 'scripts/footprint.py" selftest || fail=1' plugins/sdlc-lite/scripts/check.sh`
- `grep -qF 'scripts/footprint.py' docs/references/sdlc-internals.md`
- `grep -qF -- '--max-files' docs/references/sdlc-internals.md`
- `test -z "$( { git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"; git ls-files --others --exclude-standard -- . ":(exclude).sdlc"; } | grep -vxF -e plugins/sdlc-lite/scripts/footprint.py -e plugins/sdlc-lite/scripts/check.sh -e docs/references/sdlc-internals.md)"`
- This step's builder result holds the `footprint.py` output for each of the four tickets T-0188, T-0164, T-0181, and T-0175, and those values match the design's Baseline table: steps, role runs, files, bytes, and `.md` bytes.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/tickets.py --root .sdlc check`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- plugins docs`

## Assumptions
- The four closed dot folders are tracked and frozen, so exact-count criteria over them are stable: verified by `git ls-files .sdlc/.0181-messages-wait | wc -l` (51) and the folder names under `.sdlc/`.
- The design's Baseline numbers equal a recursive regular-file count and size sum, with role runs as `runs.jsonl` line counts: verified by a shell `find`/`stat` run that printed 8/8010/4521/2, 8/10050/6586/2, 51/214502/185323/15, and 69/224330/187209/21 for T-0188, T-0164, T-0181, and T-0175.
- Planner bytes are the top-level `planner-L*.md` files: verified that T-0181's sum is 105542, the design's figure ("three planner files total 105,542 bytes"); T-0175 has only `planner-L3-2.md` (68213).
- Steps are `^step-\d+$` dirs, with superseded dirs excluded: verified that T-0181 has 5 such dirs and T-0175 has 8, matching the table, and that `step-N.superseded-K` dirs exist elsewhere under `.sdlc/`.
- Role and level per run come from the `role` and `level` keys of each `runs.jsonl` record: verified on `.sdlc/.0181-messages-wait/runs.jsonl` and the step-1 files of T-0188 and T-0164.
- No `AGENTS.md` sits under `docs/` or `plugins/sdlc-lite/scripts/`: verified by `ls` (both missing). The nearest non-root entry for the plugin files is `plugins/sdlc-lite/AGENTS.md`.
- No other file references `footprint.py` except design and review docs, so there are no contract dependents: verified by `grep -rln footprint plugins scripts docs`.
- All step 2 gates are green at HEAD: verified by running `check.sh` (pass, shellcheck skipped because it is not installed), `check-packaging.py`, `codex_roles.py generate --check`, and `tickets.py --root .sdlc check`.
- "Record the output in the ticket's result" means step 2's builder result file: settled here, because the ticket names no other result location and planners and builders never write under closed ticket folders.

## Risks
- On this host, `check.sh` skips shellcheck, which does not cover the Python file anyway. A host that has shellcheck runs the same gate.
- If a closed folder is ever edited on main (for example, by a migrate-layout ticket), the exact-count criteria in step 1 go red after a main sync. The T-0190 migration is sequenced later by `depends`.
- `md_bytes` for T-0181 includes `.md` files in step dirs. This matches the design's definition ("Bytes are file sizes of everything in the ticket folder"), and I checked it against the table.
