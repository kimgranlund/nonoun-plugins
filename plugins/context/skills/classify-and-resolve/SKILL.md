---
name: classify-and-resolve
description: >
  Design and grow classify-and-resolve workflows: incoming items get a class from a closed set,
  with an explicit unclassified route, and go to a resolver with a declared contract, through a
  cascade of rules, observed evidence, decision models and humans, an autonomy matrix guarded by evaluation gates, and a
  taxonomy feedback loop, with a pipeline validator, a log-to-cases converter and an
  unclassified report. Use for triage, routing, dispatch and intake; "sort these into", "route each X to",
  "categorize and handle", "handle different kinds of X differently"; ticket, incident or request
  queues; intent classification; router agents and specialist agents; inbox or document
  processing; escalation paths; human-in-the-loop review queues; corpus cleanup by type; and
  before letting a resolver act on its own. Not for a one-off categorization of a
  few items in chat, pure taxonomy design with no handling (knowledge-organization-system), pure
  evaluation questions (evaluation-system), or workflow orchestration with no classification step.
---

# Classify and Resolve

Give every incoming item a class from a closed set, then hand it to the one resolver that handles that class, with a contract that says what the resolver may do on its own. Items can be anything that arrives in a stream: requests, reports, documents, messages, alerts, records to clean up. Start with a handful of classes and people doing all the work; automate a class only when measured evidence allows it.

## Topology

Three stages, in order:

1. **Classify.** A cascade of five kinds of step, in order: deterministic `rule` steps (every known convention), `observed` steps (what real data says: usage in shipped code, historical decisions), a decision model and then any expensive model (`model` steps, each a `decision-questions` question set), then a `human` step. Each step sees only what the previous steps abstained on.
2. **Resolve entities** (optional). Map mentions in the item to canonical concepts by `knowledge-organization-system` label matching: `prefLabel` and `altLabel` resolve, a `hiddenLabel` resolves with a flag.
3. **Dispatch.** Each class routes to exactly one resolver. Fan-out happens inside a resolver, never in the routing table.

"Resolve" in this skill means dispatch to a handler; mapping a mention to a concept is entity resolution.

**Abstention is a first-class outcome.** A step that is not sure passes the item on. An item no step classifies gets the reserved label `unclassified` and goes to the `unclassified_route`: a human or deferred queue, never a discard.

Three limiting factors matter more than classifier sophistication. Name them when they apply:

- **Label-set quality:** classes are mutually exclusive, clearly defined, and backed by an explicit catch-all.
- **Low-confidence policy:** what happens below the threshold is written down, and ends with a person.
- **Feedback:** misroutes (`corrected_label`) and unclassified items flow back into the label set and the evaluation cases.

## Hand-offs

- **knowledge-organization-system** owns the label set. The classes are the active concepts of one KOS scheme, referenced by concept id; hierarchical classes use `broader` and `narrower`. Hand off whenever a class is added, split, merged, renamed or redefined, then come back to update routes.
- **controlled-natural-language** owns how rules and policies are phrased. Classification rules ("If `<condition>`, then the class is `<concept>`.") and resolver policies are CNL statements. Hand off when criteria or policies are written or reviewed.
- **decision-questions** owns every `model` step's question: the question set's shape, decision mode, bands, pinned model and role, and the DecisionModel adapter contract. A model step names its set by `question_set`. Hand off whenever a model question is written, tuned or promoted.
- **evaluation-system** owns "is this good enough?". Logs convert into its Cases; every autonomy promotion is guarded by a gate in its `gates.yaml`; this skill reads gate statuses and never computes a quality metric. Hand off whenever the question is whether a classifier or resolver is good enough.
- **Without the peers**, classes may be an inline list with one-line definitions and rules plain if/then sentences. Autonomy then stays at `manual` or `suggest`, because no gate can pass, and the validator reports which guarantees are missing (`peer-absent`).

## The model

An **Item** arrives. Each cascade step writes a **Classification** (a concept id or `unclassified`, its `level` (`exact` or `broader`), confidence, typed `evidence` (`rule`, `observed` or `answer`), an optional rationale, its step and, for a model, its `model_version`). An optional **EntityMatch** maps a mention to a concept. A **Resolver** declares its contract: the classes it `accepts`, its `output_type`, its `side_effects` (`none`, `reversible`, `irreversible`) and its `autonomy` (`manual`, `suggest`, `auto`), plus a `promotion_gate` and `review_sample_rate` where the matrix requires them. A **Resolution** records the outcome (`resolved`, `escalated`, `deferred`, `rejected`), who decided, and a `corrected_label` when the item was misrouted. A **Pipeline** ties them together: a scheme, a cascade, a `fallback` (`unclassified` or `broader`), routes, the unclassified route and a `rule_repair_route` for disagreements.

These field names are a stable contract. Start from `templates/pipeline.yaml` and `templates/scheme.yaml`, and log in the shape of `templates/log.schema.json`. Field tables, cascade semantics, the entity-resolution stage, the log format and the script rules are in [references/model.md](references/model.md).

## Guardrails

- Every new resolver starts at `manual`.
- `suggest` is free unless side effects are `irreversible`; `auto` always needs a passed `promotion_gate`; `irreversible` + `auto` also needs `review_sample_rate` above 0. The full autonomy matrix and escalation design are in [references/resolvers.md](references/resolvers.md).
- Promotion is per resolver: one class moving to `auto` changes nothing for the others.
- Judge `side_effects` by the worst thing the resolver can do.

## Stages

Every change happens at one stage. Never skip a stage, and never raise autonomy without a passed gate.

| Stage | Entry criterion | Allowed change |
|---|---|---|
| 0 Manual | Items of more than one kind arrive and are handled inconsistently | KOS seed scheme with 3 to 5 classes plus `unclassified`; one `human` cascade step; all resolvers `manual`; every decision logged in the JSONL format |
| 1 Rules | At least one class has a high-volume, unambiguous signal in the logs | A deterministic `rule` step first in the cascade, written as CNL statements, abstaining on anything else; logs feed an evaluation suite via `logs_to_cases.py` |
| 2 Model | Rules and observed evidence leave a large abstained remainder, and the evaluation suite has holdout cases | A `model` step backed by a `decision-questions` question set, bands tuned on dev only. Resolvers may move to `suggest` only once that question set reaches role `suggester` |
| 3 Automate | A resolver's `promotion_gate` passes | That resolver alone moves along the autonomy matrix; other classes are unaffected |

What each stage leaves behind, the taxonomy feedback loop and the anti-patterns are in [references/growth.md](references/growth.md), which ends with a walkthrough from no pipeline through Stage 1, including a KOS change driven by the unclassified report.

## Procedure

1. **Name the items and the handling.** What arrives, from where, and what different kinds need different handling. If nothing is handled differently, there is no pipeline to build: hand pure taxonomy work to `knowledge-organization-system`.
2. **Find what exists.** Look for a pipeline file, a vocabulary, a gates registry and logs. Run `validate_pipeline.py` on what exists, with `--log` when logs exist.
3. **Name the evidence.** For a new class: the items that share its shape. For a rule: the log ids that show its signal. For a promotion: the gate and its recorded status. No evidence, no change: say what evidence would justify it and stop.
4. **Pick the stage** whose entry criterion the evidence meets. Make only the change that stage allows.
5. **Seed (Stage 0).** Copy `templates/scheme.yaml` (or reuse the project's vocabulary through `knowledge-organization-system`) with 3 to 5 classes defined by meaning, not by who handles them. Copy `templates/pipeline.yaml`: one `human` step, a `manual` resolver per class, the `unclassified_route` to a human queue. Log every Classification and Resolution from the first item, with `#tag` rationale tags on unclassified items.
6. **Grow.** Each window, run `validate_pipeline.py --log`, then `unclassified_report.py`, and take any candidate class to `knowledge-organization-system`. Route the new class, bump `version`, and correct the backlog in the same change. Add a rule step (Stage 1) only for a signal the logs show, and check it with the suite from `logs_to_cases.py` before it ships.
7. **Promote.** A resolver moves along the matrix only when `evaluation-system` records its gate as passed. Demote without a gate when a gate fails or a sample review finds harm.
8. **Report** the pipeline id and version, the stage, the classes and their routes, each resolver's side effects, autonomy and gate status, the unclassified share, candidate classes with their evidence ids, and what evidence the next stage needs.

When you only review a design and no pipeline exists, still apply the topology: ask for the closed class list, the catch-all, the low-confidence policy, each resolver's side effects and the gate behind any `auto`.

## Rules

- **Closed set, explicit catch-all.** Exactly one `unclassified_route`, leading to a human or deferred queue, never to discard.
- **One class, one resolver.** Every class in the scheme routes to exactly one resolver.
- **Abstain over guess.** A step below its `abstain_below`, or below its question set's review band, passes the item on. The final step is `human`, or can abstain to `unclassified`.
- **Broader before unclassified.** With `fallback: broader` and a hierarchical scheme, a low-confidence item gets its `broader` concept (`level: broader`) when that concept has a route, before it falls to `unclassified`.
- **Disagreement repairs rules first.** When a model step disagrees with a rule or observed step on an item, the item goes to `rule_repair_route` as a candidate rule bug, as well as to normal review.
- **Hard cases stay human.** A model step acts on hard or disputed items only when its question set has role `voter`, which is rarely earned.
- **Log everything.** Every Classification and Resolution is written in the log schema. A pipeline without logs cannot reach Stage 1.
- **Evidence before automation.** Autonomy follows the matrix. Gates live in `evaluation-system` and are never re-implemented here.
- **Drift is a defect.** Routes reference KOS concept ids. A deprecated concept still routed is an error. A class definition changed without re-running its evaluation suite is an error: the definition, the version bump and the suite run ship together.

Anti-patterns to name when you see them:

- an `other` bucket that is silently dropped
- classes defined by resolver convenience rather than meaning
- one giant model step with no rules or abstention
- automating irreversible actions without sampling
- routing tables that duplicate taxonomy
- tuning thresholds on production without a holdout
- classifier changes shipped without re-running evaluations

How to spot and fix each is in [references/growth.md](references/growth.md).

## Scripts

Standard library plus PyYAML, Python 3.9 or later. Output is deterministic.

```bash
python3 scripts/validate_pipeline.py PIPELINE [PIPELINE ...] [--vocabulary FILE] [--gates FILE] [--question-set FILE ...] [--log FILE ...] [--strict]
python3 scripts/logs_to_cases.py LOG [LOG ...] --pipeline FILE [--holdout-percent N] [--out FILE]
python3 scripts/unclassified_report.py LOG [LOG ...] --pipeline FILE [--vocabulary FILE] [--min-items N] [--out FILE]
```

- The validator exits 1 on any error, so it can run in CI. Errors: `unrouted-class`, `unknown-resolver`, `unresolved-route` (unknown or deprecated concept), `missing-unclassified-route`, `auto-unclassified`, `no-fallthrough`, `autonomy-matrix`, `unknown-gate`, `gate-not-passed`, `abstain-range`, `model-question-set` (missing, or failing `decision-questions`' `validate_questions.py`, which it runs by path), `question-set-role`, `broader-fallback`, `missing-rule-repair-route`, and `schema`. Warnings with `--log`: `idle-class`, `unclassified-share`, `unreviewed-suggest`; and `peer-absent`.
- `logs_to_cases.py` writes an `evaluation-system` suite of `production` cases: `expected` from `corrected_label` or a human decision, `added_because` the log id, the split by a hash of the item id. Validate it with that skill's `validate_suite.py`.
- `unclassified_report.py` groups unclassified items by rationale tag, then shared keyword, and writes Markdown candidates with evidence ids for a KOS change proposal.

Options and rule details are in [references/model.md](references/model.md).

## Out of scope

Queue or broker integration; hosted workflow engines; model training; clustering beyond deterministic grouping; review UIs.

## References

- [references/model.md](references/model.md): load when writing or changing a pipeline file or a log writer, adding entity resolution, or reading a script's output.
- [references/resolvers.md](references/resolvers.md): load when adding a resolver, changing autonomy, naming a promotion gate or designing escalation.
- [references/growth.md](references/growth.md): load before changing stage, adding, splitting, merging or retiring a class, changing a rule or threshold, or when an anti-pattern is suspected. It ends with the Stage 0 to Stage 1 walkthrough.
- `evals/trigger-activation.suite.yaml`: this skill's own trigger suite; rerun it when the description or scope changes.
