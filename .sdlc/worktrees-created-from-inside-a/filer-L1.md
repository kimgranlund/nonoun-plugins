<!-- role=filer level=L1 model=sonnet effort=medium -->
All three steps passed verification. Now composing the final filer output.

## Warnings
None

## PR title
T-0129: Report stray worktrees and branches created from inside a script or program a role runs

## PR body

**Summary**

When a role run (builder, verifier, etc.) creates a git worktree or branch from inside a script or program it runs — rather than through Bash tool text — `hooks/block-stray-worktree.sh` can't see it, since that hook only inspects Bash command text. This closes the gap: `scripts/run.sh` now detects and reports any such stray worktree or branch that appeared during a run, at run end.

**Changes**

- `plugins/sdlc-lite/scripts/run.sh`: snapshots worktree paths (`git worktree list --porcelain`) and local branches (`refs/heads`) before the role runs. A new `detect_strays` function (run without errexit, never fails) compares the post-run state to the snapshot, excluding this run's own `$SDLC_TMP_WORKTREES` prefix (matched by both raw and `phys`-realpath form, for macOS's `/private/var` aliasing). `report_strays` prints one stderr line per stray worktree (`run.sh: stray worktree appeared during this run: <path> [<branch>]`) and branch (`run.sh: stray branch appeared during this run: <branch>`) in `on_exit`, after `cleanup_worktrees`, covering exit 0, 1, 3, and signal exits. The runs.jsonl line gets new `stray_worktrees` and `stray_branches` array fields (always present, empty when nothing appeared). Exit codes, the required-section check, and prefix cleanup are unchanged; nothing is ever deleted outside the run's own prefix. A dry run (`SDLC_DRY_RUN=1`) takes no snapshot and reports nothing. Header comment updated to describe the report and both field names. One `# shellcheck disable=SC2016` added to a pre-existing line to keep plain `shellcheck` clean.
- `plugins/sdlc-lite/scripts/run-selftest.sh`: new cases cover a stub that creates a stray worktree and branch from inside its own script (reported on stderr and in runs.jsonl), a clean run (no report, empty arrays), a worktree under the prefix (never reported), and a failing run (exit 1) that still reports a stray it leaves behind. Existing `want_wt` case now also asserts no stray line is printed.
- `CLAUDE.md`: `scripts/run.sh` bullet documents the run-end report (fields, report-only, exit code unchanged, prefix excluded, dry run silent); `hooks/block-stray-worktree.sh` bullet notes that script/program-created worktrees bypass the hook and are caught by this run-end report instead.
- `.claude/agents/sdlc-lite-author.md`: same two notes added to the existing block-stray-worktree hazard line, kept in sync with CLAUDE.md.

`hooks/block-stray-worktree.sh` and `scripts/fanout.py` were left untouched, as required.

**Verification**

- Step 1 (builder L3 / verifier L2, pass): verifier re-ran every acceptance criterion on the built tree (all green) and confirmed each check is discriminating by reproducing red at the pre-build commit (missing fields, missing selftest coverage, and a pre-existing SC2016 shellcheck info finding). Full `check.sh` also run clean.
- Step 2 (builder L1 / verifier L1, pass): verifier confirmed all five grep criteria pass on the built tree and fail at pre-build HEAD, checked no em dashes were introduced, and traced each doc claim back to the actual mechanism in the run.sh diff.
- Step 3 (builder L1 / verifier L1, pass): gate step found nothing to fix; verifier ran the `check.sh` guard (pass), and separately proved it can go red by injecting an unassigned-variable reference into run.sh in a throwaway worktree (shellcheck caught it, rc=1).

## Changelog entry
- `run.sh` now reports, at run end, any git worktree or branch that a role created from inside a script or program (bypassing `block-stray-worktree.sh`), via stderr lines and new `stray_worktrees`/`stray_branches` fields in `runs.jsonl`. Report only; nothing is removed and exit codes are unchanged.

## Follow-ups
None
