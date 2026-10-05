## Task goal
Planner L3, which plans cross-cutting work and every replan, runs on Opus xhigh instead of Fable xhigh, and every rule that depended on the old family follows.

## Step 1: Planner L3 on Opus xhigh
level: L2

### Do
Decision, user, 2026-09-30, to fit the Claude table to the Max plan. Claude only; the Codex planner L3 (`gpt-6-astra` high) does not change. Basis: of 912 recorded role runs, Fable was 44 (5%) and about $164 of $537 (31%) of recorded cost, and planner L3 was the largest item (18 runs, about $103). Quality of Opus xhigh plans against Fable plans has not been measured.

1. In `plugins/sdlc-lite/scripts/run.sh`, change the `planner:L3)` row to `model=opus;  effort=xhigh ;;`, keeping the row's layout. Change no other row and leave the plan-reviewer family logic as it is: it already moves the review to Fable high after an Opus planner.
2. In `plugins/sdlc-lite/skills/level-rubric/SKILL.md`, change the planner table's L3 row model from `Fable xhigh` to `Opus xhigh`, keeping its text. In the plan-reviewer paragraph that says the reviewer never runs on the planner's family, add: "With planner L2 and L3 both on Opus, a review of a plan by planner L2 or L3 runs on Fable high; only a plan by the Sonnet planner L1 is reviewed on Opus high." Fix any other sentence in this file that says planner L3 runs on Fable.
3. Search `plugins/`, `docs/` (not `docs/reports/` dated records) and the skills and agents for any other statement that planner L3 or a replan runs on Fable, and correct each one. Report what you searched.
4. In `plugins/sdlc-lite/scripts/run-selftest.sh`, keep the existing family-rule cases (they use a synthetic planner header and stay valid) and add two dry-run assertions: `run.sh planner L3` prints `--model opus --effort xhigh`, and a plan-reviewer dry run after a newest planner result whose header reads `model=opus effort=xhigh` at level L3 prints `--model fable --effort high`.
5. Run `python3 plugins/sdlc-lite/scripts/codex_roles.py generate`, because the level rubric is preloaded into the planner profiles.
6. Add `docs/reports/planner-l3-opus-2026-09-30.md`, a dated note with: the decision and date, the recorded-cost figures above and their basis (`runs.jsonl` across this repository's `.sdlc/` folders, list-price cost, bench runs and lane worktrees excluded), the consequence that reviews of planner L2 and L3 plans now run on Fable high so some Fable spend moves from planner to reviewer, and the limit "the quality of Opus xhigh plans against Fable plans is not measured". Link it from `docs/README.md` next to the neighbouring entries.

### Acceptance criteria
- `grep -qE '^\s+planner:L3\)\s+model=opus; +effort=xhigh' plugins/sdlc-lite/scripts/run.sh`
- `grep -qE '^\| L3 \| Opus xhigh \| Cross-cutting or risky' plugins/sdlc-lite/skills/level-rubric/SKILL.md`
- `r="$PWD"; d=$(mktemp -d) && mkdir "$d/t" && printf '## Goal\nx\n' > "$d/t/handoff.md" && cd "$d" && git init -q && git -c user.email=a@b.c -c user.name=a commit -q --allow-empty -m i && SDLC_DRY_RUN=1 bash "$r/plugins/sdlc-lite/scripts/run.sh" planner L3 t/handoff.md | grep -qF -- "--model opus --effort xhigh"`
- `r="$PWD"; d=$(mktemp -d) && mkdir "$d/t" && printf '## Goal\nx\n' > "$d/t/handoff.md" && printf '<!-- role=planner level=L3 model=opus effort=xhigh -->\n## Goal\nx\n' > "$d/t/planner-L3.md" && cd "$d" && git init -q && git -c user.email=a@b.c -c user.name=a commit -q --allow-empty -m i && SDLC_DRY_RUN=1 bash "$r/plugins/sdlc-lite/scripts/run.sh" plan-reviewer L1 t/handoff.md | grep -qF -- "--model fable --effort high"`
- `grep -qF "not measured" docs/reports/planner-l3-opus-2026-09-30.md`
- `grep -qF "planner-l3-opus-2026-09-30.md" docs/README.md`
- (guard) `python3 plugins/sdlc-lite/scripts/check.py`
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
