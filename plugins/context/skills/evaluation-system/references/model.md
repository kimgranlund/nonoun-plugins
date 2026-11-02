# Evaluation model

Load this when you write or change a suite, a grader, a gate registry or a run reader, when a validator or runner message is unclear, or when another tool reads these files. It is the authority for the typed spine (Case, Grader, Suite, Run, Gate), field semantics, the target adapter protocol, the validator and runner rules, and worked examples. Grader kinds and their validation procedure are in [graders.md](graders.md); stages, case lifecycle and anti-patterns are in [growth.md](growth.md).

## Typed spine (stable contract)

The field names below are published as stable. `classify-and-resolve`, `decision-questions` and any other consumer read and write them by these exact names and never redefine them. Rename or remove a field only with a versioned change to every consumer. Fields marked optional and the extensions listed after the block were part of the first publication; `basis`, `kind`, `variant_of`, `coverage`, `directions`, `by_basis`, `calibration`, `question_id`, `min_coverage`, `pinned_target_version` and the `stale` status were added in the second.

```yaml
Case:   { id, input, expected, tags[], source: production|synthetic|adversarial|regression,
          basis: owner|judgment|convention|agent, kind?: standard|invariance|negation, variant_of?: case_id,
          added_because, split: dev|holdout, added_at, graders[]?, status?: active|retired, retired_reason? }
Grader: { id, kind: exact|programmatic|reference|rubric-model|human,
          config, validated_against?: { human_set, agreement, n, measured_at } }
Suite:  { id, version, target, target_spec, cases[] | cases_path, graders[], slices[] }
Run:    { id, suite_id, suite_version, target_version, started_at, split, tuning,
          results[]: { case_id, grader_id, outcome: pass|fail|score|abstain, detail },
          metrics: { slice → { value, n, interval, passes, coverage, directions? } },
          by_basis?, calibration?: { bands: [{ range, n, accuracy, confidence }], ece, n }, gates[], drift? }
Gate:   { id, suite_id, suite_version?, question_id?, metric, slice, basis?: [owner|judgment|convention|agent],
          threshold, min_n, min_coverage?, pinned_target_version, action, owner,
          status: open|passed|failed|insufficient_n|stale }
```

Any key not listed is a `schema` error, so a typo such as `addedBecause` cannot silently drop a field.

### Case

| Field | Type | Required | Meaning |
|---|---|---|---|
| `id` | string | yes | Stable within the suite; never reused, even after the case retires. |
| `input` | any JSON value | yes | What the target receives, exactly as the adapter writes it to stdin. |
| `expected` | any JSON value | yes | The outcome a grader compares against. A label is a string, `expected.label`, or each item of `expected.labels`; with a vocabulary, a label is a concept id, `prefLabel` or `altLabel`. |
| `tags` | list of strings | no | Slice keys and filters. With a vocabulary, write concept ids. |
| `source` | enum | yes | `production` (sampled from real use), `synthetic` (written or generated without a real occurrence), `adversarial` (written to break the target or probe a boundary), `regression` (a failure that was found and fixed). |
| `basis` | enum | warned when absent | Who or what decided `expected`: `owner` (the person accountable for the target), `judgment` (a reviewer's call on a case the rules do not settle), `convention` (derived from a written rule or format), `agent` (proposed or approved by a model). Missing, the validator warns (`missing-basis`); it stays a warning rather than an error while producers such as `classify-and-resolve`'s `logs_to_cases.py` do not write it. |
| `kind` | enum | no | `standard` (default), `invariance` (the same question with its options permuted; a changed answer fails), `negation` (the proposition flipped, so the expected answer flips). |
| `variant_of` | case id | with `invariance` or `negation` | The case this one permutes or negates. |
| `added_because` | string | yes | The evidence: a bug link, a log id, a spec clause, a review comment. A case nobody can explain is removed. |
| `split` | enum | no | `dev` (default) or `holdout`. Tune only on `dev`. |
| `added_at` | date | no | When the case entered the suite (`YYYY-MM-DD`). |
| `graders` | list of grader ids | no | The graders that apply to this case. Absent: every grader in the suite. |
| `status` | enum | no | `active` (default) or `retired`. A retired case is kept, never run, and never deleted. |
| `retired_reason` | string | with `retired` | Why it left: the spec clause that changed, the duplicate it was folded into. |

### Grader

| Field | Type | Required | Meaning |
|---|---|---|---|
| `id` | string | yes | Stable within the suite. |
| `kind` | enum | yes | `exact`, `programmatic`, `reference`, `rubric-model`, `human`. The `config` keys each kind reads are in [graders.md](graders.md). |
| `config` | mapping | no | Kind-specific settings. `programmatic` requires `command`; `rubric-model` requires `criteria`. |
| `validated_against` | mapping | no | The record of the grader's agreement with human judgment: `human_set` (where the human labels live), `agreement` (0 to 1), `n` (cases compared), `measured_at` (date). Required before a `rubric-model` or `reference` grader backs a gate. |

### Suite

| Field | Type | Required | Meaning |
|---|---|---|---|
| `id` | string | yes | Stable; gates and runs name it. |
| `version` | integer or string | yes | Bump it whenever a case or grader is added, retired or changed; gates may pin it. |
| `target` | string | yes | The name of what is under test (a prompt, an agent, a classifier, a review process). The command that runs it is given to the runner, so the suite stays runtime-agnostic. |
| `target_spec` | string or list of strings | yes | The behavior under test. Write it as `controlled-natural-language` statements when a rule set exists. |
| `cases` / `cases_path` | list / path | one of them | Inline cases, or a path relative to the suite file to a YAML list or a JSONL file of cases. |
| `graders` | list | yes, at least one | The graders. |
| `slices` | list | no | Named case subsets for metrics and gates. A string is a tag slice (its id is the tag). A mapping is `{id, tags: [...]}` (cases with any of the tags) or `{id, cases: [...]}` (named case ids). The slice `all` always exists. |

### Metric

One metric is defined: `pass_rate`, per slice. A case passes when every grader that applies to it passes; it fails when any of them fails; it abstains otherwise (a grader abstained, or a human grade is not recorded yet). Abstentions are left out of `n`. A `score` outcome counts as a pass when `detail.score` is at least the grader's `config.pass_at` (default 0.5). The value is `passes / n` with a 95% Wilson interval; at `n = 0` the value and interval are `null`.

Beside each value the runner reports `coverage`, the share of the slice's cases that were answered (`n` over the cases run), so abstaining or banded answers cannot raise accuracy unseen. A target abstains by writing `{"abstain": true}`.

A case's direction is the truth value it expects: `expected` itself when it is a boolean, or `expected.answer` when that is a boolean. When a slice holds directional cases, the runner reports `pass_rate` per direction (`directions.true`, `directions.false`) beside the overall value, so a question right on 95% of positives and half of negatives cannot hide behind the mean. Proposition suites are balanced: true and false cases, plus `negation` variants.

A slice is the unit a decision is made on. A metric that no gate references is a dashboard, which the validator warns about at Stage 3.

### Run

`run_suite.py` writes it as `run.json`. `split` is `dev`, `holdout` or `all`; `tuning` is true when the run fed a tuning step. `results` holds one entry per case and applicable grader; `detail` is text or a mapping (a `score` carries `detail.score`, a rubric result lists each criterion). `metrics` maps each slice id to `{value, n, interval: [low, high], passes, coverage}`, plus `directions` when the slice holds directional cases. `by_basis` appears when any case states a basis: the same measures per basis, always with an `owner` row, because agent-approved gold inherits agent biases. `calibration` appears when the target returned a `confidence`: dev cases only, ten equal-width bands, each `{range, n, accuracy, confidence}` (confidence is the band's mean), and `ece`, the expected calibration error (the n-weighted mean of the gap between accuracy and confidence). `gates` holds each gate for this suite with its computed `status`, `value`, `n`, `coverage`, `directions` and a `note`. `drift` appears when live traffic tags were supplied.

### Gate

A gate is a decision with its evidence bar. One registry file per project, usually `gates.yaml`, with a top-level `gates:` list; start from `templates/gates.yaml`.

| Field | Type | Required | Meaning |
|---|---|---|---|
| `id` | string | yes | Stable. |
| `suite_id` | string | yes | The suite it reads. |
| `suite_version` | integer or string | no | Pin a suite version. A run on another version leaves the gate `open`. |
| `question_id` | string | no | Gate one question, not the whole model: the gate reads only its slice's cases tagged with this id. Per-question accuracy on one model can range from 50% to 100%. |
| `metric` | string | yes | `pass_rate`. |
| `slice` | string | yes | A declared slice id or `all`. |
| `basis` | list of enums | no | Read only the cases whose `basis` is listed. A judgment gate (one that reads `judgment` cases) never also reads `convention` cases: rule-derived gold once inflated measured accuracy from 37% to 68%. |
| `threshold` | number 0 to 1 | yes | Passed when the value, and the value of each direction present, is at least the threshold. |
| `min_n` | integer | yes | Below it the status is `insufficient_n`, never `passed`. |
| `min_coverage` | number 0 to 1 | no | Fail when fewer than this share of the gate's cases were answered. A gate that sets it relies on confidence bands, so the suite's latest run must carry `calibration`. |
| `pinned_target_version` | integer or string | yes | The target version the decision was made on. When the target's version moves (a model alias, a prompt revision), the gate is `stale` until it is re-run and re-pinned. |
| `action` | string | yes | What a pass allows: "release the prompt", "promote billing triage to auto-resolve", "approve the policy for audit". |
| `owner` | string | yes | Who acts on the outcome. |
| `status` | enum | no | `open` until a run decides it. The runner computes the status in `run.json`; the owner records it here when acting. |

The runner decides a gate's status in this order: `open` when `suite_version` differs from the suite's; `stale` when `pinned_target_version` differs from `--target-version`; `insufficient_n` below `min_n`; `failed` below `min_coverage`, below `threshold`, or when one direction is below `threshold`; else `passed`.

## Target adapter protocol

The target is any command. The runner starts it once per case, writes the case's `input` as JSON on stdin, and reads one JSON value from stdout. When that value is a mapping, `confidence` (a number from 0 to 1) feeds calibration and `abstain: true` records an abstention instead of an answer. A non-zero exit, a timeout or output that is not JSON fails every non-human grader on that case, with the error in `detail`. The command runs without a shell, from the working folder; wrap a model call, an HTTP request, a script or a human-in-the-loop form in a small adapter that follows this protocol. `scripts/echo_target.py` is the trivial adapter: it writes its input back.

A suite whose graders are all `human` needs no target: the runner reads the recorded outcomes and produces the same run and report. That is how trigger-activation suites run.

## Validator

`python3 scripts/validate_suite.py SUITE [SUITE ...] [--gates FILE] [--vocabulary FILE] [--tune FILE] [--rules FILE] [--target-version V] [--runs PATH] [--max-validation-age DAYS] [--today YYYY-MM-DD] [--strict]`

- `--gates`: the gate registry. Its gates are checked against the suites named on the command line, so pass every suite a shared registry gates.
- `--vocabulary`: a `knowledge-organization-system` vocabulary. Expected labels must resolve to an active concept by `id`, `prefLabel` or `altLabel` (case-insensitive, whitespace collapsed); a `hiddenLabel` or a deprecated concept's label does not resolve.
- `--tune`: the tuning config, a YAML mapping `cases: [ids]` naming the cases a prompt, rule or threshold is tuned against.
- `--rules`: the `controlled-natural-language` rules file that governs rubric criteria. Lint the criteria with that skill's linter.
- `--target-version`: the target's current version. A gate recorded `passed` on another version is an error.
- `--runs`: a `run.json`, or a folder searched for them; repeatable. The latest run per suite (by `started_at`) is checked for `calibration`. Without it, gates that rely on confidence bands are not checked.
- `--max-validation-age`: how old `validated_against.measured_at` may be (default 180 days); `--today` fixes the date for reproducible output.

Each finding is one line, `SEVERITY RULE SUBJECT FIELD: problem. Fix: fix.`, sorted errors first, then by rule and subject. The last line counts errors and warnings and prints each suite's inferred stage: 3 when a gate names the suite, 2 when a case is in `holdout` or a `rubric-model` grader exists, 1 when a `regression` case exists, else 0. Exit 0 with no errors, 1 with errors (or warnings under `--strict`), 2 when an input file cannot be read.

| Rule | Severity | Fires when | Usual fix |
|---|---|---|---|
| `schema` | error | A file is not YAML, a key is unknown, a required field is missing or mistyped, or an enum value is unknown. | Correct the shape against the tables above. |
| `duplicate-case-id` | error | Two cases share an id. | Give each case its own id; retire one if they test the same thing. |
| `missing-evidence` | error | A case lacks `expected` or `added_because`. | Write the expected outcome and the evidence that produced the case. |
| `unknown-grader` | error | A case's `graders` names a grader the suite does not declare. | Correct the id or declare the grader. |
| `gate-reference` | error | A gate names a suite that was not validated with it, a metric other than `pass_rate`, or a slice the suite does not declare. | Correct the reference, declare the slice, or pass the suite. |
| `unvalidated-grader` | error | A gate's slice is graded by a `rubric-model` or `reference` grader without `validated_against`. | Measure agreement with human judgment first ([graders.md](graders.md)), or gate a slice that grader does not grade. |
| `holdout-in-tuning` | error | The tuning config names a `holdout` case. | Tune on `dev` cases only; move the case to `dev` and add a fresh holdout case. |
| `unresolved-label` | error | With `--vocabulary`, an expected label resolves to no active concept. | Use the `prefLabel` or id, or add the concept through `knowledge-organization-system` first. |
| `missing-variant` | error | An `invariance` or `negation` case has no `variant_of`, or it names no case in the suite. | Name the standard case it permutes or negates. |
| `convention-in-judgment-gate` | error | A gate reads both `judgment` and `convention` cases. | Set the gate's `basis` to exclude convention. |
| `uncalibrated-gate` | error | With `--runs`, a gate sets `min_coverage` but the suite's latest run has no `calibration`. | Run on dev with a target that returns `confidence`. |
| `stale-gate` | error | With `--target-version`, a gate recorded `passed` pins another target version. | Record `status: stale`, re-run on the new version, re-pin. |
| `synthetic-majority` | warning | More than half of a suite's active cases are `synthetic`. | Add production, adversarial or regression cases. |
| `ungated-metric` | warning | At Stage 3, a declared slice has no gate. | Gate it, or drop the slice. |
| `retired-case-gated` | warning | A gated slice names a retired case. | Repoint the slice at active cases. |
| `stale-validation` | warning | `validated_against.measured_at` is older than the configured age. | Re-measure agreement on a fresh human sample. |
| `peer-absent` | warning | Expected labels are checked with no vocabulary, or rubric criteria exist with no CNL rules file. | Configure the peer, or accept plain strings knowingly. |
| `missing-basis` | warning | Active cases state no `basis`. | Record who or what decided each case's `expected`. |
| `convention-in-judgment-suite` | warning | A suite holds both `judgment` and `convention` cases. | Give every judgment gate a `basis` without convention, or split the suite. |

`fixtures/broken-suite.yaml`, with `fixtures/gates.yaml`, `fixtures/vocabulary.yaml`, `fixtures/tune.yaml`, `fixtures/broken-run.json` and `--target-version triage-2026-10`, trips every rule except `schema` once.

## Runner

`python3 scripts/run_suite.py SUITE [--target CMD] [--target-version V] [--split dev|holdout|all] [--tune FILE] [--gates FILE] [--vocabulary FILE] [--human-results FILE] [--traffic FILE] [--max-drift X] [--out DIR] [--timeout S] [--strict]`

- It validates first (with the same `--gates`, `--vocabulary` and `--tune`) and refuses to run on any error.
- `--split` defaults to `dev`. With `--tune`, a split that includes holdout is refused. Every run that includes holdout cases appends a line to `holdout-runs.jsonl` next to the suite, and the report shows the count, so overuse is visible.
- `--human-results` is a YAML or JSON list of `{case_id, grader_id, outcome, detail}` recorded by people. A `human` grader with no recorded outcome abstains.
- `--traffic` is a YAML mapping of live tag counts. The runner compares it with the tag distribution of the cases it ran (total variation distance) and fails the run above `--max-drift` (default 0.2).
- `--target-version` is recorded in `run.json` (`unversioned` when absent). Given, every gate pinned to another version reports `stale`; absent, staleness is not judged.
- It writes `run.json` and `report.md` to `--out` (default `eval-runs/<run id>`). The report has a per-slice table (n, passes, value, interval, coverage), accuracy per direction, results by basis, a calibration table when the target returned confidence, a gate table with each status, the failing cases and the holdout count. `fixtures/proposition-suite.yaml` with `fixtures/proposition-gates.yaml` shows all of them.
- Exit 0 when no gate failed, 1 when a gate failed or drift exceeded the limit (or a gate is `insufficient_n` or `stale` under `--strict`), 2 when it refused or an input could not be read.

## Lessons ledger

`templates/LESSONS.md` is the human-readable companion to `run.json`. Each finding is one row: the claim, the run ids that show it, the numbers, the target version the runs measured, and a status of `holds`, `did not hold` or `re-measure`. Hypotheses that did not hold stay in the ledger. A finding whose runs predate the target version a gate now pins is marked `re-measure`.

## Consumers

`decision-questions` declares which cases a question set needs (invariance, negation and balanced cases, tagged by `basis`) and reads per-question gate outcomes (`question_id`) before any role promotion. The dependency is one-way: a `rubric-model` grader calls a decision model only through its `config.command` adapter (the `DecisionModel` contract), and this skill never imports that skill's schemas. `classify-and-resolve` turns its logs into cases, names the gates that guard each autonomy promotion, and reads their status.

## Worked examples

### Prompt or agent quality: a support-reply prompt

The target is a prompt that drafts replies to support tickets. A rubric judge grades each reply against CNL criteria; its agreement with two support leads was measured before it backs the release gate.

```yaml
id: support-reply
version: 4
target: support-reply-prompt
target_spec:
  - The reply shall name the customer's product.
  - If the ticket asks for a refund, then the reply shall link the refund policy.
graders:
  - id: policy-link
    kind: programmatic
    config: {command: python3 checks/policy_link.py}
  - id: tone-judge
    kind: rubric-model
    config:
      command: python3 adapters/judge.py
      criteria:
        - The reply shall answer the question the ticket asks.
        - The reply shall not promise a date the ticket does not give.
    validated_against: {human_set: evals/support/human-200.jsonl, agreement: 0.91, n: 200, measured_at: 2026-10-12}
slices: [refund, outage, billing]
cases:
  - id: refund-007
    input: {ticket: "I was charged twice for March. Can I get one back?"}
    expected: {must_link: refund-policy}
    tags: [refund]
    source: production
    basis: owner
    added_because: "ticket 48121: reply omitted the refund policy link"
    split: dev
    added_at: 2026-09-30
```

```yaml
gates:
  - {id: support-reply-release, suite_id: support-reply, suite_version: 4, metric: pass_rate, slice: all,
     threshold: 0.9, min_n: 100, pinned_target_version: support-reply-v12,
     action: release the prompt to all queues, owner: support-platform}
```

### A classifier: ticket triage

Each class is a slice, so one weak class cannot hide behind the aggregate. Labels are concept ids from the triage vocabulary, so `Billing` and `billing` resolve to one class.

```yaml
id: triage
version: 2
target: ticket-triage-classifier
target_spec: The classifier shall assign each ticket exactly one queue.
graders:
  - {id: queue-match, kind: exact, config: {field: label}}
slices: [billing, outage, account-access]
cases:
  - id: t-0412
    input: {subject: "Card declined at checkout", body: "..."}
    expected: billing
    tags: [billing]
    source: production
    basis: judgment
    added_because: "sampled from week 41 traffic, label confirmed by triage lead"
    split: holdout
```

```yaml
gates:
  - {id: triage-billing-autonomy, suite_id: triage, suite_version: 2, metric: pass_rate, slice: billing,
     basis: [owner, judgment], threshold: 0.97, min_n: 300, pinned_target_version: triage-model-2026-10,
     action: route billing tickets without human review, owner: support-ops}
```

Run `validate_suite.py suites/triage.yaml --gates gates.yaml --vocabulary vocabulary.yaml` so every expected label is checked against the vocabulary.

### A non-software corpus: policy compliance review

The target is a human process: reviewers check vendor contracts against a data-retention policy. The graders are people; their outcomes are recorded in a results file, and the gate decides whether the review checklist is ready for the external audit.

```yaml
id: contract-retention-review
version: 1
target: vendor-contract-review
target_spec:
  - The reviewer shall flag each clause that keeps personal data longer than 30 days.
graders:
  - {id: second-reviewer, kind: human}
slices: [processor, subprocessor]
cases:
  - id: acme-dpa-2024
    input: {document: contracts/acme-dpa-2024.pdf, clause: "7.2"}
    expected: {flag: true}
    tags: [processor]
    source: production
    basis: owner
    added_because: "2026 audit finding 3: clause 7.2 kept logs for 13 months"
```

```yaml
gates:
  - {id: retention-checklist-audit, suite_id: contract-retention-review, metric: pass_rate, slice: all,
     threshold: 0.95, min_n: 40, pinned_target_version: checklist-2026-q4,
     action: submit the checklist as an audit control, owner: privacy-office}
```

`run_suite.py suites/contract-review.yaml --human-results reviews/2026-q4.yaml --gates gates.yaml` needs no `--target`.
