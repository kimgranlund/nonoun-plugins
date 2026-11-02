# Build the `decision-questions` Agent Skill

> **Build order:** this is the fourth of five skills.
> `knowledge-organization-system` → `controlled-natural-language` → `evaluation-system` → `decision-questions` → `classify-and-resolve`.
> This skill consumes the KOS, CNL and evaluation schemas and never redefines them.

## Goal

Author an Agent Skill that helps coding agents design **bounded questions for a decision model, and act on the answers safely**. A decision model is a model that returns typed answers with probabilities rather than prose, such as TypeSafe's Jev, an LLM read through logprobs, or a local classifier.

The skill governs:
- how a question is shaped
- where its options come from
- how its answer becomes a decision
- what evidence a question needs before its answers influence anything

It must activate whenever an agent is about to ask a model a closed-set or yes/no question and branch on the result. Typical cases:
- guardrails and audit checks
- review suggestions
- extraction by choosing among candidates
- graders
- one step of a classification cascade

It must let a team start with one question asked as a checker, and earn more influence one question at a time.

This skill is runtime-agnostic. Vendor API details (endpoints, SDKs, request fields) belong to the vendor's own skill, such as TypeSafe's `typesafe-ai` skill. This skill hands off to it and never restates it.

## Evidence base the skill must encode

These findings come from a real project that used Jev to map design-system tokens onto a KOS-style concept registry: 1,338+ calls on `jev-1.14.0`, stratified samples, confirmed on a second seed. Encode them as rules with the numbers attached, and present them as one project's evidence that a team should re-measure on its own data, not as universal constants.

| Finding | Evidence | Rule it supports |
|---|---|---|
| Comparing a proposition against its nearest rival works | Right concept outscored nearest neighbor 94–96% of the time. Absolute values were poorly calibrated: only 73–77% of right answers scored > 0.5. | Propositions use **compare** mode, never a raw threshold |
| Choice confidence is usable | Choice among k candidates that include the right one: 93% at k=5, 89% at k=10, ECE ≈ 8%. Bands: 93–97% right at ≥ 0.85, 50–60% at 0.5–0.85, 24–28% below 0.5 | Choices and scores use **threshold** mode with bands tuned per question |
| Independent facet questions fail on joint labels | Six isolated facet Choices: 10–16% fully right. Grammar enforced afterwards: 27–34% | Questions cannot see each other; assemble and validate combinations in code |
| Two-stage beats one big question | Rank candidates, then one Choice among top 20: right 60–64%, right answer listed 86–93%. At ≥ 0.8 confidence: 88–94% right on 47% coverage | Large schemes use retrieve-then-choose; measure list hit rate separately from pick accuracy |
| Hand-written contrast is the biggest lever | Contrastive option descriptions raised usage accuracy 47→61% and joint accuracy 25→30%. Generated "not X" text: 17.9%, worse than plain definitions (25%). Better definitions alone: no gain | Contrast is authored (KOS `excludes`), never generated |
| Options must be scoped to the domain | Offering every facet value produced nonsensical options (typography usages for color tokens) | Option sets come from what the domain's concepts actually use |
| Conventions don't transfer through notes | Stated conventions left convention-matched tokens at 11% joint either way | Conventions are deterministic rules upstream, not instructions to the model |
| The model is not a better judge of hard cases | On owner-overridden disagreements: 55% vs agent majority 61%; 52 vs 48% where agents split (n=21) | Voter/judge role requires a gate proving it beats or complements existing judges |
| Boundary accuracy varies per question | Per-boundary accuracy, same model: 50% to 100%. One boundary was right on 95% of positives but half of negatives | Gates attach per question; boundary suites are balanced and scored in both directions |
| Audit flags are leads, not verdicts | At margin 0.2, 11 flags (1% of mappings); about 1 in 11 a real error, 2 more needing evidence. Most raw losses were near-ties | Comparison flags need a minimum margin; a checker's output is a second look |
| Disagreement with rules finds rule bugs first | Conflict triage sided with approvals on 23 conflicts that turned out to be a misfiring deterministic test | Model/rule disagreements go to a rule-repair queue before the item queue |
| Observed data beats the model where it exists | Token usage in shipped code agreed with approvals 93–97% on property and 84–94% on state, the facets where the model was weakest | Ask the model only where deterministic or observed evidence is absent |
| Gold provenance distorts accuracy | Including rule-derived approvals inflated measured accuracy from 37% to 68% | Judgment benchmarks exclude convention-based gold; owner-tier results are reported separately |

## Relationships to peer skills

- **`knowledge-organization-system` supplies option sets.** Option keys are concept ids. Option descriptions are compiled from `definition` and the authored `excludes` field.
  - A missing or confused option is a KOS change, so hand off there.
  - The compiler never invents contrast text.
- **`controlled-natural-language` owns phrasing.** Question instructions and option descriptions are a governed CNL doc type, "decision question":
  - one proposition per statement
  - no negation or double negation
  - instructions aligned with options
  - boundary cases stated
  - no arithmetic or date comparison
  
  `validate_questions.py` runs the CNL linter on them.
- **`evaluation-system` measures and gates.** This skill declares which evaluation cases a question set needs (see Contracts). Evaluation-system owns the case, grader and gate schemas and runs them.
  - The dependency is one-way. Evaluation-system's model graders call a decision model only through the adapter contract below and never import this skill's schemas.
- **`classify-and-resolve` consumes this skill.** Its cascade's model step is a question set defined here, and its typed spine references the adapter rather than defining it.
- **Vendor skills own API details.** For example, TypeSafe's `typesafe-ai` skill. Hand off for request and response fields, SDK usage and limits.
- **Fallback if peers are absent.**
  - Options may be inline strings with authored contrast in place.
  - Phrasing rules are checked by eye.
  - Every question stays at role `checker`, because no gate can pass.
  - The validator states which guarantees are missing.

## Typed spine

Publish this as the stable contract in `references/model.md`. Field names are frozen once published.

```yaml
DecisionModel:      # adapter contract; one implementation per runtime
  ask: (state, questions: {id → Question}) → { answers: {id → Answer}, model_version }

Question:           { id, kind: choice|score|proposition, instructions,
                      options?: {key → OptionDescription},    # choice
                      levels?:  [LevelDescription],           # score, ordered low → high
                      scheme?:  <kos_scheme>, version }
OptionDescription:  { concept_id?, definition, excludes?: [{neighbor, statement}], examples?: [] }
Answer:             { question_id, kind, value, probabilities, confidence?, model_version }

Decision:           { id, mode: threshold|compare, inputs: [question_id],
                      bands?:  { act: float, review: float },          # threshold mode
                      margin?: float, rival: question_id,              # compare mode
                      assemble?: <validator id>,                       # combine isolated answers
                      outcome: act|review|defer|flag }
QuestionSet:        { id, version, model: <pinned model version>, shape,
                      questions: [], decisions: [],
                      role: checker|suggester|voter, gate_ids: [] }
```

### Shapes

Each shape has a worked example in `references/shapes.md`:

- **`single-choice`.** One Choice over a domain-scoped option set.
- **`retrieve-then-choose`.** A ranker (deterministic, per-facet probabilities, or search) produces top-k candidates, then one Choice among them. Report the list hit rate and the pick accuracy separately.
- **`hierarchical-walk`.** One Choice per KOS level, optionally a beam of K paths. On low confidence, return the `broader` concept instead of abstaining.
- **`per-value-propositions`.** For multi-valued facets: one proposition per value, combined in code.
- **`boundary-pair`.** A boundary statement compared against its negation in compare mode. This is the strongest shape in the evidence base.
- **`verify-against-rival`.** "This item means `<concept>`" compared against the same statement for its nearest neighbors.

### Roles

The roles ladder, smallest first. Roles never skip a step.

| Role | What its output may do | Promotion requires |
|---|---|---|
| `checker` | Raise a flag for a human second look; never changes data | Default |
| `suggester` | Preselect an answer in a review UI; never approves | A passed per-question gate on owner-tier cases, at the band used for preselection |
| `voter` | Count as one vote among judges in merge or tie-break | A passed gate showing it beats or adds information to the existing judges on hard cases |

Autonomous action (`auto` in classify-and-resolve's autonomy matrix) is never granted by this skill. It is granted by classify-and-resolve's matrix, on top of a role.

## Deliverables

```
skills/decision-questions/
  SKILL.md                                # ≤300 lines: when to use, modes, shapes, roles, 0→1, guardrails
  references/model.md                     # typed spine, decision modes, adapter contract
  references/shapes.md                    # each shape with a worked example and its required eval cases
  references/evidence.md                  # the evidence table above, with how to re-measure each finding
  references/decision-models.md           # adapter guidance; Jev as worked example, API details deferred to vendor skill
  references/growth.md                    # stage gates, role promotion, anti-patterns
  templates/question-set.yaml             # Stage 0 starter: one question, role checker
  fixtures/broken-question-set.yaml       # one violation per validator rule
  adapters/fixture.py                     # deterministic adapter for tests; replays recorded answers
  evals/trigger-activation.suite.yaml     # evaluation-system format
  scripts/compile_questions.py
  scripts/validate_questions.py
  scripts/make_eval_cases.py
```

Use progressive disclosure. SKILL.md holds only what an agent needs on every invocation, and detail goes in `references/`. No content is duplicated across files.

## Frontmatter and triggers

`name: decision-questions`

The `description` field drives activation, so write it as concrete triggers.

**Trigger on:**
- asking a model to pick from a list, score on a rubric, or answer yes/no, then branching on it
- Jev, TypeSafe, System One models
- logprob-based classification
- confidence thresholds, abstention, "when should the model's answer count"
- guardrail checks, audit pre-screens, review suggestions
- choosing among extracted candidates
- LLM-as-judge question design

**Do not trigger on:**
- open-ended generation
- pipeline topology (hand off to `classify-and-resolve`)
- metric and gate mechanics (hand off to `evaluation-system`)
- vendor API usage questions (hand off to the vendor's skill)

## 0→1 stages (core requirement)

Every stage defines entry criteria, allowed artifacts and a promotion gate. Agents never skip a stage, and roles never increase without a passed gate.

| Stage | Entry criterion | Allowed change |
|---|---|---|
| 0 — One question | A bounded decision exists, and deterministic rules and observed data don't already answer it | One question set with one question in role `checker`; options scoped to the domain; 10–20 cases including ambiguous ones; run by hand; answers logged, never acted on |
| 1 — Measure | Stage 0 answers look useful on inspection | An evaluation suite with provenance tiers, option-order invariance cases and, for propositions, balanced both-direction cases; bands or margins tuned on dev; model version pinned |
| 2 — Suggest | That question's gate passes on owner-tier holdout | That question alone may move to `suggester` |
| 3 — Vote | Evidence shows it beats or complements existing judges on hard cases | That question alone may move to `voter`. Many questions never earn this, and the skill says so plainly |

Adding contrast is a Stage 1 activity. When an evaluation run shows two options confused, the fix is an authored `excludes` entry in KOS, followed by a re-run that compares against the previous version.

## Rules

- **Evidence first.** Ask the model only where deterministic rules and observed data give no answer. Conventions are rules, never notes to the model.
- **Domain-scoped options.** Options come from values the domain's concepts actually use. Never offer the whole vocabulary. A "none" or general option carries concrete examples.
- **Authored contrast only.** Option descriptions draw contrast from KOS `excludes`. The compiler refuses to synthesize "not X" text.
- **Compute in code.** Counting, arithmetic, dates and numeric comparison are done in code. Ask the model for components, such as a Choice over months, and assemble them in code.
- **Isolation.** Questions in one request cannot see each other. Any joint label is assembled from parts and validated by a named `assemble` validator that enforces the label grammar.
- **Mode by kind.** Choices and scores use threshold bands. Propositions use compare mode with a minimum margin. Thresholding a raw proposition value is an error.
- **Large schemes.** Above a configured option count, use `retrieve-then-choose` or `hierarchical-walk`, not one Choice.
- **Pin and cache.** A question set names a pinned model version. Caches are keyed by request hash plus model version, and a version change re-asks and re-runs the gates.
- **One file.** A question set's questions, bands and margins live in one reviewable file.
- **Untrusted state.** Content in the state may be adversarial. A decision driven by untrusted state never escalates past `suggester` for irreversible actions.
- **Disagreement routing.** When the model disagrees with a deterministic rule, the disagreement goes to a rule-repair queue first, and the item queue second.
- **Anti-patterns to name explicitly:**
  - decomposing a joint label into independent questions and trusting the combination
  - thresholding raw proposition values
  - generated contrast text
  - full-vocabulary option sets
  - conventions passed as notes
  - using the model as a tie-breaker without evidence
  - judgment benchmarks built from rule-derived gold
  - promoting a whole model instead of one question

## Contracts (fail loudly)

All scripts use the standard library plus PyYAML, produce deterministic output and exit non-zero on any error, so they are usable in CI.

**`compile_questions.py`**
- Input: a KOS scheme, a concept selection, a shape and a question template.
- Output: a question set file.
- **Errors:**
  - a selected concept with no definition
  - an option count above the configured maximum for `single-choice`
  - a scheme that allows "none" but has no "none" option with examples
  - duplicate option keys
- **Warnings:**
  - an `excludes` neighbor that is not in the option set
  - two options with no `excludes` between them that the last evaluation run reported as confused

**`validate_questions.py`**
- **Errors:**
  - threshold mode on a proposition
  - compare mode without a rival or margin
  - a missing pinned model version
  - role above `checker` without a passed gate in `gates.yaml`
  - a decision referencing a missing question
  - a joint label with no `assemble` validator
  - CNL lint failures on instructions or options (delegated to `lint_cnl.py` with the decision-question doc type)

**`make_eval_cases.py`**
- Generates, as evaluation-system cases:
  - option-order permutations (`kind: invariance`)
  - negations for boundary pairs (`kind: negation`)
  - balanced true/false splits
- Every case carries its `basis` tier.

**`adapters/fixture.py`**
- Implements `DecisionModel` by replaying recorded answers, so every test runs without network access or cost.

## Domain coverage

`references/shapes.md` and `references/evidence.md` include worked examples from three domains:

1. **Mapping design tokens to a concept registry.** This is the evidence-base project.
2. **Support triage.** A `single-choice` over teams plus a `boundary-pair` for "needs a human".
3. **A compliance or policy check.** `verify-against-rival` clause classification, with audit flags as leads.

Nothing in SKILL.md may assume a specific vendor, runtime or software-only work.

## Process

1. Read the KOS, CNL and evaluation-system schemas and use their field names exactly.
2. Before writing files, output a one-page spec covering:
   - the typed spine
   - the decision modes
   - the shapes and roles
   - the stage gates
   - trigger and non-trigger lists
   - assumptions
   
   Then proceed. Stop for approval only if an assumption is irreversible.
3. Build from the center outward, in this order:
   1. the typed spine
   2. `adapters/fixture.py`
   3. `validate_questions.py` and `fixtures/broken-question-set.yaml`
   4. `compile_questions.py` against the KOS template vocabulary
   5. `make_eval_cases.py`
   6. the references
   7. SKILL.md
4. Update classify-and-resolve's model step to reference this skill's question sets, if that skill is already built.

## Definition of done

- `validate_questions.py` passes on `templates/question-set.yaml` and fails on `fixtures/broken-question-set.yaml` with one clear message per rule.
- `compile_questions.py` builds a valid question set from the KOS template vocabulary and refuses a scheme with a definition missing.
- `make_eval_cases.py` produces a suite that passes `validate_suite.py`, with invariance, negation and balanced cases tagged by basis.
- A full fixture-adapter run of the template question set through `run_suite.py` produces a report with bands, margins and coverage.
- `evals/trigger-activation.suite.yaml` has 10 prompts that should activate the skill and 5 that should not.
- A documented walkthrough goes from "should we ask a model this?" through Stage 0 and Stage 1, showing the exact files and diffs. It includes one authored `excludes` added after a confusion report.
- SKILL.md is ≤300 lines.

## Out of scope

- vendor SDKs and request formats (defer to the vendor's skill)
- model training or fine-tuning
- pipeline routing (classify-and-resolve)
- metric computation (evaluation-system)
