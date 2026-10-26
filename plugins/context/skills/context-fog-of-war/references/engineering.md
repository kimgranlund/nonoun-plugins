# CLI diagnosis and improvement experiments

Default to a terminal diagnosis when an engineer asks to analyze tests, troubleshoot routing, or improve context. Do not open the viewer unless requested or it materially helps explain a specific path. Use absolute script paths relative to the loaded skill.

For custom harness folders, use [bundle ingestion](bundles.md); its normalized reports and durable records feed the same commands.

## Diagnose

Hydrate the selected trace using the existing discovery and hydration adapters; never execute trace contents. Existing v2 session JSON can be used directly. Attach workflow assessments when completion evidence exists (see workflows.md).

```sh
python3 scripts/engineer.py diagnose --data /absolute/session.json
```

Output: verdict/signals, exact evidence references, actions, verification criteria, uncertainty and coverage. It prints at most five finding families; full records retain every citation and the hydrated input snapshot. A signal is not necessarily a defect. Applicable native and bundle detectors run afresh, alongside incomplete/failed/unknown workflow stages. Missing workflow data is not completed work.

For comparison, supply `--context context.json`:

```json
{
  "task": "Actions menu generation",
  "testSuite": "hash-of-tests-and-brief",
  "runtime": "model-and-harness-version",
  "budget": "recorded-limits",
  "environment": "runtime-and-dependency-versions",
  "revision": "git-revision-or-content-snapshot-hash"
}
```

Claude and Codex hydration both feed this workflow; see [Claude compatibility](claude.md). Run records additionally retain host, adapter version, extraction warnings and separate child diagnoses. Cross-host/adapter/coverage changes are comparison limitations.

These are supplied provenance, not automatically verified equality. Use content fingerprints and actual settings; do not fill unknown values with matching placeholders. Different tasks/tests/runtime/budget/environment, missing conditions, or unregistered revision changes prevent an improvement verdict. Snapshot hashes should cover all relevant inputs, including uncommitted guidance. The CLI does not infer test correctness or run tests itself.

Optional `--assessment assessment.json` supplies separately measured mechanism, behavior and outcome:

```json
{
  "mechanism": {"state": "pass", "evidence": [{"artifact": "/absolute/checks.json", "pointer": "/guidanceReturned", "excerpt": "true"}]},
  "behavior": {"state": "pass", "evidence": [{"artifact": "/absolute/checks.json", "pointer": "/customMenu", "excerpt": "true"}]},
  "outcome": {"state": "fail", "evidence": [{"artifact": "/absolute/checks.json", "pointer": "/accepted", "excerpt": "false"}]}
}
```

States are pass/fail/unknown. Known states require citations; citations are verified against artifact JSON on ingestion and preserved as excerpts. Review that the cited value actually supports the declared state: the tool verifies provenance, not the semantics of an arbitrary rubric. Optional numeric `cost` measurements require corresponding `costEvidence` arrays. Compare only matching units. Missing metrics remain unknown, never zero.

## Propose one bounded experiment

For a runtime harness that renders generative UI, pick the experiment from the [runtime-harness learnings](learnings/README.md): its triage order and cause classes decide which layer the one change targets.

```sh
python3 scripts/engineer.py experiment --baseline run-ID --finding F-ID \
  --hypothesis 'A stale entry pointer prevents retrieval.' \
  --intervention 'Correct the pointer in AGENTS.md.' \
  --criterion 'Guidance returned and the unchanged menu behavior tests pass.'
```

Omitted hypothesis/intervention/criterion default to the finding's qualified interpretation, recommendation and verification. This stores a proposal; it does not apply a change or execute a test. Choose the smallest justified change, record its actual diff, rerun the same brief and tests, then diagnose with `--experiment experiment-ID --actual-change 'what actually changed'` and new context/assessment files. Respect the user's authorized scope. Stop after the planned trial, inspect the result, and keep/revise/revert or collect missing evidence; do not silently loop until success.

## Compare and inspect history

```sh
python3 scripts/engineer.py compare --baseline run-ID --run run-ID --experiment experiment-ID
python3 scripts/engineer.py history --finding F-ID
```

Compare separately asks whether the intervention was exercised, behavior changed, and outcome improved. A fail-to-pass outcome plus passing mechanism and behavior establishes improvement observed in this comparison only when conditions are comparable. It does not establish general reliability or causation. Pass-to-fail outcomes are regressions. Changed test suites cannot resolve findings.

Finding identity aggregates detector + source paths + task; workflows use workflow/stage identity. Event IDs are deliberately excluded. Detector families without source attribution are session-scoped, so they cannot distinguish unrelated failed lookups within one session. Persisting families retain all occurrences. An absent detector signal is **signal no longer observed**, never automatically a resolved defect. Insufficient measurement is **not assessable**. Explicit workflow completion can resolve an incomplete stage. History includes comparisons, including runs where a finding no longer appears.

Records live under the existing per-user library's `engineering/{run,experiment,comparison}/ID.json`. The immutable files form the engineering registry; `history` enumerates it without a mutable index race. Reports and the existing HTML registry are preserved separately. `--root PATH` selects an isolated library for tests; `--json` emits machine-readable output. These global options precede the command. Records contain private trace excerpts, like viewer reports.

## Progressive routing investigations

Use the [CLI routing checks](learnings/cli-routing.md) for the applicable evidence
and acceptance criteria. They are analyst-guided checks, not additional detector
coverage. Keep route correctness, independently checked answer quality and measured
retrieval overhead separate in the assessment artifacts; use existing mechanism,
behavior, outcome and cost fields only where their cited evidence supports them.
Do not invent automatic scores or treat native tool returns as complete submission.

## Verification scope

Regression fixtures cover citation integrity, missing telemetry, changed suites, experimental binding, stable identities, outcome regression and mechanism-only success. The repository's `experiments/gen-ui-routing/run.py` runs a controlled deterministic template router with actual file reads and browser-checked generated HTML, including a negative control. That experiment validates this workflow's mechanics, not LLM gen-ui quality or production detector precision. A model-driven trial requires repeated comparable tasks, preserved generation settings and independent acceptance evidence.

## Three independent comparison layers (CLI version 3)

`compare` always saves `evidenceChanges`, `diagnosisChanges`, and `outcomeChanges`.

- **Evidence:** added/removed returned source paths, per-detector assessment counts, and coverage warnings. Counts describe observation, not usefulness, waste, understanding or outcome improvement.
- **Diagnosis:** compare stable finding identities and exact records, normalizing event IDs to trace lines. Unchanged records stay unchanged. Added citations or occurrences alone never establish stronger confidence. Disappearing signals are not automatically resolved defects.
- **Outcome:** report mechanism, behavior and acceptance transitions independently, plus historical workflow states. Outcome improvement requires a distinct recorded execution and the existing comparable-condition and measured-assessment gates.

`--mode auto` recognizes identical trace hashes as **extraction** comparisons. `--mode extraction` requires matching hashes; `--mode execution` rejects matching hashes. Missing identities prevent improvement claims even with an execution mode override. Different hashes are necessary provenance, not proof of causal independence. An extraction comparison can revise our historical assessment, but cannot improve the historical execution. Cost deltas are suppressed for extraction comparisons.

To reassess a hypothesis, supply `compare --reassessment reviews.json` with an array:

```json
[{
  "finding": "F-existing-id",
  "status": "contradicted",
  "reason": "The newly attributed image returns establish inspection previously reported as missing.",
  "recommendedAction": "Preserve the inspection receipt and investigate the remaining product failures.",
  "evidence": [{"eventId": "e42", "excerpt": "exact recorded excerpt"}]
}]
```

Allowed statuses: strengthened, weakened, contradicted, unchanged, unassessable. These are explicitly attributed analyst judgments, not inferred from citation counts. Every judgment needs exact evidence verified against the after-run snapshot or a cited JSON artifact. Unknown/duplicate finding IDs, missing rationale, and mismatched excerpts fail. The saved comparison preserves the prior/new finding and proposed recommendation; it does not rewrite historical diagnoses. Review the evidence semantics yourself: verifying an excerpt does not verify an interpretation. Use artifact citations for aggregate inspection receipts. Do not reassess claims absent from the baseline as if they were recorded findings.

## Context experiments versus product repairs

New experiments should explicitly set `--type context-engineering`, `product-repair`, or `instrumentation`. Legacy/untyped experiments remain `unspecified`; never infer a context-engineering success from their names or outcome alone.

Context experiments additionally require `--contract contract.json`:

```json
{
  "contextIntervention": "Correct the entry-point pointer to applicable menu guidance.",
  "expectedBehavior": "Retrieve that guidance before choosing the menu implementation.",
  "acceptanceCheck": "Keep the existing click, Escape and focus-return browser assertions unchanged."
}
```

Register the chain before making the intervention. Bind the after-run through `--experiment` and `--actual-change`; supply independently measured mechanism, behavior and outcome citations. Acceptance must not merely assert that the new guidance was read. A passing mechanism with failing behavior or acceptance is not a successful context experiment. This contract describes intended measurements; the CLI checks its presence and assessment provenance, not whether arbitrary prose/tests truly establish causation.

Product repairs may demonstrate scoped product acceptance improvement, but cannot support a context-engineering claim. Instrumentation changes measure observability, not product quality. For an old untyped experiment only, `compare --experiment-type product-repair` adds a classification to the new comparison without altering the old record. Classifying a legacy context experiment also requires `--contract`; the comparison marks this as retrospective, not preregistered. Typed experiments cannot be reclassified by this override.

The CLI remains backward compatible with unspecified experiments, but only an explicitly typed context experiment with a complete chain and passing comparative assessments can set `contextEngineeringImprovement`. Retrospective classifications remain qualified and do not become preregistered experiments.

Diagnosis version 4 prints per-detector eligibility, blocked prerequisites, exclusions and the smallest next evidence request. See [coverage explanations](diagnostics.md#coverage-explanations-and-blind-spots). Saved records retain exact gap citations and unsupported-wrapper warnings. A zero finding count is never substituted for sufficient telemetry.
