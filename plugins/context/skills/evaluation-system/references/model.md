# Evaluation model

Load this when you write or change a suite, a grader, a gate registry or a run reader, when a validator or runner message is unclear, or when another tool reads these files. It is the authority for the typed spine (Case, Grader, Suite, Run, Gate), field semantics, the target adapter protocol, the validator and runner rules, and worked examples. Grader kinds and their validation procedure are in [graders.md](graders.md); stages, case lifecycle and anti-patterns are in [growth.md](growth.md).

## Typed spine (stable contract)

The field names below are published as stable. `classify-and-resolve` and any other consumer read and write them by these exact names and never redefine them. Rename or remove a field only with a versioned change to every consumer. Fields marked optional and the extensions listed after the block were part of the first publication.

```yaml
Case:   { id, input, expected, tags[], source: production|synthetic|adversarial|regression,
          added_because, split: dev|holdout, added_at, graders[]?, status?: active|retired, retired_reason? }
Grader: { id, kind: exact|programmatic|reference|rubric-model|human,
          config, validated_against?: { human_set, agreement, n, measured_at } }
Suite:  { id, version, target, target_spec, cases[] | cases_path, graders[], slices[] }
Run:    { id, suite_id, suite_version, target_version, started_at, split, tuning,
          results[]: { case_id, grader_id, outcome: pass|fail|score|abstain, detail },
          metrics: { slice → { value, n, interval, passes } }, gates[], drift? }
Gate:   { id, suite_id, suite_version?, metric, slice, threshold, min_n, action, owner,
          status: open|passed|failed|insufficient_n }
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

A slice is the unit a decision is made on. A metric that no gate references is a dashboard, which the validator warns about at Stage 3.

### Run

`run_suite.py` writes it as `run.json`. `split` is `dev`, `holdout` or `all`; `tuning` is true when the run fed a tuning step. `results` holds one entry per case and applicable grader; `detail` is text or a mapping (a `score` carries `detail.score`, a rubric result lists each criterion). `metrics` maps each slice id to `{value, n, interval: [low, high], passes}`. `gates` holds each gate for this suite with its computed `status`, `value` and `n`. `drift` appears when live traffic tags were supplied.

### Gate

A gate is a decision with its evidence bar. One registry file per project, usually `gates.yaml`, with a top-level `gates:` list; start from `templates/gates.yaml`.

| Field | Type | Required | Meaning |
|---|---|---|---|
| `id` | string | yes | Stable. |
| `suite_id` | string | yes | The suite it reads. |
| `suite_version` | integer or string | no | Pin a suite version. A run on another version leaves the gate `open`. |
| `metric` | string | yes | `pass_rate`. |
| `slice` | string | yes | A declared slice id or `all`. |
| `threshold` | number 0 to 1 | yes | Passed when the value is at least the threshold. |
| `min_n` | integer | yes | Below it the status is `insufficient_n`, never `passed`. |
| `action` | string | yes | What a pass allows: "release the prompt", "promote billing triage to auto-resolve", "approve the policy for audit". |
| `owner` | string | yes | Who acts on the outcome. |
| `status` | enum | no | `open` until a run decides it. The runner computes the status in `run.json`; the owner records it here when acting. |

## Target adapter protocol

The target is any command. The runner starts it once per case, writes the case's `input` as JSON on stdin, and reads one JSON value from stdout. A non-zero exit, a timeout or output that is not JSON fails every non-human grader on that case, with the error in `detail`. The command runs without a shell, from the working folder; wrap a model call, an HTTP request, a script or a human-in-the-loop form in a small adapter that follows this protocol. `scripts/echo_target.py` is the trivial adapter: it writes its input back.

A suite whose graders are all `human` needs no target: the runner reads the recorded outcomes and produces the same run and report. That is how trigger-activation suites run.

## Validator

`python3 scripts/validate_suite.py SUITE [SUITE ...] [--gates FILE] [--vocabulary FILE] [--tune FILE] [--rules FILE] [--max-validation-age DAYS] [--today YYYY-MM-DD] [--strict]`

- `--gates`: the gate registry. Its gates are checked against the suites named on the command line, so pass every suite a shared registry gates.
- `--vocabulary`: a `knowledge-organization-system` vocabulary. Expected labels must resolve to an active concept by `id`, `prefLabel` or `altLabel` (case-insensitive, whitespace collapsed); a `hiddenLabel` or a deprecated concept's label does not resolve.
- `--tune`: the tuning config, a YAML mapping `cases: [ids]` naming the cases a prompt, rule or threshold is tuned against.
- `--rules`: the `controlled-natural-language` rules file that governs rubric criteria. Lint the criteria with that skill's linter.
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
| `synthetic-majority` | warning | More than half of a suite's active cases are `synthetic`. | Add production, adversarial or regression cases. |
| `ungated-metric` | warning | At Stage 3, a declared slice has no gate. | Gate it, or drop the slice. |
| `retired-case-gated` | warning | A gated slice names a retired case. | Repoint the slice at active cases. |
| `stale-validation` | warning | `validated_against.measured_at` is older than the configured age. | Re-measure agreement on a fresh human sample. |
| `peer-absent` | warning | Expected labels are checked with no vocabulary, or rubric criteria exist with no CNL rules file. | Configure the peer, or accept plain strings knowingly. |

`fixtures/broken-suite.yaml`, with `fixtures/gates.yaml`, `fixtures/vocabulary.yaml` and `fixtures/tune.yaml`, trips every rule except `schema` once.

## Runner

`python3 scripts/run_suite.py SUITE [--target CMD] [--target-version V] [--split dev|holdout|all] [--tune FILE] [--gates FILE] [--vocabulary FILE] [--human-results FILE] [--traffic FILE] [--max-drift X] [--out DIR] [--timeout S] [--strict]`

- It validates first (with the same `--gates`, `--vocabulary` and `--tune`) and refuses to run on any error.
- `--split` defaults to `dev`. With `--tune`, a split that includes holdout is refused. Every run that includes holdout cases appends a line to `holdout-runs.jsonl` next to the suite, and the report shows the count, so overuse is visible.
- `--human-results` is a YAML or JSON list of `{case_id, grader_id, outcome, detail}` recorded by people. A `human` grader with no recorded outcome abstains.
- `--traffic` is a YAML mapping of live tag counts. The runner compares it with the tag distribution of the cases it ran (total variation distance) and fails the run above `--max-drift` (default 0.2).
- It writes `run.json` and `report.md` to `--out` (default `eval-runs/<run id>`). The report has a per-slice table (n, passes, value, interval), a gate table with each status, the failing cases and the holdout count.
- Exit 0 when no gate failed, 1 when a gate failed or drift exceeded the limit (or a gate is `insufficient_n` under `--strict`), 2 when it refused or an input could not be read.

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
    added_because: "ticket 48121: reply omitted the refund policy link"
    split: dev
    added_at: 2026-09-30
```

```yaml
gates:
  - {id: support-reply-release, suite_id: support-reply, suite_version: 4, metric: pass_rate, slice: all,
     threshold: 0.9, min_n: 100, action: release the prompt to all queues, owner: support-platform}
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
    added_because: "sampled from week 41 traffic, label confirmed by triage lead"
    split: holdout
```

```yaml
gates:
  - {id: triage-billing-autonomy, suite_id: triage, suite_version: 2, metric: pass_rate, slice: billing,
     threshold: 0.97, min_n: 300, action: route billing tickets without human review, owner: support-ops}
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
    added_because: "2026 audit finding 3: clause 7.2 kept logs for 13 months"
```

```yaml
gates:
  - {id: retention-checklist-audit, suite_id: contract-retention-review, metric: pass_rate, slice: all,
     threshold: 0.95, min_n: 40, action: submit the checklist as an audit control, owner: privacy-office}
```

`run_suite.py suites/contract-review.yaml --human-results reviews/2026-q4.yaml --gates gates.yaml` needs no `--target`.
