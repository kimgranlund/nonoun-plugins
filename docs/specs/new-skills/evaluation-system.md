# Build the `evaluation-system` Agent Skill

> **Build order:** this is the third of five skills.
> `knowledge-organization-system` → `controlled-natural-language` → `evaluation-system` → `decision-questions` → `classify-and-resolve`.
> This skill reads the KOS vocabulary schema and the CNL rules schema, and never redefines either.

## Goal

Author an Agent Skill that helps coding agents decide **whether something is good enough, using evidence**. The "something" can be:

- a prompt
- an agent
- a classifier or resolver
- a skill's triggering
- a linter's precision
- any generated artifact

The skill governs case sets, graders, metrics and gates: the decisions a metric is allowed to drive.

It must activate on its own whenever an agent is about to claim that a change works, tune a prompt or model, or promote something to more autonomy. It must let a team start with a handful of hand-written cases and grow into production-sampled, gated evaluation only as evidence demands.

## Background the skill must encode

An evaluation has five parts. The skill refuses to call anything an evaluation unless all five exist.

1. **Target.** The behavior under test, stated as a spec. Where possible, write it as CNL statements.
2. **Case set.** Inputs with expected outcomes. Each case is traceable to the evidence that produced it.
3. **Grader.** Decides pass or fail, or a score, for each case. Grader kinds:
   - `exact`: equality
   - `programmatic`: a code assertion
   - `reference`: comparison to a gold output
   - `rubric-model`: a model applies a rubric
   - `human`
4. **Metric.** Aggregated per slice, always reported with `n` and an interval.
5. **Gate.** Threshold plus minimum `n` plus action plus owner. A metric with no gate is a dashboard, not an evaluation.

**Limiting factors the skill must name.** These matter more than metric choice:

- **Gold-set quality.** Label noise in expected outcomes.
- **Grader validity.** A `rubric-model` or `reference` grader is only trusted after its agreement with human judgment is measured.
- **Distribution match.** A case set that has drifted from production passes tests that no longer matter. Treat that drift as a defect.

**Relationships to peer skills:**

- **Uses `knowledge-organization-system`.** Expected labels, tags and slice keys are concept ids. When the problem is what a label means, hand off to KOS.
- **Uses `controlled-natural-language`.** Rubric criteria and target specs are CNL statements. When the problem is how a criterion is phrased, hand off to CNL.
- **Is consumed by `decision-questions`.**
  - That skill declares which cases a question set needs: invariance, negation and balanced cases, tagged by basis.
  - It reads per-question gate outcomes before any role promotion.
  - The dependency is one-way. This skill's `rubric-model` graders call a decision model only through the `DecisionModel` adapter contract, and never import that skill's schemas.
- **Is consumed by `classify-and-resolve`.**
  - That skill emits logs that become cases.
  - It declares which gates guard each autonomy promotion.
  - It reads gate outcomes.
  - This skill owns the Case, Grader, Suite, Run and Gate schemas. Consumers never redefine them.
- **Fallback if peers are absent.** Labels may be plain strings and rubric criteria plain sentences. The validator emits a warning, not an error, noting the lost guarantees.

## Typed spine

Publish this as the stable contract in `references/model.md`. Field names are frozen once published.

```yaml
Case:   { id, input, expected, tags[], source: production|synthetic|adversarial|regression,
          basis: owner|judgment|convention|agent,       # who or what decided `expected`
          kind: standard|invariance|negation,           # invariance = permuted options; negation = flipped proposition
          variant_of?: case_id,
          added_because, split: dev|holdout, added_at }
Grader: { id, kind: exact|programmatic|reference|rubric-model|human,
          config, validated_against?: { human_set, agreement, n, measured_at } }
Suite:  { id, version, target, target_spec, cases[] | cases_path, graders[], slices[] }
Run:    { id, suite_id, suite_version, target_version, started_at,
          results[]: { case_id, grader_id, outcome: pass|fail|score|abstain, detail },
          metrics: { slice → { value, n, interval, coverage } },
          calibration?: { bands: [{ range, n, accuracy }], ece } }
Gate:   { id, suite_id, question_id?, metric, slice, basis?: [owner|judgment|convention|agent],
          threshold, min_n, min_coverage?, pinned_target_version, action, owner,
          status: open|passed|failed|insufficient_n|stale }
```

## Deliverables

```
skills/evaluation-system/
  SKILL.md                                # ≤300 lines: when to use, five parts, 0→1 procedure, guardrails
  references/model.md                     # typed spine, field semantics, worked examples
  references/graders.md                   # grader kinds, when each is valid, human-agreement validation procedure
  references/growth.md                    # stage gates, case lifecycle, anti-patterns
  templates/suite.yaml                    # Stage 0 starter suite
  templates/gates.yaml                    # empty gate registry with one commented example
  templates/LESSONS.md                    # findings ledger: claim, experiment ids, numbers, status (holds | did not hold)
  fixtures/broken-suite.yaml              # one violation per validator rule
  evals/trigger-activation.suite.yaml     # this skill's own trigger suite (dogfooding)
  scripts/validate_suite.py
  scripts/run_suite.py
```

Use progressive disclosure. SKILL.md holds only what an agent needs on every invocation, and detail goes in `references/`. No content is duplicated across files.

## Frontmatter and triggers

`name: evaluation-system`

The `description` field drives activation, so write it as concrete triggers.

**Trigger on:**

- evals, evaluation, test set, gold set, golden examples
- benchmarks, regression tests for prompts or agents
- "does this prompt/agent/classifier work", "is this good enough to ship"
- precision/recall, accuracy, confusion matrix
- LLM-as-judge, rubric grading
- A/B comparison of prompts or models
- promotion gates, quality bars, acceptance thresholds

**Do not trigger on:**

- ordinary unit tests of deterministic code with no judgment involved
- performance or load benchmarking
- casual "looks good" reviews

## 0→1 stages (core requirement)

Every stage defines entry criteria, allowed artifacts and a promotion gate. Agents never skip a stage.

| Stage | Entry criterion | Allowed change |
|---|---|---|
| 0 — Seed | A target exists and at least one real failure or expected behavior is known | One suite, 10–20 hand-written cases, each with `added_because`; one `exact` or `programmatic` grader; run manually |
| 1 — Regression | Stage 0 suite runs green | Run in CI on every change to the target. Every newly found failure becomes a `regression` case in the same change as its fix |
| 2 — Measure | ≥50 cases, or a decision now depends on the result | Dev/holdout split; per-slice metrics with intervals; `rubric-model` graders allowed only after `validated_against` is recorded |
| 3 — Gate | A real decision (release, autonomy promotion) needs an automated answer | Gates in `gates.yaml`; production sampling into the case set; distribution drift check between case tags and live traffic |

## Rules

- **Evidence before cases.** Every case states `added_because`, for example a bug link, log id, or a spec clause. Synthetic cases are allowed but never make up a whole suite. The validator warns when synthetic exceeds 50% of a suite.
- **No metric without a decision.** Every Stage 3 metric is referenced by a gate. Unreferenced metrics are warnings.
- **Small n honesty.** Below `min_n`, a gate reports `insufficient_n`, never pass. Reports show counts alongside rates and give intervals for every rate (Wilson for proportions).
- **Holdout is sacred.** Prompts, rules and thresholds are tuned against `dev` only. The runner refuses `--split holdout` together with `--tune`. Holdout runs are logged so overuse is visible.
- **Graders earn trust.** A `rubric-model` or `reference` grader without `validated_against` cannot back a gate. Rubric criteria are CNL statements, so each criterion is checked separately.
- **Gold has provenance.** Every case states `basis`, meaning who or what decided `expected`.
  - Judgment gates exclude `convention` cases. In one project, rule-derived gold inflated measured accuracy from 37% to 68%.
  - Reports always show `owner`-tier results as their own slice, because agent-approved gold inherits agent biases.
  - The validator warns when a judgment suite contains convention cases.
- **Gate the question, not the model.** In the same project, per-question accuracy on the same model ranged from 50% to 100%, so gates may name a `question_id`.
- **Score both directions.** Proposition suites are balanced, with true and false cases plus `negation` variants, and accuracy is reported per direction. A question that is right on 95% of positives but only half of negatives must fail its gate.
- **Coverage is reported beside accuracy.** Any metric over abstaining or banded answers reports `coverage`, the share answered. Gates may set `min_coverage`.
- **Calibration is measured.** Any gate that relies on confidence bands requires `Run.calibration`: per-band accuracy and ECE, computed on dev.
- **Invariance cases.** Choice-based targets include option-order permutations (`kind: invariance`). A changed answer is a failure, because option-order bias is a documented failure mode.
- **Version changes stale the gates.** A gate pins `pinned_target_version`. When the target's version changes, for example when a model alias moves, every gate on it becomes `stale` until it is re-run.
- **Retire, don't delete.** Obsolete cases move to `status: retired` with a reason. Gates pin a suite version.
- **Keep a lessons ledger.** `LESSONS.md` is the human-readable companion to `run.json`. Each finding states:
  - the claim
  - the run or experiment ids that show it
  - the numbers
  - whether it holds
  
  Hypotheses that did not hold stay in the ledger, marked as such. A finding whose runs are older than the current pinned target version is marked for re-measurement.
- **Drift is a defect.** If the target spec changes, the affected cases change in the same commit. If production tags diverge from case tags beyond a configured threshold, the run fails.
- **Anti-patterns to name explicitly:**
  - tuning on holdout
  - dashboards without gates
  - unvalidated LLM judges
  - percentages on tiny samples
  - all-synthetic suites
  - cases nobody can explain
  - one aggregate number hiding a failing slice

## Contracts (fail loudly)

**`validate_suite.py`**

- Uses the standard library plus PyYAML. Output is deterministic. Exits non-zero on any error, so it is usable in CI.
- **Errors:**
  - duplicate case ids
  - a case missing `expected` or `added_because`
  - an unknown grader reference
  - a gate referencing a missing suite, metric or slice
  - a gate backed by an unvalidated `rubric-model`/`reference` grader
  - a case missing `basis`
  - a judgment gate whose slice includes `convention` cases
  - a gate relying on confidence bands with no calibration in its latest run
  - an `invariance` or `negation` case whose `variant_of` is missing
  - a `passed` gate whose `pinned_target_version` differs from the target's current version (it should be `stale`)
  - a holdout case referenced by tuning config
  - an expected label that fails to resolve in the KOS vocabulary (when one is configured)
- **Warnings:**
  - >50% synthetic cases
  - a metric with no gate at Stage 3
  - a retired case still referenced by a gate
  - stale `validated_against` (older than a configured age)

**`run_suite.py`**

- **Runtime-agnostic target adapter.** The target is a command that reads one case's `input` as JSON on stdin and writes its output as JSON on stdout.
- **Human grading.** `human` graders read recorded outcomes from a results file, so human-graded suites and trigger-activation suites still run through the same pipeline.
- **Outputs:** `run.json` (a typed Run) and `report.md` (per-slice table with n, value, interval, gate status).
- **Exit codes:** non-zero if any gate is `failed`. `insufficient_n` does not fail the run unless invoked with `--strict`.

## Domain coverage

`references/model.md` and `references/growth.md` include worked examples from three domains:

1. **Prompt or agent quality.** A support-reply prompt graded by a validated rubric.
2. **A classifier.** A triage classifier with per-class slices and an autonomy gate.
3. **A non-software corpus.** A policy or compliance review where the "target" is a human process and graders are `human`.

Nothing in SKILL.md may assume software-only work.

## Process

1. Read the `knowledge-organization-system` and `controlled-natural-language` schemas and use their field names exactly.
2. Before writing files, output a one-page spec covering:
   - the typed spine
   - the stage gates
   - the target adapter protocol
   - trigger and non-trigger lists
   - assumptions
   
   Then proceed. Stop for approval only if an assumption is irreversible.
3. Build from the center outward, in this order:
   1. the typed spine in `references/model.md`
   2. `validate_suite.py` with `fixtures/broken-suite.yaml`
   3. `run_suite.py` with `templates/suite.yaml` and a trivial echo target
   4. the remaining references
   5. SKILL.md
4. Retrofit the peers. Convert the KOS and CNL trigger-activation suites to this format if they were built before this skill.

## Definition of done

- `validate_suite.py` passes on the templates and on all three peer trigger-activation suites. It fails on `fixtures/broken-suite.yaml` with one clear message per rule.
- `run_suite.py` runs the template suite against an echo target and produces `run.json` and `report.md`, with intervals and gate statuses including one `insufficient_n`.
- `evals/trigger-activation.suite.yaml` has 10 prompts that should activate the skill and 5 that should not.
- A documented walkthrough goes from no evaluation to Stage 0 and Stage 1 for a prompt, showing the exact files and diffs at each step.
- SKILL.md is ≤300 lines.

## Out of scope

- hosted evaluation platforms
- dashboards and UIs
- statistical testing beyond proportion intervals and simple paired comparisons
- load and performance benchmarking
