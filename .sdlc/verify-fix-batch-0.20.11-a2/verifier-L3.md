<!-- role=verifier level=L3 model=fable effort=xhigh -->
## Verdict
fail

## Criteria
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: pass. Evidence: real tree at 832bb36, exit 0, 244 `ok:` lines, `steps selftest: PASS`, empty stderr.
  - Bite: in a throwaway worktree at HEAD I removed the one line `reasons += lean_only_reasons(plan, t, review_line)` (`steps.py:1749`). Selftest gave exit 1 with only `(lane) lean stays strict: planner L3, a replan, and a ## Plan review line each keep a ticket full...` red. Restored from `git show HEAD:`, PASS again.
  - That selftest fixture has no Merge title, so the merge branch of `lean_only_reasons` is proven only by the CLI runs under criterion 4.
- `python3 plugins/sdlc-lite/scripts/check.py`: pass. Evidence: exit 0, `ok: 19 role levels, 9 agents checked`.
  - Bite: in the throwaway, the rubric row `| plan-reviewer | L1 | Opus high |` changed to `Opus low` gave exit 1 with `FAIL level-rubric: plan-reviewer:L1 = Opus low, run.sh = Opus high`. Restored, exit 0.
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: pass. Evidence: exit 0, `Codex agent definitions verified`.
  - Bite: in the throwaway, putting "(a merge step is L4 or higher)" back into `skills/level-rubric/SKILL.md` gave exit 2 with `generated agent drift: .../sdlc-planner-l1.toml`. Restored, exit 0.
  - The five TOML changes in 832bb36 hold only that rubric sentence (word diff: `L5 (a merge step is L4 or higher).` to `L5.`, plus `merge step, a`).
- The fixture gives lane `full` and review `split`; no dependent text contradicts the code: fail. The fixture half passes; the text half fails.
  - Fixture half, pass. Fixture: size M, `planner-L3.md` plus `planner-L3-2.md`, step 1 titled `Merge x` at L2, a `## Plan review` line, in a fresh git repo per run because `lane` writes `skips.md`.
    - `steps.py lane` at HEAD prints `full` with four reasons: `planner-L3-2.md is a planner L3 plan`, `the plan has a merge step`, `2 planner results (a replan)`, `handoff.md holds ## Plan review`. At 3482207 it prints the same four. At 0e85edb it prints `lean`, so the check goes red before the fix.
    - `steps.py review` at HEAD prints `split` (`planner-L3-2.md is a routine plan; no plan review is required`). At 3482207 it prints `review L1`.
    - One variable at a time at HEAD, two-step planner-L2 fixtures: the plain one is `lean`; a Merge title, a replan, a `## Plan review` line, and a planner-L3 file each give `full` with exactly their one reason. An L4 step gives `full` and `review L1`; the other five give `split`.
  - Text that agrees with those runs:
    - `plugins/sdlc-lite/scripts/steps.py:124-125` (review docstring) and `steps.py:164-166` (lane docstring).
    - `plugins/sdlc-lite/skills/chain/SKILL.md:19,23`.
    - `docs/lean-sdlc/design.md:78-80,85,91,217,283`.
    - `plugins/sdlc-lite/skills/level-rubric/SKILL.md:58` and `plugins/sdlc-lite/skills/handoff-format/SKILL.md:19`.
    - `plugins/sdlc-lite/agents/conductor.md:12,33,42` and `plugins/sdlc-lite/AGENTS.md:9`.
  - No text claims a merge step is L4 or higher: a `git grep` for that claim over live tracked files prints nothing, and `grep -l "merge step is L4 or higher"` over the 28 generated TOMLs exits 1. `agents/planner.md:51` says "Pick the level with the rubric as usual".
  - Text half, fail 1: the lint usage text contradicts the lint code. The Do names both spots.
    - `steps.py:103-108` (lint docstring) and the `--help` epilog (`steps.py:3775-3778`, read from a real `python3 steps.py --help` run) say a plan with a Merge step, a replan, or a `## Plan review` line does not meet the lean plan conditions and gets no warning.
    - `lean_warnings` (`steps.py:1129-1138`) checks only the planner level and `review_required()`. The fix wired `lean_only_reasons` into `lane_action` and not into lint.
    - Observed on lint-clean three-step planner-L2 fixtures, warnings at 3482207 / 0e85edb / HEAD: Merge title 0 / 1 / 1, replan 0 / 1 / 1, `## Plan review` line 0 / 1 / 1. Controls: plain plan 1 / 1 / 1, planner L3 0 / 0 / 0, L4 step 0 / 0 / 0.
    - The HEAD warning reads "3 steps; the coarse-step rule allows at most 2 in a plan that meets the lean plan conditions" (`steps.py:1142-1143`). `steps.py lane` on the same three dirs prints `full` with the merge, replan, or `## Plan review` reason, so lint and lane still disagree on what lean is.
    - `docs/lean-sdlc/design.md:97` says lint warns on a "lean-eligible plan", which those three are not.
    - The T-0294 build narrowed two records to the loose reading: `agents/planner.md:18` and the selftest case at `steps.py:2480-2488`, which lost its merge, replan, and `## Plan review` quiet cases. The records are split, not just stale.
  - Text half, fail 2: `docs/maintenance/sdlc-internals.md:57` still states the old rules.
    - Its review sentence reads "a review is required for a planner L3 plan, a step at `level: L4` or `L5`, a step titled `Merge ...`, two or more planner results (a replan), or a `## Plan review` line in `handoff.md`". It is byte-identical at 3482207 and HEAD, and `review` prints `split` on every one of those at HEAD.
    - Its lint sentence carries the same strict list as fail 1.
    - Its lane sentence says lean needs only `review_required()` to give no reason, which leaves out the four lean-only reasons.
  - Steelman, fail 1. Rebuttal: the lint docstring agrees with the strict lane, and `planner.md:18` and the selftest were updated to match the code, so only wording is left. Response: the criterion is text against code, the Do names the epilog and the lint docstring, and the runs show lint doing what both say it does not. It survives.
  - Steelman, fail 2. Rebuttal: `sdlc-internals.md` is on no file list. Response: the criterion says "no dependent text", and `plugins/sdlc-lite/AGENTS.md:17` sends maintainers to that file as the implementation reference for step internals. It survives, and is filed as a plan defect for that reason.
  - Not a fail: `design.md:85` cites `steps.py:103` for the review rule and line 103 is now in the lint section. The citation is the same at 3482207, so it predates this fix.

## Out of scope changes
None.
- `git show --stat 832bb36` lists 8 files: `steps.py`, the two skills named in the task goal, and five generated Codex TOMLs that carry the rubric sentence.
- `git status --short` is the same before and after my runs: only untracked run.sh bookkeeping under the three `.sdlc/verify-fix-batch-0.20.11-*` folders. HEAD is still 832bb36 with no tracked diff.
- My three throwaway worktrees are removed. A cleanup command for my scratch fixtures was denied, so `/tmp/vfix-a2.tYo8Iv` and a few `/tmp/vfix-a2-*` files remain outside the repo.

## For the next attempt
plan defect: the fix's file list and this handoff's Do omit a dependent of the changed `review_required` contract, `docs/references/sdlc-internals.md` (line 57: the review sentence, the lint sentence, and the lane sentence). Widen the scope to include it.

The lane and review behavior is verified and needs no change. What is left is lint and the text around it.

1. Pick one meaning of "lean plan conditions" for lint. This is a user decision; "lean stays strict", lane's behavior, and `design.md:97` point to the first option.
   - Strict, as lane: `lean_warnings` (`steps.py:1129-1138`) also returns `[]` when `lean_only_reasons` gives a reason, which needs the `## Plan review` line from `handoff.md`. Put back the three quiet cases in the selftest at `steps.py:2480-2488` and the `err == ''` in case `(j)` at `steps.py:2462-2463`. Put the merge, replan, and `## Plan review` conditions back in `agents/planner.md:18`, then run `codex_roles.py generate`.
   - Loose, as the code is now: change `steps.py:103-108`, the epilog at `steps.py:3775-3778`, and the lint sentence in `sdlc-internals.md:57` to the three-condition list in `planner.md:18`, and reword `design.md:97`.
2. Rewrite the review sentence in `docs/maintenance/sdlc-internals.md:57` to the L4 or L5 rule, and add the four lean-only reasons to its lane sentence.
3. Add a Merge-title plan to the `(lane) lean stays strict` selftest fixture so the merge branch of `lean_only_reasons` has its own red.
