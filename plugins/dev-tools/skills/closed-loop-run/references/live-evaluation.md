# Live Evaluation

How to run one H3 cycle against a live system that is nondeterministic and charges per run: a hosted model, an agent, a paid API. SKILL.md section 17 is the summary; [experiment-series.md](experiment-series.md) covers how cycles chain into a series.

Observed in a nine-cycle study of one generative UI runtime measured live on three model sizes; treat each rule as a hypothesis and run its check on a new system.

## 1. Single-sample noise, and when to sample N

One run per case is an anecdote. A cheap series can afford sample 1 for discovery, but read every single-sample result as "seen once", not as a rate.

Sample a case N times (and report k of N) when:

- it flips between cycles with no change that touches it;
- it fails on a new cause cycle after cycle (an unstable flow, not a fixed defect);
- the claim is a rate or a comparison (the cheapest model that passes, a fix that "usually" works);
- a decision rides on it (adopting a model, closing a ticket on a live pass).

Set the pass floor before the run (for example, at least k of N), count a missing output or a halt (the system gave up with no answer) against the cell rather than dropping it, and treat a cell with zero usable samples after its N attempts as failed. A cell not run at all (a cap stop, a quarantined provider error) is partial: it stays outside the rate and is never a pass to fail regression. A failure that does not recur once, with nothing relevant changed, stays open with "cause not determined".

Check: every rate in the report states its N.

## 2. Cheapest first under a hard cap

- **No run without a cap.** The runner refuses to start without one, and nothing removes it. The cap is enforced by the runner from measured usage at a pinned price table taken from a source document, never from memory; list prices without discounts (caching, batching) are an upper bound, which errs safe.
- **Order runs cheapest first.** Cheap models and short cases run before expensive ones, so a stop at the cap leaves the cheap cells filled instead of one expensive cell.
- **Resume, do not restart.** The runner skips cases that already have a result and keeps the cycle's start time and spend baseline, so a restart after a stop stays one cycle.
- **Estimate from the last identical cycle.** The approval gate ([experiment-series.md](experiment-series.md) section 5) quotes measured spend from the same comparison set; report estimate against actual afterwards. The first cycle of a series has no identical predecessor: estimate it from dry-run token counts at list prices, or from a one-model pilot of a few cases.
- **Cost the repair loop.** When the system repairs its own output in rounds, report the spend of repair rounds per failure code; the costliest code is a priority signal by itself.

## 3. A dry run before spend

Before the paid cycle, run everything that costs nothing:

1. Generate the run list and print it: case count, models, order, the cap. Diff it against the previous identical cycle's list.
2. Run the runner's own keyless self-test (a fake cycle that must stop at a fake cap and resume).
3. Run the keyless replay suite, so known failures are pinned and a fix that already flipped one is visible before money is spent.
4. Confirm the archive location is durable (not a temporary checkout that gets deleted) and that every trace, payload and ledger of the cycle will be kept.

## 4. Credential and quota preflight

Make one cheap live call per credential and per provider the cycle will use, and confirm the remaining quota or usage limit covers the estimate with margin. A credential that reaches its usage limit mid-cycle turns the rest of the cycle into provider errors and splits it; a preflight catches that before the first case. Keep credentials out of the test tooling itself: the runner and probes reach the provider through one boundary that holds the key, and no report, trace or replay prints one.

## 5. Quarantine provider errors

Rate limits, usage limits, overload, authentication failures, provider timeouts and a crash of your own runner are not results. They say nothing about the system under test.

- Detect them by their own signal (status, error class), not by a failed check.
- Remove the affected runs from the cycle's results and rerun them clean once the cause is cleared (a new credential, a wait, a runner fix).
- Keep the raw lines in the archive so line numbers and ledger ranges stay valid; exclude or blank them only in the copy the analysis ingests.
- State the exclusion in the report with its count and time window. When there were none, say "no provider error, nothing excluded": silence is ambiguous.
- Uniform provider errors across every case are the strongest form of the uniform-errors rule (SKILL.md section 6): stop the cycle, fix the pipeline, and re-approve.

## 6. Freeze useful failures as keyless replays before fixing

A live failure is expensive to reproduce and may not recur. A useful failure is one a fix will target: a real failure, not noise that did not recur and not a quarantined provider error. Before changing anything:

1. Record the system's actual responses for the failing case as a fixture.
2. Build a keyless replay from it that makes no network call (a replay that reaches a provider fails) and pin it to today's failing behavior, marked as an expected failure tied to its ticket.
3. The fix flips the pin in the same change; an expected failure that starts passing without its fix being cited fails the suite.
4. When no check fails offline (a gap where nothing fired), pin the replay on the recorded shape (the rounds, the codes, the missing output) rather than on a failing check.

The replay is then a V0 check for the fix that costs nothing, and the suite proves fixes between paid cycles.

## 7. Recorded versus authored repair rounds

An authored fixture (a hand-built response that triggers a check and a repair) proves the mechanism: the check fires, the repair text is sent, the loop ends as designed. It cannot prove live compliance, because the live system may still answer the repair the wrong way. Claims about how the system behaves cite a recorded live run; claims about how your machinery behaves may cite an authored one. Say which in the report.

Measure the mechanism, not only compliance: for a forced retry, count how many forced rounds called the tool; for a new check, how often it fired and how often its repair saved the case. A rise in pass rate with the mechanism never exercised is not evidence for the fix.

## 8. Keep everything

Every cycle keeps its traces, payloads, run reports, spend ledger and manifest (commit, cap, stop reason, window, price table) in a durable home, with an entry file that says what each file is and how to read it, and a generated index across cycles. Live runs never run in continuous integration; replays do.

Related field lessons for model-driven systems: test-loop lessons (`context:context-fog-of-war` `references/learnings/test-loop.md`), instrumentation lessons (`context:context-fog-of-war` `references/learnings/instrument.md`) and validation and repair lessons (`context:context-fog-of-war` `references/learnings/validation-and-repair.md`) in the context-fog-of-war skill.
