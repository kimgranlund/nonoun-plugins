<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Selftest exits 0 and prints `hook live probe selftest: PASS`: pass. Evidence: I ran `bash hook-live-probe.sh --selftest`. It printed `hook live probe selftest: PASS` and `rc=0`.
- `grep -q "(e)"` on the script: pass. Evidence: `grep=0`. The diff adds `# (e)` at the new case and in two comments. At HEAD the script has none of these lines.
- Mutation check turns the selftest red: pass. Evidence: I ran the handoff's command as written. The sed deletes the `"$hook_rc" != "2"` check and its next line in a copy, and the mutated selftest exited nonzero, so `mut=0`. Case (e) is the biting variable: the `nodeny` stub runs the hook with `SDLC_HEADLESS` and `SDLC_ROLE` unset, so it exits 0 for a boolean-true payload, and only the `hook_rc != 2` check turns that into `FAIL: hook exit code 0, not 2`. I did not run the mutation against HEAD in a throwaway worktree. The handoff states it is red at HEAD, and the diff shows case (e) as the only thing that changes the result.
- No temp dir left behind: pass. Evidence: I ran the selftest with a fresh `TMPDIR`. The output had 0 `temp dir left behind` lines, and `ls -A` on the dir showed 0 entries.
- Diff only above the `# Live mode.` banner: pass. Evidence: the awk guard gave `guard=0`. The banner is at line 128 and every hunk sits above it. The `git diff` shows only selftest-block hunks.
- `check.sh` exits 0: pass. Evidence: `check=0`. The tail shows `hook live probe selftest: PASS`, `ok: shellcheck` and `ok: plugin validate`.

## Out of scope changes
None. The `.sdlc/add-a-hook-live-probe/` changes (`handoff.md`, planner, runs and step files) are task artifacts, not project files. The only source file changed is `plugins/sdlc-lite/scripts/hook-live-probe.sh`. Cases (a) to (d) and live mode are untouched in the diff.

## For the next attempt
None
