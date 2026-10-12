<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
- process deviation: red-checkpoint: retrospective: attempt 7daddc1571174d6e86da2e430ce16719, handoff sha256 e97b3ef0b2fc, 7 of 7 (red) criteria without a pre-edit red control. The `redck.py record` call ran after the tree already held earlier work. The verifier's note on the same line is that it read the criteria as red without the report, which does not clear the deviation.
- Verifier L1 verdict for step 1 is pass on all 9 criteria. Its negative fixture for the scope guard (criterion 8) was not run, because the worktree hook refused `git worktree add`. The verifier read the predicate instead.
- The report quotes the third `budget.txt` line with a one-character truncation (`plan defec` against `plan defect`). No criterion checks it. Fix it in the loose-ends step.
- The task did not do what the ticket asked. Only 3 priced cells ran: `rts-step10` L1 A and B, and `ndc-step2` L5 arm A. The replay stopped at the $20 cap. The L1 task that ran replayed the fixed handoff (`8974d49f`, not the blocked `fceea3cc`), so it could not test blocking. The L5 pair is half run, and arm A blocked on a plan defect. The retest did not reach the ticket's question.
- Spend: replay $10.04, ticket $19.30 before this filer. Both are under the $20 cap.

## PR title
T-0458: Retest the builder overlays on blocking tasks; replay stopped at the cap, verdict drop on an unbitten rule

## PR body
### Summary
This adds the dated report `docs/reports/2026-10-12-builder-overlay-retest.md` with its evidence folder `docs/reports/2026-10-12-builder-overlay-retest/`. The report carries `Verdict: drop`, `L1 overlay: drop` and `L5 overlay: unverified`. The drop comes from the T-0442 blocked-rate rule. That rule could not bite here (0 of 1 versus 0 of 1), as in the first A/B. The report says so. It adds no evidence beyond the first A/B, whose drop the maintainer overruled on 2026-10-11. The report records the verdict only. It does not delete the overlay, and T-0443 stays gated.

Only 3 cells ran before the cap:

| task | level | arm | cost | blocked | verifier |
|---|---|---|---|---|---|
| `rts-step10` | L1 | A | $0.34 | no | pass |
| `rts-step10` | L1 | B | $0.28 | no | pass |
| `ndc-step2` | L5 | A | $8.54 | yes (plan defect) | n/a |

The L1 pair used the fixed handoff, so it did not test blocking. L5 arm B did not run. The report lists the other L1 pairs, repetition 2, and the other tasks under `## Not run`, each marked unverified. It also records the first A/B miss on `figma-stale-skip-report` for the verifier prompt work and does not fix it. Replay spend is $10.04. Ticket spend is $19.30 before the builder, verifier and filer of this step.

### Changes
- New report `docs/reports/2026-10-12-builder-overlay-retest.md`, with per-run rows, rule outcomes, the stop at the cap, method, Not run, and raw rows.
- New evidence folder `docs/reports/2026-10-12-builder-overlay-retest/`: `budget.txt`, `preflight.txt`, `cell.py`, and the three cell directories.
- No overlay, agent, adapter, skill or script changed.

### Verification
Verifier L1 passed all 9 criteria: 7 (red) and 2 (guard).
- Header, verdict lines and the per-run table header are present.
- The 3 table rows match the 3 `run-log.md` rows.
- The `Spend:` line, `rows.jsonl` and the table sum all give 10.04.
- Ticket spend is 19.30, under 20.
- `## Not run` names every skipped item.
- The report has no em dashes or trailing whitespace, and its links resolve.
- The 5 raw rows match the 5 `rows.jsonl` rows.
- The scope guard found no stray paths.
- `python3 plugins/sdlc-lite/scripts/check.py` printed `ok: 19 role levels, 9 agents, 22 generated definitions checked`.

Process deviation: the 7 (red) controls were recorded after the tree already held earlier work, not before the edit. A passing verdict does not clear this.

Not verified: any overlay effect on blocked rate, first-pass rate or cost on a blocking task. No hidden-check grade exists (`n/a` in all rows). The L5 overlay is unverified.

## Changelog entry
- Added the T-0458 builder overlay retest report. It is a partial replay: 3 priced cells ran before the $20 cap. The report carries `Verdict: drop` for the L1 overlay on a rule that could not bite, with L5 unverified.

## Follow-ups
- fix-now: Correct the truncated third `budget.txt` quote (`plan defec` to `plan defect`) in the `## Stop at the cap` section of `docs/reports/2026-10-12-builder-overlay-retest.md`.
- decide: The retest did not answer the ticket's question, because no L1 run tested blocking and the L5 pair is half run. Whether to file one follow-up ticket for a funded replay with reproducible blocked handoffs is for the maintainer to choose. A funded replay needs the blocked `rts-step10` handoff `fceea3cc` (never committed, now gone) or another reproducible blocked task.
- note: The `figma-stale-skip-report` hidden check `staleskipnotice` failed in all four first A/B runs while both verifier levels passed it. Pass this to the verifier prompt work.
- note: The `t0378` hidden check is red at base `b599114e` and green at `a8b39893` and `e1fa6e04`. The earlier plan's claim of red at `a8b39893` was false.
- note: Planner handoffs cited paths in other repos in a form the `steps.py lint` links gate refused, and this cost one replan. A future replay plan should cite them as absolute paths, `<sha>:<path>`, or plain words.
