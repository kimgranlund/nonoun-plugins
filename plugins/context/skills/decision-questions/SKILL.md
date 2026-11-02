---
name: decision-questions
description: >
  Design bounded questions for a decision model and act on the answers safely: question shape,
  domain-scoped options with authored contrast, threshold bands for choices and scores, compare
  mode with a margin for yes/no propositions, joint labels assembled in code, and a checker,
  suggester, voter role ladder earned one question at a time behind evaluation gates, with a
  question compiler, a validator, an eval-case generator and a fixture adapter. Use when a model is
  asked to pick from a list, score on a rubric or answer yes/no and the result is branched on;
  decision models that return typed answers with probabilities; logprob-based classification;
  confidence thresholds, abstention, "when should the model's answer count"; guardrail checks,
  audit pre-screens, review suggestions; choosing among extracted candidates; LLM-as-judge
  question design. Not for open-ended generation, pipeline topology (classify-and-resolve), metric
  and gate mechanics (evaluation-system), or vendor API usage (the vendor's own skill).
---

# Decision Questions

Ask a model a bounded question, then let its answer count only as far as measured evidence allows. A decision model returns typed answers with probabilities rather than prose: a purpose-built decision model, a general model read through log probabilities, or a local classifier. Start with one question whose answers a person reads, and earn influence one question at a time.

## When a question is worth asking

Ask the model only where deterministic rules and observed data give no answer. Conventions become rules upstream, never notes in the instructions. If a rule or observed evidence (how an item is actually used, a field that already holds the answer) settles the item, use it and ask nothing.

## Hand-offs

- **knowledge-organization-system** supplies options. Option keys are concept ids; option text is the concept's `definition` and its authored `excludes`. A missing or confused option is a KOS change: hand off, then recompile.
- **controlled-natural-language** owns phrasing. Instructions and option text form its decision-question doc type: one proposition per statement, no negation, instructions aligned with options, boundary cases stated, no arithmetic or date comparison. `validate_questions.py` runs its linter.
- **evaluation-system** measures and gates. This skill declares the cases a question set needs and reads per-question gate status (`question_id`, `pinned_target_version`); it never computes a metric.
- **classify-and-resolve** consumes question sets as its cascade's model step.
- **The vendor's own skill** owns request and response fields, SDKs and limits. This skill hands off and never restates them.
- **Without the peers**, options may be inline strings with authored contrast, phrasing is checked by eye, and every question stays `checker`, because no gate can pass. The validator reports what was not checked (`peer-absent`).

## The model

A **QuestionSet** is one reviewable file: its questions, decisions, bands and margins, a pinned `model` version, a `shape` and a `role`. A **Question** is a `choice` over `options`, a `score` over ordered `levels`, or a yes/no `proposition`. An adapter implements **DecisionModel** `ask(state, questions)` and returns one **Answer** per question with probabilities. A **Decision** turns answers into an outcome (`act`, `review`, `defer`, `flag`).

Field tables, decision semantics, the adapter contract and the script rules are in [references/model.md](references/model.md).

## Decision modes

- **Threshold** for choices and scores. Confidence at or above `bands.act` fires the outcome; at or above `bands.review` it goes to review; below that it defers. Tune bands per question on dev cases.
- **Compare** for propositions. The proposition's value minus its `rival`'s fires the outcome at or above `margin`; a near-tie defers. Never threshold a raw proposition value.
- **Assemble** joint labels. Questions in one request cannot see each other. A decision that reads several questions names an `assemble` validator: code that enforces the label grammar.

## Shapes

| Shape | Use for |
|---|---|
| `single-choice` | One label from a small, domain-scoped set |
| `retrieve-then-choose` | A large set: rank candidates, then one Choice among the top k; report list hit rate and pick accuracy apart |
| `hierarchical-walk` | One Choice per hierarchy level; on low confidence return the broader concept |
| `per-value-propositions` | Multi-valued facets: one proposition per value, combined in code |
| `boundary-pair` | A boundary statement against its positive complement, in compare mode |
| `verify-against-rival` | "This item means X" against the same statement for its nearest neighbors; audit flags |

Each shape's worked example and required eval cases are in [references/shapes.md](references/shapes.md).

## Roles

| Role | Its output may | Promotion requires |
|---|---|---|
| `checker` | Raise a flag for a human second look; never changes data | Default |
| `suggester` | Preselect an answer in a review UI; never approves | A passed per-question gate on owner-tier cases, at the band used for preselection |
| `voter` | Count as one vote among judges in a merge or tie-break | A passed gate showing it beats or adds information to existing judges on hard cases |

Roles never skip a step. Promote one question at a time, in its own question set. Acting without a person is never granted here; `classify-and-resolve`'s autonomy matrix grants it on top of a role.

## Stages

| Stage | Entry criterion | Allowed change |
|---|---|---|
| 0 One question | A bounded decision exists; rules and observed data do not answer it | One question set, one question, role `checker`; domain-scoped options; 10 to 20 cases including ambiguous ones; run by hand; answers logged, never acted on |
| 1 Measure | Stage 0 answers look useful on inspection | An evaluation suite with `basis` on every case, invariance cases and, for propositions, balanced both-direction cases; bands or margins tuned on dev; model pinned; contrast added as KOS `excludes` |
| 2 Suggest | That question's gate passes on owner-tier holdout | That question alone moves to `suggester` |
| 3 Vote | Evidence shows it beats or complements existing judges on hard cases | That question alone moves to `voter`. Many questions never earn this |

Stage gates, demotion, gates in `gates.yaml` and the walkthrough from "should we ask a model this?" through Stage 1 are in [references/growth.md](references/growth.md).

## Procedure

1. **Name the decision.** What the answer changes, who acts on it, and what happens when it is wrong. No branch on the answer means no question set.
2. **Check for evidence first.** Name the rules and observed data that already decide some items. Ask only about the rest.
3. **Find what exists.** A question set, a vocabulary, a gates registry, an eval suite, recorded answers. Run `validate_questions.py` on any question set.
4. **Pick the shape** from the table above and the stage whose entry criterion the evidence meets. Make only the change that stage allows.
5. **Seed (Stage 0).** Copy `templates/question-set.yaml` and `templates/seed-cases.yaml`. Compile options from the KOS scheme with `compile_questions.py` where a vocabulary exists. Pin `model`. Write the instructions as decision-question sentences with the boundary cases stated.
6. **Measure (Stage 1).** Generate the suite with `make_eval_cases.py`, run it through the adapter with `evaluation-system`'s `run_suite.py`, and read accuracy per direction, coverage and calibration. When two options are confused, author an `excludes` entry in KOS, recompile, and re-run against the previous version.
7. **Promote** one question only when its gate is recorded `passed` on the pinned model version. Demote when a gate fails or goes stale.
8. **Report** the question set id, version, pinned model, shape, role, each question's decision mode with its bands or margin, gate status per question, and the evidence the next stage needs.

## Rules

- **Domain-scoped options.** Offer the values the domain's concepts actually use, never the whole vocabulary. A `none` or general option carries concrete examples.
- **Authored contrast only.** Contrast comes from KOS `excludes`, written by hand after an observed confusion. Generated "not X" text does worse than none; the compiler refuses to write it.
- **Compute in code.** Counting, arithmetic, dates and numeric comparison happen in code. Ask the model for the parts, such as a Choice over months.
- **Large schemes.** Above about 12 options, use `retrieve-then-choose` or `hierarchical-walk`.
- **Pin and cache.** Cache by request hash plus model version. A version change re-asks and re-runs the gates.
- **Untrusted state.** State may be adversarial. A decision driven by untrusted state never goes past `suggester` for an irreversible action.
- **Disagreement routing.** When the model disagrees with a deterministic rule, the disagreement goes to a rule-repair queue first, the item queue second.
- **Per-question gates.** Accuracy varies from question to question on one model; a gate attaches to one question, and boundary suites are scored in both directions.

Anti-patterns to name when you see them:

- decomposing a joint label into independent questions and trusting the combination
- thresholding raw proposition values
- generated contrast text
- full-vocabulary option sets
- conventions passed as notes
- using the model as a tie-breaker without evidence
- judgment benchmarks built from rule-derived gold
- promoting a whole model instead of one question

How to spot and fix each is in [references/growth.md](references/growth.md). The evidence behind every rule, with how to re-measure it, is in [references/evidence.md](references/evidence.md).

## Scripts

Standard library plus PyYAML, Python 3.9 or later. Output is deterministic; every script exits non-zero on an error, so each can run in CI.

```bash
python3 scripts/validate_questions.py QUESTION_SET [...] [--gates FILE] [--vocabulary FILE] [--rules FILE] [--lint FILE] [--strict]
python3 scripts/compile_questions.py VOCABULARY --template FILE --shape single-choice|retrieve-then-choose [--scheme ID] [--concepts IDS] [--allow-none] [--run RUN_JSON] [--out FILE]
python3 scripts/make_eval_cases.py QUESTION_SET --seeds FILE [--holdout-percent N] [--permutations N] [--out FILE]
python3 adapters/fixture.py --recordings FILE --question-set FILE [--abstain-below review|act|none]
```

- The validator's errors: `threshold-on-proposition`, `compare-incomplete`, `unpinned-model`, `ungated-role`, `missing-question`, `missing-assemble`, `cnl`, and `schema`; warning `peer-absent`.
- The compiler copies KOS text verbatim and refuses a concept with no definition, too many single-choice options, a missing `none` option with examples, and duplicate keys.
- The case generator writes `evaluation-system` cases with `basis`, invariance and negation variants (`variant_of`) and balanced splits; validate it with that skill's `validate_suite.py`.
- The fixture adapter replays recorded answers as a `run_suite.py` target, so tests and demos run without network access or cost.

Options and rule details are in [references/model.md](references/model.md).

## Out of scope

Vendor SDKs and request formats; model training or fine-tuning; pipeline routing; metric computation.

## References

- [references/model.md](references/model.md): load when writing or changing a question set, an adapter or a decision, or reading a script's output.
- [references/shapes.md](references/shapes.md): load when picking a shape or listing the eval cases a shape needs.
- [references/evidence.md](references/evidence.md): load when a rule is questioned, when setting bands or margins, or when planning a measurement.
- [references/decision-models.md](references/decision-models.md): load when writing an adapter for a runtime.
- [references/growth.md](references/growth.md): load before changing stage or role, adding contrast, or when an anti-pattern is suspected. It ends with the Stage 0 to Stage 1 walkthrough.
- `evals/trigger-activation.suite.yaml`: this skill's own trigger suite; rerun it when the description or scope changes.
