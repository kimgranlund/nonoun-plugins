# Experiment Series

How to run H4 as a series of H3 cycles against a system whose output varies between runs and whose runs cost money: a model, an agent, a generative pipeline, a live service. SKILL.md section 17 is the summary; [live-evaluation.md](live-evaluation.md) covers the mechanics of one paid cycle (sampling, the cap, preflight, quarantine, replays).

The lessons here come from a nine-cycle study of one generative UI runtime: a producer loop that composes persona text, shared guidance, retrieved exemplars and tool calls, validates the output, and repairs it in bounded rounds, measured on three model sizes. Treat each rule as a hypothesis for a new system and run its check before relying on it.

## The series loop

```text
cycle N report
  → one ticket per root cause, each with a keyless replay pinned to today's failure
  → fix with a test that is red first; one independent verifier per fix
  → plan cycle N+1: comparison set, kind (full or targeted), estimate, cap, dry run
  → approval gate
  → cycle N+1 runs; provider errors quarantined
  → report: transitions against the last identical cycle, one mechanism metric per fix,
    the cost each fix shifted, tooling gaps
  → fix tooling gaps under test before the next cycle needs them
```

Each cycle is still a full H3 cycle with its own report and stop. The series adds three things: cycles stay comparable, every fix is measured by its mechanism, and spend is gated.

## 1. A fixed comparison set

A comparison set is the exact list of cases (scenario, input script, model, settings such as effort or temperature, sample count, order) that a full cycle runs. Give it an id and generate it from a pinned source, so the list itself is under test and cannot drift between cycles.

- **Compare only identical runs.** A pass rate means something only against the same case under the same settings. A case renamed, reworded, moved to another model or rerun at another sample count is a new case. Record the commit, the prompt or guidance digests, the version of any analysis configuration (such as a trace-to-analysis mapping) and the price table with each cycle.
- **A changed set is a new set.** When a scenario must change (it was itself the defect), the change gets its own id and its first cycle is a new baseline for that case, never a "fix" of the old one.
- **Read rates, not totals, across different sets.** Targeted cycles run subsets; their cells are partial. Mark them partial in every comparison table instead of summing them against a full cycle.
- **Rerun the previous cycle's passes that touch changed content.** A content or guidance change can create failures elsewhere (an added list item made an existing ask ambiguous); only an unchanged rerun shows it.

Check: two consecutive full cycles produce the same case list from the generator, and the report states the commit and digests of each.

## 2. Alternate targeted and full cycles

- **Targeted cycle:** rerun the last cycle's failures under the same names, plus the long or high-risk flows nearest the changed code. Cheap (a small fraction of a full cycle) and fast; it tells you whether the fixes hold on the cases they were made for.
- **Full cycle:** rerun the whole comparison set unchanged. Expensive; it is the only way to see a case that passed before and fails now.

Alternate them: after a targeted cycle clears its failures, run a full cycle before claiming the fixes hold. A targeted cycle cannot see regressions outside its subset; a run of only full cycles spends most of the budget re-proving passes. Plan the alternation in the series frame, and break it only with a stated reason (a fix so local that a targeted rerun is the full radius, or a cap that cannot cover a full cycle).

Check: no claim of "fixed" for a series rests only on targeted cycles since the last full one.

## 3. Regression accounting

Report transitions, not only the pass rate. For every case in the comparison set, against the last identical cycle:

| Transition | Meaning |
|---|---|
| fail to pass | a fix held, or noise; name which fix, or say none applies |
| pass to fail | a regression; open it even when the total rose. With sample 1 it may be noise: if no change touches the case, sample it N times before fixing |
| fail to fail, same cause | the fix did not reach it |
| fail to fail, new cause | the old cause is gone and another surfaced; a case that fails on a new cause cycle after cycle is unstable, sample it N times ([live-evaluation.md](live-evaluation.md)) |
| pass to pass | stable |

In the study, one full cycle gained a single net pass while eight failures turned green and seven passes turned red; the pass rate alone would have hidden the seven. Report "any" and "only" counts per failure cluster, and cost each cluster's extra repair rounds when repair is automatic.

Check: the report lists every pass to fail case by name, with its cluster.

## 4. One mechanism metric per fix

A fix is a claim about a mechanism (a forced retry calls the tool, a new check fires and its repair saves the turn, a decoder accepts a near-miss payload). Pass or fail on the original case cannot show the mechanism: the case may pass for another reason or fail on a new cause. So every fix names, before the next cycle runs, one metric that shows its mechanism working live, with the previous cycle's value:

- how often the guarded condition occurred (the code fired N times);
- how often the mechanism then did its job (saved M of N, called the tool on K of K forced rounds);
- what it cost (extra rounds, tokens, latency), the cost the fix shifted (SKILL.md section 15).

Give each fix one verdict per cycle: **fixed live** (the mechanism fired and worked), **partly** (it fired and sometimes worked, or worked on one path), **not exercised** (its condition never occurred; the keyless test still carries it, but nothing live proves it), **regressed**. "Not exercised" is not "fixed". A failure that does not recur with no relevant change is noise, not a fix.

Check: every fix in the cycle report has a metric row with a value and a previous value.

## 5. An approval gate before each paid cycle

Before any cycle that spends money, present to the owner (the person or governing caller who holds the budget; SKILL.md section 1) and get the owner's explicit approval for:

1. the comparison set id and kind (full or targeted), with the case count;
2. the spend estimate, taken from the last identical cycle's measured spend (for the first cycle, from dry-run token counts at list prices or a one-model pilot), and the hard cap;
3. what the cycle measures: the fixes under test and each one's mechanism metric;
4. the dry run output and the credential preflight result ([live-evaluation.md](live-evaluation.md)).

The approval covers that cycle only; a report's `next_cycle.required` never stands in for it. A cycle stopped at its cap, a crash, or a credential failure is reported and approved again before it resumes; a resumed cycle keeps its start time and spend baseline so its totals stay one cycle.

## 6. When tooling gaps are fixed

Each cycle report ends with the steps the cycle's tooling (the runner, the analysis or tracing tool, its detectors, the replay builder) could not do and a person or agent did by hand: a stop reason no detector read, a provider error the ingest had no step for, a mapping that missed a source. These are findings like any other.

- Fix a gap under test, with its own record, before the next cycle that needs the step. A gap left open costs the same manual step every cycle and hides from the next reader.
- Do not change the measuring tooling and the product in one step without saying so. When the tooling changed between cycles (a new field, a new mapping version), record the change and compare coverage against the prior cycle, so a new signal is not mistaken for a new failure.
- When the product starts recording something new (a stop reason, a digest), check that the analysis tooling reads it; recording without a reader is a gap.

Check: every tooling gap from cycle N has a fix, a ticket, or a ruling to leave it before cycle N+1 runs.

## 7. When a series stops

Stop the series, with a final report, when any is true: every remaining failure has a ticket or a ruling and a full cycle showed no new pass to fail case; the budget is spent; the same clusters persist across two full cycles with no information gain (escalate the diagnosis); or the owner ends it. A series never continues because the last cycle was close.

Related field lessons for model-driven systems: test-loop lessons (`context:context-fog-of-war` `references/learnings/test-loop.md`) and model-choice lessons (`context:context-fog-of-war` `references/learnings/model-choice.md`) in the context-fog-of-war skill.
