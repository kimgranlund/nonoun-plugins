<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- The overwrites grep finds no line saying a rerun overwrites a result: pass. Evidence: `grep -rn "overwrites" plugins/sdlc-lite/skills plugins/sdlc-lite/scripts CLAUDE.md` now returns 3 lines, and each says "never overwrites": run.sh:5, CLAUDE.md:15, board.py:16. At HEAD (throwaway worktree /tmp/vwt-s2) the same grep returned `handoff-format/SKILL.md:25: ... Rerunning the same role and level overwrites them`, so the check went red before the change. The `skills/` line is gone now.
- `grep -n "<role>-<level>-<k>"` matches in both handoff-format/SKILL.md and CLAUDE.md: pass. Evidence: it matches handoff-format/SKILL.md:26 and CLAUDE.md:15. At HEAD it exited with rc=1 (no match).
- `grep -n "newest"` in chain/SKILL.md matches the replan instruction: pass. Evidence: chain/SKILL.md:30 reads "run planner L3 ... (replan; it writes a new `planner-L3[-k].md`), rewrite the remaining step handoffs from the newest planner file (earlier plans stay in place)". At HEAD it exited with rc=1. The §4.4 rebuild text is at line 32 and names `builder-L<n>-<k>.md` and the rubric's blocked count, as the Do list asks. The layout example has the `planner-L3-2.md` line at SKILL.md:15.
- `grep -n "run selftest\|run-selftest"` matches in both CLAUDE.md and sdlc-lite-author.md: pass. Evidence: it matches CLAUDE.md:11 ("tickets, board, and run selftests") and .claude/agents/sdlc-lite-author.md:19 ("board selftest, run selftest,"). At HEAD it exited with rc=1.
- `plugins/sdlc-lite/scripts/check.sh` exits 0: pass. Evidence: an observed run gave rc=0. The output ended with "run selftest: PASS", "ok: shellcheck" and "ok: plugin validate". The builder ran check.sh before its last reorder of the layout line. This run came after that reorder, so it covers the final tree.

## Out of scope changes
None. Step 1 owns the other modified files: run.sh, board.py, check.sh and the new run-selftest.sh. Its handoff lists all four. `.sdlc/replan-overwrites-plan/handoff.md` has 3 inserted lines. Those are task bookkeeping, not a project change from this step.

## For the next attempt
None
