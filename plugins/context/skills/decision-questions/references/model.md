# Question model

Load this when you write or change a question set, an adapter, a decision or a gate reference, when a script message is unclear, or when another tool reads a question set. It is the authority for the typed spine, the decision modes, the adapter contract, which text is governed, and the script rules. Shapes and their eval cases are in [shapes.md](shapes.md); stages and promotion are in [growth.md](growth.md).

## Typed spine (stable contract)

The field names below are published as stable. `classify-and-resolve` and any other consumer read them by these exact names. Rename or remove a field only with a versioned change to every consumer.

```yaml
DecisionModel:      # adapter contract; one implementation per runtime
  ask: (state, questions: {id → Question}) → { answers: {id → Answer}, model_version }

Question:           { id, kind: choice|score|proposition, instructions,
                      options?: {key → OptionDescription},    # choice
                      levels?:  [LevelDescription],           # score, ordered low → high
                      scheme?:  <kos_scheme>, version }
OptionDescription:  { concept_id?, definition, excludes?: [{neighbor, statement}], examples?: [] }
LevelDescription:   { description, examples?: [] }
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

Any key not listed is a `schema` error, so a typo such as `gateIds` cannot silently drop a field. Peer fields keep their owners' names: an option key and `concept_id` are `knowledge-organization-system` concept ids, `excludes` is that skill's `{neighbor, statement}` list copied verbatim, and `gate_ids` name `evaluation-system` gates read by `id`, `question_id`, `status` and `pinned_target_version`.

## QuestionSet

One YAML file per question set: questions, bands and margins in one reviewable file. Start from `templates/question-set.yaml`.

| Field | Type | Required | Meaning |
|---|---|---|---|
| `id` | string | yes | Stable; gates, eval suites and cascade steps name it. |
| `version` | integer or string | yes | Bump it whenever a question, an option, a band or a margin changes. |
| `model` | string | yes | The exact model version the set was measured on, as the adapter reports it. An alias that moves (`latest`, `default`, `stable`, a `-latest` suffix, a `*`) is not a pin. |
| `shape` | enum | yes | `single-choice`, `retrieve-then-choose`, `hierarchical-walk`, `per-value-propositions`, `boundary-pair`, `verify-against-rival` ([shapes.md](shapes.md)). |
| `questions` | list | yes | The questions. Ids are unique within the set. |
| `decisions` | list | yes | How answers become outcomes. May be empty at Stage 0, when answers are only logged. |
| `role` | enum | yes | `checker`, `suggester` or `voter`: the most any outcome in this set may do. |
| `gate_ids` | list of gate ids | no | The `evaluation-system` gates that back the role. |

## Question

| Field | Type | Required | Meaning |
|---|---|---|---|
| `id` | string | yes | Stable within the set; eval cases are tagged with it and a Gate's `question_id` names it. |
| `kind` | enum | yes | `choice` (pick one option), `score` (pick one level), `proposition` (yes or no). |
| `instructions` | string | yes | What the model reads first, as decision-question sentences: the instruction, then any boundary cases. |
| `options` | mapping | with `choice` | Option key to OptionDescription. Keys are concept ids when a vocabulary exists. |
| `levels` | list | with `score` | LevelDescriptions, lowest first; level numbers start at 1. |
| `scheme` | string | no | The KOS scheme the options come from. |
| `version` | integer or string | no | The question's own revision, when one set holds questions that change at different rates. |

An OptionDescription carries `definition` (required), `concept_id` (the KOS concept its text came from), `excludes` (the authored contrast) and `examples` (concrete inputs that belong to it; required on a `none` or general option). A LevelDescription carries `description` and optional `examples`.

## Answer

The adapter returns one Answer per question asked. `value` is the option key for a choice, the level number for a score, and the probability of yes for a proposition. `probabilities` maps every option key, level number or `yes` and `no` to a probability. `confidence` is the probability of the chosen value for a choice or a score; a proposition has none, because raw proposition values are poorly calibrated (see [evidence.md](evidence.md)). `model_version` is what the runtime reports, never what the caller asked for.

## Decisions

A decision turns answers into one outcome. Its `outcome` field names what it produces when it fires; the set's `role` caps what that outcome may do (a `checker`'s `act` still only raises a flag).

**Threshold mode** (choices and scores). With `confidence` from the input's Answer: at or above `bands.act` the decision fires its `outcome`; at or above `bands.review` it returns `review`; below that it returns `defer`. `review` may not exceed `act`, and both lie in [0, 1]. Bands are tuned per question on `dev` cases only.

**Compare mode** (propositions). With `delta` = the input's `value` minus the `rival`'s `value`: at or above `margin` the decision fires its `outcome`; otherwise it returns `defer`. A near-tie never fires. The rival is the proposition the input competes with: the boundary statement's negation (`boundary-pair`) or the same statement for the nearest neighbor (`verify-against-rival`). For an audit flag, the input is the neighbor's statement and the rival is the current one, so the flag fires only when the neighbor wins by the margin.

**Joint labels.** A decision with more than one input combines isolated answers into one label. Questions in one request cannot see each other, so it names an `assemble` validator: code that enforces the label grammar and refuses impossible combinations.

Compare mode needs a proposition input and a proposition rival; threshold mode on a proposition is an error.

## Adapter contract

One adapter per runtime implements `ask(state, questions)`. It sends the questions with the state, returns `{answers: {id → Answer}, model_version}`, and never sends a question the set does not define. Vendor request and response fields belong to the vendor's own skill ([decision-models.md](decision-models.md)).

- **Pin and cache.** A cache is keyed by the request hash plus the model version. When the reported version differs from the set's `model`, the adapter refuses: re-ask, re-run the gates, then re-pin.
- **Untrusted state.** State may hold adversarial text. Send it as data, never as instructions.
- **Target face.** To run under `evaluation-system`'s `run_suite.py`, an adapter also reads one case `input` (`{question_id, state, options?}`, where `options` is the option order to present) as JSON on stdin and writes one JSON value: `{value, confidence, probabilities, outcome, model_version}` for a choice or score, `{answer, delta, probabilities, model_version}` for a proposition, or `{abstain: true, ...}` below the review band or within the margin. The runner's coverage then shows how much the bands or margin left unanswered.

`adapters/fixture.py` is the reference implementation: it replays recorded answers, so tests run without network access or cost.

```bash
python3 adapters/fixture.py --recordings FILE --question-set FILE [--abstain-below review|act|none]
```

A recordings file has `model_version` and `answers`, a list of `{state, question, probabilities}` with an optional `order` (the option order that recording applies to). `state` is the state's `id`, or a hash of the state when it has none. A missing recording, or a `model_version` other than the set's `model`, exits 1.

## Governed text

What the model reads is a `controlled-natural-language` decision-question doc. `validate_questions.py` renders it and runs that skill's `lint_cnl.py` with `templates/decision-question.rules.yaml`.

| Text | Owner | Lint |
|---|---|---|
| `instructions` | this file | Every sentence must fit a pattern: the question instruction, `Answer yes when ...`, `Choose <option> when ...` or a boundary case. |
| `levels[].description` | this file | Rendered as `Level <n> means <description>.` |
| An option without `concept_id`: `definition` and `excludes[].statement` | this file | Words only: banned conjunctions, negations, counting and date comparison. |
| An option with `concept_id`: `definition` and `excludes` | `knowledge-organization-system` | Not linted here. Copied verbatim by the compiler; change it in the vocabulary, where `validate_kos.py` checks it. |
| `examples` | the domain | Not linted: examples are real inputs, negations and all. |

Option slots (`Choose {option} when ...`) resolve against `--vocabulary` when given, else against the set's own option keys.

## Scripts

Standard library plus PyYAML, Python 3.9 or later, deterministic output. Each finding is one line, `SEVERITY RULE SUBJECT FIELD: problem. Fix: fix.`, errors first, then by rule and subject. Exit 0 with no errors, 1 with errors (or warnings under `--strict`), 2 when an input cannot be read. Peer scripts are called as subprocesses by path, never imported.

### validate_questions.py

`python3 scripts/validate_questions.py QUESTION_SET [...] [--gates FILE] [--vocabulary FILE] [--rules FILE] [--lint FILE] [--strict]`

`--rules` and `--lint` default to the `controlled-natural-language` folder beside this skill. Without them the lint is skipped with `peer-absent`.

| Rule | Severity | Fires when | Usual fix |
|---|---|---|---|
| `schema` | error | The file is not YAML, a key is unknown, a required field is missing or mistyped, an id repeats, bands are out of order, or compare mode reads a non-proposition. | Correct the shape against the tables above. |
| `threshold-on-proposition` | error | A threshold decision reads a proposition. | Use compare mode with a rival and a margin. |
| `compare-incomplete` | error | A compare decision has no `rival` or no `margin`. | Name the rival proposition and a margin tuned on dev. |
| `unpinned-model` | error | `model` is missing, blank or a moving alias. | Pin the exact version the adapter reports. |
| `ungated-role` | error | `role` is above `checker` and a question a decision reads has no passed gate in `gates.yaml` among `gate_ids`, with `question_id` naming it and `pinned_target_version` equal to `model`. | Run the per-question gate, or keep the role at `checker`. |
| `missing-question` | error | A decision's `inputs` or `rival` names a question the set does not define. | Correct the id or add the question. |
| `missing-assemble` | error | A decision reads more than one input with no `assemble` validator. | Name the code validator that enforces the label grammar. |
| `cnl` | error or warning | `lint_cnl.py` reports a finding on governed text; the message carries the lint rule and the offending field. | Rewrite the sentence to a decision-question pattern. |
| `peer-absent` | warning | The CNL rules file or linter is missing. | Install `controlled-natural-language` beside this skill, or check phrasing by eye knowingly. |

`fixtures/broken-question-set.yaml` trips each error rule except `schema` once, with no companion files.

### compile_questions.py

`python3 scripts/compile_questions.py VOCABULARY --template FILE --shape single-choice|retrieve-then-choose [--scheme ID] [--concepts ID,...] [--max-options N] [--allow-none] [--run RUN_JSON] [--out FILE]`

It reads the KOS vocabulary by field name (`schemes`, `concepts`, `id`, `definition`, `excludes`, `scheme`, `deprecated`) and builds the template's first question from the selected active concepts: each option keyed by concept id, with `concept_id`, `definition` and `excludes` copied verbatim. It never writes contrast text. The rest of the template (id, version, model, role, gate ids, decisions) is kept. Findings go to stderr; the question set goes to `--out` or stdout, and nothing is written when there is an error. Other shapes are authored by hand from [shapes.md](shapes.md).

| Rule | Severity | Fires when |
|---|---|---|
| `missing-definition` | error | A selected concept has no definition. |
| `too-many-options` | error | `single-choice` with more options than `--max-options` (default 12): use `retrieve-then-choose`. |
| `none-without-examples` | error | `--allow-none`, and no `none` option with examples (from the template or a concept with id `none`). |
| `duplicate-option` | error | Two options share a key. |
| `unknown-selection` | error | `--scheme` or a `--concepts` id is not in the vocabulary, or a selected concept is deprecated. |
| `excludes-outside-options` | warning | An `excludes` neighbor is not in the option set. |
| `unaddressed-confusion` | warning | With `--run`: an `evaluation-system` run's `exact` grader reported one option picked for another, and neither option has an `excludes` entry naming the other. |

### make_eval_cases.py

`python3 scripts/make_eval_cases.py QUESTION_SET --seeds FILE [--holdout-percent N] [--permutations N] [--out FILE]`

Seeds are a YAML list (or a `cases:` list) of `{id, question, state, expected, basis, added_because}` with optional `source`, `split` and `tags`; `expected` is an option key, a level number or `true`/`false`. It writes an `evaluation-system` suite (see that skill's `references/model.md`):

- every case tagged with its `question` id and sliced by it, so a Gate's `question_id` reads only that question;
- standard cases with `expected: {value: ...}` (choice, score) or `expected: {answer: ...}` (proposition), graded by `exact` on `value` or `answer`;
- option-order permutations as `kind: invariance` with `variant_of` (choices: reversed, then rotations; propositions: `[no, yes]`);
- for `boundary-pair`, the rival asked with the answer flipped, as `kind: negation` with `variant_of`;
- splits stratified by expected value, so dev and holdout keep the true and false balance; variants follow their base case's split.

Every case carries its seed's `basis`; variants are `source: adversarial`. It exits 1 when a seed has no `basis` or `added_because`, names an unknown question or option, or when a proposition question's true and false cases are unequal after negations.
