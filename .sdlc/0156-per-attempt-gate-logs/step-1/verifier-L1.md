<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Two-run probe (the full command from the handoff, run from the repo root): pass. Evidence: on the built tree the command exited 0. At the base commit c9dfd26 (detached worktree) the same setup gave run 1 rc=1 and run 2 rc=0, but `logs/` held only `gate-alpha-T-0001-1.log`. `grep -l attempt-one` on that file matched nothing (a=1), because the rerun overwrote it. So the probe can go red, and it is green now.
- `grep -qF "gate retry case" plugins/sdlc-lite/scripts/fanout.py`: pass. Evidence: exit 0; the case-10 code is in the diff.
- `! grep -qF "gate-<lane>-<id>-<k>.log" plugins/sdlc-lite/scripts/fanout.py docs/maintenance/sdlc-internals.md`: pass. Evidence: grep exited 1, so the negation holds. Both files exist, and the diff shows the old string replaced in each.
- `! grep -qF "Driver and gate log files keep their names and are overwritten" plugins/sdlc-lite/scripts/fanout.py`: pass. Evidence: grep exited 1. The diff replaces the sentence with "Driver logs are overwritten; gate logs are never overwritten, one file per attempt."
- Scope check (`git diff --name-only "$SDLC_BASE_SHA"` plus untracked files, with the three allowed paths excluded): pass. Evidence: the command printed an empty result. `git status` shows only `fanout.py`, `sdlc-internals.md` and `.sdlc` files changed.
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: pass. Evidence: "fanout selftest: PASS". It includes the new case 10.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: exit 0. It printed "skip: shellcheck not installed" and "ok: plugin validate".
- (guard) `python3 scripts/check-packaging.py`: pass. Evidence: "PASS: catalog parity, identity, skill routes, hook isolation and context links".
- (guard) `git diff --check`: pass. Evidence: exit 0.

Steelman: I drafted a fail on the missing shellcheck. The builder's rebuttal holds: the check is a skip printed by the script and the script exits 0, so I dropped it.

Builder claims checked: the probe pass, the selftest and check.sh exit 0 (rerun by me). The builder's note that it never ran the probe at base is answered by my base run above.

The regex-not-mtime requirement is met. `fanout.py` uses `re.compile(re.escape(stem) + r'(\d+)\.log$')` and takes the max, defaulting to 1.

## Out of scope changes
None.

## For the next attempt
None
