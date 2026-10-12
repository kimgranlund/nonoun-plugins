<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
- process deviation: red-checkpoint: retrospective: attempt 5cde5f81297b421892c1bb8c26875006, handoff sha256 4b04d1922281. Step 2 had 4 of 4 (red) criteria without a pre-edit red control: the `check.sh` grep for `lanes.py" selftest`, the `sdlc-internals.md` heading grep, the config-key loop, and the `lanes.py --help` grep. The verifier verdict does not clear this. The builder says step 1's untracked `lanes.py` already differed from the base, so redck stored the controls as retrospective. The builder also says all four criteria were red at base before any edit, and the verifier confirmed the base lacked the `check.sh` line.
- Step 1 recorded 7 pre-edit controls for 8 `(red)` criteria. The missing one is the `--help` strings check, which was red at base anyway because the file did not exist. Step 1's verifier found no `process-deviations.md` for step 1.
- Step 1 criterion 8 (selftest leaves worktrees and refs unchanged) failed on the builder's first run, because another session wrote refs inside the run window. A rerun passed, and so did the verifier's run.
- Step 2's guard (`check.sh`) exited 1 on the builder's first run, and the output was not captured. A second run exited 0 with no edits in between. The builder suspects load but did not confirm it.
- Step 2's verifier reran `check.sh` and saw no failure lines in the tail, but did not capture the exit code, so that pass rests on the output tail.
- Both steps have a verifier verdict of pass.

## PR title
T-0451: lanes.py core: open, close, sweep, list, check, port (lane lifecycle A)

## PR body
Summary: adds `plugins/sdlc-lite/scripts/lanes.py`, the one script that owns the lane lifecycle (ticket A of `docs/specs/sdlc-lite/lane-lifecycle.md`, amended in section 17.9). It also adds the `check.sh` selftest line and documents the script and its config keys. No caller is wired to it yet.

Changes:
- `plugins/sdlc-lite/scripts/lanes.py` (new, 1831 lines, Python 3.9 stdlib plus git):
  - Subcommands: `open`, `close`, `sweep` (dry run by default, `--apply` acts), `list`, `check`, `port`, `archive list`, `archive restore`, `selftest`.
  - Docstring: holds the kinds table, truth table, close steps, record fields and config keys.
  - Importable API: `open_lane`, `close_lane`, `sweep`, `list_lanes`, `still_open`, `landed`, `config`.
  - Safety: archive refs are annotated tag objects under `refs/archive/<date>/<branch>`, written before any removal. Dirty, locked, recent and unmerged lanes are kept.
  - Claim rule (section 8.1): `open` refuses a lane whose ticket is not claimed. `close` prints `ticket still open` for a merged lane whose ticket is open.
  - `close` also runs `git config --remove-section branch.<b>` after `update-ref -d`, as `git branch -D` would, so a reopened name does not inherit a stale description.
- `plugins/sdlc-lite/scripts/check.sh`: runs `lanes.py selftest`, and `lanes.py` is added to the header list.
- `docs/references/sdlc-internals.md`: new `scripts/lanes.py` section with the 9 config keys and defaults. It points to `lanes.py --help` for the tables.

Verification:
- `lanes.py selftest` exits 0 and ends `ok: lanes.py selftest`.
  - It has a case per truth-table row (1 to 12, plus pr merged, recent, in use, locked) and per C1 to C6, C9, C10 and C13 control.
  - It runs 9 mutants, each observed failing its case.
  - The verifier broke the dirty check and the `--no-renames` flag in a copy of `lanes.py`, and the selftest failed each time.
- `--help` names every subcommand and the seven required strings. `list --all --json` parses.
- `check-packaging.py` passes, `git diff --check` is clean, and scope is limited to the three allowed files.
- `check.sh` was run in full by the builder and the verifier, with a caveat on exit-code capture (see Warnings).
- One selftest run takes about 72 s on this host.
- Process deviations are listed in Warnings and apply to this PR.

## Changelog entry
- Added `lanes.py`, one script for the lane lifecycle: open, close, sweep, list, check, port and archive, with a built-in selftest that `check.sh` now runs. `open` refuses a lane whose ticket is not claimed. `close` archives the branch under `refs/archive/` before removing it, and it keeps dirty, locked, recent and unmerged lanes.

## Follow-ups
- decide: criterion 8 (worktrees and refs unchanged around the selftest) compares `refs/heads` and the worktree list, which every lane in the repo shares, so concurrent lanes make it fail spuriously. Decide whether to scope it to the selftest's own temp repo.
- note: `git worktree lock` at open, unlock at close, the finished-agent rule and `extensions.worktreeConfig` are ticket A2, not built here. Sweep and list only read the lock.
- note: `lanes.py` is not wired into fanout, solo_run, tickets or dispatch (tickets B and C), and the hook message (D), `wait` and board columns are later tickets.
- note: `lanes.py list --all --json` on this checkout makes one read-only `gh pr list` call per lane, with a 30 s timeout.
- note: the step 2 `check.sh` guard failed once with no captured output, then passed with no edits in between. The cause is unknown, and the exit code was not captured on the verifier's run.
