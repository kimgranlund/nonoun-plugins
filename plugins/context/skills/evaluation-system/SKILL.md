---
name: evaluation-system
description: >
  Decide whether something is good enough using evidence: case sets, graders, metrics and
  gates for prompts, agents, classifiers and resolvers, a skill's triggering, a linter's
  precision, generated artifacts or human review processes, grown in evidence-gated stages
  with a suite validator and a runner. Use for evals, evaluation, test sets, gold sets,
  golden examples, benchmarks, regression tests for prompts or agents, "does this work",
  "is this good enough to ship", precision and recall, accuracy, confusion matrices,
  LLM-as-judge and rubric grading, A/B comparison of prompts or models, promotion gates,
  quality bars and acceptance thresholds, and before claiming a change works or promoting
  something to more autonomy. Not for ordinary unit tests of deterministic code,
  performance or load benchmarking, or casual "looks good" reviews.
---

# Evaluation System

Decide whether something is good enough, with evidence a second person can check. The "something" can be a prompt, an agent, a classifier or resolver, a skill's triggering, a linter's precision, any generated artifact, or a process people carry out. Start with a handful of hand-written cases and grow into sampled, gated evaluation only as evidence demands.

## The five parts

Call something an evaluation only when all five exist. If one is missing, say which, and build that part before quoting any number.

1. **Target.** The behavior under test, stated as a spec (`target_spec`), as `controlled-natural-language` statements where a rule set exists.
2. **Case set.** Inputs with expected outcomes, each traceable to the evidence that produced it (`added_because`).
3. **Grader.** Decides pass, fail or a score for each case: `exact`, `programmatic`, `reference`, `rubric-model` or `human`.
4. **Metric.** `pass_rate` per slice, always reported with `n` and a Wilson interval.
5. **Gate.** Threshold, minimum `n`, action and owner. A metric with no gate is a dashboard, not an evaluation.

Three limiting factors matter more than the choice of metric. Name them when they apply:

- **Gold-set quality:** label noise in `expected` makes correct outputs fail, and gold nobody can trace to a decider cannot be weighed. Every case records its `basis`.
- **Grader validity:** a `rubric-model` or `reference` grader is trusted only after its agreement with human judgment is measured.
- **Distribution match:** a case set that has drifted from live inputs passes tests that no longer matter. Drift is a defect.

## Hand-offs

- **knowledge-organization-system** owns what a label means. Expected labels, tags and slice keys are concept ids from its `vocabulary.yaml`. When a dispute is about what a label means or which label to use, hand it off, then come back.
- **controlled-natural-language** owns how a statement is phrased. Target specs and rubric criteria are CNL statements. When a criterion has two readings or a vague word, hand it off.
- **decision-questions** consumes this skill: it declares which cases a question set needs (invariance, negation and balanced cases, tagged by basis) and reads per-question gate outcomes before any role promotion. The dependency is one-way: a `rubric-model` grader reaches a decision model only through its command adapter (the `DecisionModel` contract), and this skill never imports that skill's schemas.
- **classify-and-resolve** consumes this skill: its logs become cases, it names the gates that guard each autonomy promotion, and it reads gate outcomes. This skill owns the Case, Grader, Suite, Run and Gate schemas; consumers never redefine them.
- **Without the peers**, labels may be plain strings and criteria plain sentences. The validator warns (`peer-absent`) that those guarantees are lost.

## The model

A **suite** holds the target's name and spec, its cases, graders and slices. A **case** has an `input`, an `expected` outcome, a `source` (`production`, `synthetic`, `adversarial`, `regression`), a `basis` (who decided `expected`: `owner`, `judgment`, `convention`, `agent`), a `kind` (`standard`, `invariance`, `negation`, the last two with `variant_of`), `added_because`, `tags`, a `split` (`dev` or `holdout`) and, when it leaves, `status: retired` with a reason. A **grader** has a `kind`, a `config` and, for a judge, `validated_against` (human set, agreement, n, date). A **run** records every case result, the per-slice metrics with coverage and accuracy per direction, results by basis, and calibration when the target returns confidence. A **gate** reads one slice's `pass_rate`, optionally narrowed to one `question_id` and a `basis` list, pins a `pinned_target_version`, and returns `passed`, `failed`, `insufficient_n`, `stale` or `open`.

These field names are a stable contract. Start from `templates/suite.yaml`, `templates/gates.yaml` and `templates/LESSONS.md`. Field tables, the target adapter protocol, the validator and runner rules, and worked examples from three domains are in [references/model.md](references/model.md).

## Stages

Every change happens at one stage. Never skip a stage, and never build structure for a decision nobody has to make yet.

| Stage | Entry criterion | Allowed change |
|---|---|---|
| 0 Seed | A target exists and at least one real failure or expected behavior is known | One suite, 10 to 20 hand-written cases, each with `added_because`; one `exact` or `programmatic` grader; run by hand |
| 1 Regression | The Stage 0 suite runs green | Run on every change to the target. Every newly found failure becomes a `regression` case in the same change as its fix |
| 2 Measure | 50 or more cases, or a decision now depends on the result | Dev and holdout split; per-slice metrics with intervals; `rubric-model` graders only after `validated_against` is recorded |
| 3 Gate | A real decision (a release, an autonomy promotion, an audit submission) needs an automated answer | Gates in `gates.yaml`; production sampling into the case set; a drift check of case tags against live traffic |

Allowed artifacts, the gate to leave each stage, the case lifecycle and the anti-patterns are in [references/growth.md](references/growth.md), which ends with a walkthrough from no evaluation through Stage 0 and Stage 1 for a prompt.

## Procedure

1. **Name the claim and the decision.** What is about to be claimed ("the new prompt handles refunds", "the classifier can route billing alone", "the checklist catches retention breaches") and what action depends on it. No decision yet means no gate yet.
2. **Find the suite.** Look for a suite for this target (often `evals/<target>/suite.yaml`) and a `gates.yaml`. Run the validator on what exists.
3. **Name the evidence.** For a new suite: the real failure or expected behavior that starts it. For a new case: its `added_because`. For a new stage: the entry criterion it meets. No evidence, no change: say what evidence would justify it and stop.
4. **Pick the stage** whose entry criterion the evidence meets. Make only the change that stage allows.
5. **Seed (Stage 0).** Copy `templates/suite.yaml`. Write the target spec, 10 to 20 cases from known failures and the spec, and one `exact` or `programmatic` grader. Wrap the target in an adapter that reads one input as JSON on stdin and writes JSON on stdout.
6. **Run.** Run the validator, then the runner. Read every slice with its `n` and interval; report counts ("7 of 10"), not bare percentages.
7. **Fix and grow.** Fix the target, not the cases. Each new failure becomes a `regression` case in the same change as its fix. Move up a stage only when its entry criterion holds.
8. **Report** the target and version, the suite id and version, the stage, each slice's n, value, interval and coverage (per direction for propositions), each gate's status with its owner, cases added or retired with their evidence, the `LESSONS.md` rows written, and what evidence the next stage needs.

When you only review a claim and no suite exists, still apply the five parts: ask for the cases behind the claim, the grader, the n and the decision it drives. Offer Stage 0 when the user names a real failure or expected behavior.

## Rules

- **Evidence before cases.** Every case states `added_because`: a bug link, a log id, a spec clause. Synthetic cases are allowed but never make up a whole suite.
- **No metric without a decision.** Every Stage 3 metric is read by a gate; anything else is a dashboard.
- **Small n honesty.** Below `min_n` a gate reports `insufficient_n`, never pass. Reports show counts beside rates and an interval for every rate.
- **Holdout is sacred.** Tune prompts, rules and thresholds on `dev` only. Holdout runs are logged so overuse shows.
- **Graders earn trust.** A `rubric-model` or `reference` grader without `validated_against` cannot back a gate. Rubric criteria are checked one at a time.
- **Gold has provenance.** Every case states `basis`. Judgment gates exclude `convention` cases (rule-derived gold once inflated measured accuracy from 37% to 68%). Reports show `owner` cases as their own slice, because agent-approved gold inherits agent biases.
- **Gate the question, not the model.** Per-question accuracy on one model can range from 50% to 100%, so a gate may name a `question_id`.
- **Score both directions.** Proposition suites hold true and false cases plus `negation` variants, and accuracy is reported per direction. A question right on 95% of positives and half of negatives fails its gate.
- **Coverage beside accuracy.** Any metric over abstaining or banded answers reports `coverage`, the share answered; a gate may set `min_coverage`.
- **Calibration is measured.** A gate that relies on confidence bands needs `calibration` (per-band accuracy and ECE, on dev) in its latest run.
- **Invariance cases.** Choice-based targets include option-order permutations (`kind: invariance`); a changed answer is a failure.
- **Version changes stale the gates.** A gate pins `pinned_target_version`. When the target's version moves (a model alias, a prompt revision), every gate on it is `stale` until it is re-run and re-pinned.
- **Retire, don't delete.** An obsolete case gets `status: retired` and a reason. Gates pin a suite version.
- **Keep a lessons ledger.** `LESSONS.md` holds each finding: the claim, the run ids, the numbers, and whether it holds. Findings that did not hold stay, marked; a finding measured on an older target version is marked `re-measure`.
- **Drift is a defect.** When the target spec changes, the affected cases change in the same commit. When live tags diverge from case tags past the limit, the run fails.

Anti-patterns to name when you see them:

- tuning on holdout
- dashboards without gates
- unvalidated LLM judges
- percentages on tiny samples
- all-synthetic suites
- cases nobody can explain
- one aggregate number hiding a failing slice

How to spot and fix each is in [references/growth.md](references/growth.md).

## Scripts

Standard library plus PyYAML, Python 3.9 or later. Output is deterministic, one finding per line with rule id, subject and fix.

```bash
python3 scripts/validate_suite.py SUITE [SUITE ...] [--gates FILE] [--vocabulary FILE] [--tune FILE] [--rules FILE] [--target-version V] [--runs PATH] [--strict]
python3 scripts/run_suite.py SUITE [--target CMD] [--target-version V] [--split dev|holdout|all] [--gates FILE] [--human-results FILE] [--traffic FILE] [--out DIR] [--strict]
```

- The validator exits 1 on any error, so it can run in CI. Errors: `duplicate-case-id`, `missing-evidence` (no `expected` or `added_because`), `unknown-grader`, `gate-reference` (a missing suite, metric or slice), `unvalidated-grader` (a judge without `validated_against` backing a gate), `holdout-in-tuning`, `unresolved-label` (an expected label missing from the vocabulary), `missing-variant` (an invariance or negation case without `variant_of`), `convention-in-judgment-gate`, `uncalibrated-gate` (a `min_coverage` gate whose latest run in `--runs` has no calibration), `stale-gate` (a `passed` gate pinned to a version other than `--target-version`), and `schema`. Warnings: `synthetic-majority`, `ungated-metric`, `retired-case-gated`, `stale-validation`, `peer-absent`, `missing-basis`, `convention-in-judgment-suite`.
- The runner sends each case's `input` to the target command as JSON on stdin and reads JSON from stdout, so any runtime fits behind a small adapter (`scripts/echo_target.py` is the trivial one). `human` graders read recorded outcomes from `--human-results`, so human-graded and trigger-activation suites run through the same pipeline. A target may return `confidence` (calibration) or `abstain: true` (coverage). It writes `run.json` and `report.md` with coverage, accuracy per direction, results by basis and calibration, refuses `--tune` with a holdout split, marks a gate `stale` when its `pinned_target_version` differs from `--target-version`, and exits 1 when a gate fails; `insufficient_n` and `stale` fail the run only with `--strict`.

Options and rule details are in [references/model.md](references/model.md).

## Out of scope

Hosted evaluation platforms; dashboards and UIs; statistical testing beyond proportion intervals and simple paired comparisons; load and performance benchmarking.

## References

- [references/model.md](references/model.md): load when writing or changing a suite, a gate registry or a run reader, wiring a target adapter, or reading a validator or runner message.
- [references/graders.md](references/graders.md): load when choosing or configuring a grader, writing rubric criteria, validating a judge against human judgment, or comparing two versions.
- [references/growth.md](references/growth.md): load before moving a suite to a new stage, adding, splitting or retiring cases, proposing a gate, or when an anti-pattern is suspected. It ends with the Stage 0 to Stage 1 walkthrough.
- `evals/trigger-activation.suite.yaml`: this skill's own trigger suite; rerun it when the description or scope changes.
