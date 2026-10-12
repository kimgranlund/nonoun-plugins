<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout35/i/docs/reports/2026-10-11-builder-overlay-ab.md`: new report. It holds the verdict lines, the per-run table, rule outcomes, Method, the not-run section, Limits, and Raw rows (20 jsonl rows).
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout35/i/.sdlc/evals/0005-builder-overlays.md`: new eval, written by `evals.py add`.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout35/i/.sdlc/0442-builder-overlay-ab/step-2/red-checkpoint.jsonl`: written by `redck.py record`.
- Under the git-ignored prefix `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout35/i/.worktrees/tmp/0442-s2-builder-L3/`: arm roots `armA` and `armB`, ten cell clones `ab-<task>-L1-<arm>-<rep>`, the driver scripts `cell.py` and `pairs.py`, and `evidence/` (preflight jsonl, per-cell logs, prepare, claude, record and grade output, `summary.jsonl`, `budget.log`, `table.md`, `raw.jsonl`).

## Checks
- `redck.py record <handoff>` ran before the first edit and exited 0. It printed "retrospective: 3 source path(s) already differ from the base ... recorded 6 retrospective control(s) red".
- Preflight `claude -p --plugin-dir <arm>/plugins/sdlc-lite --model haiku --output-format stream-json --verbose "ok"`, armA and armB: both exited 0. The init `plugins` list held a single `sdlc-lite@inline` entry at the arm path. A third preflight from inside the first cell clone, with armA, showed the same.
- Arm diff: `diff -rq armA/plugins armB/plugins` lists only `agents/builder-L1.md` and `builder-L5.md`. Each has one hunk, and that hunk is the `## At this level` section. `git diff --stat 00735e20^ HEAD -- plugins/sdlc-lite/agents/builder.md` printed nothing.
- Cells: 10 builder runs and 10 verifier runs, each through `dispatch.py prepare`, headless `claude -p`, and `dispatch.py record --transcript`.
  - All 20 records exited 0 with a priced row (`cost_basis` "usage fields x rates").
  - Grading ran 8 times: subagent-tool-names passed 4 of 4 and figma-stale-skip-report failed 4 of 4. command-modal-footer is `n/a` by the handoff.
- (red) The verdict-line grep, the exact table header, the A/B row count (A=5, B=5), Spend versus the table sum (7.94 vs 7.92, within 0.05), the not-run names plus `## Raw rows`, and the eval file grep: all exited 0.
- (guard) The `git diff --quiet` scope check on overlays, agents, adapters and scripts exited 0.
- (guard) The python scope check printed `[]` and exited 0.
- (guard) `evals.py check` exited 0: "ok (6 evals, lock cites .sdlc/evals/0004-solo-l2-high.md)".
- (guard) `check.py` exited 0 and `check-packaging.py` exited 0. Both were re-run to read the exit code, because `PIPESTATUS` is empty under zsh.
- (guard) `git diff --check "$SDLC_BASE_SHA"` exited 0. It does not cover the untracked report, so I also grepped the report and eval for trailing whitespace and for em dashes: none found.

## Notes
- Red checkpoint: `redck.py record` ran before this step's first edit. It still stored the 6 controls as retrospective, because step 1's three bench task edits were already in the tree.
- Result: Verdict drop, L1 overlay drop, L5 overlay unverified, Null at this sample size no, Spend 7.94 USD. Arm B passed 3 of 5.
- The L1 drop comes only from the blocked-rate rule. No builder blocked in either arm (0 of 5 each), so B can never be "below" A. Everything else matched or moved within noise:
  - first pass identical per task
  - builder cost +3.3 percent
  - no hidden-check regression
  - minutes moved both ways
- The null line is the one judgment call. I applied the handoff's rule as written: all four L1 rule outcomes are the same in both reps, and L5 has no reps, so the line is `no`. That definition differs from the design's meaning of null ("no visible effect at this cost"), which is what the data shows. The report says this. The planner may want to repair the rule. Rep 2 covered only two tasks, so its rules were compared on those two.
- Budget: command-modal-footer L1 rep 2 was skipped (7.94 + 2.28 > 10), and all six L5 pairs were skipped (7.94 + 8.00 > 10). All are listed as unverified. My estimate was twice the costliest single cell (builder plus verifier). Reading it as twice (costliest builder + costliest verifier) gives 2.30 and changes no start or skip.
- figma-stale-skip-report failed the same hidden gate, `staleskipnotice`, in all four runs, and the verifier passed it every time. That miss is the same in both arms, and the archived run also failed.
- Clones, not worktrees: the stray-worktree hook blocked `git worktree add` (SDLC_TMP_WORKTREES unset). As the handoff notes direct, arms and cells are `git clone --shared` copies, and the report's Method records this.
  - The child sessions got `SDLC_TMP_WORKTREES` set to the prepare tmp_prefix, with FANOUT_* and CLAUDE_CODE_AGENT removed, the same for both arms.
  - The clones are kept, not removed: handoff step 5 says never delete cell trees, and the verifier needs the arms to re-run the diff.
- No `prepare` refused anywhere. Every dispatch had an empty `lane_override` and `specgate`.
