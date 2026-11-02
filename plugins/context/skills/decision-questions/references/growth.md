# Growth

Load this before changing a question set's stage or role, adding contrast, tuning a band or margin, or when an anti-pattern is suspected. It ends with a walkthrough from "should we ask a model this?" through Stage 1. Field names are in [model.md](model.md).

## Stages

Each stage has an entry criterion, the artifacts it allows, and a promotion gate. Never skip a stage; a role never rises without a passed gate.

| Stage | Entry criterion | Allowed artifacts | Promotion gate |
|---|---|---|---|
| 0 One question | A bounded decision exists, and deterministic rules and observed data do not already answer it | One question set with one question, role `checker`; options scoped to the domain; 10 to 20 seed cases including ambiguous ones; answers run by hand and logged, never acted on | Stage 0 answers look useful on inspection |
| 1 Measure | Stage 0 answers look useful | An `evaluation-system` suite from `make_eval_cases.py`: `basis` on every case, invariance cases, balanced both-direction cases for propositions; bands or margins tuned on `dev`; `model` pinned; contrast added as KOS `excludes` | A per-question gate passes on owner-tier holdout |
| 2 Suggest | That question's gate passes on owner-tier holdout, at the band used for preselection | That question alone moves to role `suggester`, in its own question set, with its gate in `gate_ids` | Evidence that it beats or complements existing judges on hard cases |
| 3 Vote | That evidence exists, as a passed gate on owner-tier hard cases | That question alone moves to role `voter` | None: this is the top of the ladder |

Many questions never reach Stage 3, and that is the expected outcome, not a failure: in the evidence base the model judged hard cases no better than the agents it would have joined.

## Roles

| Role | Its output may | Promotion requires |
|---|---|---|
| `checker` | Raise a flag for a human second look; it never changes data | Default |
| `suggester` | Preselect an answer in a review UI; it never approves | A passed per-question gate on owner-tier cases, at the band used for preselection |
| `voter` | Count as one vote among judges in a merge or tie-break | A passed gate showing it beats or adds information to the existing judges on hard cases |

- **Per question.** A role belongs to a question set, so promote one question by moving it into its own set. `validate_questions.py` requires a passed gate for every question a decision reads (`ungated-role`), with `question_id` naming it and `pinned_target_version` equal to `model`.
- **Autonomy is not granted here.** Acting without a person (`auto` in `classify-and-resolve`'s autonomy matrix) is granted by that matrix, on top of a role.
- **Untrusted state caps the role.** A decision driven by state that may be adversarial never goes past `suggester` for an irreversible action.
- **Demote without a gate.** When a gate fails, goes `stale` after a model change, or a review finds harm, drop the role to `checker` in the same change.

## Gates

Gates live in `evaluation-system`'s `gates.yaml`. A question set names them in `gate_ids` and never computes a metric.

```yaml
gates:
  - {id: support-team-suggest, suite_id: support-team-cases, suite_version: 3, question_id: team,
     metric: pass_rate, slice: team, basis: [owner], threshold: 0.93, min_n: 200, min_coverage: 0.4,
     pinned_target_version: example-model-2026-11-01, action: preselect the team in the triage UI,
     owner: support-ops, status: passed}
```

`min_coverage` makes the gate read the band: a question right 93% of the time on the 40% of messages above `act` passes; one that only gets there by abstaining on almost everything does not.

## Model changes

A new model version is a new target. Re-ask every seed, re-run every gate on the new version, and re-pin `model` and each gate's `pinned_target_version` in one change. Until then the gates are `stale` and the role falls back to `checker`.

## Anti-patterns

| Anti-pattern | How it shows | Fix |
|---|---|---|
| Decomposing a joint label into independent questions and trusting the combination | A decision with several inputs and no `assemble` (`missing-assemble`); joint accuracy far below each part's | Name an `assemble` validator that enforces the label grammar; score the joint label separately |
| Thresholding raw proposition values | A threshold decision on a proposition (`threshold-on-proposition`) | Compare against a rival with a margin |
| Generated contrast text | Option descriptions with "not X" lines nobody wrote by hand | Delete them; author `excludes` in KOS after an observed confusion |
| Full-vocabulary option sets | Options no item in the domain ever uses; picks that make no sense | Select the concepts the domain uses (`--concepts`), or use `retrieve-then-choose` |
| Conventions passed as notes | Instructions that say "by convention, X means Y" | Turn the convention into a deterministic rule upstream; ask the model only what remains |
| Using the model as a tie-breaker without evidence | Role `voter` with no gate on hard cases | Keep it at `checker` or `suggester` until a hard-case gate passes |
| Judgment benchmarks built from rule-derived gold | `convention` cases read by a judgment gate | Set the gate's `basis` without `convention`; report owner-tier apart |
| Promoting a whole model instead of one question | A set with several questions moved to `suggester` at once | Promote each question in its own set, behind its own gate |

## Disagreement routing

When the model disagrees with a deterministic rule, send the disagreement to a rule-repair queue first and the item queue second. In the evidence base, 23 such conflicts all traced to one misfiring rule.

## Walkthrough: from a question to Stage 1

A support team routes customer messages to teams. Keyword rules already route messages that name an invoice number; the rest go to a shared inbox.

**Should we ask a model this?** The decision is bounded: one team out of three, or none. Rules cover the invoice-number messages, and no observed data (such as the product area of a linked error) exists for the rest. The decision qualifies for Stage 0.

**Stage 0.** Copy `templates/question-set.yaml` and `templates/seed-cases.yaml`. Pin `model` to the exact version the adapter reports and check the file:

```bash
python3 scripts/validate_questions.py questions/support-team.yaml
# 1 question set(s): 0 error(s), 0 warning(s)
```

Ask the 13 seed messages by hand through the adapter and log each answer next to its seed. Nothing acts on them. On inspection the answers look useful: the confident ones are right, and the misses cluster on locked-for-payment messages.

**Stage 1, measure.** Generate the suite and run it on dev with the adapter (here the fixture adapter replaying recorded answers):

```bash
python3 scripts/make_eval_cases.py questions/support-team.yaml --seeds questions/support-team.seeds.yaml --out evals/support-team.suite.yaml
python3 <evaluation-system>/scripts/run_suite.py evals/support-team.suite.yaml \
  --target "python3 adapters/fixture.py --recordings fixtures/recorded-answers.yaml --question-set questions/support-team.yaml" \
  --target-version example-model-2026-11-01 --out eval-runs/v1
```

The report shows pass rate 0.88 on 33 answered cases, coverage 0.92 (3 below the review band), calibration bands with every answer at 0.6 or above right, and four failures: `t13` and its two permutations picked `account-access` for a locked-for-payment message, and `t02-perm1` picked `none` when the options were reversed.

**Move the options to KOS.** Compile the options from the team's vocabulary instead of writing them inline, passing the run so confusions are checked:

```bash
python3 scripts/compile_questions.py vocabulary.yaml --template questions/support-team.yaml \
  --shape single-choice --allow-none --run eval-runs/v1/run.json --out questions/support-team.yaml
# WARNING unaddressed-confusion support-team options.account-access: the last evaluation run confused
#   'account-access' and 'billing', and neither option has an excludes entry naming the other. ...
# WARNING unaddressed-confusion support-team options.billing: the last evaluation run confused 'billing' and 'none', ...
```

The second warning comes from `t02-perm1`, an invariance failure: the answer moved with the option order, which contrast does not fix. Record it and watch it across runs.

**Author the contrast.** The first warning is a real confusion. Write the `excludes` entry by hand in the vocabulary, with the run as evidence:

```diff
   - id: account-access
     prefLabel: account access
     definition: The team that handles failed sign-ins to a customer account.
+    excludes:
+      - neighbor: billing
+        statement: A sign-in blocked by an unpaid invoice belongs to billing; account access covers credentials, resets and lockouts.
     scheme: support
-    evidence: [questions/triage.md:11]
+    evidence: [questions/triage.md:11, "eval run support-team-cases v1: t13, a locked-for-payment message, picked account-access in all three option orders"]
```

Check it with `knowledge-organization-system`'s `validate_kos.py`, then recompile. The option gains the entry verbatim and the first warning is gone:

```diff
     account-access:
       concept_id: account-access
       definition: The team that handles failed sign-ins to a customer account.
+      excludes:
+      - neighbor: billing
+        statement: A sign-in blocked by an unpaid invoice belongs to billing; account access covers credentials,
+          resets and lockouts.
```

`fixtures/support.vocabulary.yaml` is the vocabulary after this change.

**Re-run and compare.** Bump the set's `version`, regenerate the suite, re-ask the seeds on the same model version, and run again to `eval-runs/v2`. Compare v1 and v2 case by case on the same suite version and split (the paired comparison in `evaluation-system`'s `references/graders.md`); with this few cases the comparison is `insufficient_n`, so the contrast stays on the strength of the observed confusion and the suite grows until it can be measured. Tune `bands` on dev only, and only then write the per-question gate for Stage 2.
