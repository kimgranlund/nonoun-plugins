<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `grep -q "build L3 done, no verifier -> verify L2" plugins/sdlc-lite/scripts/steps.py`: pass. Evidence: exit 0 on the tree. It bites: the same grep exits 1 in a throwaway `git worktree add HEAD` copy. The case is at steps.py:998-999, right after the L4 → verify L3 check at :996-997, in the same two-line style.
- Mutant check: pass. Evidence: I ran the criterion's command verbatim on the tree and it exited 0. In a separate run of the mutant copy, the selftest exited with rc=1 and printed `steps selftest: FAIL, these did not hold:` with `  - next verify: build L3 done, no verifier -> verify L2` as the only listed case. The grep therefore matches a FAIL entry, not an `ok:` line. It bites: the same command on the HEAD worktree exited 1, and that mutant's selftest ended `steps selftest: PASS`. The biting variable is the new case. The `! cmp` conjunct only confirms that sed changed the copy; steps.py:456 holds `else 2 if build_level == 3 else 3`, so the sed pattern matches.
- (guard) tree selftest ends `steps selftest: PASS`: pass. Evidence: exit 0 on the tree. This guard is meant to be green now, so its red side is covered by the mutant run above, where the selftest's last line was the FAIL list.
- (guard) no deleted lines in the steps.py diff: pass. Evidence: exit 0. `git diff` shows only 2 `+` lines in one hunk. It bites: the same predicate on a fake diff containing `-removed` exits 1.
- (guard) every hunk sits inside `def selftest`: pass. Evidence: exit 0. The only hunk header is `@@ -995,6 +995,8 @@ def selftest():`. It bites: a fake header naming `def verifier_level(build_level):` makes the predicate exit 1.
- (guard) nothing outside `.sdlc/` other than steps.py is modified or untracked: pass. Evidence: exit 0. `git status --short` lists only `.sdlc/...` paths and steps.py. It bites: after I touched an untracked `zz_probe` in the throwaway HEAD worktree, the predicate exited 1. I deleted the file afterwards.
- `check.sh` exits 0 with no new findings versus HEAD: pass. Evidence: `plugins/sdlc-lite/scripts/check.sh` gave rc=0 on the tree and rc=0 in the HEAD worktree. The two outputs' lines matching `fail|error|warn` (case-insensitive) are identical (`diff` rc=0), and the tree output ends with `ok: shellcheck` and `ok: plugin validate`. I removed the worktree afterwards (`git worktree list` shows 0 `head` entries).
- Builder claim "Changes: none needed": accepted. The only diff in steps.py is the 2-line addition described in the handoff, which came from the superseded attempt.

## Out of scope changes
None. `.sdlc/add-a-steps-py-selftest/handoff.md` is modified and the other `.sdlc/` paths are untracked. The handoff excludes `.sdlc/` on purpose because it holds task and role-run files, and the porcelain guard above confirms nothing else changed.

## For the next attempt
None
