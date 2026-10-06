<!-- role=verifier level=L3 model=fable effort=xhigh -->
## Verdict
fail

## Criteria
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: pass. Evidence: real tree at c461bc6, exit 0, 244 `ok:` lines, `steps selftest: PASS`, empty stderr. The new cases are present: `(precheck) the refusal names the ## Task goal heading it found`, `(split) a handoff with only ## Task goal names it as found`, `split: step 2 inherits the path step 1 widened...`, `(r) plan review only for L4 or L5...`, `(lane) before planning, size alone decides...`. The gate can go red: see the four controls below, each exit 1.
- `python3 plugins/sdlc-lite/scripts/check.py`: pass. Evidence: exit 0, `ok: 19 role levels, 9 agents checked`.
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: pass. Evidence: exit 0, `Codex agent definitions verified`. Bite check in a throwaway worktree at HEAD: one line appended to `agents/planner.md` gave exit 2 with `generated agent drift: .../sdlc-planner-l1.toml`; restored, exit 0.
- `python3 scripts/check-packaging.py`: pass. Evidence: exit 0, `PASS: catalog parity, identity, skill routes, hook isolation and context links`.
- Each of the four regression cases goes red with its fix reverted: pass. Evidence: throwaway worktree `$SDLC_TMP_WORKTREES/base` at HEAD, baseline selftest exit 0. Each control reverted only the non-test hunk by exact string replace (one match asserted, `py_compile` clean), ran `steps.py selftest`, then restored from `git show HEAD:`.
  - 0294, `review_required` back to the old five-trigger body: exit 1. Red: `(r) plan review only for L4 or L5: ...`, `(r) review_required returns the unresolved items and every reason review prints, in order`, `(lane) planner L3, a replan, and a ## Plan review line alone no longer make a ticket full`.
  - 0295, `near`/`hint` lines in `read_goal` replaced by the old single `raise Fail`: exit 1. Red: `(precheck) the refusal names the ## Task goal heading it found`, `(split) a handoff with only ## Task goal names it as found`.
  - 0296, the three-line `ticket_k > LANE_MAX_TICKET_CRITERIA` block deleted from `lane_action`: exit 1. Red: `(lane) before planning, size alone decides: S and M solo, L and XL full, no size full`. The 20/21 case is folded into that check's accumulated `ok`, so the red carries the older name.
  - 0297, `inherit_widened` call in `split` replaced by the old direct `write_text`: exit 1. Red: `split: step 2 inherits the path step 1 widened, in its allow-list and its Scope widened section`.
  - Second leg, the real CLI on identical fixtures, a worktree at 3482207 against HEAD:
    - `review`: a planner-L3 plan, a replan, a `## Plan review` line, and a Merge title each print `review L1` before and `split` now. L4 and L5 print `review L1` on both. An `unresolved:` assumption prints `stop` on both.
    - `precheck` and `split` on a `## Task goal` handoff: now add `; found ## Task goal instead, expected ## Goal`. A `## Notes` handoff gives byte-identical messages on both.
    - `lane`: size M with 21 boxes prints `solo` before and `full` with `ticket lists 21 criteria (limit 20 for size S or M); split it into tickets of at most 20` now. M with 20 prints `solo` on both. S with 21 and M with 21 `- [x]` boxes print `full` now. L with 21 is unchanged.
    - `split --only 2`: the step 2 scope span gains `-e p/inherit.txt` plus a `## Scope widened` entry now. With no earlier widening the step 2 handoff is identical on both (`diff` empty).
- Do check, 0294 changed no model or effort value: pass. Evidence:
  - `git diff --quiet 3482207 HEAD -- plugins/sdlc-lite/adapters/codex/models.json` exits 0.
  - The `run.sh` diff holds only T-0298 `limit_marker` hunks (commit 91cf128). The role:level, `model=`, and `effort=` lines extracted at both shas are identical (25 lines).
  - The level-rubric table lines at both shas are identical (29 lines).
  - None of 48e25a3, 9456b37, 9d8f3be, 3a75c8b touches `run.sh` or `models.json`.
- Do check, the four files state plan review is for L4 and L5 only: pass. Evidence: `skills/chain/SKILL.md:23,48,53`, `agents/conductor.md:33`, `docs/lean-sdlc/design.md:85,217`, `skills/level-rubric/SKILL.md:58`.
- Ticket text criteria for 0295, 0296, 0297: pass. Evidence: `docs/maintenance/sdlc-internals.md:55` (found-heading sentence), the sdlc-internals lane sentence naming the limit of 20 and `docs/lean-sdlc/design.md:91`, and one dry-run sentence in `agents/planner.md` (`grep -c` gives 1).
- Dismissed, T-0295 says "lint" fails: `steps.py lint` exits 0 on the `## Task goal` fixture at both 3482207 and HEAD, and `read_goal` has two callers only (`steps.py:1016` split, `steps.py:1103` precheck). Lint never raised this refusal, so there was nothing to extend.
- Dismissed, weakened selftest assertion `(j)` (dropped `err == ''`): a replan now gets a lean warning on stderr, observed (`lint` on the replan fixture gives 0 warnings before, 1 now). It follows from the rule change.
- Diff review, dependents of the changed `review_required` contract: fail. Evidence, all from T-0294:
  1. Lean eligibility changed and its records were not updated.
     - Fixture: size M, `planner-L3.md` plus `planner-L3-2.md`, a `Merge x` step at L2, and a `## Plan review` line.
     - `steps.py lane` prints `full` with four reasons at 3482207. At HEAD it prints `lean` with `every lean condition holds: size M, planner L3, 2 steps at L1 to L3, one AGENTS.md owner (.)`.
     - `skills/chain/SKILL.md:19` still says lean needs "planner L1 or L2; ... no merge step; no replan". `docs/lean-sdlc/design.md:78-80` says the same.
     - `lint` still excludes planner L3 from the lean plan conditions (`steps.py:1131`, 0 warnings on the planner-L3 fixture at HEAD), so `lint` and `lane` now disagree on what lean is.
  2. `steps.py` usage text is half updated.
     - `steps.py:165` was changed, but `steps.py:103-108` (lint lean conditions) and `steps.py:124-126` (review "required when") still state the old triggers.
     - The argparse epilog at `steps.py:3754-3757` prints at runtime: `python3 steps.py --help` shows "no Merge step, no replan, no ## Plan review line in handoff.md".
     - At HEAD `lint` does warn on the Merge-title, replan, and `## Plan review` fixtures (0 warnings each at 3482207, 1 each at HEAD), so the help text is false.
  3. `skills/level-rubric/SKILL.md:58` adds "(a merge step is L4 or higher)", which is not true at source.
     - `agents/planner.md:51` says "Pick the level with the rubric as usual" and the template at `planner.md:59` is `level: L<n>`.
     - `steps.py` enforces no merge-step level.
     - A Merge-titled L1 plan prints `split` at HEAD, so a merge step below L4 now gets no plan review.
  4. `skills/handoff-format/SKILL.md:19` still reads "plan review (planner L3, a step at L4 or L5, a merge step, or a replan)".
- Steelman of that fail: the builder's rebuttal is that the ticket named chain, conductor, design, and rubric only for the review-rule sentence, and all four state it. Response: the ticket also said to keep `steps.py lane` consistent, and the build changed lane's lean outcome and added a selftest asserting it. It left the lean conditions in those same named files and the script's own help text stating the old rule. The finding rests on observed runs, not on a reading. It survives.

## Out of scope changes
None from the four fix commits.
- `plugins/sdlc-lite/scripts/steps.py.bak` was added by 9456b37 and removed by 0e85edb: `test ! -e` passes and `git ls-files` lists no `.bak` file.
- The other changes since 3482207 (gate_lock.py, solo_run.py, fanout.py, board.py, run.sh, check.py, check.sh, run-selftest.sh) belong to T-0293 and T-0298 to T-0304, per `git log 3482207..HEAD`.
- The untracked `base-sha` and `verifier-L3.attempt.json` files in both batch folders are run.sh bookkeeping, timestamped 08:56 with the run lock.

## For the next attempt
plan defect: T-0294 rests on the premise "a Merge step is L4 or higher by its template", which is false (`plugins/sdlc-lite/agents/planner.md:51,59`), and its file list omits dependents of the rule: `plugins/sdlc-lite/skills/handoff-format/SKILL.md` and the usage text inside `plugins/sdlc-lite/scripts/steps.py`.

T-0295, T-0296, and T-0297 are verified and need no change. T-0294 needs two user decisions, then text repair.

1. Merge steps: keep a merge trigger in `review_required`, pin merge steps at L4 in the planner template, or accept no review below L4. Then correct `skills/level-rubric/SKILL.md:58` to match.
2. Lean lane: either `lane` keeps refusing planner L3, a replan, and a merge step with its own reasons, or the lean conditions in `skills/chain/SKILL.md:19` and `docs/lean-sdlc/design.md:78-80` drop them and `lint` (`steps.py:1131`) follows the same rule as `lane`.
3. Repair `steps.py:103-108`, `steps.py:124-126`, and the epilog at `steps.py:3754-3757` to the rule that results, and `skills/handoff-format/SKILL.md:19`. Run `codex_roles.py generate` if a preloaded skill body changes.
