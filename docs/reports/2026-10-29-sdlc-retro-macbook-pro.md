# SDLC retro macbook-pro 2026-10-29

Host: MacBook-Pro.local, 18 cores, 64 GB RAM. Claude Code 2.1.312. Plugin: sdlc-lite 0.40.0 at /Users/kimba/.claude/plugins/cache/sdlc-lite/sdlc-lite/0.40.0 (active install per installed_plugins.json, lastUpdated 2026-10-29T02:24:14Z; 0.39.0 was active before that); other plugins: github f8c5e7a1dcb7 (its MCP server failed to connect in this session). Note: the conductor's land, sync and settle helpers ran sdlc-lite 0.37.0 scripts all night (see Findings 1).
Window: 2026-10-29T01:00:00Z (2026-10-28 18:00 PDT) to 2026-10-29T17:25Z (10:25 PDT). Repos: ultimate-tokens-color-science: `runs: 97 deduped, $150.35, 0 interrupted, 0 limit markers`, interview reply.

## Summary
- 52 tickets closed on main in the window (T-0231..T-0287 range, minus T-0286 still in flight and T-0111 parked) [V: ultimate-tokens-color-science-closes.txt].
- Spend $150.35 across 97 runs by the collector; $154.29 by summing the run records directly (difference is T-0286's solo, $3.95, which the collector counted as unmetered) [V]. Every cost is estimated from usage x rates; no run record has a duration [V].
- Minutes lost: 273 min with no work in progress, 07:32Z to 12:05Z, after the backlog ran dry at 00:32 PDT. Filing more tickets needed the person, so nothing ran until they returned [V: conductor-transcript-gaps.txt, conductor-asks.txt]. Other losses add up to about 150 min, mostly overlapping with lanes that were still running (see Interruptions).
- Biggest problem: the run had no work queued for the night. The second biggest is that the conductor's helper scripts pinned sdlc-lite 0.37.0 for land, sync, settle and close, so the 0.40.0 close fix (T-0797) never ran. skips.md was dropped at close and had to be restored by hand 6 times [V].

## Repos
| Repo | Tickets closed | Tickets open | Runs | Spend $ | Wall h | Interrupted | Limit hits | Lanes (solo/lean/full/fix) | Findings |
|---|---|---|---|---|---|---|---|---|---|
| ultimate-tokens-color-science | 52 | 2 (T-0111 parked, T-0286 in verification) | 97 | 150.35 | 16.4 window, about 11.7 with work running | 0 | 0 | 49/0/2/0 | 2 detector + 15 retro |

## Tickets
| Repo | Ticket | Level | Lane | Roles run (role:level x count) | Attempts | Verifier verdicts | Spend $ | Wall min | Closed? | Note |
|---|---|---|---|---|---|---|---|---|---|---|
| ultimate-tokens-color-science | T-0232 | L3 | full | builder:L4 x2, verifier:L3 x1 | 3 | pass | 11.52 | 23.9 | yes 18:34 PDT | chain tail from before window; builder L4 retry |
| ultimate-tokens-color-science | T-0235 | L2 | solo | solo:L2 x1, verifier:L2 x1 | 2 | pass | 3.66 | 32.6 | yes 18:52 PDT | - |
| ultimate-tokens-color-science | T-0236 | L2 | solo | solo:L2 x1, verifier:L2 x1 | 2 | pass | 5.03 | 45.6 | yes 18:59 PDT | - |
| ultimate-tokens-color-science | T-0239 | L2 | solo | verifier:L2 x1 | 1 | pass | 0.45 | 3.4 | yes 18:20 PDT | solo ran before window |
| ultimate-tokens-color-science | T-0240 | L2 | solo | solo:L2 x1, verifier:L2 x1 | 2 | pass | 1.45 | 26.2 | yes 19:07 PDT | - |
| ultimate-tokens-color-science | T-0241 | L2 | solo | solo:L2 x1, verifier:L2 x1 | 2 | pass | 1.26 | 16.5 | yes 19:20 PDT | - |
| ultimate-tokens-color-science | T-0242 | L2 | solo | solo:L2 x1, verifier:L2 x2 | 3 | pass/pass | 1.80 | 31.9 | yes 19:30 PDT | land conflict with T-0236, re-solo + 2nd verifier |
| ultimate-tokens-color-science | T-0244 | L2 | solo | verifier:L2 x1 | 1 | pass | 0.27 | 2.5 | yes 18:26 PDT | solo ran before window |
| ultimate-tokens-color-science | T-0245 | L2 | solo | solo:L2 x1, verifier:L2 x1 | 2 | pass | 2.29 | 35.9 | yes 19:14 PDT | - |
| ultimate-tokens-color-science | T-0246 | L2 | solo | solo:L2 x1, verifier:L2 x1 | 2 | pass | 1.44 | 12.0 | yes 18:45 PDT | - |
| ultimate-tokens-color-science | T-0247 | L2 | solo | solo:L2 x1, verifier:L2 x1 | 2 | pass | 2.57 | 45.7 | yes 20:47 PDT | - |
| ultimate-tokens-color-science | T-0248 | L2 | solo | solo:L2 x1, verifier:L2 x2 | 3 | pass/pass | 4.14 | 79.1 | yes 21:14 PDT | diff verifier passed; land gate caught dashboard regression; 2nd verifier |
| ultimate-tokens-color-science | T-0249 | L2 | solo | solo:L2 x1, verifier:L2 x1 | 2 | pass | 1.51 | 11.6 | yes 19:55 PDT | - |
| ultimate-tokens-color-science | T-0250 | L2 | solo | solo:L2 x1, verifier:L2 x1 | 2 | pass | 1.80 | 21.1 | yes 20:10 PDT | - |
| ultimate-tokens-color-science | T-0251 | L2 | solo | solo:L2 x1, verifier:L2 x1 | 2 | pass | 3.32 | 33.4 | yes 20:23 PDT | - |
| ultimate-tokens-color-science | T-0252 | L2 | solo | solo:L2 x1, verifier:L2 x1 | 2 | pass | 3.31 | 73.4 | yes 21:22 PDT | - |
| ultimate-tokens-color-science | T-0253 | L1 | solo | solo:L1 x1 | 1 | none (solo L1) | 0.94 | unmetered | yes 22:06 PDT | - |
| ultimate-tokens-color-science | T-0254 | L2 | solo | solo:L2 x1, verifier:L2 x1 | 2 | pass | 3.44 | 44.8 | yes 21:02 PDT | - |
| ultimate-tokens-color-science | T-0255 | L2 | solo | solo:L2 x1, verifier:L2 x1 | 2 | pass | 2.42 | 62.2 | yes 21:39 PDT | - |
| ultimate-tokens-color-science | T-0256 | L2 | solo | solo:L2 x1, verifier:L2 x1 | 2 | pass | 4.61 | 53.3 | yes 21:56 PDT | - |
| ultimate-tokens-color-science | T-0257 | L2 | solo | solo:L2 x1, verifier:L2 x1 | 2 | pass | 1.65 | 15.6 | yes 22:46 PDT | - |
| ultimate-tokens-color-science | T-0258 | L1 | solo | solo:L1 x1 | 1 | none (solo L1) | 0.65 | unmetered | yes 22:13 PDT | - |
| ultimate-tokens-color-science | T-0259 | L2 | solo | solo:L2 x1, verifier:L2 x1 | 2 | pass | 1.44 | 22.6 | yes 23:30 PDT | - |
| ultimate-tokens-color-science | T-0260 | L1 | solo | solo:L1 x1 | 1 | none (solo L1) | 0.66 | unmetered | yes 22:37 PDT | - |
| ultimate-tokens-color-science | T-0261 | L2 | solo | solo:L2 x1, verifier:L2 x1 | 2 | pass | 2.49 | 40.9 | yes 23:12 PDT | - |
| ultimate-tokens-color-science | T-0262 | L2 | solo | solo:L2 x1, verifier:L2 x1 | 2 | pass | 1.86 | 24.8 | yes 23:01 PDT | - |
| ultimate-tokens-color-science | T-0263 | L2 | solo | solo:L2 x1, verifier:L2 x1 | 2 | pass | 2.17 | 51.8 | yes 23:23 PDT | - |
| ultimate-tokens-color-science | T-0264 | L2 | solo | solo:L2 x1, verifier:L2 x1 | 2 | pass | 3.57 | 26.8 | yes 00:17 PDT | - |
| ultimate-tokens-color-science | T-0265 | L1 | solo | solo:L1 x1 | 1 | none (solo L1) | 0.71 | unmetered | yes 23:50 PDT | - |
| ultimate-tokens-color-science | T-0266 | L2 | solo | solo:L2 x1 | 1 | none (verifier prepared, never run; orphaned) | 1.46 | unmetered | yes 00:31 PDT | already fixed (sweep used axe 4.10.2); closed not reproducible; verifier attempt orphaned |
| ultimate-tokens-color-science | T-0267 | L2 | solo | solo:L2 x1, verifier:L2 x1 | 2 | pass | 2.70 | 25.0 | yes 00:10 PDT | - |
| ultimate-tokens-color-science | T-0268 | L2 | solo | solo:L2 x1, verifier:L2 x1 | 2 | pass | 3.49 | 33.2 | yes 00:23 PDT | - |
| ultimate-tokens-color-science | T-0269 | L1 | solo | solo:L1 x1 | 1 | none (solo L1) | 0.67 | unmetered | yes 23:57 PDT | - |
| ultimate-tokens-color-science | T-0270 | L2 | solo | solo:L2 x1, verifier:L2 x1 | 2 | pass | 2.57 | 76.0 | yes 06:30 PDT | verifier 42.3 min vs 25 budget |
| ultimate-tokens-color-science | T-0271 | L1 | solo | solo:L1 x1 | 1 | none (solo L1) | 0.59 | unmetered | yes 05:47 PDT | - |
| ultimate-tokens-color-science | T-0272 | L2 | solo | solo:L2 x1, verifier:L2 x1 | 2 | pass | 2.70 | 84.4 | yes 06:40 PDT | blocked at 375 px; waited 28.6 min on person |
| ultimate-tokens-color-science | T-0273 | L2 | solo | solo:L2 x1, verifier:L2 x1 | 2 | pass | 4.95 | 81.8 | yes 08:46 PDT | land red x2 (suite leak), helper mis-call x1 |
| ultimate-tokens-color-science | T-0274 | L1 | solo | solo:L1 x1 | 1 | none (solo L1) | 1.60 | unmetered | yes 07:01 PDT | - |
| ultimate-tokens-color-science | T-0275 | L2 then L3 | full | solo:L2 x1, planner:L3 x2, plan-reviewer:L1 x2, builder:L4 x2, verifier:L3 x1, builder:L3 x1, verifier:L2 x1 | 10 | pass/pass | 36.13 | 171.4 | yes 09:39 PDT | solo L2 blocked; person chose new manifest; full lane; builder plan defect; replan |
| ultimate-tokens-color-science | T-0276 | L1 | solo | solo:L1 x1 | 1 | none (solo L1) | 1.14 | unmetered | yes 07:39 PDT | - |
| ultimate-tokens-color-science | T-0277 | L1 | solo | solo:L1 x1 | 1 | none (solo L1) | 1.34 | unmetered | yes 07:49 PDT | - |
| ultimate-tokens-color-science | T-0278 | L1 | solo | solo:L1 x1 | 1 | none (solo L1) | 2.08 | unmetered | yes 08:19 PDT | - |
| ultimate-tokens-color-science | T-0279 | L1 | solo | solo:L1 x1 | 1 | none (solo L1) | 1.65 | unmetered | yes 08:54 PDT | helper mis-call x1 (no lane kind) |
| ultimate-tokens-color-science | T-0280 | L1 | solo | solo:L1 x1 | 1 | none (solo L1) | 1.71 | unmetered | yes 09:21 PDT | - |
| ultimate-tokens-color-science | T-0281 | L2 | solo | solo:L2 x1, verifier:L2 x1 | 2 | pass | 2.47 | 33.3 | yes 07:10 PDT | - |
| ultimate-tokens-color-science | T-0282 | L2 | solo | solo:L2 x1, verifier:L2 x1 | 2 | pass | 2.17 | 36.0 | yes 09:29 PDT | - |
| ultimate-tokens-color-science | T-0283 | L1 | solo | solo:L1 x1 | 1 | none (solo L1) | 1.08 | unmetered | yes 06:52 PDT | - |
| ultimate-tokens-color-science | T-0284 | L2 | solo | solo:L2 x1, verifier:L2 x1 | 2 | pass | 2.43 | 26.8 | yes 09:12 PDT | - |
| ultimate-tokens-color-science | T-0285 | L2 | solo | solo:L2 x1, verifier:L2 x1 | 2 | pass | 1.76 | 20.7 | yes 09:47 PDT | - |
| ultimate-tokens-color-science | T-0286 | L2 | solo | solo:L2 x1, verifier:L2 x1 (no run record yet), verifier:L3 x1 (running) | 3 | fail/running | 3.95 | 32.6 | no | diff verifier escalate: full; verifier L3 running at report time |
| ultimate-tokens-color-science | T-0287 | L2 | solo | solo:L2 x1, verifier:L2 x2 | 3 | fail/pass | 3.18 | 58.6 | yes 08:38 PDT | filed after settle red; diff verifier fail (abs path in handoff), pass on 2nd |

Wall min = first solo record or attempt start, to last attempt end (ultimate-tokens-color-science-ticket-wall.jsonl). Solo records carry their prepare time only, so a ticket with no attempt file (solo L1) has unmetered wall [V]. Closures with no run in the window (T-0231, T-0233, T-0234, T-0237) are counted in the 52 but have no row.

## Timeline
| Time | Repo | Event | Evidence |
|---|---|---|---|
| 01:00Z | ultimate-tokens-color-science | Window opens. Lanes are being opened with sdlc-lite 0.39.0 scripts and `--no-claim` (open24..open28.sh) | logs/open24.sh |
| 01:01Z | ultimate-tokens-color-science | First close in window (T-0237); lands run every 7-25 min from here to 07:31Z | ultimate-tokens-color-science-closes.txt |
| 01:27Z | ultimate-tokens-color-science | T-0232 chain step verifier L3 passes; landed 01:34Z | ultimate-tokens-color-science-attempts.jsonl |
| 02:15Z | ultimate-tokens-color-science | T-0242 land hits a merge conflict with T-0236 and goes back to its solo | conductor transcript 02:15:02Z |
| 02:24Z | ultimate-tokens-color-science | Person runs /plugin and /reload-plugins: 0.40.0 goes live. Person asks "what else can be fanned out?"; question answered in 7 s | conductor-asks.txt |
| 02:36Z | ultimate-tokens-color-science | settle32 rc=0 to main | logs/settle32.log |
| 02:58Z | ultimate-tokens-color-science | First `Scope: diff` verifier (T-0248) | ultimate-tokens-color-science-attempts.jsonl |
| 03:31Z | ultimate-tokens-color-science | Next-wave question answered in 8 s | conductor-asks.txt |
| 03:35Z | ultimate-tokens-color-science | T-0248 land gate red on a dashboard route test after its diff verifier passed; sent back to solo | conductor transcript 03:35:30Z |
| 04:17Z | ultimate-tokens-color-science | Decision question (retire v3, palette-service); 6.6 min wait on person | conductor-asks.txt |
| 05:43Z | ultimate-tokens-color-science | Person asks "are you merging as we go so it doesn't build up?" | conductor-transcript-gaps.txt |
| 05:53Z | ultimate-tokens-color-science | settle33 rc=0 | logs/settle33.log |
| 06:33Z | ultimate-tokens-color-science | Person: "fan them out when ready" | conductor-transcript-gaps.txt |
| 06:37Z | ultimate-tokens-color-science | settle34 rc=0 | logs/settle34.log |
| 07:30Z | ultimate-tokens-color-science | T-0266 solo reports already fixed. `advance` had already prepared a verifier, which never ran and was left `running` | ultimate-tokens-color-science-status.txt |
| 07:31Z | ultimate-tokens-color-science | settle35 rc=0 (main aa3af06d); T-0266 closed as not reproducible | logs/settle35.log |
| 07:32Z | ultimate-tokens-color-science | Conductor: "every ticket filed is done"; idle starts, waiting on the person | conductor-transcript-gaps.txt |
| 08:27Z | ultimate-tokens-color-science | Auto-compaction while idle (591,750 tokens before); goal check-in: nothing to do | conductor-transcript-gaps.txt |
| 10:27Z | ultimate-tokens-color-science | Goal check-in: still waiting on a ui-kit-neue T-0326 watcher for T-0111; nothing else to do | conductor transcript 10:27:26Z |
| 12:05Z | ultimate-tokens-color-science | Person returns: "what else can be fanned out?"; 273 min idle ends; new wave filed | conductor-asks.txt |
| 12:11Z | ultimate-tokens-color-science | T-0272 blocked at 375 px; 28.6 min wait on person | conductor-asks.txt |
| 12:47Z | ultimate-tokens-color-science | UI sweep round 4 picks; 30.5 min wait on person | conductor-asks.txt |
| 13:40Z | ultimate-tokens-color-science | T-0275 solo L2 blocked on a persistence-format question; person answers in 1 min; ticket moves to the full lane | conductor-asks.txt |
| 14:20Z | ultimate-tokens-color-science | settle36 rc=1: browser suite red from a cross-file test leak; settle37 rc=1 at 14:31Z; main stays blocked | logs/settle36.log, logs/settle37.log |
| 14:32Z | ultimate-tokens-color-science | T-0287 opened to fix the leak | ultimate-tokens-color-science-runs.jsonl |
| 14:44Z | ultimate-tokens-color-science | T-0275 builder L4 blocked with `plan defect:`; replan, then plan review again | ultimate-tokens-color-science-attempts.jsonl |
| 15:01Z | ultimate-tokens-color-science | T-0273 land red; red again 15:10Z | logs/land-openconfirm.log, logs/land-openconfirm2.log |
| 15:24Z | ultimate-tokens-color-science | T-0287 diff verifier fails: absolute path in the handoff trips check:standards; passes 15:31Z | .sdlc/runtime/tasks/0287-focus-test-suite-order/verifier-L2.md |
| 15:38Z | ultimate-tokens-color-science | native-land.sh called without a lane kind: `--lane: expected one argument`, rc=2 for T-0273 and T-0279 | logs/land-openconfirm-3.log, logs/land-pickerphone-3.log |
| 15:46Z | ultimate-tokens-color-science | T-0273 merged | logs/land-openconfirm-4.log |
| 16:03Z | ultimate-tokens-color-science | settle38 rc=0 (main 5d4746cc); main unblocked after about 103 min; skips.md restored by hand | logs/settle38.log, gitlog 382979d2 |
| 16:24Z | ultimate-tokens-color-science | T-0275 step-2 builder L3 ends after 50.1 min against a 45 min budget | ultimate-tokens-color-science-attempts.jsonl |
| 16:55Z | ultimate-tokens-color-science | settle39 rc=0 (main b99662d9); skips.md restored by hand again (f467cb13) | logs/settle39.log |
| 17:19Z | ultimate-tokens-color-science | T-0286 diff verifier returns `escalate: full`; verifier L3 starts and is still running at report time | colorjs7 worktree .sdlc/runtime/tasks/0286-colorjs-07/verifier-L2.md |

## 0.40.0 feature check
| Ticket | Feature | Exercised (count) | Worked as intended? | Evidence | [V]/[U] |
|---|---|---|---|---|---|
| T-0799 | Scope: diff verifier | 17 diff briefs, 1 escalated (T-0286) | Partly. Escalation fired correctly on out-of-scope computation edits. Diff scope was not cheaper (mean $0.47 vs $0.48 full) and was slower (mean 11.6 vs 7.9 min). One diff pass (T-0248) let a regression through that the land gate caught | ultimate-tokens-color-science-attempts.jsonl :: scope, cost, wall | [V] |
| T-0800 | lanes.py open --claim / finish, background backup | 0 (53 opens across 28 overnight open*.sh, all `--no-claim`; 0 `lanes.py finish`) | not exercised | logs/open*.sh; conductor-lane-commands.txt; no .git/sdlc-backup.log | [V] |
| T-0802 | failed backup reported by next finish | 0 | not exercised (no finish, no backup log, repo has no git remote) | `ls ~/Projects/ultimate-tokens-color-science/.git/sdlc-backup.log` (absent); ultimate-tokens-color-science.json :: ci.error | [V] |
| T-0803 | verifier `plan defect:` line | 0 verifier results. 1 builder result (T-0275 builder L4) | not exercised for verifiers. The builder plan-defect path worked: the replan confirmed the defect with a green run on a copy of the tree, and step 1 then passed | ultimate-tokens-color-science-attempts.jsonl :: pd | [V] |
| T-0804 | lane_landing config, open --claim commits the claim | 0 (no `lane_landing:` line in .sdlc/config; no --claim) | not exercised | `grep lane_landing ~/Projects/ultimate-tokens-color-science/.sdlc/config` (no match) | [V] |
| T-0796 | orphaned attempts, stall_attempts | 1 orphaned (T-0266 verifier-L2); 0 stall_attempts findings | Yes in dispatch.py status. fleet_collect still reports 0 orphaned because the parent pid is alive (Finding 6) | ultimate-tokens-color-science-status.txt; ultimate-tokens-color-science.json :: runs.orphaned.count; findings.jsonl | [V] |
| T-0797 | close keeps committed skips.md | 0 closes kept it; 6 manual restore commits in window | not exercised on 0.40.0. Closes ran through 0.37.0 fanout.py from the pinned helpers, and the old bug recurred | gitlog 93e108aa (close T-0285 deletes skips.md); ultimate-tokens-color-science-gitlog.txt "restore skips.md"; logs/native-land.sh | [V] |
| T-0788 | pre-verify review rerun on changed content | 0 | not exercised (no pre_verify_paths in .sdlc/config) | `grep -c pre_verify ~/Projects/ultimate-tokens-color-science/.sdlc/config` = 0 | [V] |
| budget guards | prepare refusals on budget or `time budget:`; over-budget attempts | 0 refusals; 0 over-budget in status; 2 completed attempts ran past their time budget (T-0270 verifier 42.3/25 min; T-0275 step-2 builder 50.1/45 min) | Partly. Nothing was refused, and overruns surface only while an attempt is still running | conductor transcript tool results (no match); ultimate-tokens-color-science-attempts.jsonl :: wall, budget | [V] |

## Verifier scope
| Repo | Ticket | Scope (diff/full) | Escalated? | Verdict | Cost $ | Wall min | Caught a real defect? |
|---|---|---|---|---|---|---|---|
| ultimate-tokens-color-science | T-0248 (1st) | diff | no | pass | 0.57 | 13.2 | no; missed a dashboard route regression that the land gate caught |
| ultimate-tokens-color-science | T-0247 | diff | no | pass | 0.61 | 23.6 | no defect present [U] |
| ultimate-tokens-color-science | T-0248 (2nd) | diff | no | pass | 0.36 | 7.4 | n/a, rechecked the fix |
| ultimate-tokens-color-science | T-0252 | diff | no | pass | 0.41 | 13.8 | no defect present [U] |
| ultimate-tokens-color-science | T-0255 | diff | no | pass | 0.51 | 8.9 | no defect present [U] |
| ultimate-tokens-color-science | T-0263 | diff | no | pass | 0.67 | 13.2 | no defect present [U] |
| ultimate-tokens-color-science | T-0259 | diff | no | pass | 0.41 | 9.5 | no defect present [U] |
| ultimate-tokens-color-science | T-0267 | diff | no | pass | 0.38 | 2.1 | no defect present [U] |
| ultimate-tokens-color-science | T-0264 | diff | no | pass | 0.40 | 3.3 | no defect present [U] |
| ultimate-tokens-color-science | T-0268 | diff | no | pass | 0.64 | 9.5 | no defect present [U] |
| ultimate-tokens-color-science | T-0270 | diff | no | pass | 0.60 | 42.3 | no defect present [U]; ran 17 min over budget |
| ultimate-tokens-color-science | T-0272 | diff | no | pass | 0.45 | 12.6 | no defect present [U] |
| ultimate-tokens-color-science | T-0273 | diff | no | pass | 0.89 | 19.6 | no; land then went red twice on the suite leak (pre-existing, not T-0273's) |
| ultimate-tokens-color-science | T-0287 (1st) | diff | no | fail | 0.48 | 9.8 | yes: absolute path in the handoff fails check:standards (task-text defect) |
| ultimate-tokens-color-science | T-0287 (2nd) | diff | no | pass | 0.26 | 5.5 | n/a |
| ultimate-tokens-color-science | T-0285 | diff | no | pass | 0.33 | 2.3 | no defect present [U] |
| ultimate-tokens-color-science | T-0286 | diff | yes, `escalate: full` | fail | unmetered (no run record yet) | 0.8 | yes: out-of-scope computation edit (css-notation.ts); L3 verdict pending |
| ultimate-tokens-color-science | 22 L2 full-scope attempts (T-0235..T-0284, T-0275 step 2; see attempts file) | full | no | 22 pass | 10.54 total, mean 0.48 | mean 7.9 | none recorded |
| ultimate-tokens-color-science | T-0232 step 1, T-0275 step 1 | full (L3) | no | pass, pass | 4.44, 4.84 | 18.0, 12.1 | none recorded |

## Interruptions and stalls
| Repo | Ticket | Role | Start | End | Minutes lost | Cause | How it recovered | Evidence | [V]/[U] |
|---|---|---|---|---|---|---|---|---|---|
| ultimate-tokens-color-science | all | conductor | 07:32Z | 12:05Z | 273 | Backlog empty; new tickets need the person to choose them in an AskUserQuestion round | Person returned and asked "what else can be fanned out?" | conductor-transcript-gaps.txt (GAP rows 07:35-12:05) | [V] |
| ultimate-tokens-color-science | T-0287 (main) | settle | 14:20Z | 16:03Z | about 103 for main promotion; lanes kept landing into integration | Cross-file localStorage leak in the browser suite turned the settle gate red | Filed T-0287, fixed createAppPage, settle38 green | logs/settle36.log, logs/settle38.log | [V] |
| ultimate-tokens-color-science | T-0275 | builder L4 / planner / plan-reviewer | 14:23Z | 15:12Z | about 48 (20.8 + 8.4 + 18.6) | Plan required fixtures to stay v1 while v2 writes change version digests (plan defect) | Replan, second plan review, rebuild passed | ultimate-tokens-color-science-attempts.jsonl | [V] |
| ultimate-tokens-color-science | T-0273 | land | 15:01Z | 15:46Z | about 45 | Land gate red twice: first on 120 s computation-test timeouts under load (a1 log), then on the suite leak (a2 log); then 2 helper calls with no lane kind | Rerun after T-0287 landed, with the kind passed | logs/land-openconfirm*.log | [V] |
| ultimate-tokens-color-science | T-0248 | land / solo / verifier | 03:35Z | 04:15Z | about 40 | Land gate red on a dashboard route test the diff verifier did not run | Solo fixed it, 2nd verifier, relanded | conductor transcript 03:35:30Z, 03:49:36Z | [V] |
| ultimate-tokens-color-science | T-0272 | solo | 12:11Z | 12:39Z | 28.6 waiting on person; other lanes kept running | Solo blocked at 375 px | Person picked "Widen T-0272" | conductor-asks.txt | [V] |
| ultimate-tokens-color-science | T-0270 | verifier L2 | 12:40Z | 13:22Z | 17 over budget | Unmeasured (verifier ran long on the browser tests) | Finished with a pass | ultimate-tokens-color-science-attempts.jsonl | [V] |
| ultimate-tokens-color-science | T-0242 | land / solo / verifier | 02:15Z | 02:30Z | about 15 | Merge conflict with T-0236 on legacy-canvas-dom.ts | Solo merged, 2nd verifier, relanded | conductor transcript 02:15:02Z | [V] |
| ultimate-tokens-color-science | T-0266 | verifier L2 | 07:30Z | open | 0 (never ran) | `advance` prepared a verifier before the conductor saw "already fixed", then the ticket was closed | Left `running`; dispatch.py status shows it orphaned | ultimate-tokens-color-science-status.txt | [V] |

## Findings
| # | Repo | Symptom | Evidence | Mechanism | Cost | [V]/[U] | Layer (sdlc-lite / project / host / task text) | Proposed prevention |
|---|---|---|---|---|---|---|---|---|
| 1 | ultimate-tokens-color-science | 273 min of nothing running overnight | conductor-transcript-gaps.txt; conductor-asks.txt (12:05Z) | Backlog was exhausted at 00:32 PDT. The conductor files new work only after an AskUserQuestion pick, and goal check-ins at 08:27Z and 10:27Z found nothing to do | 273 min | [V] | sdlc-lite / task text | Before an unattended goal, run /ask once to pre-approve a queue (sweeps plus their L1/L2 follow-ups), or let the goal text allow sweeps to file L1/L2 tickets without asking |
| 2 | ultimate-tokens-color-science | Land, sync, settle and close ran sdlc-lite 0.37.0 all night. 58 of 91 overnight logs print `0.37.0 in use; 0.40.0 installed: re-resolve the scripts path` | logs/native-land.sh, logs/settle-force.sh (S=.../0.37.0/scripts); logs/version-mismatch-logs.txt | Project helper scripts hard-code a plugin path; the scripts warn but do not stop | 6 manual skips.md restore commits; unmeasured minutes | [V] | project (with an sdlc-lite gap: a warning, not a stop) | Resolve the scripts dir at call time (the installed_plugins.json installPath), and make fanout.py exit nonzero on a version mismatch unless a flag allows it |
| 3 | ultimate-tokens-color-science | close dropped a committed skips.md on every fanout close | gitlog 93e108aa; 6 "restore skips.md" commits in ultimate-tokens-color-science-gitlog.txt | Consequence of 2: the T-0797 fix lives in 0.40.0 tickets.py, but closes went through 0.37.0 | 6 conductor commits; unmeasured | [V] | project | Fixed by 2. After the fix, check that `git show --stat` of the next close keeps skips.md |
| 4 | ultimate-tokens-color-science | T-0275 sized L2 turned into the most expensive ticket ($36.13, 171 min) | ultimate-tokens-color-science-runs.jsonl; docs/tickets/.0275-collection-names-kept/skips.md | A persistence-format question hid behind a UI ticket. The solo blocked, the person chose a new manifest version, and the full lane then hit a plan defect and replanned | $13.42 on the defect loop (builder $4.04, planner $2.28, plan-reviewer $7.10); about 48 min | [V] | task text | Flag sweep findings that touch stored formats or contracts (core-pipelines rule) as L3 at filing time |
| 5 | ultimate-tokens-color-science | Settle gate red for about 103 min on a cross-file test leak | logs/settle36.log, logs/settle37.log, logs/settle38.log | The browser suite had an order-dependent localStorage leak that lane-level gates (single files) never exercised | $3.18 (T-0287) plus about 45 min of T-0273 land retries | [V] | project | Keep T-0287's `localStorage.clear()` in createAppPage. Add a shuffled-order browser run to the lane gate |
| 6 | ultimate-tokens-color-science | Collector reports 0 orphaned; dispatch.py status shows T-0266 verifier-L2 orphaned | ultimate-tokens-color-science.json :: runs.orphaned.count; ultimate-tokens-color-science-status.txt | fleet_collect counts an orphan only when its parent pid is dead (fleet_collect.py:620). T-0796 also orphans a running attempt whose ticket is closed | unmeasured (retro undercount) | [V] | sdlc-lite | Have fleet_collect reuse dispatch.attempt_state_at so the two agree |
| 7 | ultimate-tokens-color-science | Verifier prepared for an already-fixed solo and left running | ultimate-tokens-color-science-status.txt; .sdlc/runtime/tasks/0266-tonal-band-scroll-region/verifier-L2.attempt.json | `dispatch.py advance` prepares the ticket verifier on any solo `done`-like result, including `already-fixed` | $0; leaves a stale attempt | [V] | sdlc-lite | advance should not prepare a verifier for an already-fixed result, or tickets.py close should mark that ticket's running attempts dropped |
| 8 | ultimate-tokens-color-science | Diff-scope verifiers cost the same as full scope and took longer | ultimate-tokens-color-science-attempts.jsonl (17 diff: mean $0.47 / 11.6 min; 22 full L2: $0.48 / 7.9 min) | Step (3) reverts the fix in a throwaway worktree, which adds wall time; the diff brief does not shorten the browser-test criteria | about 0 dollars saved; unmeasured minutes | [V] | sdlc-lite | Measure diff scope over more runs before keeping it as the default. Consider dropping step (3) when the Outcome carries red/green evidence |
| 9 | ultimate-tokens-color-science | T-0248 diff verifier passed a change that broke an untouched test | conductor transcript 03:35:30Z | Diff scope runs only the ticket's criteria. The regression was in a test outside the diff | about 40 min | [V] | sdlc-lite / task text | Add a named related-suite criterion to UI tickets, or let a diff verifier run the test files that import the changed modules |
| 10 | ultimate-tokens-color-science | T-0266 filed from a sweep using axe-core 4.10.2; the repo pins 4.14.0 and does not reproduce | conductor transcript 07:30:43Z, 07:31:15Z | The sweep tool used a different axe version from the repo | $1.46 | [V] | task text | Sweeps should run the repo's pinned axe-core (npx from the repo) |
| 11 | ultimate-tokens-color-science | T-0287 verifier failed on an absolute local path the conductor wrote into the handoff | .sdlc/runtime/tasks/0287-focus-test-suite-order/verifier-L2.md | Handoff criteria named gate_lock.py by its /Users/... path, which trips the W-12 standards rule | $0.48 plus about 7 min | [V] | task text | Write plugin script paths in handoffs as `~/.claude/...` or by name; lint handoffs with check:standards before dispatch |
| 12 | ultimate-tokens-color-science | Two land calls failed with `--lane: expected one argument` | logs/land-openconfirm-3.log, logs/land-pickerphone-3.log | native-land.sh takes lane:ticket:kind; per the conductor, a zsh `$l:solo` modifier mangled the spec [U] | about 8 min | [V] | project | Have native-land.sh refuse a spec with a missing field before it syncs |
| 13 | ultimate-tokens-color-science | Two attempts ran past their time budget with no signal after the fact | ultimate-tokens-color-science-attempts.jsonl (T-0270 verifier 42.3/25; T-0275 step-2 builder 50.1/45) | Status flags over-budget only while an attempt is running; completed overruns are not reported | 22 min over budget | [V] | sdlc-lite | Have status and fleet_collect report completed attempts that ran over their time_budget_min |
| 14 | ultimate-tokens-color-science | Land output repeats stale `close refused` rows for T-0047 and T-0178 on every land | logs/land-openconfirm.log | The ledger keeps old refused closes and land prints them each time | unmeasured (log noise) | [V] | sdlc-lite / project | Run `fanout.py run --rewrite-refs` once for those two, or have land print only this run's rows |
| 17 | ultimate-tokens-color-science | T-0273 first land: 120 s timeouts in three computation tests | logs/gate-fanout-2026-10-21-openconfirm-T-0273-2-a1.log (6 timeout lines) | Gate ran under machine load; the conductor reports load 15.6 against a cap of 10 [U, not saved] | part of the ~45 min T-0273 loss | [V] log, [U] load | host / project | Run fleet-doctor before a land retry. Raise the timeout of computation tests that run under gate_lock, or gate them with --need compute_units |
| 15 | ultimate-tokens-color-science | chromium_load: 59 processes, 12,238 MB RSS | findings.jsonl; processes-browser.txt | Mostly Google Chrome Canary, open for 6 days; 7 Playwright headless shells belong to the live T-0286 verifier | unmeasured | [V] | host | None needed for sdlc-lite. Closing Canary frees about 12 GB for gates |
| 16 | ultimate-tokens-color-science | chromium_load rss rule fired (same root as 15) | findings.jsonl line 2 | as 15 | unmeasured | [V] | host | as 15 |

## Conductor interviews
### ultimate-tokens-color-science
Question: "What cost you the most time overnight, and what is your evidence?"
Reply (verbatim, relayed by team-lead; marks are the conductor's):

> The most time went to a settle into main that was blocked by an order-dependent browser test. Two settles failed on the same test, and the T-0287 fix took about 1.5 to 2 hours before the settle passed [U: wall time from my memory of notification order, unmeasured]. Evidence:
> - The first settle went red on focus-after-actions.browser.test.ts "palette selection (a)" in Chromium, 1 failed of 2703: .worktrees/fanout/logs/cover-fanout-93ef86857a72-2.log [V]
> - The retry went red on the same test in Chromium and WebKit: .worktrees/fanout/logs/cover-fanout-7d769c6d1ef4-2.log [V]
> - The test passed 14/14 alone through gate_lock, so I first read it as load flakiness and retried, which cost one full settle (about 15 to 20 min) [V for the pass, U for the minutes]
> - Root cause: localStorage shared across browser test files (canvas pan and panel scheme). Fixed in packages/ui/testing/app-page.ts. T-0287 report: .worktrees/fanout/focusorder/.sdlc/runtime/tasks/0287-focus-test-suite-order/0287-solo-L2.md [V]
> - The same leak also failed T-0273's land on tonal-band-fit.browser.test.ts: logs/gate-fanout-2026-10-21-openconfirm-T-0273-2-a2.log [V]
>
> Second: land gates timed out under machine load. T-0273's first land hit 120 s timeouts in three computation tests: logs/gate-fanout-2026-10-21-openconfirm-T-0273-2-a1.log [V]. One gate_lock wait showed load 15.6 against a cap of 10 [V in my focus-recheck output; not saved to a file].
>
> Third: T-0275 was escalated from solo L2, which blocked on a stored-format change, to a full chain at L3. That added a user question, planner L3, plan review, builder L4 blocked by a plan defect (sync fixtures), replan, plan review, builder L4, verifier L3, builder L3 and verifier L2. Evidence: .worktrees/fanout/collnames/.sdlc/runtime/tasks/0275-collection-names-kept/ (0275-solo-L2.md, step-1.superseded-1/builder-L4.md, planner-L3-2.md) [V]. The size was right in hindsight [U].
>
> Self-inflicted, smaller:
> - a zsh `$l:solo` modifier mangled two land calls (land-openconfirm-3.log, rc=2 "--lane: expected one argument") [V]
> - a stray T-0227 lane opened by a copied helper header [U]
> - steps.py split --supersede left one stale step-1/builder-L4.md path that dispatch.py prepare refused; I fixed it by hand [V: scratchpad b0275b.json first output, overwritten]
> - sdlc-lite #83: skips.md removed on close, restored by hand twice (commits f467cb13 and the earlier T-0270..T-0287 restore) [V]

Retro cross-check: the four cited logs exist and are copied to logs/ [V]. The a1 gate log has 6 timeout lines [V]. The settle block measured 14:20Z to 16:03Z, about 103 min, which falls inside the conductor's 1.5 to 2 h [V]. The conductor counts 2 skips.md restores; git log shows 6 in the window [V]. The 273 min idle on an empty backlog (Finding 1) does not appear in the reply.

## Friction for the person
- 7 AskUserQuestion rounds overnight. Waits: 7 s, 8 s, 6.6 min, 12 s, 28.6 min (T-0272 block), 30.5 min (sweep round 4 picks), 1 min (T-0275 format). The skill flow requires a person to approve new tickets and to rule on blocked solos [V: conductor-asks.txt].
- The person asked "what else can be fanned out?" 8 times (02:24Z to 12:05Z). No rule forced this: the conductor had no standing instruction to refill the queue [V: conductor-transcript-gaps.txt].
- The person ran /plugin and /reload-plugins at 02:24Z to move to 0.40.0. The helpers still used 0.37.0 afterwards [V].
- The T-0275 persistence-format choice is required by the project rule that a contract change is a person's decision [U: docs/agents/core-pipelines.md not reopened in this retro].

## Not checked
- Other repos: out of scope by the person's instruction (2026-10-29); this retro covers ultimate-tokens-color-science only.
- `--gh`: CI and PR data unavailable; the repo has no git remote (ultimate-tokens-color-science.json :: ci.error).
- Per-role wall time for solo runs: run records have duration_ms null and solo records carry only the prepare time, so it is unmetered.
- Gate durations per land: gate logs carry no timestamps and land.jsonl has no ts. Some land logs (for example land-phonecanvas.log) were overwritten by the retry, so first-attempt failures are known only from the conductor's transcript.
- Whether each diff-scope pass missed a defect: only T-0248 has evidence (the land gate). The others are marked [U].
- T-0286 verifier L3 verdict: still running at report time.
- Heavy test gates: not run, by instruction.

## Evidence files
- ultimate-tokens-color-science.json: fleet_collect fingerprint, window 2026-10-28T18:00-07:00 onward.
- ultimate-tokens-color-science.collect.stderr: the collector's `runs:` line.
- findings.jsonl / detect.stderr: fleet_detect output (2 chromium_load findings).
- fleet-config-active.txt: `fleet_config.py show --active` output (no fleet.json).
- ultimate-tokens-color-science-status.txt: `dispatch.py status` for every task dir touched overnight, in main, colorjs7 and integration.
- ultimate-tokens-color-science-runs.jsonl: all overnight run records (97), deduplicated across main, colorjs7 and integration, including step-* folders; `_task` and `_src` added.
- ultimate-tokens-color-science-attempts.jsonl: every overnight attempt record (51), with verdict, Scope line, escalate and plan-defect lines, wall, budget and cost.
- ultimate-tokens-color-science-ticket-wall.jsonl: per-ticket start, wall minutes and verdicts derived from runs and attempts.
- ultimate-tokens-color-science-closes.txt: 52 `close T-` commits on main in the window (local time).
- ultimate-tokens-color-science-gitlog.txt, -gitlog-integration.txt, -gitlog-colorjs7.txt: `git log --since='2026-10-28 18:00'` for main and the two lane worktrees.
- ultimate-tokens-color-science-worktrees.txt: `git worktree list`. No .git/sdlc-backup.log exists.
- conductor-transcript-gaps.txt: main-thread gaps over 10 min and human messages, from the conductor transcript b8497289.
- conductor-asks.txt: every AskUserQuestion with its question and answer times.
- conductor-lane-commands.txt: the conductor's Bash calls that touch lanes.py, fanout.py, native-land.sh or settle-force.sh.
- processes-browser.txt: ps snapshot of browser, vite and Playwright processes at report time.
- logs/: cover-fanout and T-0273 gate logs cited by the conductor; copies of the overnight open*.sh lane-open scripts, native-land.sh, settle-force.sh, settle32-39 logs, the T-0273 and T-0279 land logs, land-ts6.log, and version-mismatch-logs.txt (the 58 logs that print the 0.37.0 warning).
