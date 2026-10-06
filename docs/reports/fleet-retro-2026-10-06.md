# Fleet retro 2026-10-06

Repos: agent-ui (193 deduped runs, $786.95, 2 interrupted, 0 limit markers; window up to 2026-10-06T14:06:53Z, the cutoff of its own report); ui-kit-maison (1230 deduped runs, $1048.90 metered, 944 runs with no cost, 16 interrupted, 0 limit markers; no cutoff). Interview: skipped, no person present (`SDLC_HEADLESS=1`); each repo's `.sdlc/root-cause-2026-10-06.md` stands in for the reply and is cited as evidence with its own [V] and [U] marks. gen-ui-kit is not in this run. Plugin: 0.20.11 at `plugins/sdlc-lite` of this worktree, `claude` from the fingerprints, collected 2026-10-06T21:07Z. Work folder: `.sdlc/fleet-retro-2026-10-06/` (`<name>.json` fingerprints, `findings.jsonl`, `verify/`). A fingerprint path below reads `<file> :: <key path>` inside that folder.

## Cross-repo table

| Repo | Runs | Spend | Plan-review share | Interrupted + limit | Findings |
|---|---|---|---|---|---|
| agent-ui | 193 (13 solo, 180 full) | $786.95 | 55.5 percent, over the 40 percent line | 2 + 0 | 1, 3, 4, 5 |
| ui-kit-maison | 1230 (215 solo, 1015 full) | $1048.90 (metered runs only) | 29.0 percent | 16 + 0 | 2, 3, 4 |

## Findings

| # | Repo | Symptom | Evidence | Mechanism | Cost | [V] or [U] | Check | Prevention |
|---|---|---|---|---|---|---|---|---|
| 1 | agent-ui | Planning plus plan review is 55.5 percent of spend: planner 37 runs $250.0 and plan-reviewer 25 runs $186.5 of $786.95 | `agent-ui.json :: plan_review_share` (0.5546; detail planner 249.96, plan-reviewer 186.48, total 786.95); `~/Projects/nonoun/agent-ui/.sdlc/root-cause-2026-10-06.md` section 4 | Plan review repeated "builder readiness" findings on L-size plans that a builder resolves by reading code (the agent-ui report) | $436.44 | [V] | sampled, reproduced; not actionable: G2 (T-0294) | Review only L4 and L5 plans; turn readiness findings into builder notes |
| 2 | ui-kit-maison | Five tickets with more than 5 planner results: 0105-structured-component-contracts 20, first-wave-components 11, 0012-seventh-wave-release-readiness 8, 0106-gen-ui-evaluation-lab 7, .0037-domain-shared-presentation 6 | `ui-kit-maison.json :: runs.by_ticket["tickets/0105-structured-component-contracts"].planner` (20) and the four sibling keys of `findings.jsonl`; `~/Projects/maison/ui-kit-maison/.sdlc/root-cause-2026-10-06.md` section 3, "Plan-review loop" | For 0105: the split was refused for `## Task goal` against `## Goal`, about 2 hours (maison report). The other four are not diagnosed | unmeasured (the 2 hours is the maison report's own figure) | [V] | not sampled; not actionable: G2 (T-0295) | `steps.py lint` naming the exact heading (maison report) |
| 3 | ui-kit-maison | 16 attempts interrupted, 0 limit markers | `ui-kit-maison.json :: runs.interrupted.count + runs.limit_markers.count` (16); maison report section 3, "Killed by session exit" and "Session or usage limit" | The maison report names 3 planner runs killed with their parent shell and 6 Wave D lanes lost to a session limit; the other interrupted attempts are not diagnosed | unmeasured | [V] | not sampled; not actionable: G4 (session and host causes) | Keep roles alive past the session; a pre-launch limit probe (maison report) |
| 4 | agent-ui, ui-kit-maison (one machine) | Chromium over the threshold: 59 processes and 14259 MB in the agent-ui snapshot, 57 and 14193 MB in the maison snapshot | `agent-ui.json :: processes.chromium.count` (59) and `:: processes.chromium.rss_mb` (14258.8); `ui-kit-maison.json :: processes.chromium.count` (57); maison report section 1 ("53 Chromium processes holding about 10 GB") | Browser shards of several lanes' Playwright runs, which are the projects' tests (maison report) | unmeasured | [V] | not sampled; not actionable: G4 (project shards; plugin half is T-0292) | A machine-wide cap on concurrent heavy gates (T-0292) |
| 5 | agent-ui | The no-barrels ticket has 6 planner results; the agent-ui report says 12 | `agent-ui.json :: runs.by_ticket["no-barrels"].planner` (6); agent-ui report section 3, "12 planner results and 5 plan reviews for no-barrels" | The agent-ui report names four causes (specgate duplicate criteria, scope allow-lists, `split --only` on a red guard, a step written before the ADR) | unmeasured | [V] | not sampled; not actionable: G2 (T-0297) | Generate criteria and allow-lists; have the planner dry-run its guards (agent-ui report) |
| 6 | agent-ui | `block-pattern-kill.sh`, `block-stray-worktree.sh`, `block-disk-scan.sh` each at about 100 percent CPU for 30+ s on a long heredoc Bash call | agent-ui report section 1, "Runaway hooks"; `docs/reports/hook-perf.md` timings table; `agent-ui.json :: processes.hooks.count` (0 now) | A bracket substitution and a `tr` fallback quadratic in the command length, in four hooks; T-0291 replaced them | 3 cores per Bash call; 8.8 s at 4 KB (`docs/reports/hook-perf.md`) | [V] | sampled, reproduced; not actionable: G2 (T-0291), outcome check `moved` | `hook-selftest.sh` runs a 20 KB heredoc under 2 s; the outcome check is `hook_cpu` going silent |

## Verification

Verifier: `run.sh verifier L1` on `.sdlc/fleet-retro-2026-10-06/verify/handoff.md` (lint ok); result `.sdlc/fleet-retro-2026-10-06/verify/verifier-L1.md`, which `results.py validate` accepts. The verifier made one run for the whole report.

- Sample: 6 [V] rows, so rows 1 and 6 (ceil of 6/5 is 2, ranks 1 and 6). Row 1: `plan_review_share` 0.5546 and planner plus plan-reviewer $436.44 reproduce. Row 6: the `block-disk-scan.sh` timing row is in `docs/reports/hook-perf.md` line 18. Neither was downgraded.
- Control: the planted [V] claim "agent-ui has 250 deduped runs", pointing at `agent-ui.json :: runs.total`, is not in the table. In the batched run its criterion exited 1 on the fingerprint's 193, but the verifier wrote `pass` and explained it meant "claim rejected", because the criterion was not phrased as a claim that holds. The skill now words it `The planted claim holds: ...`. Rerun alone with that wording (`.sdlc/fleet-retro-2026-10-06/control/verifier-L1.md`): verdict `fail`, evidence 193, "the claim is false", so the claim is downgraded to [U] and the check is not vacuous.
- Rubric, all 6 rows: 0 of 6 actionable (every one scores 0 at a gate). Rows 1, 2, 5 and 6 fail G2: T-0294 (L4 and L5 plan review only), T-0295 (`steps.py lint` hint), T-0297 (planner guard dry-run, `split` inherits widenings) and T-0291 (linear hooks) all landed in v0.20.11 after the evidence. Rows 3 and 4 fail G4: the causes are a parent-shell kill and a usage limit, and the projects' Playwright shards.
- Rubric fixtures (`plugins/sdlc-lite/skills/fleet-retro/fixtures.md`, graded as of 24ef333 by the independent batched verifier, `.sdlc/0308-fleet-retro-skill/verifier-L3-2.md`, before it read the Calibration table): F1 passes G1 to G5 and scores 7 or 8 of 10 (above the threshold); F2 fails G2, the stale-version misattribution (T-0258 in v0.20.9 fixed what maison saw on 0.20.7), score 0; F3 passes G1 and G2 and fails G3, the unmeasured ceiling guess, score 0. An earlier run of the same verifier (`verifier-L3.md`) failed F1 at G2 because the rubric did not say how a pinned fixture is graded; the as-of rule in G2 and the fixtures header fixed that.
- Observed: the agent-ui run total at the report's cutoff is 193, as its own report says; without `--until` the collector prints more runs because the repo keeps working.

## Not actionable

Rows 1 to 6, none filed, with the reasons in the Check column. Row 1 is the plan-review share the detect rule flags (55.5 percent against the 40 percent line); T-0294 changed the rule that produced it, and T-0315 owns the re-measure.

The re-measure, run here for the outcome check: `--since 2026-10-06T14:30:00Z` after 0.20.11, fingerprints `*.post-fix.json`, `findings.post-fix.jsonl`.

| Repo | Runs since | Spend | Plan-review share | Interrupted | Planner findings | Hooks over limit |
|---|---|---|---|---|---|---|
| agent-ui | 19 | $90.21 | 0.0 percent (was 55.5) | 2 | none | none |
| ui-kit-maison | 17 | $92.19 | 10.2 percent (was 29.0) | 1 | none | none |

Chromium stays over the threshold in both snapshots (57 to 58 processes, 14.5 GB: `*.post-fix.json :: processes.chromium`); it is machine state and the project's shards, so it did not move. The interrupted attempts in the new window (2 and 1) are not diagnosed; the stall rule's threshold is 3, so it stays silent. No finding survives for filing.

## Open

- Interview: not run. A person must be present for SendMessage replies; a conductor reply could add rows this run could not see.
- gen-ui-kit was not collected.
- 944 maison runs record no cost, so its spend is a lower bound.
