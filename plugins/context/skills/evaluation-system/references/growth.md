# Growth

Load this before moving a suite to its next stage, when adding, retiring or re-splitting cases, when a gate is proposed, or when you suspect an anti-pattern. The stage table with entry criteria is in SKILL.md; this file holds what each stage may produce, the gate to leave it, the case lifecycle, anti-patterns, examples and the Stage 0 to Stage 1 walkthrough. Field semantics are in [model.md](model.md); grader rules are in [graders.md](graders.md).

## Stage gates

The validator prints the stage a suite's contents imply (`inferred stage N`): 1 once a `regression` case exists, 2 once a case is in `holdout` or a `rubric-model` grader exists, 3 once a gate names the suite. Reaching a stage takes its entry criterion; contents ahead of the criterion are the anti-pattern, not progress.

### Stage 0 (Seed)

- Entry: a target exists and at least one real failure or expected behavior is known.
- Allowed artifacts: one suite copied from `templates/suite.yaml`; 10 to 20 hand-written cases, each with `added_because`; one `exact` or `programmatic` grader; a target adapter; manual runs.
- Not allowed: gates, splits, model judges, cases with no evidence, a suite made only of `synthetic` cases.
- Gate to leave: the validator exits 0 and the suite runs green against the fixed target.

### Stage 1 (Regression)

- Entry: the Stage 0 suite runs green.
- Allowed artifacts: a CI step that runs the suite on every change to the target; a `regression` case for each newly found failure, added in the same change as its fix; more `exact` or `programmatic` graders for spec clauses that failures exposed.
- Not allowed: removing a case to make the run green (retire it with a reason instead), percentages quoted as quality claims.
- Gate to leave: 50 or more active cases, or a decision now depends on the result.

### Stage 2 (Measure)

- Entry: 50 or more cases, or a decision depends on the result.
- Allowed artifacts: a `dev` and `holdout` split (assign holdout when a case is added, roughly one case in four, never by looking at its outcome); per-slice metrics with intervals; a tuning config naming the `dev` cases tuned against; `rubric-model` or `reference` graders once `validated_against` is recorded.
- Not allowed: tuning on holdout, gates, an aggregate number without its slices.
- Gate to leave: a real decision (a release, an autonomy promotion, an audit submission) needs an automated answer and has an owner.

### Stage 3 (Gate)

- Entry: a real decision needs an automated answer.
- Allowed artifacts: gates in `gates.yaml` (threshold, `min_n`, action, owner, a pinned suite version, a `pinned_target_version`, and where it fits a `question_id`, a `basis` list and `min_coverage`); production sampling into the case set; a drift check of case tags against live traffic (`--traffic`); a `LESSONS.md` ledger from `templates/LESSONS.md`.
- Not allowed: a gate on a slice graded by an unvalidated judge, a gate whose slice cannot reach `min_n`, metrics no gate reads, a judgment gate that also reads convention cases, a coverage gate without calibration on dev, a `passed` gate kept after the target version moved.
- Steady state: no `ungated-metric`, `stale-validation`, `retired-case-gated` or `missing-basis` warnings; holdout runs stay rare (the report counts them); every gate pins the target version that is live.

## Case lifecycle

- **Add** with evidence: a bug link, a log id, a spec clause, a review comment, in `added_because`. Set `source` honestly; a case written to probe a boundary is `adversarial`, one written from imagination is `synthetic`, one from a fixed failure is `regression`.
- **Record who decided the gold** in `basis`. Report `owner` cases as their own slice (the runner's by-basis table does), because `agent`-approved gold inherits the agent's biases and `convention` gold rewards rule-following, not judgment.
- **Add variants** for choice and proposition targets: an `invariance` case per option-order permutation (a changed answer is a failure; option-order bias is a documented failure mode) and a `negation` case that flips the proposition, each with `variant_of`. Keep true and false cases balanced so accuracy per direction means something.
- **Version.** Bump the suite `version` whenever a case or grader is added, retired or changed. Gates pin a version, so a changed suite does not silently move a gate's bar.
- **Split** at Stage 2. A holdout case that was looked at during tuning is spent: move it to `dev` and add a fresh holdout case.
- **Change with the spec.** When the target spec changes, the affected cases change in the same commit; a case that tests a removed clause retires.
- **Retire, don't delete.** `status: retired` with `retired_reason`. A retired case is never run, keeps its id, and explains old runs.
- **Sample production** at Stage 3: draw new cases from live traffic by tag, label them, and add them with `source: production` and the log id.

## Anti-patterns

| Anti-pattern | Looks like | Caught by | Fix |
|---|---|---|---|
| Tuning on holdout | Few-shot examples or a threshold picked by looking at holdout results. | `holdout-in-tuning`; the runner refuses `--tune` with a holdout split | Tune on `dev`; replace the spent holdout cases. |
| Dashboards without gates | A metric tracked weekly that no decision reads. | `ungated-metric` at Stage 3; the report says when no gate reads the suite | Gate it with an action and an owner, or stop computing it. |
| Unvalidated LLM judges | "The judge says 92% good." | `unvalidated-grader` | Run the agreement procedure in [graders.md](graders.md). |
| Percentages on tiny samples | "100% pass" on 6 cases. | `insufficient_n` below `min_n`; every rate carries n and an interval | Report counts; collect cases until the interval can clear the bar. |
| All-synthetic suites | Fifty generated paraphrases of one prompt. | `synthetic-majority` | Add production, adversarial and regression cases. |
| Cases nobody can explain | An expected output no one can justify. | `missing-evidence` | Record the evidence, or retire the case. |
| One aggregate hiding a failing slice | 94% overall, 61% on refunds. | Per-slice metrics in every report; gates on slices | Gate the weak slice, not only `all`. |
| One direction hiding the other | 95% on true cases, 50% on false ones, 80% overall. | Accuracy per direction in the report; a gate fails when either direction is below its threshold | Add negation variants and false cases; gate the question (`question_id`). |
| Rule-derived gold in a judgment score | Convention cases lift measured judgment accuracy from 37% to 68%. | `convention-in-judgment-gate`, `convention-in-judgment-suite` | Give the gate a `basis` list without convention. |
| A gate that outlived its target | A gate passed on last month's model alias still reads `passed`. | `stale` from the runner; `stale-gate` in the validator | Re-run on the new version, then re-pin. |

## Lessons ledger

Keep `LESSONS.md` beside the suite (copy `templates/LESSONS.md`) once runs start deciding things. Each row is a claim with the run ids, the counts and intervals, and the target version measured, marked `holds`, `did not hold` or `re-measure`. Write the row in the same change that quotes the claim; never delete a refuted one, so nobody re-tests it blind. When a gate re-pins to a new target version, mark every row measured on the old one `re-measure`.

## Examples across domains

### Prompt or agent quality: support replies reach Stage 3

The support-reply suite (model.md) reached 140 cases from production tickets and fixed failures. The team split it, validated the tone judge against two support leads (agreement 0.91, the leads agreed with each other at 0.93), and only then added the release gate on `all` and a second gate on the `refund` slice, which had been hiding behind the aggregate at 0.84. The tuning config lists the 20 dev cases used to pick few-shot examples.

### A classifier: triage autonomy with drift

The triage suite has one slice per queue. Billing reached 300 holdout cases at 0.967 (290 of 300, interval 0.94 to 0.98), so `triage-billing-autonomy` (threshold 0.97, `min_n` 300) reports `failed` on the value and the team keeps human review. The weekly run passes `--traffic` with live queue counts; when a pricing change tripled `outage` tickets, the tag distance passed 0.2, the run failed, and the team sampled 60 new outage tickets into the suite before trusting any metric again.

### A non-software corpus: a compliance review at Stage 1

The contract-retention review (model.md) is a human process. Stage 0 seeded 15 cases from the 2026 audit's findings, each `added_because` an audit item, graded by a second reviewer (`human`). At Stage 1, every clause the external auditor flagged and the team missed became a `regression` case in the same week the checklist was fixed. The suite has no gate yet: at 15 cases, any rate is a count with a wide interval (14 of 15 is 0.70 to 0.99), so the team reports counts.

## Walkthrough: a prompt from no evaluation to Stage 1

The target is `prompts/support-reply.md`, a prompt that drafts replies to support tickets. Nobody has evaluated it. Ticket 48121 got a reply that ignored a refund request and did not link the refund policy.

### Before: no evaluation

```text
prompts/support-reply.md
```

The claim "the new prompt handles refunds" has no evidence. Stop and seed a suite before changing the prompt.

### Stage 0: seed one suite

The entry criterion holds: the target exists and a real failure is known. Add three files:

```text
prompts/support-reply.md
evals/support-reply/suite.yaml        # copied from templates/suite.yaml
evals/support-reply/target.py         # adapter: {ticket} on stdin, {reply} on stdout
evals/support-reply/policy_link.py    # programmatic grader
```

```diff
--- /dev/null
+++ evals/support-reply/suite.yaml
+id: support-reply
+version: 1
+target: support-reply-prompt
+target_spec:
+  - If the ticket asks for a refund, then the reply shall link the refund policy.
+graders:
+  - id: policy-link
+    kind: programmatic
+    config: {command: python3 evals/support-reply/policy_link.py}
+slices: []
+cases:
+  - id: refund-001
+    input: {ticket: "I was charged twice for March. Can I get one back?"}
+    expected: {must_link: refund-policy}
+    source: production
+    added_because: "ticket 48121: reply omitted the refund policy link"
+    added_at: 2026-11-01
+  - id: no-refund-001
+    input: {ticket: "How do I export my invoices as CSV?"}
+    expected: {must_link: none}
+    source: production
+    added_because: "ticket 48090: a non-refund ticket, so no policy link is expected"
+    added_at: 2026-11-01
+  # ... eight more cases from the support queue and the spec clause
```

`policy_link.py` reads `{input, output, expected}` and exits 0 when the reply links the policy exactly when `expected.must_link` asks for it, 1 otherwise. `target.py` sends the ticket to the prompt and prints `{"reply": "..."}`.

```bash
python3 scripts/validate_suite.py evals/support-reply/suite.yaml
# evals/support-reply/suite.yaml: 0 error(s), 0 warning(s), inferred stage 0
python3 scripts/run_suite.py evals/support-reply/suite.yaml --target "python3 evals/support-reply/target.py" --target-version prompt-v1 --out eval-runs/v1
```

```text
| Slice | n | Passes | Value | 95% interval (Wilson) |
| all   | 10 | 7     | 0.70  | 0.40 to 0.89          |
```

Three refund tickets fail. Fix the prompt, rerun with `--target-version prompt-v2`, and get 10 of 10 (0.72 to 1.00). Report "10 of 10 cases", not "100%". The suite is green, so the Stage 1 entry criterion holds.

### Stage 1: run it on every change, and turn each new failure into a case

Add the run to whatever runs on a change to the prompt (CI, a pre-merge script, a release checklist):

```diff
+# runs on every change to prompts/support-reply.md
+python3 scripts/validate_suite.py evals/support-reply/suite.yaml
+python3 scripts/run_suite.py evals/support-reply/suite.yaml --target "python3 evals/support-reply/target.py" --target-version "$(git rev-parse --short HEAD)" --out eval-runs/ci
```

A week later ticket 48877 gets a reply that promises a refund "by Friday", a date the ticket never gave. The fix and its regression case ship in one change:

```diff
--- a/evals/support-reply/suite.yaml
+++ b/evals/support-reply/suite.yaml
-version: 1
+version: 2
 target_spec:
   - If the ticket asks for a refund, then the reply shall link the refund policy.
+  - The reply shall not promise a date the ticket does not give.
 graders:
   - id: policy-link
     kind: programmatic
     config: {command: python3 evals/support-reply/policy_link.py}
+  - id: no-promised-date
+    kind: programmatic
+    config: {command: python3 evals/support-reply/no_promised_date.py}
 ...
+  - id: refund-011
+    input: {ticket: "Please refund order 5521, it arrived broken."}
+    expected: {must_link: refund-policy, promised_date: none}
+    source: regression
+    added_because: "ticket 48877: reply promised a refund date the ticket never gave"
+    added_at: 2026-11-08
```

```diff
--- a/prompts/support-reply.md
+++ b/prompts/support-reply.md
+Never state a date for a refund or a fix unless the ticket gives one.
```

The run shows 11 of 11 (0.74 to 1.00) and the validator now infers stage 1. The suite stays at Stage 1 until it holds 50 cases or a release decision depends on it; only then do splits, intervals per slice and a judge for tone arrive (Stage 2).
