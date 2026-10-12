---
doc-type: report
---

# Ceremony audit: cost versus defects caught (T-0464)

Result: the filer-warning close refusal stalled 8 distinct tickets in waves f50 to f59 (6 of them closed in this tree), each of the 6 closed ones was cleared by `--ack-warnings`, and the warning kind present on all 6 closed ones, the retrospective red-checkpoint, has no recorded catch; the other ceremony sites either caught real defects (plan-reviewer, verifier, inherited red) or are already covered by shipped work, so 3 changes are proposed.

## Method

Recorded 2026-10-12 on branch `fanout/wave41-w` at base `46a1f500`. Everything below is read-only; the other three repos were read, never written. Run every command from the repository root.

- Main counter: `python3 docs/reports/2026-10-12-ceremony-audit/count.py > docs/reports/2026-10-12-ceremony-audit/counts.txt`. Output captured in `docs/reports/2026-10-12-ceremony-audit/counts.txt`; its sections A to J are cited below as "counts A" and so on. It reads every `runs.jsonl` under each ticket folder (step folders included), the result files, the `## Closed` line of each closed `handoff.md`, the git commit that created each closed folder, and `/tmp/fanout-f5N.log` when present. It orders verifier results with the plugin's own `plugins/sdlc-lite/scripts/order.py`, never by file time.
- Sets: WINDOW is the 27 closed folders `.sdlc/.0431-*` to `.sdlc/.0459-*` (closed since T-0431); ALL is the 439 closed `.sdlc/.0NNN-*` folders in this tree.
- First case, this repo: `find .sdlc -maxdepth 2 -path '.sdlc/.04*' -name 'filer-L1*.md' | wc -l` gives 11 files; count A groups them per ticket.
- First case, other repos (the settled sample): `find <root> -maxdepth 2 -name 'filer-L1*.md' | wc -l` for the three roots gives 20 (`/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets`), 12 (`/Users/kimgranlund/Projects/nonoun/agent-ui/.sdlc`) and 8 (`/Users/kimgranlund/Projects/nonoun/ultimate-tokens/.sdlc`), matching the planner probe. Count A2 classifies them.
- Close refusals: `grep -ho 'T-04[0-9][0-9] merged, close refused: [^:]*: filer warnings are open' /tmp/fanout-f5*.log | sort -u | wc -l` gives 8 distinct tickets; without the `filer warnings are open` suffix the same pipeline gives 11 (three refused for other reasons). Each refusal appears twice in a log (event line and report table row), so raw `grep -c` hits are double.
- Plan-reviewer verdicts: `for f in $(find .sdlc -path '.sdlc/.0*' -name 'plan-reviewer-L*.md'); do sed -n '/^## Verdict/{n;p;}' $f; done | sort | uniq -c` gives pass 17, replan 7.
- Cost: `runs.jsonl` `cost_usd` and `duration_ms` summed by role and level (counts B, J). Cross-check: `python3 plugins/sdlc-lite/scripts/fleet_collect.py collect . --since 2026-10-10` (method from `docs/reports/2026-10-11-solo-fails-and-blocks.md`); its summary is in `docs/reports/2026-10-12-ceremony-audit/fleet-collect.txt`. The collector reads every worktree's runs, so a rerun on a later date gives larger totals. Dollars and minutes are a floor: unmetered runs record $0 (14 unmetered since 2026-10-10 per the collector), and nothing outside sdlc-lite is counted.
- "Minutes" in cost columns are model minutes (sum of `duration_ms`), not wall clock.
- Prompt lint: `python3 plugins/sdlc-lite/scripts/prompt_lint.py`, then `python3 plugins/sdlc-lite/scripts/prompt_lint.py | grep -c '^info P-6'` gives 72. Wording counts, from `plugins/sdlc-lite/`: `grep -oiE '<pattern>' agents/*.md skills/*/SKILL.md overlays/*.md | wc -l` with `\bloops?\b`, `\bre-?verif[a-z]*` and `\bre-?run[a-z]*`.
- Warning kinds are assigned by keyword in `count.py` (`kind()`): a `process deviation` line naming `red-checkpoint` is that kind; then flake words; then unverified-claim words; else other. The keyword rule is a heuristic [U]; the per-ticket rows in counts A let a reader re-judge each entry.

## Per-site table

Window figures are WINDOW (T-0431 to T-0459); "all" figures are ALL closed folders. Catches are defects a site found that the work would otherwise have shipped with.

| Site | Cost (dollars, model minutes) | Defects caught (count, pointers) | Manual acks | Source |
|---|---|---|---|---|
| plan-reviewer L1 (the only level with results) | all: 24 runs, $100.17, 166 min ($4.17 a run); window: 0 runs | 7 replan verdicts of 24 (29%): `.sdlc/.0179-messages-entry-files/plan-reviewer-L1.md`, `.sdlc/.0181-messages-wait/plan-reviewer-L1-4.md`, `.sdlc/.0183-supervisor-script/plan-reviewer-L1.md`, `.sdlc/.0184-role-result-schema/plan-reviewer-L1.md`, `.sdlc/.0195-runner-family-task-dir/plan-reviewer-L1-2.md`, `.sdlc/.0197-lane/plan-reviewer-L1.md`, `.sdlc/.0233-reorg-apply/plan-reviewer-L1.md` | 0 | counts B, E |
| plan-reviewer L2 to L5 | no result file exists at any other level | none recorded | 0 | counts E |
| filer on solo tickets | all: 10 runs, $1.55, 3 min (6 of 261 solo tickets have a filer); window: 0 runs, every solo ticket closed by `--reason` | 0 recorded [U] | 0 | counts A, C |
| filer on chain tickets | all: 167 runs, $39.74, 66 min; window: 10 runs, $1.98, 4 min | 0 found first by the filer [U]; 2 of its warnings preceded follow-up tickets (T-0451 and T-0452 flake entries, then T-0459; the T-0442 L5 entry, then T-0458), but builder or verifier notes reported each first | 6 in window (every chain ticket with warnings) | counts A, B, C |
| second verifier round | 14 later-round results in 14 folders (all); dollars not split out [U] | 1 later-round fail: `.sdlc/.0356-verifier-routing-by-level/verifier-L3-2.md`; 0 later rounds ran after a pass | 0 | counts D |
| full chain for L3 | all: 23 chain L3 tickets, $459.55, median $13.07 and 74 min a ticket; 5 solo L3 tickets, median $10.91 and 49 min; window: 8 chain tickets $73.68, of which planner plus filer $29.05 (39%) | 3 verifier fails in chain L3 tickets: `.sdlc/.0175-ticket-root-router/step-7/verifier-L2.md`, `.sdlc/.0177-mailbox-core/step-1/verifier-L3.md`, `.sdlc/.0212-handoff-freeze/step-1/verifier-L3.md` (verifier catches, which a solo lane with one verifier keeps) | 6 (the window acks above all fell on chain L3 tickets) | counts F, J |
| `inherited red` stops | 2 of 428 builder results; cost not split out [U] | 2, both real: `.sdlc/.0183-supervisor-script/step-11/builder-L2.md` (traces selftest corpus), `.sdlc/.0447-doc-standards-suite/step-4/builder-L3.md` (gate_lock selftest, later fixed by T-0459) | 0 | counts G |
| gate-lock timeouts or contention reported as red | 18 closed files in 10 tickets mention the gate lock with flake, contention or timeout; window tickets T-0447, T-0451, T-0452, T-0456, T-0459; 0 gate timeout lines in `/tmp/fanout-f50.log` to `/tmp/fanout-f59.log` | 0 product defects; 2 tooling defects found and fixed: the selftest touching the real root (T-0459) and cheap gates queuing behind heavy ones (T-0456) | 2 (T-0451, T-0452 acks name the flake) | counts I |
| replans | all: 19 superseded step folders in 11 tickets; 27 tickets with two or more planner results ($214.70, 1018 min of planner runs, first plans included); `refusals.jsonl`: 11 `steps.py lint`, 1 `steps.py split`; collector: 24 early and 1 late plan defects since 2026-10-10; window: 3 second-planner runs (T-0441, T-0444, T-0450), planner-L3 $7.64, 32 min | window: 0 real plan defects [U]; all three were `steps.py lint` cited-path refusals of paths that a step would create, that belonged to another repo, or that were test fixtures | 0 | counts H, J |
| questions that did not change the output | builder results whose Notes open with `question:`: 0 of 428 | none recorded | 0 | counts G; conductor questions are not in the artifacts [U] |
| rules that re-verify or re-run a green result | none found that require it | n/a | 0 | see Prompt lint signals |

## First case: filer-warning close refusal

Claims in the T-0464 handoff, checked:

- "9 of 11 filers since T-0431 carry a retrospective red-checkpoint": corrected. The 11 is a per-file count of `.sdlc/.04*/filer-L1*.md` that includes T-0427 (before T-0431) and four second files (`filer-L1-2.md`). Per ticket, 7 closed tickets since T-0431 have a filer (T-0441, T-0442, T-0444, T-0448, T-0450, T-0451, T-0452) and 6 of the 7 carry a retrospective red-checkpoint deviation; T-0450's filer says `None`. The other 20 window tickets have no filer: 19 solo tickets and T-0447, whose `## Closed` line says "filer skipped (close-first)".
- "about 6 lane stalls": confirmed for this tree and widened. The fanout logs show 8 distinct tickets refused for open filer warnings: T-0441 and T-0444 (`/tmp/fanout-f51.log`), T-0448 (`/tmp/fanout-f53.log`), T-0442 and T-0451 (`/tmp/fanout-f54.log`), T-0452 (`/tmp/fanout-f57.log`), T-0458 and T-0460 (`/tmp/fanout-f59.log`). The 6 closed in this tree are the "about 6"; T-0458 and T-0460 merged in wave 40 and are still open here. Three more refusals had another cause: T-0421 (stale references to the folder), T-0450 and T-0462 (`skips.md` lane full with no `## Skipped` entry).

Per closed ticket (counts A; entries are from the latest filer file, which `close` reads):

| Ticket | Warning entries by kind | Refused | Cleared by | Led to | Wall minutes, last run to close commit [U] |
|---|---|---|---|---|---|
| T-0441 | red-checkpoint retrospective 1, unverified claim 1, other 2 | yes, f51 | `--ack-warnings` | none | 38 |
| T-0442 | red-checkpoint retrospective 2, unverified claim 1 | yes, f54 | `--ack-warnings` | the L5-unverified entry preceded T-0458 | 38 |
| T-0444 | red-checkpoint retrospective 2, unverified claim 3, other 2 | yes, f51 | `--ack-warnings` | none | 62 |
| T-0448 | red-checkpoint retrospective 2, unverified claim 1, other 1 | yes, f53 | `--ack-warnings` | none | 11 |
| T-0450 | None | yes, f55, for `skips.md`, not warnings | n/a | none | 0 |
| T-0451 | red-checkpoint retrospective 1, flake 2, unverified claim 1, other 2 | yes, f54 | `--ack-warnings` | the flake entries preceded T-0459 | 138 |
| T-0452 | red-checkpoint retrospective 2, flake 1, other 2 | yes, f57 | `--ack-warnings` | the flake entry preceded T-0459 | 260 |

Totals over the 7 latest filer files: 29 entries; red-checkpoint retrospective 10, unverified claim 7, flake 3, other 9. Most "other" entries are pass summaries such as "All three steps passed".

Kinds and outcomes:

- Red-checkpoint retrospective (10 entries, 6 tickets): every entry names step 2 or later and gives one cause, earlier steps' uncommitted work already in the shared tree, so `redck.py record` stored the controls as retrospective (the phase rule is in the `plugins/sdlc-lite/scripts/redck.py` docstring). In each entry the step verifier ran its own red control or probed the base and found the criterion red. None led to a fix, a reopened ticket or a later defect: no closed or open handoff reopens these tickets, and the `## Closed` line of each says the verifiers passed [U for "no later defect", which rests on the absence of a record]. Prior redck work (T-0420, `.sdlc/.0420-redck-execution-tree/`; T-0395) narrowed the cause but did not remove it for multi-step chains.
- Flake (3 entries, 2 tickets): gate_lock selftest and `check.sh` reds under parallel sessions. These led to T-0459 (its handoff names T-0447 and T-0452). A real catch, but of a flaky check, and the builder notes saw it first.
- Unverified claim (7 entries): builder claims the verifier could not re-observe (removed clones in T-0442, a non-independent replay in T-0448). The T-0442 entry preceded T-0458, which re-tests the overlays. The others led to nothing recorded [U].
- How cleared: all 6 by `--ack-warnings` (each `## Closed` line starts "warnings acknowledged:"); none by `--force`; `--reason` closed the 19 filer-less solo tickets and T-0447 (`tickets.py close` refuses a filer-less close without `--reason`; see the usage line in `plugins/sdlc-lite/scripts/tickets.py`).
- Minutes lost: the fanout logs have no timestamps and the ack lines carry dates only. The bound used is the last `runs.jsonl` timestamp to the commit that created the closed folder: 547 wall minutes over 6 tickets, median 50. It includes merge gates and idle time, so it is an upper bound, not working minutes [U]. The model spend on the ack itself is not recorded (the ack is a conductor action, not a role run).

Other repos (counts A2):

| Root | Filer files | Task folders | Folders whose latest filer has warnings | Entries by kind | Acked closes |
|---|---|---|---|---|---|
| `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets` | 20 | 19 (17 closed) | 5 | other 10, unverified claim 2, red-checkpoint missing 2, red-checkpoint retrospective 1 | 3 |
| `/Users/kimgranlund/Projects/nonoun/agent-ui/.sdlc` | 12 | 10 | 0 | none | 0 |
| `/Users/kimgranlund/Projects/nonoun/ultimate-tokens/.sdlc` | 8 | 8 | 1 | other 4, red-checkpoint missing 1, unverified claim 1 | 1 |

In those repos the filer warnings are rarer (6 of 37 folders) and more often substantive, for example the ui-kit-maison R4 integration filer with a final L3 verifier fail (`/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/.0332-r4-mega-wave-integration/filer-L1.md`). Their fanout logs are not on this host, so whether a close was refused there is unknown [U]. agent-ui and ultimate-tokens keep closed task folders without a dot prefix, so "closed" there rests on each handoff, which the script did not read for status [U].

## Prompt lint signals

`prompt_lint.py` over its defaults (72 files): 0 errors, 8 warnings, all P-5 (no "closed step" or "closed ticket" line in archaeologist, architect, filer, plan-reviewer, planner, researcher, scout and verifier), and 72 P-6 info lines, one per file.

P-6 against `docs/reports/2026-10-11-agent-prompt-lint-baseline.md` (base files only; generated `-L<n>` copies repeat the base counts):

| File | Baseline prohibitions / NEVER / vague | Now prohibitions / NEVER / vague |
|---|---|---|
| `plugins/sdlc-lite/agents/builder.md` | 14 / 11 / 6 | 19 / 0 / 0 |
| `plugins/sdlc-lite/agents/solo.md` | 17 / 11 / 14 | 19 / 0 / 0 |
| `plugins/sdlc-lite/agents/verifier.md` | 15 / 12 / 6 | 20 / 0 / 0 |
| `plugins/sdlc-lite/agents/planner.md` | 36 / 33 / 6 | 40 / 0 / 0 |
| `plugins/sdlc-lite/agents/conductor.md` | 29 / 26 / 3 | 30 / 0 / 2 |
| `plugins/sdlc-lite/agents/plan-reviewer.md` | 8 / 8 / 4 | 10 / 0 / 0 |
| `plugins/sdlc-lite/overlays/builder.md` | 0 / 0 / 0 | 0 / 0 / 0 |

The baseline came from the upstream `potency_lint.py`, a different tool with different word lists, so the two columns are not a like-for-like diff [U]: the NEVER column going to 0 may be a counting difference rather than a rewrite.

Wording counts over `agents/*.md`, `skills/*/SKILL.md` and `overlays/*.md` under `plugins/sdlc-lite/` (informational only): loop 36, verify (`re-verify` family) 9, re-run 55; these match the planner probe. Reading the re-run lines in the role files: `plugins/sdlc-lite/agents/builder.md` (line 27) and `plugins/sdlc-lite/agents/solo.md` (line 17) say "re-run no green check", and `plugins/sdlc-lite/agents/conductor.md` (line 9) says to reverify a pass only when a verified file changed. No rule found tells a role to re-run or re-verify a green result. The remaining hits are reruns after a fail, a missing verdict, or a swap [U: judged from the matched lines, not each file read in full].

## Ranked changes

Ranked by measured cost removed, with every check that has a real catch kept. Quality guard for each: K-005 first-pass rate (`docs/kpi/005-solo-first-pass-rate.md`, baseline 72, target 85 or more) must not fall, and rework after close (a reopened ticket or a follow-up bug naming the closed one) must stay at zero.

1. [propose a ticket] Stop a retrospective red-checkpoint on a later step of a shared tree from blocking close. Cost: 6 of 6 manual acks in the window (the outcome metric), 547 wall minutes upper bound [U], and a lane stall each time. Catches: 0 recorded across 10 entries [U]; in every case the step verifier ran its own red control. Change: when every step verifier passed and the step's verifier recorded a red control at the base, the filer writes the deviation under a non-blocking heading (or `tickets.py close` treats that one kind as info), while `process-deviations.md` keeps the record. A root fix is a per-step base for `redck.py record` (the tree at the end of the previous step) so the control is pre-edit again. Measure: manual acks per wave, from 6 across waves 32 to 38 to at most 1. Guard: K-005, rework after close, and a negative control showing that a retrospective deviation without a verifier red control still blocks.
2. [propose a ticket] Make `steps.py lint` stop refusing test-fixture paths in criteria. Cost: window replans T-0444 (fixture spans under `$d/.sdlc/0001-a/`) plus this ticket's own refusal (`## Plan review` of T-0464, a probe fixture path); the window's three second-planner runs cost $7.64 and 32 model minutes, and `refusals.jsonl` holds 11 lint refusals in all. Catches: 0 real defects among the window refusals [U]. Change: a cited path built under a shell variable or a scratch prefix is not a citation. Measure: plan defects from `steps.py lint` per wave (collector `plan_defects.early`, 24 since 2026-10-10). Guard: the existing negative case, a cited path that should exist and does not, must still refuse.
3. [propose a ticket] Trial solo L3 with one independent verifier for L3 tickets with no merge step and no cross-cutting scope. Cost: chain L3 median $13.07 and 74 model minutes against solo L3 $10.91 and 49 (n = 5, so [U]); in the window, planner plus filer were $29.05 of $73.68 on 8 chain tickets, and every manual ack fell on a chain L3 ticket. Catches kept: the 3 verifier fails in chain L3 tickets are verifier catches, which this lane keeps; plan-reviewer did not run on any window ticket. Change: route those L3 tickets to `solo-L3` for a measured batch. What is cut is the planner and the filer (no catch of their own in the window); the independent verifier is kept, run once per ticket instead of once per step. The plan-reviewer is not affected: it ran on no window ticket. Measure: dollars and model minutes per L3 ticket, rounds to close. Guard: K-005 and rework after close on the batch against the chain L3 history; stop the trial at the first rework.
4. Keep the plan-reviewer. It costs $4.17 a run and caught a replan in 7 of 24 runs; no change.
5. Keep `inherited red` stops and the builder's pre-build base check (`plugins/sdlc-lite/agents/builder.md` rule 8): 2 stops, 2 real catches.
6. Keep the second verifier round as is: 14 rounds with 1 catch, and the conductor already reverifies a pass only after a change.
7. Watch the `skips.md` close refusal (T-0450, T-0462: lane full with planner or filer skipped and no `## Skipped` entry). Two tickets, minutes not recorded [U]; no ticket proposed until a second wave shows it.

## Already covered

- T-0428 (close-first doctrine, `.sdlc/.0428-close-first-doctrine/`): roles stop at "done and checked once"; it is why solo tickets close with `--reason` and no filer, and why T-0447 skipped its filer.
- T-0456 (cheap gates queue behind heavy, `.sdlc/.0456-cheap-gates-queue-behind-heavy/`): a cheap fanout gate no longer waits behind heavy browser jobs, so a queue wait never reads as a red gate. Covers the gate-lock-timeout-as-red site.
- T-0459 (gate-lock selftest real-root flake, `.sdlc/.0459-gate-lock-selftest-real-root-flake/`): the selftest no longer fails under concurrent real-lock use. Covers the flake warnings of T-0451 and T-0452 and the T-0447 inherited red.
- T-0446 (record finds transcript, `.sdlc/.0446-record-finds-transcript/`): `dispatch.py record` prices a sub-agent run without `--transcript`, so fewer runs land unmetered; it raises the floor of every cost figure here.
- T-0445 (collector ignores completed attempts, `.sdlc/.0445-collector-ignores-completed-attempts/`): K-002 lost minutes count only truly interrupted attempts, so lost-minute figures are not inflated by finished runs.
- T-0457 (lint cited paths, future and foreign, `.sdlc/.0457-lint-cited-paths-future-and-foreign/`): `steps.py lint` accepts a path the step creates and a path in another repo. Covers the T-0441 and T-0450 replans; change 2 above is only the fixture-path case it leaves.
- T-0461 (open): applies the controlled language system to `/clarify` (closed vocabularies, a handoff grammar lint). Covers part of "questions that did not change the output" by narrowing what clarify asks.
- T-0462 (open): designs merging the plan-* skills into one `/plan` with kinds and one lint. Covers planning-skill sprawl, not the per-ticket planner cost.

## Unverified

- Minutes lost per refusal: the 547 wall minutes are an upper bound from the last run to the close commit; the time the conductor actually spent on each ack is not recorded.
- "No later defect" for the retrospective red-checkpoint entries rests on the absence of a reopen or a follow-up naming the ticket, not on a search of every later bug.
- Warning kinds come from a keyword rule; a reader may class some "other" or "unverified claim" entries differently.
- Close refusals in ui-kit-maison, agent-ui and ultimate-tokens: no fanout logs for them on this host. `fleet_collect.py` was run on this repo only, to stay inside the $8 cap; the other three repos' cost was not collected.
- Second verifier round dollars, inherited red stop minutes and gate-lock rerun minutes were not split out of the role totals.
- Questions that did not change the output: conductor `AskUserQuestion` rounds leave no artifact, so this site could not be counted beyond the builder `question:` notes (0).
- Solo L3 comparison rests on 5 tickets.
- Prompt lint baseline comparison crosses two different tools.
- T-0450 sits in a closed (dot) folder with no `## Closed` line, so its close path is not recorded.
- Dollars include $0 rows for unmetered runs (for example T-0435 and T-0440 in counts J), so every cost is a floor.
