<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/traces/detectors/hygiene.py` (new): `detect(rows, aux, thresholds)` with 7 detectors: stray-worktree, tracked-runtime-file, integration-reset (plus the reflog-gone case), stale-log-lines, overwritten-gate-log, ticket-id-collision, unregistered-external-branch.
- `plugins/sdlc-lite/scripts/traces/detectors/thresholds.py`: added the hygiene severity keys: stray-worktree 2, tracked-runtime-file 2, integration-reset 3, reflog-gone 1, stale-log-lines 2, stale-log-lines-legacy 1, overwritten-gate-log 1, ticket-id-collision 3, unregistered-external-branch 2.
- `plugins/sdlc-lite/scripts/traces/detectors/__init__.py`: docstring now lists the hygiene family.
- `plugins/sdlc-lite/scripts/traces/selftest.py`:
  - Moved the step 6 legacy and prefixed lanes fixtures into writers (`_fanout_legacy_files`, `_fanout_prefixed_files`). The step 6 cases' assertions are unchanged.
  - Added 18 `hygiene:` cases: 7 fires, 7 quiet on control, and 4 extra.
  - Imports `contextlib`.

## Checks
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k hygiene`: rc 0, 18 ok, PASS.
- The acceptance for-loop over all 7 detectors (`fires` and `quiet on control` greps): rc 0.
- `test -f plugins/sdlc-lite/scripts/traces/detectors/hygiene.py`: rc 0.
- (guard) scope command, as written in the handoff: rc 0.
- `python3 plugins/sdlc-lite/scripts/traces.py selftest` (all families): rc 0, 76 ok, PASS.
- Mutation check: I replaced each of the 7 detector functions in turn with `lambda ctx: []` and ran `selftest.run('hygiene')`. Every run gave rc 1, with at least one missed case each.
- `git diff --check`: clean. `git worktree list` shows no leftover worktrees from the fixtures, which live in tempfile dirs.

## Notes
- **Control fixture edit:** the step 6 prefixed fixture's `beta-T-0002.log` mixes run ids, which is exactly the stale-log-lines defect. The hygiene control rewrites it to a single id, and the control also registers `codex/work` and creates that branch so the fixture is clean. The unchanged prefixed fixture is used in a separate case: mixed ids give severity 2, with evidence at line 2 (the first line of the second id).
- **Integration worktree:** both the fires and control fixtures point the report's integration worktree at the throwaway repo. Left at the fixture's `/nowhere` path, it produces `reflog-gone` instead of integration-reset, and a separate case checks that: severity 1, no integration-reset.
- **Evidence entries without a file line:** worktrees, tracked paths, whole logs and the ticket root carry `line: None`. Extra keys hold detail (`reflog`, `commit`, `problem`, `branch`, `worktree`). Paths inside the repo are repo-relative; lanes-dir paths outside it stay absolute.
- **integration-reset pairing:**
  - Only the first lanes dir whose integration worktree exists is paired with `aux.git.resets`, matching the one `ingest` reads the reflog from.
  - Lost-edit signals are: report rows or fanout.log lines with `red: ... rc=`, `integration dirty`, or `wip `, plus `wip(` commits from `aux.git.commits`.
  - Each reset gives one finding, with evidence of the reflog entry and the first signal.
  - `reflog-gone` fires once for each lanes dir whose integration worktree is gone and that has one of its own line signals.
- **External branches:** the "registered but no local branch" check is skipped when `aux.git.branches` is empty, since that means the git read failed.
