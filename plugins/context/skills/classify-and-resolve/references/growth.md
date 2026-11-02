# Growth

Load this before moving a pipeline to a new stage, adding, splitting, merging or retiring a class, changing a rule or threshold, or when an anti-pattern is suspected. The stage table (entry criterion and allowed change) is in SKILL.md; this file holds what each stage leaves behind, the taxonomy feedback loop, the anti-patterns, and a walkthrough from no pipeline through Stage 1. Field names are in [model.md](model.md); resolver autonomy is in [resolvers.md](resolvers.md).

## Stage gates

A stage is left only when its exit evidence exists. Autonomy never rises without a passed gate, and no stage is skipped.

| Stage | Artifacts it leaves | Evidence to leave it |
|---|---|---|
| 0 Manual | A KOS scheme with 3 to 5 defined classes; a pipeline with one `human` step, every resolver `manual`, an `unclassified_route`; a JSONL log of every decision | The log shows one class with a high-volume signal a rule can state without exceptions |
| 1 Rules | A `rule` step first in the cascade, written as CNL statements that abstain on anything else, then any `observed` step that reads real data; a suite from `logs_to_cases.py`, run on every rule change | Rules and observed evidence leave a large abstained remainder, and the suite has `holdout` cases |
| 2 Model | A `model` step backed by a `decision-questions` question set, bands tuned on `dev` cases only; a `rule_repair_route` for disagreements; resolvers may be `suggest` once the set reaches role `suggester` | A resolver's slice has enough cases for a gate's `min_n` |
| 3 Automate | A gate in `gates.yaml` per promoted resolver; `review_sample_rate` on `irreversible` + `auto` | Stays at 3; each further resolver promotes on its own gate |

Changes at any stage:

- **Rules.** A rule is added only with the log ids that show its signal, and only after the suite shows it fires on no case of another class. A rule that needs an exception is two rules or a model's job.
- **Thresholds.** `abstain_below` and a question set's bands are tuned on `dev` cases. A holdout run reports; it never tunes.
- **Disagreements.** Work the `rule_repair_route` queue before relabeling: a model that disagrees with a rule or observed step is first evidence that the rule misfires.
- **Versions.** Every class, route, cascade or resolver change bumps `Pipeline.version` and re-runs the suites for the affected classes in the same change. Log records carry `pipeline_version`, so a report can split before and after.

## Taxonomy feedback loop

The pipeline grows its own label set. Unclassified items and misroutes are the evidence; `knowledge-organization-system` decides the change.

1. Run `unclassified_report.py` on the window's logs. `--min-items` is N, the evidence a new class needs (default 3; raise it for high-volume queues).
2. Read the candidates and the corrections table, and propose one of:
   - **New class:** N or more unclassified items share a shape (one candidate group). Write its definition from the items, not from the resolver you want to send them to.
   - **Split:** one class's corrections show two populations, for example `billing → refund` and `billing → pricing` both recurring. Split the concept (two narrower concepts or two new ones and a deprecation) and route each.
   - **Merge:** the corrections show the classifier confusing two classes back and forth, and their resolvers produce equivalent outputs. Deprecate one with `replacedBy` the other.
   - **Definition or rule fix:** the items fit an existing class (the report flags candidates that match a concept). Fix the definition or the rule; the label set stays.
3. Hand the proposal to `knowledge-organization-system`, which applies its own growth rules and validator.
4. In the same change: route each new class, bump `Pipeline.version`, run `validate_pipeline.py` (it fails with `unrouted-class` until the route exists), work the backlog items with `corrected_label`, and re-run the affected suites.
5. Retire on evidence too: an `idle-class` warning over several windows is a merge or deprecation candidate. Deprecate, never delete, so old logs still resolve.

## Anti-patterns

| Anti-pattern | How to spot it | Fix |
|---|---|---|
| An `other` bucket that is silently dropped | A class named `other` or `misc` routed to an auto-closing or archiving resolver; no `unclassified` records in the logs | Route abstentions to a human or deferred queue (`unclassified_route`) and report on them. |
| Classes defined by resolver convenience | Definitions that name a team ("things the payments team handles"); a class whose items share no meaning | Define classes by what the item is; let routing map meaning to handler. |
| One giant model step | A cascade with a single `model` step whose question set never abstains (`no-fallthrough`) | Put deterministic rules and observed evidence first, give the question set a review band, end with a human or unclassified. |
| Automating irreversible actions without sampling | `irreversible` + `auto` with no `review_sample_rate` (`autonomy-matrix`) | Add sample review, or stay at `suggest`. |
| Routing tables that duplicate taxonomy | Classes listed in the pipeline when a vocabulary exists; route keys written as labels | Keep classes in the KOS scheme and route by concept id; inline `classes` only when no vocabulary exists. |
| Tuning thresholds on production without a holdout | `abstain_below` or a question set's bands changed after looking at live traffic or holdout results | Tune on `dev`; read holdout once per decision. |
| Classifier changes shipped without re-running evaluations | A rule, threshold or definition change with no suite run in the same change | Run the suites for the affected classes before the change lands. |

## Examples across domains

### Software support or incident triage: one resolver reaches Stage 3

The support pipeline has run rules and a model for months. The `stuck-worker` class has 640 logged cases, and the restart runbook has sat at `suggest` with corrections logged. Gate `stuck-worker-autonomy` (slice `stuck-worker`, threshold 0.98, `min_n` 200) passes, so the runbook alone moves to `auto`. The outage resolver stays `manual`; it has no gate.

### Document intake for a policy or legal corpus: a split

Corrections show `contract → nda` six times and `contract → order-form` five times in a quarter. `knowledge-organization-system` adds `nda` and `order-form` as narrower concepts of `contract`; the pipeline routes both, bumps its version, and re-runs the contract suite, whose cases now expect the narrower ids.

### Agent routing: a merge

The router keeps confusing `data-question` and `analytics-request`, and both specialist agents return the same kind of query result. The corrections table shows the pair in both directions. `analytics-request` is deprecated with `replacedBy: data-question`; its route is removed in the same change, and `validate_pipeline.py` would report `unresolved-route` had it stayed.

## Walkthrough: a support inbox from no pipeline to Stage 1

Three people answer a support inbox, each sorting tickets their own way; refunds wait while outages sit in the general queue. The files below are the skill's sample fixtures (`fixtures/sample-vocabulary.yaml`, `fixtures/sample-pipeline.yaml`, `fixtures/sample-log.jsonl`) under project paths. A real queue counts the same signals over hundreds of items; this one has 15.

### Before: no pipeline

```text
inbox (no classes, no log)
```

Items of more than one kind arrive and are handled inconsistently: the Stage 0 entry criterion holds.

### Stage 0: seed a scheme, a manual pipeline and a log

```text
triage/vocabulary.yaml      # from templates/scheme.yaml; 3 classes, validated by knowledge-organization-system
triage/pipeline.yaml        # from templates/pipeline.yaml
triage/gates.yaml           # evaluation-system's empty registry
triage/logs/2026-10.jsonl   # one Classification and one Resolution per ticket
```

```diff
--- /dev/null
+++ triage/pipeline.yaml
+id: support-triage
+version: 1
+scheme: support
+cascade:
+  - classifier_id: triage-lead
+    kind: human
+routes:
+  billing: billing-desk
+  outage: on-call
+  account-access: access-desk
+unclassified_route: triage-backlog
+resolvers:
+  - {id: billing-desk, accepts: [billing], output_type: a reply and, when owed, a refund request, side_effects: none, autonomy: manual}
+  # on-call, access-desk and triage-backlog alike: side_effects none, autonomy manual
```

The triage lead logs every ticket. A ticket that fits no class is logged `unclassified` with a rationale tag:

```json
{"log_id": "l-019", "at": "2026-10-10T09:00:00Z", "pipeline_id": "support-triage", "pipeline_version": 1, "record": "classification", "item_id": "i-010", "item": {"id": "i-010", "source": "support-inbox", "payload": {"subject": "How do I export all invoices as CSV?", "body": "Our accountant needs a year of invoices."}, "received_at": "2026-10-10T08:55:00Z"}, "label": "unclassified", "level": "exact", "confidence": null, "rationale": "#data-export no class fits a data export request", "evidence": [], "classifier_id": "triage-lead", "cascade_step": 0}
```

After two weeks the log holds 30 records. The validator, given the log, flags the share:

```bash
python3 scripts/validate_pipeline.py triage/pipeline.yaml --vocabulary triage/vocabulary.yaml --gates triage/gates.yaml --log triage/logs/2026-10.jsonl --today 2026-10-31
# WARNING unclassified-share support-triage unclassified_route: 6 of 15 items (0.40) ended unclassified, above 0.2. Fix: run unclassified_report.py and propose the missing classes to knowledge-organization-system.
# triage/pipeline.yaml: 0 error(s), 1 warning(s), inferred stage 0
```

### The KOS change the unclassified report drives

```bash
python3 scripts/unclassified_report.py triage/logs/2026-10.jsonl --pipeline triage/pipeline.yaml --vocabulary triage/vocabulary.yaml --out triage/unclassified-2026-10.md
```

```text
### 1. `data-export` (4 items, rationale tag `data-export`)

- Evidence: i-010 (l-019), i-011 (l-021), i-012 (l-023), i-013 (l-025)
- Shared keywords: export (4), data (3), accountant (1), auditors (1), bulk (1)
- Examples: "How do I export all invoices as CSV?"; "Full data export for our auditors"; "Monthly export of usage data"

## Corrections

| From | To | Items |
|---|---|---|
| billing | account-access | i-004 (l-008) |
| unclassified | billing | i-015 (l-030) |
```

Four items share a shape, so a new class meets N = 3. The corrections are single pairs, so no split or merge yet; `#feedback` (i-014) stays ungrouped. The proposal goes to `knowledge-organization-system`, which adds the concept with a definition written from the items:

```diff
--- a/triage/vocabulary.yaml
+++ b/triage/vocabulary.yaml
@@ concepts:
+  - id: data-export
+    prefLabel: data export
+    definition: A ticket asking for the customer's own records delivered as a file, once or on a schedule.
+    scopeNote: Excludes a broken export button, which is an outage.
+    scheme: support
+    evidence: [logs/2026-10.jsonl l-019, l-021, l-023, l-025, unclassified-2026-10.md]
```

With only the vocabulary changed, the pipeline no longer validates:

```text
ERROR unrouted-class support-triage:data-export routes: class 'data-export' in scheme 'support' has no route. Fix: route it to exactly one resolver, or deprecate the concept through knowledge-organization-system.
```

The route, a new manual resolver and the version bump ship in the same change:

```diff
--- a/triage/pipeline.yaml
+++ b/triage/pipeline.yaml
-version: 1
+version: 2
@@ routes:
   account-access: access-desk
+  data-export: export-desk
@@ resolvers:
+  - id: export-desk
+    accepts: [data-export]
+    output_type: an export file sent to the customer
+    side_effects: none
+    autonomy: manual
```

The triage lead works the four deferred items and logs each one's class:

```json
{"log_id": "l-031", "at": "2026-10-20T10:00:00Z", "pipeline_id": "support-triage", "pipeline_version": 2, "record": "resolution", "item_id": "i-010", "resolver_id": "triage-backlog", "status": "escalated", "output": {"rerouted_to": "export-desk"}, "decided_by": "human", "corrected_label": "data-export"}
```

`validate_kos.py triage/vocabulary.yaml` and `validate_pipeline.py` both report 0 errors.

### Stage 1: a rule step and a suite from the logs

Billing tickets carry an unambiguous signal in their subjects: the Stage 1 entry criterion holds for one class. First, turn the log into a suite:

```bash
python3 scripts/logs_to_cases.py triage/logs/2026-10.jsonl --pipeline triage/pipeline.yaml --out triage/evals/classification.suite.yaml
# 14 case(s), 2 in holdout; left out: 1 unclassified
python3 <evaluation-system>/scripts/validate_suite.py triage/evals/classification.suite.yaml --vocabulary triage/vocabulary.yaml
# triage/evals/classification.suite.yaml: 0 error(s), 0 warning(s), inferred stage 2
```

The four backlog items are now cases expecting `data-export`, each with `added_because` naming its correction (`l-031` to `l-034`); `case-i-004` and `case-i-013` are in holdout by hash. Draft the rule, run it on `dev` through a small adapter (`triage/evals/billing_rule.py` reads `{subject, body}` and prints `{"label": "billing"}` or `{"label": "unclassified"}`), and read the failing rows. Rows that say `got "unclassified"` are the abstentions the human step handles; a row that says `got "billing"` is the rule firing on another class:

```text
| case-i-010 | label-match | expected "data-export", got "billing" |
```

"invoice" catches "export all invoices". The rule that ships drops it:

```diff
--- a/triage/pipeline.yaml
+++ b/triage/pipeline.yaml
-version: 2
+version: 3
 cascade:
+  - classifier_id: billing-keywords
+    kind: rule
+    rules:
+      - If the subject contains "refund", "charged" or "VAT", then the class is billing.
   - classifier_id: triage-lead
     kind: human
```

The rerun has no `got "billing"` row outside the billing slice; `validate_pipeline.py` reports 0 errors and infers stage 1. From here every rule or definition change reruns this suite in the same change, and new logs are converted on each window. The pipeline stays at Stage 1 until the rules leave a large remainder and the suite has enough holdout cases for a model step (Stage 2).
