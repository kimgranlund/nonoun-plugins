# Solo lane assessment
Subject: `sdlc-lite/solo-lane`, criteria in [solo-lane-contract.md](solo-lane-contract.md) (blob e60e1b04c912).

## Revision and environment
Implementation checked: repository commit 27875a3 plus the contract commit ff8aae5. Content digests (git blob ids, first 12): `agents/solo.md` 28b61bd1320c, `scripts/steps.py` 59481bfa07ad, `scripts/solo_run.py` a3ef495bb1b8, `scripts/fanout.py` a589aa3ef7b0, `scripts/budget.py` 8c27972f1df1.
Checks run at this revision (2026-10-05, macOS, python3): `steps.py selftest`, `fanout.py selftest`, `solo_run.py selftest` and `budget.py selftest`, each rc=0.
The live runs below were recorded at earlier plugin commits (each record names its own commit and environment). I did not diff those commits against this revision, so a live result supports a criterion but is not shown current here.

## Criteria
| # | Criterion | Check and result | Evidence | Status |
|---|---|---|---|---|
| 1 | Lane choice | `steps.py selftest` rc=0 at this revision; `steps.py lane` printed `solo` for the size M fixture in the live runs | [solo-live-run](../validation/solo-live-run.md) | met |
| 2 | Tiers | Claude M: model `claude-sonnet-5-5`, launch flag `--effort xhigh`; Claude S: `runs.jsonl` says sonnet, low, level L1; Codex M: rollout records `gpt-6.1-sol` high, role `sdlc-solo-l2`; Codex S: run record `gpt-6.1-sol` low, backend codex | [solo-live-run](../validation/solo-live-run.md), [solo-budget-gate](../validation/solo-budget-gate-live-run.md), [codex-fanout](../validation/codex-fanout-live-run.md) | met for S and M; tier L not assessed |
| 3 | Metering | One real session through `solo_run.py` wrote a `role solo` record whose cost equals the result event (0.1315212); null cost handled by `solo_run.py selftest` | [solo-cost](../validation/solo-cost-live-run.md) | met for Claude through the wrapper; the raw command and a Codex solo record nothing or null |
| 4 | Budget gate | A 90 percent ticket was refused with exit 4 and no session; after `budget.py ack` it ran; boundary (80 refused, 79 starts) in `solo_run.py selftest`; fanout case 18 covers a gated lane | [solo-budget-gate](../validation/solo-budget-gate-live-run.md) | met; the gate reads recorded cost only |
| 5 | Close | A headless conductor closed a size M ticket with `tickets.py close --reason`, exit 0, guard live; a 4-lane fanout rerun merged and closed all four; the steps selftest negative control refuses without the entries | [solo-close](../validation/solo-close-live-run.md), [fanout-solo](../validation/fanout-solo-live-run.md) | met on Claude; Codex close not assessed here |
| 6 | Verification | Claude M: one L3 `fable xhigh` verifier passed (a different family from the Sonnet solo); fanout M lane: Fable verifier passed | [solo-live-run](../validation/solo-live-run.md), [fanout-solo](../validation/fanout-solo-live-run.md) | met on Claude; the Codex solo's own verifier step not exercised; tier L not assessed |
| 7 | Outcome | Hidden checks passed: 20 of 20 (Claude and Codex, M), 9 of 9, 24 of 24, 13 of 13 (via `/agent solo`), Codex 8 of 8 (fanout, S) and 12 of 12 (conductor start, M) | the records above, [agent-command](../validation/agent-command-live-run.md), [codex-conductor](../validation/codex-conductor-solo-live-run.md) | met on seven small fixtures, one run each |
| 8 | Authority | No run tested a hostile ticket body or a push attempt; the criterion rests on the text of `agents/solo.md` and the role hook | none | not assessed |

## Limits and accepted use
Seven small fixture tasks, one run per cell, one machine, no consumer-repo run. The benchmark's solo arm used plain Opus high, not this agent ([benchmark](../validation/solo-vs-lean-benchmark-2026-10-04.md)). Codex solo cost is null by design and a conductor-started Codex solo is unmetered. No tier L task has run.
Accepted use scope: size S and M tickets on Claude Code, with Codex partly shown. Not qualified for independent reuse: no separate consumer context has exercised the public interface.

## What the format lacked
- A status for "assessed at an earlier revision, not rechecked here". `evidence.md` has not assessed, failed and stale, but stale means inputs changed, and here it is unknown.
- A way to say declared versus observed (the Codex solo model is declared by the tier table in some runs and observed in a rollout in others).
- A rule for a contract whose implementation is five files: one digest per file worked, but the format names a single revision.
- A place to record a criterion split across hosts (Claude and Codex met different parts).
