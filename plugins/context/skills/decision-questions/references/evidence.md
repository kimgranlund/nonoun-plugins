# Evidence

Load this when a rule in this skill is questioned, when you set a band or a margin, or when you plan a measurement on your own data. These findings come from one project and one model; treat each number as a prior to re-measure, never as a constant.

## The evidence-base project

A team mapped design-system tokens onto a KOS-style concept registry with TypeSafe's Jev (`jev-1.14.0`): 1,338+ calls on stratified samples, each finding confirmed on a second seed. Owners approved or overrode the mappings, so owner-tier gold existed for most items.

## Findings and the rules they support

| Finding | Evidence | Rule | Re-measure on your data |
|---|---|---|---|
| Comparing a proposition against its nearest rival works | The right concept outscored its nearest neighbor 94 to 96% of the time. Only 73 to 77% of right answers scored above 0.5. | Propositions use compare mode, never a raw threshold. | On balanced proposition cases, compare the share where the right statement beats its rival with the share above 0.5. |
| Choice confidence is usable | Choice among k candidates that include the right one: 93% at k=5, 89% at k=10, ECE about 8%. At 0.85 or more, 93 to 97% right; 0.5 to 0.85, 50 to 60%; below 0.5, 24 to 28%. | Choices and scores use threshold bands, tuned per question. | Run the suite on dev with confidence; read the calibration table and ECE in `run_suite.py`'s report, then set `act` and `review` where the band accuracy meets your bar. |
| Independent facet questions fail on joint labels | Six isolated facet Choices: 10 to 16% fully right; with the grammar enforced afterwards, 27 to 34%. | Assemble joint labels in code with a named `assemble` validator. | Score each part and the joint label separately; the gap is what isolation costs. |
| Two stages beat one big question | Rank, then one Choice among the top 20: right 60 to 64%, right answer listed 86 to 93%. At 0.8 or more: 88 to 94% right on 47% coverage. | Large schemes use `retrieve-then-choose`; report list hit rate and pick accuracy apart. | Log whether the right answer was listed; compute pick accuracy only on listed cases. |
| Hand-written contrast is the biggest lever | Contrastive option descriptions raised usage accuracy from 47 to 61% and joint accuracy from 25 to 30%. Generated "not X" text: 17.9%, worse than plain definitions (25%). Better definitions alone: no gain. | Contrast comes from authored KOS `excludes`; the compiler never generates it. | Re-run the same suite version before and after one `excludes` entry; compare the confused pair's cases. |
| Options must be scoped to the domain | Offering every facet value produced nonsensical options, such as typography usages for color tokens. | Options are the values the domain's concepts use. | Count picks of options the domain never uses; any is a scoping defect. |
| Conventions do not transfer through notes | Stated conventions left convention-matched tokens at 11% joint accuracy either way. | Conventions are deterministic rules upstream, never notes to the model. | Compare accuracy on convention-matched items with and without the note. |
| The model is not a better judge of hard cases | On owner-overridden disagreements: 55% against an agent majority's 61%; 52 against 48% where agents split (n=21). | The `voter` role needs a gate showing it beats or complements existing judges. | Score the model and each existing judge on the same hard, owner-tier cases. |
| Boundary accuracy varies per question | Per-boundary accuracy on one model: 50% to 100%. One boundary was right on 95% of positives and half of negatives. | Gates attach per question; boundary suites are balanced and scored in both directions. | Read `run_suite.py`'s accuracy per direction for each question slice. |
| Audit flags are leads, not verdicts | At margin 0.2: 11 flags (1% of mappings); about 1 in 11 a real error, 2 more needing evidence. Most raw losses were near-ties. | Comparison flags need a minimum margin; a checker's output is a second look. | Review every flag for one window; record real, needs-evidence and noise. |
| Disagreement with rules finds rule bugs first | Conflict triage sided with approvals on 23 conflicts that came from a misfiring deterministic test. | Model and rule disagreements go to a rule-repair queue before the item queue. | Sample disagreements and classify each as a rule defect or a model defect. |
| Observed data beats the model where it exists | Token usage in shipped code agreed with approvals 93 to 97% on property and 84 to 94% on state, the facets where the model was weakest. | Ask the model only where deterministic or observed evidence is absent. | Measure observed evidence against owner gold before adding a question. |
| Gold provenance distorts accuracy | Including rule-derived approvals inflated measured accuracy from 37% to 68%. | Judgment benchmarks exclude convention gold; owner-tier results are reported apart. | Tag every case's `basis`; read the by-basis table; set gate `basis` without `convention`. |

## Applying it in other domains

**Support triage.** A `single-choice` over teams with bands tuned on dev. Expect the calibration shape above: a confident top band, a middle that needs review. The `needs-human` boundary pair is gated per direction, because missing a legal deadline costs more than an extra review.

**Policy and compliance.** `verify-against-rival` over clause labels. Expect few flags and treat each as a lead: in the evidence base, most flags were near-ties or needed more evidence. Owner-tier gold comes from the privacy office, not from a checklist rule.

**Design tokens.** The source project. Where shipped code shows how a token is used, that observed evidence answers first; the model is asked only about tokens with no usage.

## Measuring well

- Keep `owner` gold apart from `agent` and `convention` gold in every report.
- Stratify samples by option and by direction; a mean hides a weak boundary.
- Pin the model version on every run and every gate; a version change makes every number here a prior again.
