# Adjudicated trace benchmark

Run a labeled suite through the real adapters and diagnostic layer:

```sh
python3 scripts/engineer.py benchmark --suite /absolute/suite/manifest.json --out /absolute/new-results
```

The CLI writes detailed results and a terminal summary, and saves an immutable `engineering/benchmark` record in the user library. Recorded commands are never executed. Trace and repository hashes are checked before hydration. Use a separate output directory outside the suite. The standalone `scripts/benchmark.py` also runs suites without publishing to the library.

The development suite in this project's `benchmarks/trace-v1` contains 28 cases across Codex, Claude and web-chat, including a frozen Seatcraft store/load subset. Most cases are synthetic; all are author-adjudicated development material. These are not independent holdout or production precision estimates. The harness and documentation ship in the skill; private/domain trace suites remain separate explicit inputs.

## Truth and score definitions

Freeze truth before running the analyzer. Each case records raw trace provenance, host, exact expected detector/anchor-line occurrences, actionable problems, returned source/result-line pairs, explicit call/result or target relationships, and a rationale. Score occurrences one-to-one: duplicate predictions are false positives, not extra successes. Do not alter labels to accommodate analyzer behavior. If a label is wrong, document its correction, bump the suite version, preserve the old scores, and re-adjudicate affected actions.

- **Signal detection:** exact detector plus final evidence line. It measures detection of recorded patterns, not harm.
- **Problem triage:** result format v2 retains the original all-signals score as `candidateProblemTriage`. `problemTriage` excludes only explicitly qualified likely-benign signals; needs-review signals remain candidates and still count as false positives against nonproblem truth. Both use the same frozen actionable-problem labels. Report both scores so the changed prediction policy is visible. The classifier cannot use labels or review rationales. Deliberate verification and intentional filtering without recorded intent remain unresolvable, not automatically benign.
- **Returned attribution:** exact source path and return line, deduplicated per event. Precision measures unsupported claims; recall measures recoverable paths missed. Read and partial count as returned; this does not evaluate full-vs-partial classification, understanding, retention or causality.
- **Relationship attribution:** exact endpoint trace lines for matched call/result and explicit request/delivery links. Other inferred or guidance edges are outside this metric. Web-chat chunk identities are not content reads, so empty returned-source denominators are null, not perfect scores.
- **Abstention:** ambiguous cases should not emit diagnostic signals. Valid partial exposure can still be reported.
- **Action relevance:** a separate author review judges the actual recommendation against the known failure: addresses, partial, unrelated, or not-needed. Ratings bind to the action text, raw trace and full case-label hashes. Changed text or truth becomes unreviewed, never silently inherits a pass. Report rated-suggestion coverage and problem coverage alongside relevance; missed problems have no useful recommendation. This evaluates relevance, not experimentally verified remedy effectiveness.

Report micro totals and per-host scores. Host cases differ; aggregate accuracy does not establish host parity. Zero denominators remain unknown. Retain every miss, false positive, ambiguity violation, exact recommendation and citation in results. Before proposing a detector change, inspect whether the failure is extraction, eligibility, matching, diagnosis semantics or recommendation specificity. A benchmark score increase is analyzer performance on that suite, not a workflow/product improvement.

## Extending and reviewing

Add raw traces with declared consent/scope, a stable repository snapshot, adjudicator identity, exact evidence, and alternative explanations. Keep a separate untouched holdout set and obtain independent review before making reliability claims. Negative cases should resemble positive cases; include benign repeats, missing output, mixed batches, conflicting identities and incomplete assembly. Context interventions require separate execution experiments, not merely passing this benchmark.

The initial baseline exposed missed Claude broken-reference/truncation signals and missing Codex byte-limited read attribution. The unchanged development suite now recovers those signals and returns; retain the original baseline for comparison. Benign truncation remains a valid signal but a false positive when interpreted as an actionable problem. The two recovered problem recommendations have been separately author-adjudicated: broken-reference addresses the pointer failure; truncation is partial because it lacks a concrete generated-log recovery procedure. Their hashes remain bound to the unchanged expected labels. These judgments do not measure remedy effectiveness. Do not label all guidance as effective because it contains an expected keyword.
