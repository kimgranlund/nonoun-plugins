<!-- role=solo level=L1 model=sonnet effort=low -->
## Output
🟢 T-0502 is done. `lanes.py open` now copies the starting checkout's `.claude/settings.local.json` into a new lane worktree. It is a byte-for-byte copy and never overwrites an existing file. No other ignored file is copied, and the contents are never logged. A failed copy adds one line to the open output naming only the OS error.

**Files changed:** `plugins/sdlc-lite/scripts/lanes.py` only. That is the copy step in `open_lane`, plus a new `case_local_settings` selftest case wired into `run_selftest`.

**Checks:**
- **Red control:** with the case in and the fix not yet made, `lanes.py selftest` failed with "want the ignored settings file in the lane, byte for byte".
- **Green:** after the fix, `python3 plugins/sdlc-lite/scripts/lanes.py selftest` passes, including all existing cases and the mutant checks. The new case also asserts that a second ignored file, `.claude/other.json`, is not copied.
- `git diff --check` is clean.

**Open:**
- I did not run `check.sh`, since the change is confined to `lanes.py` and its own selftest.
- The ticket is L1, so there is no verifier step and I did not write acceptance criteria.
- `.sdlc/0502-lane-copies-local-settings/skips.md` is untracked and was not created by me.
