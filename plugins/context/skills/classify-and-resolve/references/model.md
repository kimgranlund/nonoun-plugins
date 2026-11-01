# Pipeline model

Load this when you write or change a pipeline file or a log writer, add an entity-resolution stage, read a validator message, or turn logs into cases or a report. It is the authority for the typed spine, cascade semantics, the entity-resolution stage, the pipeline and log file shapes, and the rules of the three scripts. Resolver contracts and the autonomy matrix are in [resolvers.md](resolvers.md); stages, the taxonomy feedback loop and anti-patterns are in [growth.md](growth.md).

Peer schemas are read by their own field names and never redefined here: concepts (`id`, `prefLabel`, `altLabel`, `hiddenLabel`, `scheme`, `deprecated`, `replacedBy`, `broader`, `narrower`) belong to the `knowledge-organization-system` skill's `references/model.md`; Case, Suite and Gate (`gates.yaml`) to the `evaluation-system` skill's `references/model.md`; rule statements to the `controlled-natural-language` skill's `references/patterns.md`.

## Typed spine (stable contract)

The field names below are published as stable. Logs, pipeline files and the scripts read and write them by these exact names. Rename or remove a field only with a versioned change to every consumer.

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

Three optional fields extend the spine in the pipeline file: `classes` on a Pipeline (the fallback when no vocabulary exists), `rules` on a `rule` cascade step and `policy` on a Resolver (both lists of `controlled-natural-language` statements). Any other key is a `schema` error, so a typo such as `abstainBelow` cannot silently drop a threshold.

| Type | Field | Meaning |
|---|---|---|
| Item | `id`, `source`, `payload`, `received_at` | One thing to classify: where it came from, what the classifier saw, when it arrived. |
| Classification | `label` | A concept id from the pipeline's scheme, or the reserved value `unclassified`. |
| | `confidence` | 0 to 1, or `null` for a human or a rule that states none. |
| | `rationale` | Why the step chose or abstained. A `#tag` token in it is a rationale tag that `unclassified_report.py` groups by. |
| | `evidence` | What the decision rests on: a rule id, a span, a matched label. |
| | `classifier_id`, `cascade_step` | Which classifier decided, and its index in `Pipeline.cascade`. |
| EntityMatch | `mention`, `concept_id`, `matched_via` | A span of the item mapped to a canonical concept, and the label kind that matched. |
| Resolution | `status` | `resolved`, `escalated` (sent on), `deferred` (queued for later) or `rejected` (refused as not this resolver's). |
| | `decided_by` | `resolver` when it acted alone, `human` when a person decided or approved. |
| | `corrected_label` | The misroute signal: the class the item should have had. It turns logs into evaluation cases and KOS evidence. |
| Pipeline | `version` | Bump it on every class, route, cascade or resolver change. |
| | `scheme` | The KOS scheme whose active concepts are the classes. |
| | `routes` | Each class id to exactly one resolver id. Fan-out happens inside a resolver. |
| | `unclassified_route` | The resolver that receives abstentions: a human or deferred queue, never a discard. |

## The reserved label `unclassified`

`unclassified` is an outcome, not a class. It is never a concept in the scheme, never a key in `routes`, and is routed only by `unclassified_route`. An item stays unclassified until a human gives it a `corrected_label`. Unclassified items with no correction are taxonomy evidence: `unclassified_report.py` reads them, and `logs_to_cases.py` leaves them out, since no class is known to be right for them.

## Cascade semantics

The cascade runs in order. Each step sees only the items every earlier step abstained on.

| Kind | Abstains when | `abstain_below` |
|---|---|---|
| `rule` | No rule fires. Rules are CNL statements such as "If the subject contains 'refund', then the class is billing." | Optional; a rule step usually states no confidence. |
| `model` | Its confidence is below `abstain_below`. | Required in practice. Missing or 0 means the step never abstains. Tune it on `dev` cases only. |
| `human` | The person chooses `unclassified`. | Not used. |

An item the final step abstains on gets the label `unclassified` and goes to `unclassified_route`. The final step is therefore a `human` step, or a step that can abstain: a `rule` step, or a `model` step with `abstain_below` above 0. A final model that never abstains is `no-fallthrough`, the "one giant model step" anti-pattern in validator form.

Log every step's Classification, including abstentions (`label: unclassified`), with its `cascade_step`. The item's class is the label of its last Classification. Log the Item once, in the `item` field of its first Classification, so the logs can become cases.

## Entity-resolution stage (optional)

Between classify and dispatch, a pipeline may map mentions in the item (a party, a clause, a product) to canonical concepts, so a resolver receives ids instead of strings. It delegates to KOS label matching and never builds its own synonym list:

- A mention matching a concept's `prefLabel` or `altLabel` resolves, with `matched_via` naming which.
- A mention matching a `hiddenLabel`, or any label of a deprecated concept, resolves with `matched_via: hiddenLabel`, to the concept itself or to the deprecated concept's `replacedBy`. The flag tells the resolver the source used a retired form.
- Matching follows the KOS rule: case-insensitive, whitespace collapsed, whole word, a trailing `s` or `es` allowed. A mention that matches nothing stays unresolved and is never guessed; a repeated unresolved mention is evidence for a new `altLabel`, which `knowledge-organization-system` decides.

Write each match as an EntityMatch record in the resolver's input. Entity resolution never changes the item's class.

## Pipeline file

One YAML file per pipeline, usually next to the vocabulary; start from `templates/pipeline.yaml`. A file may hold several YAML documents; each is one pipeline, validated on its own. Required: `id`, `version`, `scheme`, `cascade`, `routes`, `resolvers`; `unclassified_route` has its own rule. Each step needs `classifier_id` and `kind`; each resolver needs `id`, `accepts`, `output_type`, `side_effects` and `autonomy` ([resolvers.md](resolvers.md)).

Without a vocabulary, list the classes inline: `classes: [{id, definition}]`, with a one-line definition each. The validator then reports `peer-absent`, and route keys are checked only against that list.

## Log format

JSONL, one record per line, shaped by `templates/log.schema.json`. Every record carries an envelope, `{log_id, at, pipeline_id, pipeline_version, record, item_id}`, where `record` is `classification` or `resolution` and the rest of the record is that spine type's fields. `log_id` is unique across the log; `at` starts with a `YYYY-MM-DD` date. The scripts check every record and reject a log with any malformed one, naming the file and line.

## Validator

`python3 scripts/validate_pipeline.py PIPELINE [PIPELINE ...] [--vocabulary FILE] [--gates FILE] [--log FILE ...] [--window-days N] [--max-unclassified-share X] [--today YYYY-MM-DD] [--strict]`

- `--vocabulary`: the `knowledge-organization-system` vocabulary. The classes are the active concepts whose `scheme` is the pipeline's `scheme`.
- `--gates`: the `evaluation-system` gate registry. A gate's `status` there is read as recorded; this skill never computes a metric.
- `--log`: JSONL logs, which enable the three volume warnings over the last `--window-days` (default 30) ending `--today`. `--max-unclassified-share` defaults to 0.2.

Each finding is one line, `SEVERITY RULE SUBJECT FIELD: problem. Fix: fix.`, sorted errors first, then by rule and subject. The subject is `<pipeline id>` or `<pipeline id>:<class, resolver or step>`. The last line counts errors and warnings and prints the inferred stage: 3 when a resolver sits above the matrix's free cells, 2 with a `model` step or a `suggest` resolver, 1 with a `rule` step, else 0. Exit 0 with no errors, 1 with errors (or warnings under `--strict`), 2 when an input file cannot be read.

| Rule | Severity | Fires when | Usual fix |
|---|---|---|---|
| `schema` | error | A file is not YAML, a key is unknown, a required field is missing or mistyped, an enum value is unknown, the scheme is not in the vocabulary, `unclassified` is a route key, or a log record breaks the log schema. | Correct the shape against the tables above. |
| `unrouted-class` | error | An active class in the scheme has no route. | Route it to one resolver, or deprecate the concept through KOS. |
| `unknown-resolver` | error | A route or `unclassified_route` names an undeclared resolver. | Declare it, or correct the id. |
| `unresolved-route` | error | A route key is not a concept id in the scheme, or is deprecated. | Use the concept id, or the `replacedBy` concept. |
| `missing-unclassified-route` | error | The pipeline has no `unclassified_route`. | Route abstentions to a manual human or deferred queue. |
| `auto-unclassified` | error | `unclassified_route` leads to a resolver with `autonomy: auto`. | Send unclassified items to a resolver a human works. |
| `no-fallthrough` | error | The final cascade step is a `model` that never abstains. | End with a `human` step, or set `abstain_below` above 0. |
| `autonomy-matrix` | error | A resolver sits in a matrix cell without a `promotion_gate`, or is irreversible and `auto` without `review_sample_rate` above 0. | Lower the autonomy, or add what the cell requires. |
| `unknown-gate` | error | A `promotion_gate` is not in the gate registry. | Add the gate through `evaluation-system`, or correct the id. |
| `gate-not-passed` | error | A resolver above the free cells names a gate whose status is not `passed` (or no registry was given). | Keep it at `manual` until the gate passes. |
| `abstain-range` | error | `abstain_below` is outside [0, 1]. | Write a confidence between 0 and 1. |
| `idle-class` | warning | With `--log`: a class has no items in the window. | A retirement candidate: merge or deprecate it through KOS. |
| `unclassified-share` | warning | With `--log`: more than the threshold share of items ended unclassified. | Run `unclassified_report.py` and propose classes. |
| `unreviewed-suggest` | warning | With `--log`: a `suggest` resolver has no correction in the window. | Check that someone reviews its suggestions and logs `corrected_label`. |
| `peer-absent` | warning | No vocabulary was given, or resolvers name gates and no registry was given. | Pass the peer file, or accept the lost guarantee knowingly. |

`fixtures/broken-pipeline.yaml`, with `fixtures/broken-vocabulary.yaml` and `fixtures/broken-gates.yaml`, trips every error rule except `schema` once. Its two documents exist because a missing `unclassified_route` and an `auto` one cannot share a pipeline.

The validator does not compare a class definition's history with suite runs. "A definition changed without re-running its evaluation suite" is enforced by the procedure in [growth.md](growth.md): the definition change, the `version` bump and the suite run ship in one change.

## Logs to cases

`python3 scripts/logs_to_cases.py LOG [LOG ...] --pipeline FILE [--suite-id ID] [--suite-version V] [--holdout-percent N] [--out FILE]`

It writes an `evaluation-system` suite with one `exact` grader (`label-match`, field `label`) and one slice per class. An item becomes a case only when a human settled its class:

1. A Resolution with `corrected_label`: that label, and that record's `log_id`.
2. Otherwise a final Classification from a `human` cascade step: its label and `log_id`.
3. Otherwise a Resolution with `decided_by: human` that did not reject the item: the final label, and that Resolution's `log_id`.

Each case has `input` (the logged Item's `payload`), `expected` (the concept id), `tags: [concept id]`, `source: production`, `added_because` (the deciding log id), `added_at` and `split`: `holdout` when `sha256(item id) mod 100` is below `--holdout-percent` (default 20), else `dev`, so an item never changes split as the log grows. Items settled as `unclassified`, never settled by a human, or logged without an Item are left out and counted on stderr. Validate the suite with `evaluation-system`'s `validate_suite.py --vocabulary`.

## Unclassified report

`python3 scripts/unclassified_report.py LOG [LOG ...] --pipeline FILE [--vocabulary FILE] [--min-items N] [--out FILE]`

It reads items whose last label is `unclassified` with no correction and groups them, greedily and deterministically (largest group first, ties by name), first by rationale tag, then the rest by a shared keyword (four letters or more, common words left out) from the payload and rationale. A group needs `--min-items` items (default 3). Each candidate concept lists its evidence item and log ids, shared keywords, examples, and a proposed KOS entry whose definition the proposer writes. With `--vocabulary`, a candidate whose name matches an existing concept is reported as a definition or rule gap instead. Two more sections list corrections as `from → to` pairs and the items no group took. The output is Markdown for a KOS change proposal.

## Worked examples

### Software support or incident triage

```yaml
id: support-triage
version: 4
scheme: support
cascade:
  - classifier_id: keyword-rules
    kind: rule
    rules:
      - If the subject contains "invoice" or "refund", then the class is billing.
      - If the alert source is the status monitor, then the class is outage.
  - classifier_id: triage-lead
    kind: human
routes: {billing: billing-desk, outage: on-call, account-access: access-desk}
unclassified_route: triage-backlog
```

An alert from the status monitor stops at step 0 with `label: outage, cascade_step: 0, evidence: [rule-2]`. A ticket saying "can't log in after the outage" fires no rule, reaches the triage lead, and is logged twice: an abstention at step 0 and `account-access` at step 1.

### Document intake for a policy or legal corpus

The scheme `contracts` holds `nda`, `msa` and `amendment` from the legal team's vocabulary. After classification, an entity-resolution stage maps "ACME Corp." to the party concept `acme` (`matched_via: altLabel`) and "the Data Processing Addendum" to `dpa` (`matched_via: prefLabel`). A draft citing "Schedule B", a `hiddenLabel` of the retired concept that `dpa` replaced, resolves to `dpa` with `matched_via: hiddenLabel`, and the filing resolver adds a note asking for current wording.

### Agent routing

A router classifies user requests into `code-change`, `data-question` and `incident-help`; each resolver is a specialist subagent whose contract states what it accepts and what it may touch. The router's model step has `abstain_below: 0.7`; below it the request goes to `human-dispatch`, the `unclassified_route`, where a person picks a specialist and logs `corrected_label` whenever the router's guess was wrong. This is one runtime among many: the same spine fits a queue worker, a spreadsheet macro or a person with a checklist.
