<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/fanout.py`:
  - `run_ticket`: when the pre-sync `wip_commit` returns a sha, the ticket now returns `('dirty before sync', 'wip <sha>')` before the sync, and the comment above the call is updated. The clean-tree path is unchanged.
  - Module docstring: the old "Before each sync" sentence is replaced with the new behavior, and a paragraph for case 8 and its control is added.
  - `selftest()`: new case 8 (`dirty-sync case:`) and its negative control (`dirty-sync control:`).
- `plugins/sdlc-lite/skills/fanout/SKILL.md`: line 9 now describes the new pre-sync behavior.
- `CLAUDE.md`: only the wip sentence in the `scripts/fanout.py` bullet is rewritten. It covers the stop case and the pre-sync case, and says both commits stay on the lane branch and are never merged.

## Checks
- AC1, the end-to-end mktemp run from the git toplevel: exit 0. Its `fatal: path 'dirty.txt' does not exist` stderr line comes from the negated `cat-file` and is expected.
- AC2 `grep -qF "dirty-sync case:" ...`: exit 0.
- AC3 `grep -qF "dirty-sync control:" ...`: exit 0.
- AC4 (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: exit 0, printed `fanout selftest: PASS`.
- AC5 `sed -n "1,/^import /p" ... | grep -qF "dirty before sync"`: exit 0.
- AC6 `! grep -qF "Before each sync, a dirty lane tree is WIP-committed first" ...`: exit 0.
- AC7 `grep -qF "dirty before sync" .../SKILL.md`: exit 0.
- AC8 `! grep -qF "a dirty tree is also WIP-committed before each sync" .../SKILL.md`: exit 0.
- AC9 `grep -qF "dirty before sync" CLAUDE.md`: exit 0.
- AC10 `! grep -qF "and before a sync finds a dirty lane tree" CLAUDE.md`: exit 0.
- AC11 `git diff --quiet HEAD -- .claude/agents/sdlc-lite-author.md`: exit 0.
- Negative check, not a criterion: I removed the new `return` line and ran the selftest. It printed `FAIL` on 6 of the 7 `dirty-sync case:` checks (only the main-unchanged check held). T-0002 merged, `dirty.txt` reached the integration branch, and T-0002 closed, which reproduces the original bug. The file was then restored and the selftest passed again.
- Extra: `python3 plugins/sdlc-lite/scripts/check.py` exit 0 (`ok: 18 role levels, 8 agents checked`).

## Notes
- The case 8 gate path goes through `shlex.quote` so a temp dir with spaces cannot break it. Otherwise the case matches the handoff exactly.
- `.claude/agents/sdlc-lite-author.md` is unchanged, as the handoff says.
- I did not run the full `scripts/check.sh`. That belongs to step 2 (Gates green).
- The negative check kept its backup copy of `fanout.py` in `/tmp` and deleted it afterwards. No worktree was created.
