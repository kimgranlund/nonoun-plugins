<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0156: Keep fanout gate logs per attempt instead of overwriting

## PR body
### Summary
A rerun of `fanout.py run` after a red gate overwrote `logs/gate-<lane>-<id>-<k>.log`, so the first failure was lost. Each gate attempt now writes its own file, `logs/gate-<lane>-<id>-<k>-a<n>.log`. Here `<k>` numbers the gates and `a<n>` numbers the attempts. The ticket asked whether sdlc-lite owns this overwrite. It does, so it is not closed as not-sdlc.

### Changes
- `plugins/sdlc-lite/scripts/fanout.py`:
  - `run_ticket` picks `n` as 1 plus the highest `a<n>` already in `logs/`, found by regex (mtime is never used). It starts at 1 when none exists.
  - The module docstring and the `run_logged` docstring now say gate logs are never overwritten (one file per attempt) and driver logs still are.
  - Selftest case 9 uses the attempt-1 file name.
  - New selftest case 10, "gate retry case": run 1 is red, run 2 is green, and the two attempt logs hold `attempt-one` and `attempt-two`.
- `docs/references/sdlc-internals.md`: the fanout entry gives the per-attempt name and says earlier attempts survive.

### How verified
Verifier L1 verdict: pass. Every criterion passed.
- The two-run probe (red first run, green rerun, in a `mktemp -d` dir outside the tree) exits 0 on the built tree. At base commit c9dfd26 the same setup left one `gate-alpha-T-0001-1.log` with no `attempt-one`, so the probe fails there.
- Grep checks: "gate retry case" is present, the old `gate-<lane>-<id>-<k>.log` string is gone from both files, and the old "keep their names and are overwritten" sentence is gone.
- The scope check is empty: only `fanout.py`, `sdlc-internals.md` and `.sdlc` files changed.
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest` passes, including case 10.
- `bash plugins/sdlc-lite/scripts/check.sh` exits 0. Its shellcheck step was skipped because shellcheck is not installed on this host.
- `python3 scripts/check-packaging.py` passes.
- `git diff --check` exits 0.

### Limitations
- Shell lint did not run (shellcheck not installed).
- Driver logs (`<lane>-<id>.log`) still overwrite on a rerun. This was out of scope.
- Old gate logs without an attempt part stay untouched, and new runs start at `a1` beside them.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- fanout: gate logs are now written per attempt as `logs/gate-<lane>-<id>-<k>-a<n>.log`, so a retried gate keeps the first failure's log. Driver logs are unchanged.

## Follow-ups
- note: driver logs (`<lane>-<id>.log`) are still overwritten on a fanout rerun. The planner left this to T-0157 or a later follow-up.
- note: shellcheck is not installed on this host, so `check.sh` skipped shell lint for this change.
