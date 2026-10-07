# Fleet retro 2026-10-07

Repos: agent-ui (87 deduped, $363.13, 2 interrupted, 0 limit markers; interview: replied, `agent-ui/.sdlc/fleet-retro-2026-10-07.md`), gen-ui-kit (0 deduped, $0.00, 0 interrupted, 0 limit markers; interview: replied via the rootcause worktree, `.git-worktrees/rootcause/.sdlc/fleet-retro-2026-10-07.md`), sdlc-lite (142 deduped, $577.06, 0 interrupted, 2 limit markers; interview: none, this repo), ui-kit-maison (115 deduped, $639.24, 1 interrupted, 0 limit markers; interview: replied), ultimate-tokens (31 deduped, $62.05, 1 interrupted, 0 limit markers; interview: replied). Plugin: 0.21.0 at `/Users/kimgranlund/Projects/nonoun/sdlc-lite/plugins/sdlc-lite` (installed cache copy 0.21.0), Claude Code 2.1.292. Window: since 2026-10-06, until open.

Fingerprints and `findings.jsonl` live in `.sdlc/fleet-retro-2026-10-07/` (W). The conductors quoted larger windows (`--days 4`, `--since 2026-10-05`), so their totals differ from the fingerprints; every number below is the fingerprint's. fleet_detect printed only `chromium_load` findings (10 lines, one machine); no other rule crossed its threshold (`plan_review_share` is under 0.40 in all five repos, `stall_attempts` under 3).

## Cross-repo table
| Repo | Runs | Spend | Plan-review share | Interrupted + limit | Findings |
|---|---|---|---|---|---|
| agent-ui | 87 | $363.13 | 0.3374 | 2 + 0 | 2 |
| gen-ui-kit | 0 | $0.00 | none | 0 + 0 | 3 |
| sdlc-lite | 142 | $577.06 | 0.0774 | 0 + 2 | 0 (machine row 6 counts once) |
| ui-kit-maison | 115 | $639.24 | 0.2899 | 1 + 0 | 3 |
| ultimate-tokens | 31 | $62.05 | 0.3574 | 1 + 0 | 3 |

Findings counts exclude the machine row.

## Findings
| # | Repo | Symptom | Evidence | Mechanism | Cost | [V] or [U] | Check | Prevention |
|---|---|---|---|---|---|---|---|---|
| 1 | ui-kit-maison | Verifier runs are the largest spend: 38 of 115 runs (conductor: 44 percent over 4 days, T-0105 with 39 verifier runs) | `.sdlc/fleet-retro-2026-10-07/ui-kit-maison.json :: runs.by_role.verifier.cost_usd` | One verifier per step plus reruns, level follows the build level (`plugins/sdlc-lite/skills/level-rubric/SKILL.md`, verifier follow rule); the per-ticket repeat is not diagnosed to a rule | $230.01 of $639.24 (36 percent) | [V] | not actionable: score 5 of 10 (C2 0) | Cap verifier reruns per ticket in `steps.py` next-action and show it on /board; check: `runs.by_ticket` verifier count per ticket over 5 goes red |
| 2 | ui-kit-maison | Planner plus plan-reviewer take 29 percent of spend; conductor names T-0105 with 20 planner and 20 plan-reviewer runs on a heading mismatch loop | `.sdlc/fleet-retro-2026-10-07/ui-kit-maison.json :: runs.by_role.planner.cost_usd + runs.by_role["plan-reviewer"].cost_usd` | Plan review on every plan and replan loops; `plugins/sdlc-lite/skills/level-rubric/SKILL.md` plan-reviewer rule was L1-L3 wide until T-0294 (48e25a3a, 2026-10-06) | $185.32 of $639.24 (29 percent) | [V] | not actionable: G2 (T-0294 48e25a3a and T-0295 9456b377 landed 2026-10-06) | `plan_review_share` stays under 0.40 on the next collect; T-0315 re-measures |
| 3 | agent-ui | Planning and plan review are 34 percent of spend (conductor: 47 percent over `--since 2026-10-05`) | `.sdlc/fleet-retro-2026-10-07/agent-ui.json :: runs.by_role.planner.cost_usd + runs.by_role["plan-reviewer"].cost_usd` | Same plan-reviewer rule as row 2 (T-0294); a2ui-test-kit alone ran 3 planner and 2 plan-reviewer runs | $122.52 of $363.13 (34 percent) | [V] | not actionable: G2 (T-0294) | `plan_review_share` under 0.40 on the next collect |
| 4 | ultimate-tokens | Planner ran 3 times on docs-reconcile (plan, then two replans) | `.sdlc/fleet-retro-2026-10-07/ultimate-tokens.json :: runs.by_role.planner.cost_usd`; `/Users/kimgranlund/Projects/nonoun/ultimate-tokens/.sdlc/docs-reconcile/step-1.superseded-1` | Plan-written guards contradicted real git behavior (`A` versus `R100`, rename similarity 33 percent); the guards were written before `plugins/sdlc-lite/agents/planner.md:27` told the planner to dry-run each guard (T-0297, 2026-10-06 07:25); which plugin version the planner ran on is not recorded in the row | $22.17 and 4013 s of planner time, plus 2 wasted builder runs | [V] | not actionable: G2 (planner.md:27 now dry-runs guards, T-0297 3a75c8b3) | Planner dry-runs each guard on a temp copy; selftest: a plan whose guard fails its own dry run is refused by `plan_check.py` |
| 5 | gen-ui-kit | GitHub Actions: 77 runs and 258 wall minutes in one day (conductor: 792 CI minutes since Oct 1, billed past a cap) | `.sdlc/fleet-retro-2026-10-07/gen-ui-kit.json :: ci.wall_minutes` | Project workflow design (every push and PR ran the 5-job train); `ci_push_duplicates` is silent (`push_dup_7d` 0), so the plugin side is not shown | 258.2 min | [V] | not actionable: G4 (project workflow) | none for the plugin; `ci_push_duplicates` already covers duplicate push runs |
| 6 | machine (all repos) | 42 Chromium processes at 19.4 GB RSS, over the 30 and 6 GB thresholds, in every fingerprint | `.sdlc/fleet-retro-2026-10-07/sdlc-lite.json :: processes.chromium.count`; `.sdlc/fleet-retro-2026-10-07/findings.jsonl` (`chromium_load`) | Parallel browser gates from many sessions; the plugin half is the gate semaphore (`plugins/sdlc-lite/scripts/gate_lock.py`, T-0292, T-0303); orphan reaping was added to `gate_lock.py` by T-0304 (c24032c2) | unmeasured (19402.9 MB, 42 processes) | [V] | not actionable: G4 (project browser shards; T-0292, T-0304 own the plugin half) | `fleet_detect.py` `chromium_load` goes silent on a fresh collect after orphans are reaped |
| 7 | ui-kit-maison | Hash-bound single-writer chain: each merge round regenerates sha256-bound artifacts and reruns a full check (conductor: 1 to 2 h per round, 6 rounds) | `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/overnight-logs/full-check-candidate-3.log` | The generated files and lock are bound by the project's `generate:all`; fanout serializes them at merge (`plugins/sdlc-lite/scripts/fanout.py` merge step) | unmeasured (41:34 stated by the conductor, not in the log) | [V] | not actionable: G3 (cost not in the log); G4 (project generate:all) | One integration ticket per batch; `plan_check.py` flags generated-file overlap before a fanout launch |
| 8 | gen-ui-kit | Integration PRs red on bundle budgets, typography tokens, traits and goldens after lane merges: 2 extra pushes on #380, 1 on #383 | `gh pr checks 380 --repo adia/ui-kit`; `gh pr checks 383 --repo adia/ui-kit` | `plugins/sdlc-lite/scripts/fanout.py` gates each lane, then merges; no post-merge budget gate on the integration branch | unmeasured (about 3 x 25 min, conductor estimate) | [V] | not actionable: G3 (estimate) | `fanout.py` runs the integration gate list after the last lane merge; selftest with a lane pair that only fails combined |
| 9 | ultimate-tokens | Two fanout lanes went red on the repo gate because the lane commit included `verifier-L3.log` and `.run.lock` | `plugins/sdlc-lite/scripts/fanout.py:1139` (`git add -A`; the step is described at `fanout.py:157`); `.sdlc/0339-fanout-lane-stages-logs/handoff.md` | The lane commit stages everything, including run artifacts | unmeasured (about 15 min, conductor estimate) | [V] | not actionable: G3 (estimate); already ticketed T-0339 | Already ticketed T-0339: a selftest with a planted log and lock file in the lane tree |
| 10 | agent-ui | Two verifier L3 attempts interrupted (devtools-meta-replay, sub-tag-aliases); conductor saw exit 137 on T-0018, under a browser-heavy gate | `.sdlc/fleet-retro-2026-10-07/agent-ui.json :: runs.interrupted.count` | Session ended while the role was alive; memory link from a heavy gate is unchecked (the T-0018 log tail is not at a named path) | unmeasured (2 attempts) | [U] | not actionable: G4 (no plugin file named) | `stall_attempts` stays under 3 on the next collect; gate lock (`gate_lock.py`) already shipped |
| 11 | gen-ui-kit | The collector sees 0 runs and 0 ticket rows: lanes are headless `claude -p` in worktrees with no `.sdlc` task dir, so /board and the fleet view are blind | `.sdlc/fleet-retro-2026-10-07/gen-ui-kit.json :: runs.total` | `plugins/sdlc-lite/scripts/fleet_collect.py` reads only `.sdlc` task folders; the plugin never sees a lane that skips them | unmeasured (0 of an unknown run count) | [V] | not actionable: score 4 of 10 | `fleet_collect.py` flags a repo with commits in the window and 0 runs as `no trace`; selftest fixture |
| 12 | ultimate-tokens | A stale `scout-L1.attempt.json` left by a spawn the hook denied blocked the next `dispatch.py prepare` until `run_lifecycle.py recover` ran by hand | `.sdlc/fleet-retro-2026-10-07/ultimate-tokens.json :: runs.interrupted.attempts[0].path` | `plugins/sdlc-lite/scripts/dispatch.py` `recover_orphans` recovers only attempts whose parent pid is dead; this attempt was left by a denied spawn (T-0340 names the exact gap) | unmeasured (about 10 min, conductor estimate) | [V] | not actionable: G3 (estimate); already ticketed T-0340 | Already ticketed T-0340: a selftest with a planted dead attempt |

Dropped before this table: agent-ui "full lane costs 3x solo per run" (the fingerprint has full $164.82 over 56 runs and solo $198.30 over 31, so per run the solo lane costs more; the conductor's $710.87 and $220.71 are a different window, and `.sdlc/fleet-retro-2026-10-07/agent-ui.json :: runs.by_lane` does not support the claim); ultimate-tokens "verifier cannot finish 14 min sweeps" (its only pointers, `.sdlc/gh-784/verifier-L3.md` and the fanout lane logs, no longer exist on disk).

## Verification

One verifier run (L1, `.sdlc/fleet-retro-2026-10-07/verify/verifier-L1.md`, handoff `.sdlc/fleet-retro-2026-10-07/verify/handoff.md`). Sampled [V] rows 1, 6, 11 reproduced from the fingerprints. The planted control (a verifier cost of 999.99 against the real 230.0145) exited 1 and the verifier reported it rejected. `dispatch.py record` refused the result because it carries a `Verdict: fail` line instead of a `## Verdict` heading; the `## Criteria` table was read directly, and no rerun was made because the verdict is present. The control is not in the table above. No row was downgraded. Rows 7 and 12 carry rule-text checks the verifier did not sample (`not sampled`).

## Not actionable

Every row failed the rubric, so none is filed. The fixes for rows 2, 3 and 4 landed on 2026-10-06, inside a window that starts the same day, so those rows mix runs from before and after the fix; the next retro should start its window after the fix commit and read the outcome metric.

| # | Why |
|---|---|
| 1 | score 5 of 10: one repo, per-ticket repeat not diagnosed to a rule |
| 2, 3 | G2: T-0294 and T-0295 landed first |
| 4 | G2: planner.md:27 (T-0297) now dry-runs guards |
| 5 | G4: project CI workflow design |
| 6 | G4: project browser shards; T-0292, T-0303, T-0304 own the plugin half |
| 7 | G3: the 41:34 figure is not in the log; G4: project `generate:all` |
| 8 | G3: estimate |
| 9, 12 | G3: estimate; both already ticketed (T-0339, T-0340) |
| 10 | G4: no plugin file named |
| 11 | score 4 of 10: unmeasured, one repo |

## Drafts (not filed: unattended)

Nothing passed the rubric, so no draft is eligible. Closest candidates, with the sdlc-lite file each names, for the user to judge:

1. Verifier reruns per ticket (row 1, `plugins/sdlc-lite/scripts/steps.py`): needs diagnosis of why maison tickets repeat verifier runs; `/review-traces ui-kit-maison` is the next step. Outcome metric: `runs.by_ticket` verifier count per ticket.
2. Collector blind to headless lanes (row 11, `plugins/sdlc-lite/scripts/fleet_collect.py`): flag a repo with commits in the window and 0 runs. Outcome metric: `runs.total` of gen-ui-kit after its lanes move to ticketed sub-agents.
3. Post-merge gates on the integration branch (row 8, `plugins/sdlc-lite/scripts/fanout.py`): run the budget gates after the last lane merge. Outcome metric: extra fix pushes per integration PR (needs a measured baseline first).
