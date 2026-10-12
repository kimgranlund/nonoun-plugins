<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout35/h/plugins/sdlc-lite/scripts/check.sh: added the `lanes.py selftest` line right after the `gate_lock.py` line, and added `lanes.py` to the selftest list in the header comment.
- /Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout35/h/docs/references/sdlc-internals.md: added a ``## `scripts/lanes.py` `` section before the `scripts/fanout.py` section. It says what the script owns, points to `lanes.py --help` for the tables, names the importable API, notes that ticket A2 adds the worktree lock and worktree config, lists the 9 config keys with their defaults, and links to `../specs/sdlc-lite/lane-lifecycle.md`.

## Checks
- `redck.py record` exit 0. It saved 4 red controls, but as retrospective entries (see Notes).
- Red criteria 1 to 4 (the check.sh grep, the heading grep, the config-key loop, the `lanes.py --help` grep): all exit 0.
- `python3 scripts/check-packaging.py`: exit 0.
- `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`: exit 0.
- Scope `test -z ...` criterion: exit 0.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: the first run exited 1. I did not capture its stdout, so I don't know which part failed. A second run exited 0 with no edits in between. Its log shows `ok: lanes.py selftest`, `ok: shellcheck`, `ok: plugin validate`, and `docs_check: 0 errors`.

## Notes
- redck stored the controls as retrospective rather than pre-edit, because step 1's untracked `lanes.py` already differed from the base before this step's first edit. All 4 red criteria were red at base before any edit.
- The guard's first exit 1 had no visible failure line; I suspect concurrent load. A third full run was not done.
