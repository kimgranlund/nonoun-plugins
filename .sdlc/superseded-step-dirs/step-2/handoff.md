## Task goal
Define `step-<n>.superseded-<k>/` as the name for a step dir replaced by a replan. `board.py` and `bench-summary.sh` skip it when counting steps, but still count its cost, and `/chain` and `handoff-format` document and perform the rename.

## Step 2: bench-summary.sh skips superseded dirs for steps, keeps their cost
level: L1
### Do
In `plugins/sdlc-lite/scripts/bench-summary.sh`, in the step loop at line 13:
- After the `[[ -d "$s" ]] || continue` check, add a skip for any dir whose basename does not match `^step-[0-9]+$`. For example, `[[ "$(basename "$s")" =~ ^step-[0-9]+$ ]] || continue`.
- Leave the cost line (20), which globs `step-*/runs.jsonl`, unchanged.
- Add a comment saying superseded dirs count for cost only.

### Acceptance criteria
- Build a temp bench dir with `results/2026-01-01-t/step-1/` (a passing `verifier-L1.md` and a builder `runs.jsonl` line with cost 1.00) and `results/2026-01-01-t/step-1.superseded-1/` (a builder `runs.jsonl` line with cost 2.00).
- Run `SDLC_BENCH_DIR=<tmp> plugins/sdlc-lite/scripts/bench-summary.sh`. The output shows steps=1, passed=1, attempts=1, cost=3.00.
- `shellcheck plugins/sdlc-lite/scripts/bench-summary.sh` is clean.

## Paths
Edit only files in this worktree (/Users/kimba/Projects/nonoun/sdlc-lite-wt-tickets7/plugins/sdlc-lite). Do not commit.

## Previous attempt
The literal shellcheck criterion fails on an older SC2012 info finding at `plugins/sdlc-lite/scripts/bench-summary.sh:19` (`ls -t "$s"verifier-*.md | head -1`). Either of these fixes it:
- Replace that `ls -t` pick with one that does not parse `ls`, keeping the newest-verifier behavior. Then re-run the fixture and confirm steps=1, passed=1, attempts=1.
- Have the planner change the criterion to `shellcheck --severity=warning`, which matches `scripts/check.sh:14` and already passes.

The step logic itself is correct and was observed red at HEAD and green in the working tree.
