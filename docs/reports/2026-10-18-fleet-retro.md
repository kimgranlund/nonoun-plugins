# Fleet retro 2026-10-18

Repos: ui-kit-maison: runs: 59 deduped, $239.80, 0 interrupted, 0 limit markers, interview: none. agent-ui: runs: 92 deduped, $285.63, 0 interrupted, 0 limit markers, interview: none. gen-ui-kit: runs: 1 deduped, $0.00, 0 interrupted, 0 limit markers, interview: `W/gen-ui-kit-interview.md`. ultimate-tokens: runs: 0 deduped, $0.00, 0 interrupted, 0 limit markers, interview: none (no conductor session). sdlc-lite: runs: 24 deduped, $21.41, 0 interrupted, 0 limit markers, interview: none (the session running this retro). Plugin: 0.24.5, `/Users/kimgranlund/.claude/plugins/cache/sdlc-lite/sdlc-lite/0.24.5`, Claude Code 2.1.301. Window: 2026-10-17, open.

`W` is `.sdlc/runtime/tasks/fleet-retro-2026-10-18/`. gen-ui-kit reports 13 merged PRs and a $62.53 solo run in the window, while its fingerprint holds 1 run from 1 runs file: its lanes were swept and no lane records reached `main/.sdlc` [U on where the records went].

## Cross-repo table
| Repo | Runs | Spend | Plan-review share | Interrupted + limit | Findings |
|---|---|---|---|---|---|
| ui-kit-maison | 59 | $239.80 | 18.4% | 0 + 0 | 1 + machine |
| agent-ui | 92 | $285.63 | 10.8% | 0 + 0 | machine |
| gen-ui-kit | 1 | $0.00 | 0% | 0 + 0 | 7 interview + machine |
| ultimate-tokens | 0 | $0.00 | 0% | 0 + 0 | machine |
| sdlc-lite | 24 | $21.41 | 0% | 0 + 0 | machine |

## Findings
| # | Repo | Symptom | Evidence | Mechanism | Cost | [V] or [U] | Check | Prevention |
|---|---|---|---|---|---|---|---|---|
| 1 | gen-ui-kit | Highest single lane cost: cf7 solo L3 | `dispatch.py record` output "solo recorded, cost_usd 62.529069" for lane `/Users/kimgranlund/Projects/adia/ui-kit/lanes/cf7` (swept) | Large deletion lane ran land:local and the full check repeatedly | $62.53 | [U] | downgraded; not actionable: G1 (lane swept) | none |
| 2 | gen-ui-kit | cf7 verifier L3 failed 1 of 11 criteria with no code defect | `plugins/sdlc-lite/scripts/dispatch.py:1130` ("Never run the full check.sh"); lanes/cf7 verifier-L3.md (swept) | The prepared verifier brief forbids the full check while the handoff criterion named `npm run check`; the answer to the verifier's question arrived after its 50 min budget | about 45 min plus one L3 verifier run | [U] | not actionable: G3 | prepare's verifier brief exempts a gate the handoff criteria name |
| 3 | gen-ui-kit | Two lanes sent back for a missing ticket file | cf4, cf5 send-back messages | The conductor's own cf4 and cf5 briefs omitted the "file one ticket" line | about 15 min, 2 amend rounds | [V] | not actionable: G1 | none (conductor brief template) |
| 4 | gen-ui-kit | Conductor edit lost when a merged lane worktree was removed mid-edit | `git status` in lanes/cf6 showed 6,415 deleted tracked lines, then "fatal: must be run in a work tree" | Merged lanes are swept soon after merge; the conductor reused lanes/cf6 for a follow-up branch | about 10 min and one discarded edit | [U] | not actionable: G1 (lane swept) | sweep skips a worktree whose branch is not the merged lane branch or that has uncommitted changes |
| 5 | gen-ui-kit | Solo final reports truncated in the idle notification | cf6 and cf2 notifications ended "[result truncated]" | Notification size cap; cf6 wrote no solo-report.md | about 5 min, 2 round trips | [V] | not actionable: G1 | solo writes solo-report.md before idling; record points at it |
| 6 | machine | 37 Chromium processes using 17546.9 MB | `W/ui-kit-maison.json :: processes.chromium.rss_mb` (and `processes.chromium.count`, 37) | not diagnosed | unmeasured | [V] | not actionable: G4, needs diagnosis | none |
| 7 | ui-kit-maison | Ticket T-0332 at level L2 carries 32 criteria (threshold 20) | `W/ui-kit-maison.json :: tickets.items[161].criteria` | not diagnosed | unmeasured | [V] | not sampled; not actionable: G4, needs diagnosis | `/review-traces ui-kit-maison` |
| 8 | gen-ui-kit | Ticket-id collisions between parallel lanes | SendMessage exchange cf2/cf3 (ids 11396/11397 swapped twice) | Lanes read `.counter` on origin/main independently; peer-message reservations arrived late | 4 extra messages, one amend round | [U] | downgraded; not actionable: G1 | a counter reservation command in tickets.py |
| 9 | gen-ui-kit | Solo then independent verifier per lane, merge on green | 13 PRs merged 2026-10-18 (#575 to #590) | solo_run plus dispatch prepare and record kept each lane to one build and one verify | unmeasured | [V] | not actionable: G1, G5 | keep |

## Not actionable

Verifier: `.sdlc/runtime/tasks/fleet-retro-2026-10-18/verify/verifier-L1.md`. Sampled [V] rows 1 and 8 did not reproduce (row 1's lane `lanes/cf7` was swept; no message file holds the row 8 ids), so both are [U]. The planted control failed as required.

- Rows 1, 3, 4, 5, 8: G1, the evidence lived in swept lanes or peer messages with no openable record.
- Row 2: G3, "about 45 min" has no source. The mechanism is real (`dispatch.py:1130` forbids the full check even when a criterion names it); a measured repeat would make it actionable.
- Rows 6 and 7: G4, needs diagnosis. Row 7 is the same T-0332 finding as the 2026-10-17 retro.
- Row 9: G1 and G5, a positive observation (keep).

Drafts filed: none.

## Observation

The gen-ui-kit fingerprint holds 1 run while its conductor reports 13 merged lanes in the window: lane records are lost when its lanes are swept, so this repo's spend is invisible to the collector. Most of the G1 failures above share that cause.
