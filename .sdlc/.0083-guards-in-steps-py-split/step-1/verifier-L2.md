<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- A guard that creates an untracked file in a git repo refuses (writes no handoff, `plan defect:` last line names path): pass. Evidence: ran the exact criterion command from handoff.md; output `plan defect: step 1 (guard) criteria changed the work tree: sdlc-guard-made; replan this step (/chain 3)`, `test ! -e .../step-1/handoff.md` succeeded.
- A guard that modifies a tracked file refuses the same way: pass. Evidence: ran the exact criterion command; last line `plan defect: step 1 (guard) criteria changed the work tree: tracked.txt; replan this step (/chain 3)`, no handoff written.
- (guard) A guard that changes nothing passes: pass. Evidence: ran the command, `split` exited 0 and `step-1/handoff.md` was written.
- (guard) A tree dirty before the guards passes: pass. Evidence: ran the command, `split` exited 0 and `step-1/handoff.md` was written.
- `(o)` selftest count ≥ 3: pass. Evidence: `python3 steps.py selftest | grep -c '^ok: (o)'` → 7.
- `grep -q "changed the work tree" steps.py`: pass. Evidence: grep found the phrase (docstring lines 25-29 of `plugins/sdlc-lite/scripts/steps.py`).
- (guard) selftest last line is `steps selftest: PASS`: pass. Evidence: observed exact line.
- (guard) `(n)` count ≥ 7: pass. Evidence: `grep -c '^ok: (n)'` → 7.
- Observable: no edit to existing `(n)` selftest case bodies: pass. Evidence: `git diff HEAD -- plugins/sdlc-lite/scripts/steps.py | grep -E '^[-+].*\(n\)'` produced zero lines (only additive `(o)` block appended, confirmed by reading the full diff hunk).
- Checks-that-bite (own control, not just the builder's claim): confirmed red-then-green independently. In a throwaway `git worktree add /tmp/verify-guards-preimage HEAD` (pre-fix state), the untracked-file criterion's `split` succeeded and wrote `step-1/handoff.md` (side effect NOT caught) — proving the check bites. In the working tree (post-fix) the same scenario refuses and writes nothing. Worktree removed after.
- Combined red-guard + changed-tree case (per Do: "Report both, with a single `plan defect:` last line"): pass. Evidence: manual run with one tree-changing guard and one genuinely red guard (`test -e <nonexistent>`) produced both a red-guard line and a changed-tree line, and exactly one `plan defect:` line naming both.
- `scripts/check.sh` stays green: pass. Evidence: ran `plugins/sdlc-lite/scripts/check.sh`, rc=0, all selftests PASS including `steps selftest: PASS`, shellcheck ok, plugin validate ok.

## Out of scope changes
`.sdlc/0083-guards-in-steps-py-split/handoff.md` is modified (Goal and Constraints filled in) but this predates the build: file mtime 14:26:12, versus `planner-L2.md` at 14:31:30 and `builder-L3.md` at 14:37:08 — it was written during an earlier pipeline stage (clarify/handoff creation), before the planner or this builder ran. Checked `git diff` for step-2's files (`check.py`, `CLAUDE.md`, `.claude/agents/sdlc-lite-author.md`, `skills/chain/SKILL.md`, `agents/planner.md`) — `git diff --stat` on all five produced no output, confirming step-1's builder did not touch step-2's scope. No other files outside `plugins/sdlc-lite/scripts/steps.py` were changed by this build. Dismissing both as non-issues.

## For the next attempt
None.
