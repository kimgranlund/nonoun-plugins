# Build the `classify-and-resolve` Agent Skill

> **Build order:** this is the fourth of four skills.
> `knowledge-organization-system` → `controlled-natural-language` → `evaluation-system` → `classify-and-resolve`.
> This skill consumes all three peers' schemas and never redefines them.

## Goal

Author an Agent Skill that helps coding agents design and grow **classify-and-resolve workflows**. Incoming items get a class from a closed set and are dispatched to a resolver with a declared contract. Examples:

- ticket triage
- incident routing
- document intake
- review queues
- intent routing to specialist agents
- inbox processing
- corpus cleanup

The skill produces a typed pipeline spec plus a runtime-agnostic scaffold. It does not lock to any queue, framework or agent runtime.

It must activate on its own when an agent is asked to sort, triage, route, or dispatch items by type. It must let a team start with a handful of classes and fully manual resolution, then grow toward automation only as measured evidence allows. The pipeline is also the growth engine for its own taxonomy: unclassified items and misroutes are the evidence that drives KOS changes.

## Background the skill must encode

**Topology.** There are three stages: classify → (optional) resolve entities → dispatch to resolver.

**Classification is a cascade.** Each step sees only what the previous step abstained on:

1. deterministic rules
2. cheap model
3. expensive model
4. human

**Abstention is a first-class outcome.** Every pipeline has an `unclassified` route, and it is never silently dropped.

**Two meanings of "resolve."** This skill uses "resolve" to mean dispatch to a handler. Entity resolution (mapping a mention to a canonical concept) is an optional stage that delegates to KOS label matching:

- `prefLabel` and `altLabel` resolve
- `hiddenLabel` resolves with a flag

**Resolvers have contracts.** Each resolver declares:

- the classes it accepts
- its output type
- its `side_effects` (`none`, `reversible` or `irreversible`)
- its `autonomy` (`manual`, `suggest` or `auto`)

The `side_effects` × `autonomy` matrix is where the guardrails live.

**Limiting factors the skill must name:**

- label-set quality (mutually exclusive, clearly defined, with an explicit catch-all)
- the low-confidence policy
- whether misroutes feed back into the design

Classifier sophistication is rarely the bottleneck.

**Relationships to peer skills:**

- **`knowledge-organization-system`.** The label set is a KOS concept scheme. Every class is a concept id, and hierarchical classes use `broader`/`narrower`. Hand off whenever a class is added, split, merged, renamed or redefined.
- **`controlled-natural-language`.** Classification rules and resolver policies are CNL statements, for example "If `<condition>`, then the class is `<concept>`". Hand off whenever criteria or policies are written or reviewed.
- **`evaluation-system`.**
  - Classification and Resolution logs convert into evaluation Cases.
  - Every autonomy promotion is guarded by a gate in `gates.yaml`.
  - This skill reads gate statuses and never computes quality metrics itself.
  - Hand off whenever the question is "is this good enough?"
- **Fallback if peers are absent.** Classes may be an inline list with one-line definitions. Rules may be plain if/then sentences. Autonomy stays at `manual`/`suggest`, because no gate can pass. The validator states which guarantees are missing.

## Typed spine

Publish this as the stable contract in `references/model.md`.

```yaml
Item:           { id, source, payload, received_at }
Classification: { item_id, label: <concept_id> | "unclassified", confidence, rationale,
                  evidence[], classifier_id, cascade_step }
EntityMatch:    { item_id, mention, concept_id, matched_via: prefLabel|altLabel|hiddenLabel }
Resolver:       { id, accepts: [concept_id], output_type, side_effects: none|reversible|irreversible,
                  autonomy: manual|suggest|auto, promotion_gate?: <gate_id>, review_sample_rate? }
Resolution:     { item_id, resolver_id, status: resolved|escalated|deferred|rejected,
                  output, decided_by: resolver|human, corrected_label? }
Pipeline:       { id, version, scheme: <kos_scheme>, cascade[]: { classifier_id, kind: rule|model|human,
                  abstain_below }, routes: { concept_id → resolver_id }, unclassified_route: resolver_id }
```

`corrected_label` on a Resolution is the misroute signal. It is what turns the logs into evaluation cases and KOS evidence.

## Autonomy matrix

| side_effects | manual | suggest | auto |
|---|---|---|---|
| none | allowed | allowed | requires passed `promotion_gate` |
| reversible | allowed | allowed | requires passed `promotion_gate` |
| irreversible | allowed | requires passed `promotion_gate` | requires passed `promotion_gate` **and** `review_sample_rate` > 0 |

The default for every new resolver is `manual`.

## Deliverables

```
skills/classify-and-resolve/
  SKILL.md                                # ≤300 lines: when to use, topology, 0→1 procedure, guardrails
  references/model.md                     # typed spine, cascade semantics, entity-resolution stage
  references/resolvers.md                 # resolver contracts, autonomy matrix, escalation design
  references/growth.md                    # stage gates, taxonomy feedback loop, anti-patterns
  templates/pipeline.yaml                 # Stage 0 starter: 3 classes + unclassified, manual resolvers
  templates/log.schema.json               # JSONL record schema for Classification + Resolution
  fixtures/broken-pipeline.yaml           # one violation per validator rule
  evals/trigger-activation.suite.yaml     # in evaluation-system format
  scripts/validate_pipeline.py
  scripts/logs_to_cases.py
  scripts/unclassified_report.py
```

Use progressive disclosure. SKILL.md holds only what an agent needs on every invocation, and detail goes in `references/`. No content is duplicated across files.

## Frontmatter and triggers

`name: classify-and-resolve`

The `description` field drives activation, so write it as concrete triggers.

**Trigger on:**

- triage, routing, dispatch, intake
- "sort these into…", "route each X to…", "categorize and handle"
- ticket or incident or request queues
- intent classification
- router agents and specialist agents
- inbox or document processing workflows
- "handle different kinds of X differently"
- escalation paths
- human-in-the-loop review queues

**Do not trigger on:**

- a one-off categorization of a few items in chat
- pure taxonomy design with no handling (hand off to `knowledge-organization-system`)
- pure evaluation questions (hand off to `evaluation-system`)
- general workflow orchestration with no classification step

## 0→1 stages (core requirement)

Every stage defines entry criteria, allowed artifacts and a promotion gate. Agents never skip a stage, and autonomy never increases without a passed gate.

| Stage | Entry criterion | Allowed change |
|---|---|---|
| 0 — Manual | Items of more than one kind arrive and are handled inconsistently | KOS seed scheme with 3–5 classes + `unclassified`; one `human` cascade step; all resolvers `manual`; every decision logged in the JSONL format |
| 1 — Rules | ≥1 class has a high-volume, unambiguous signal in the logs | Deterministic `rule` step first in the cascade, written as CNL statements, abstaining on anything else; logs feed a Stage 0–1 evaluation suite via `logs_to_cases.py` |
| 2 — Model | Rules leave a large abstained remainder and the evaluation suite has holdout cases | `model` cascade step with `abstain_below` tuned on dev only; resolvers may move to `suggest` |
| 3 — Automate | A resolver's `promotion_gate` passes | That resolver alone moves along the autonomy matrix; other classes are unaffected |

### Taxonomy feedback loop

`unclassified_report.py` groups unclassified items by classifier-supplied rationale tags and keywords. It uses the standard library only, with no ML. It emits candidate concepts with evidence item ids. These candidates feed the KOS growth rules:

- **New class.** Add one when ≥N unclassified items share a shape (N is configurable).
- **Split a class.** Split when one resolver's corrections show two distinct populations.
- **Merge classes.** Merge when the classifier confuses two classes and their resolvers produce equivalent outputs.

Every class change bumps `Pipeline.version` and re-runs the affected evaluation suites.

## Rules

- **Closed set, explicit catch-all.** Every pipeline has exactly one `unclassified_route`, and it must lead to a human or deferred queue, never to discard.
- **One class, one resolver.** Every class in the scheme routes to exactly one resolver. Fan-out happens inside a resolver, not in the routing table.
- **Abstain over guess.** A classifier below `abstain_below` passes the item to the next step. The final step is always `human` or `unclassified`.
- **Log everything.** Every Classification and Resolution is written in the log schema. A pipeline without logs cannot reach Stage 1.
- **Evidence before automation.** Autonomy follows the matrix. Gates live in `evaluation-system` and are never re-implemented here.
- **Drift is a defect.** Routes reference KOS ids. A deprecated concept still routed is an error. A class definition changed without re-running its evaluation suite is an error.
- **Anti-patterns to name explicitly:**
  - an `other` bucket that is silently dropped
  - classes defined by resolver convenience rather than meaning
  - one giant model step with no rules or abstention
  - automating irreversible actions without sampling
  - routing tables that duplicate taxonomy
  - tuning thresholds on production without a holdout
  - classifier changes shipped without re-running evaluations

## Contracts (fail loudly)

**`validate_pipeline.py`**

- Uses the standard library plus PyYAML. Output is deterministic. Exits non-zero on any error, so it is usable in CI.
- **Errors:**
  - a class in the scheme with no route
  - a route to an unknown resolver
  - a route key that fails to resolve in the KOS vocabulary, or that is deprecated
  - a missing `unclassified_route`
  - an `unclassified_route` leading to a resolver with `autonomy: auto`
  - a cascade whose final step is not `human` and has no `unclassified` fallthrough
  - any resolver violating the autonomy matrix
  - a `promotion_gate` id missing from `gates.yaml`
  - a promoted resolver whose gate status is not `passed`
  - `abstain_below` outside [0, 1]
- **Warnings:**
  - a class with no log volume over a configured window (a retirement candidate)
  - `unclassified` share above a configured threshold
  - a resolver at `suggest` with no corrections recorded (possibly unreviewed)

**`logs_to_cases.py`**

- Converts JSONL logs to evaluation Cases with `source: production`.
- Sets `expected` from `corrected_label` when present, or else from human-decided labels.
- Sets `added_because` to the log id.
- Assigns the split deterministically by hashing the item id.

**`unclassified_report.py`**

- Produces deterministic candidate groups, each with evidence ids.
- Output is Markdown suitable for a KOS change proposal.

## Domain coverage

`references/model.md`, `references/resolvers.md` and `references/growth.md` include worked examples from three domains:

1. **Software support or incident triage.** Resolvers are a mix of runbooks and humans.
2. **Document intake for a policy or legal corpus.** Classes come from a KOS scheme, with entity resolution to canonical parties and clauses.
3. **Agent routing.** A router dispatches to specialist subagents as resolvers. This is one example only, not the default runtime.

Nothing in SKILL.md may assume a specific runtime or software-only work.

## Process

1. Read the `knowledge-organization-system`, `controlled-natural-language` and `evaluation-system` schemas, and use their field names exactly.
2. Before writing files, output a one-page spec covering:
   - the typed spine
   - the autonomy matrix
   - the stage gates
   - the log schema
   - trigger and non-trigger lists
   - assumptions
   
   Then proceed. Stop for approval only if an assumption is irreversible.
3. Build from the center outward, in this order:
   1. the typed spine and `templates/log.schema.json`
   2. `validate_pipeline.py` with `fixtures/broken-pipeline.yaml`
   3. `templates/pipeline.yaml`
   4. `logs_to_cases.py` and `unclassified_report.py` against a small sample log
   5. the references
   6. SKILL.md

## Definition of done

- `validate_pipeline.py` passes on `templates/pipeline.yaml` against the KOS template vocabulary and an empty `gates.yaml`. It fails on `fixtures/broken-pipeline.yaml` with one clear message per rule.
- `logs_to_cases.py` turns a 30-record sample log into a suite that passes `validate_suite.py`.
- `unclassified_report.py` on the same log produces at least one candidate concept with evidence ids.
- `evals/trigger-activation.suite.yaml` has 10 prompts that should activate the skill and 5 that should not, and it validates.
- A documented walkthrough goes from no pipeline through Stage 0 and Stage 1. It shows the exact files and diffs, including one KOS change driven by the unclassified report.
- SKILL.md is ≤300 lines.

## Out of scope

- queue or broker integration
- hosted workflow engines
- ML model training
- clustering beyond deterministic grouping
- a UI for review queues
