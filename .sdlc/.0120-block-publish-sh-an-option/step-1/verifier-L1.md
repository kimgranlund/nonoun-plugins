<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `python3 -X dev -c '...git push...'` exits 2: pass. Evidence: ran the exact criterion command in the built tree, `exit1=2`.
- `python3 -W ignore -c '...git push...'` exits 2: pass. Evidence: ran in built tree, `exit2=2`.
- `node --require x -e '...gh pr create...'` exits 2: pass. Evidence: ran in built tree, `exit3=2`.
- `perl -I lib -e '...git push...'` exits 2: pass. Evidence: ran in built tree, `exit4=2`.
- `ruby -I lib -e '...git push...'` exits 2: pass. Evidence: ran in built tree, `exit5=2`.
- (guard) `python3 -X dev scripts/check.py "git push"` exits 0: pass. Evidence: ran in built tree, `g1=0`.
- (guard) `python3 scripts/check.py -c "git push"` exits 0: pass. Evidence: ran in built tree, `g2=0`.
- `grep -qF -- '-X dev' plugins/sdlc-lite/scripts/hook-selftest.sh`: pass. Evidence: `grep1=0`.
- `grep -qF -- '--require' plugins/sdlc-lite/scripts/hook-selftest.sh`: pass. Evidence: `grep2=0`.
- `grep -qF -- '-X dev' plugins/sdlc-lite/hooks/block-publish.sh`: pass. Evidence: `grep3=0`.
- `grep -F 'hooks/block-publish.sh' CLAUDE.md | grep -qF -- '-X dev'`: pass. Evidence: `grep4=0`.
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`: pass. Evidence: `hook selftest: PASS`, exit 0.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: full output ending `ok: shellcheck`, `ok: plugin validate`, exit 0.

Check-bites confirmation: ran the blocked-exit and grep criteria in a throwaway worktree (`git worktree add --detach "$SDLC_TMP_WORKTREES/base" HEAD`, HEAD = a652269, the pre-build commit, since the builder made no commit). There: `python3 -X dev -c ...` gave exit 0 (not blocked), `node --require x -e ...` gave exit 0, the two `-X dev` greps both failed (exit 1), and `hook-selftest.sh` still passed (old fixtures don't cover the new case) — so every criterion that discriminates the change actually goes red pre-build and green post-build. Worktree removed after (`git worktree remove --force`, then `git worktree prune`; `git worktree list` confirms only the three permanent worktrees remain).

## Out of scope changes
`.sdlc/0120-block-publish-sh-an-option/handoff.md` (Goal/Constraints filled in) is changed but not by the builder: `.sdlc/0120-block-publish-sh-an-option/runs.jsonl` shows a planner L2 run at 2026-09-27T03:15:25Z (file mtime 20:15) writing `planner-L2.md`, before the builder's step-1 run (step-1 dir mtime 20:29); this is upstream planning output, not builder scope creep. The untracked `planner-L2.md`, task-level `runs.jsonl`, and `step-1/` artifacts are the normal SDLC process trail. No other files outside the Do's named targets (`plugins/sdlc-lite/hooks/block-publish.sh`, `plugins/sdlc-lite/scripts/hook-selftest.sh`, `CLAUDE.md`) were touched, confirmed by `git status --porcelain`.

## For the next attempt
None.
