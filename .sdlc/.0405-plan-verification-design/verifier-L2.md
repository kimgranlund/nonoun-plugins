## Verdict
pass

## Criteria
- 1. plan-verification.md exists, status line, no em or en dash: pass. Evidence: `grep -nP '\x{2014}|\x{2013}' docs/specs/sdlc-lite/plan-verification.md` printed nothing, exit=1. The check bites: the same grep on a planted file `/tmp/nc-dash.md` holding a U+2014 printed `1:a — b`, exit=0. A byte-level count (`grep -c $'\xe2\x80\x94\|\xe2\x80\x93'`) gives 0 for the new doc and the three edited index files. Status line at docs/specs/sdlc-lite/plan-verification.md:3 reads "Design for review, not implemented. Version 0.1, 2026-10-09, ticket T-0405." It sits right after the title, the same layout as gate-lock-admission.md:3.
- 2. Covers Intent items 1 to 6: pass. Evidence, by file:line in docs/specs/sdlc-lite/plan-verification.md:
  - (1) The outcome block table at 17-22 has four parts: Outcome with `Why:`, Measured by with a K id or command plus `before:` and `target:`, a Rubric of 3 to 5 criteria with `pass:` thresholds, and one Negative control. The example is at 26-34 and the procedure at 36-45.
  - (2) "Does not own" table at 49-57 covers the planner, the verifier and the handoff Intent.
  - (3) How plan-goal calls it at 61-63, with the plan_check rules at 65-74.
  - (4) plan-loop, plan-fanout and ticket decisions at 78-82.
  - (5) Shared reference path `plugins/sdlc-lite/skills/plan-verification/references/outcome-block.md` at 88.
  - (6) Build ticket and its 5 checks at 109-115, migration note at 117.
  I checked the doc's factual claims against source:
  - plan-goal has steps `## 1. Gather` to `## 4. Return` and five sections (plan-goal/SKILL.md:14-26, :20).
  - `CHECKABLE` accepts `merged|closed` (plan_check.py:18) and `done-uncheckable` says "a merged ticket" (:81). The 5000 cap is at plan_check.py:84.
  - check.py item 31 exists (:128) and item 42 allows `${CLAUDE_PLUGIN_ROOT}` (:1110). The highest existing item is 47 (:185), so "new item 48" is correct.
  - docs_check G-1 to G-5 and G-4's `none:` escape are at docs_check.py:393, :437.
  - `fleet_collect.py collect <repo> --since` matches fleet_collect.py:4. K-001 exists with a `<= 5` target.
  - fleet-retro rubric.md:29 carries `outcome metric: ..., before:`.
  - docs/reports/plan-skills-live-run.md exists.
- 3. Files the build changes (section 7), the two fail rules with negative controls, rejected alternatives: pass. Evidence:
  - Section 7 table at 92-105 names 10 build files plus a "Not changed" line.
  - `git grep -ln 'plan-goal'` outside closed tickets and reports finds only plan-goal/SKILL.md, sdlc-lite/SKILL.md, check.py, docs/README.md, specs/sdlc-lite/README.md and goals-and-kpi.md. The first five are in the table. The goals-and-kpi.md:92 line ("blocks may cite a goal id") stays true after the build, so the list is complete.
  - Rules `outcome-block` (69, 7 mutants) and `done-measured` (70, 2 mutants) each carry negative controls.
  - Ran the claimed "passes today" mutant: `check_goal(GOOD_GOAL.replace('Done when: tickets.py check exits 0 and T-0001','Done when: T-0001'))` returned `([], [])`. That confirms the gap the `done-measured` control targets.
  - Rejected alternatives at 121 (extend plan-goal only) and 122 (tickets only), plus two more at 123-124.
- 4. docs_check.py and check.py exit 0: pass. Evidence: `python3 plugins/sdlc-lite/scripts/docs_check.py --root .` gave "docs_check: 0 errors, 16 warnings", exit=0. None of the warnings names a changed file; the D-10 link check reports no unresolved link in plan-verification.md. `python3 plugins/sdlc-lite/scripts/check.py` gave exit=0, "ok: 19 role levels, 9 agents, 22 generated definitions checked".
- 5. Listed in the three indexes; no plugin change: pass. Evidence:
  - grep finds the new doc at docs/README.md:30, docs/specs/sdlc-lite/README.md:15 and inside the managed block at docs/specs/sdlc-lite/AGENTS.md:14.
  - `python3 plugins/sdlc-lite/scripts/onboard.py check` reports `current docs/specs/sdlc-lite/AGENTS.md`, so the block hash e91d63de5f65 matches a regenerated block.
  - Negative control: in a git-archive copy at /tmp/0405nc2.6YSH with the diff applied and the plan-verification line removed from the block, onboard check reported `edited docs/specs/sdlc-lite/AGENTS.md: the managed block was edited by hand`. docs_check stayed at 0 errors in that control, so docs_check alone does not prove the listing. The grep and onboard check above carry this criterion.
  - `git diff --stat bc2d1377 -- plugins` is empty, and `git status --short -- plugins` is empty.

## Out of scope changes
None.
- `.sdlc/0405-plan-verification-design/handoff.md` gained an `## Acceptance criteria` section. Its sha256 cf6c1d69... equals the `handoff_sha256` in verifier-L2.dispatch.json, so these are the frozen criteria this verification was dispatched on. They restate the Intent's Done when, so this is ticket scope.
- `base-sha`, `verifier-L2.attempt.json` and `verifier-L2.dispatch.json` are run records.
- `git diff --check bc2d1377` exit=0.
- Steelman of the one concern I considered: section 4 line 74 says `kpi-unresolved` reads the repository root "from `--root`, as `check_fanout` already does", but plan_check.py:443 defaults `--root` to `.sdlc`, the record folder, not the repo root. Builder's likely rebuttal: the repo root is the parent of `--root`, so this is build detail and no criterion covers it. I accept that and file it as a note for the build ticket, not a fail.

## For the next attempt
None.
