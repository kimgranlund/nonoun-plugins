# Graders

Load this when you pick or configure a grader, write a rubric, wire a judge or a check command into the runner, or measure a grader's agreement with human judgment. Field names are defined in [model.md](model.md); stages and anti-patterns are in [growth.md](growth.md).

## Choosing a kind

Pick the cheapest grader that decides the outcome the target spec states. A grader that needs judgment is a measurement instrument and earns trust before it backs a decision.

| Kind | Decides | Valid when | Trusted for a gate |
|---|---|---|---|
| `exact` | Equality of the output (or one field) with `expected` | The right answer is one value: a label, a number, a yes or no | Yes |
| `programmatic` | A code assertion on the output | The spec clause is checkable by code: a link is present, JSON parses, a date is not promised | Yes, once the check is reviewed like code |
| `reference` | Similarity to a gold output | A gold output exists and close wording is the goal (a summary, a translation) | Only with `validated_against` |
| `rubric-model` | A model applies rubric criteria | The quality is judgment (tone, completeness) and a human can grade a sample | Only with `validated_against` |
| `human` | A person records the outcome | The target is a human process, or the judgment cannot be delegated yet | Yes; it is the reference other graders are validated against |

Stage 0 allows one `exact` or `programmatic` grader. `rubric-model` graders arrive at Stage 2, and only after `validated_against` is recorded.

## Configuration and runner protocol

Each grader sees one case at a time. Command graders follow the target's protocol: JSON on stdin, JSON on stdout, no shell.

| Kind | `config` keys | What the runner does |
|---|---|---|
| `exact` | `field` (dotted path in the output; when `expected` is a mapping holding the same field, that value is compared), `normalize` (compare strings case-insensitively with whitespace collapsed) | Compares values. With `--vocabulary`, two labels compare by concept id, so an `altLabel` output matches its `prefLabel`. |
| `programmatic` | `command` | Sends `{input, output, expected}`. A stdout `{outcome, detail}` wins; otherwise exit 0 is pass, 1 is fail, anything else abstains. |
| `reference` | `field`, `pass_at` (default 0.8), or `command` | Without a command: token F1 between the output and the gold `expected`, pass at or above `pass_at`, the score in `detail`. With a command: as `programmatic`. |
| `rubric-model` | `command`, `criteria` | Calls the command once per criterion with `{input, output, expected, criterion}`. The case passes when every criterion passes; `detail.criteria` records each one. |
| `human` | `pass_at` for `score` outcomes (default 0.5) | Reads `--human-results`: a list of `{case_id, grader_id, outcome, detail}`. A case with no record abstains. |

When a target call fails (non-zero exit, timeout, output that is not JSON), every non-human grader fails that case. A target that crashes on an input has failed it.

## Rubric criteria

A criterion is one checkable statement, written as a `controlled-natural-language` statement when the project has a rule set: "The reply shall link the refund policy." "The reply shall not promise a date the ticket does not give." Check each criterion separately, never a holistic 1 to 10 score: a single number hides which criterion failed and cannot be validated per criterion. When the problem is how a criterion is worded (two readings, a vague adjective), hand it to `controlled-natural-language`; when it is what a term in it means, to `knowledge-organization-system`.

A judge adapter receives one criterion and returns `{"outcome": "pass" | "fail", "detail": "<one-line reason>"}`. Keep the model, its prompt and its temperature in the adapter, version them, and re-measure agreement when any of them changes.

## Human-agreement validation

A `rubric-model` or `reference` grader backs a gate only after this procedure, recorded as `validated_against`.

1. **Sample.** Draw at least 50 cases (100 for a gate with `min_n` of 100 or more) from the suite's `dev` split, covering every gated slice. Store the sample's case ids and human labels in a file; that path is `human_set`.
2. **Label by humans.** Two people grade each case against the same criteria, independently. Record their agreement with each other: it is the ceiling a model grader can reach. Settle disagreements by discussion and keep the settled label as the human label.
3. **Grade by the model.** Run the grader on the same cases with the same criteria and adapter version.
4. **Measure.** `agreement` is the share of cases where the grader's outcome equals the human label, with its Wilson interval. Compute it per gated slice as well; one weak slice disqualifies the grader for that slice's gate.
5. **Decide.** Trust the grader for a gate when its agreement is within 0.05 of the human-human agreement and its interval's lower bound is above the gate's threshold. Otherwise fix the rubric or adapter, or keep the slice on `human` grading.
6. **Record** `validated_against: {human_set, agreement, n, measured_at}` in the suite, in the change that adds the gate.
7. **Re-measure** when the rubric, the judge model, its prompt or the target's output style changes, and when `measured_at` is older than the configured age (`stale-validation`).

## Limiting factors

- **Gold-set quality.** A wrong `expected` makes a correct output fail. Double-label a sample of the gold set the way step 2 does; when two careful people disagree on more than a few percent of cases, fix the labels or the spec before reading any metric to the second decimal.
- **Grader validity.** An unvalidated judge measures its own preferences. The validator refuses to let one back a gate (`unvalidated-grader`).
- **Distribution match.** A suite that no longer resembles live inputs passes tests that no longer matter. At Stage 3, `run_suite.py --traffic` compares case tags with live tag counts and fails the run past the limit.

## Comparing two versions

Run both versions on the same suite version and split, then compare case by case. Count the discordant pairs: `b` cases pass on A and fail on B, `c` the reverse. Agreements carry no information. With `b + c` under 10 the comparison is `insufficient_n`. Otherwise use the exact sign test (binomial with p = 0.5 on `b + c` trials) and call a winner only below 0.05, per slice as well as overall. Overlapping per-version intervals alone do not settle a paired comparison either way.
