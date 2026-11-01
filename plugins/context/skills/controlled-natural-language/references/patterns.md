# Patterns

Load this when you write or change `rules.yaml`, add a pattern, read a linter message, or need a pattern for a doc type you are about to govern. It is the authority for the rules file shape, slot types, how the linter reads a doc, and the linter's rules. Stage gates and change rules are in [growth.md](growth.md). Concept fields (`id`, `prefLabel`, `altLabel`, `hiddenLabel`, `deprecated`, `replacedBy`) mean what the `knowledge-organization-system` skill's `references/model.md` says; this file never redefines them.

## Rules file shape

One `rules.yaml` per corpus, next to the corpus's `vocabulary.yaml`. Start from `templates/rules.yaml`. Any key not listed here is a `schema` error.

| Key | Where | Required | Meaning |
|---|---|---|---|
| `version` | top | no | Rules schema version; `1`. |
| `bannedWords` | top or doc type | no | A list of `{word, fix}`. Top-level words apply to every governed doc type; doc-type words add to them. `word` may be a phrase. |
| `docTypes` | top | yes | The governed doc types. |
| `id` | doc type | yes | Stable doc type id, also the front matter value. |
| `description` | doc type | no | What the doc type is and who reads it. |
| `paths` | doc type | no | Path globs. `**` spans folders; `*` and `?` stay inside one. |
| `patterns` | top | yes | The allowed sentence patterns. |
| `id` | pattern | yes | Stable pattern id; never reused. |
| `docType` | pattern | yes | The doc type id the pattern belongs to. |
| `template` | pattern | yes | Literal words with `{slot}` placeholders, ending in its punctuation. |
| `slots` | pattern | yes | One entry per placeholder, no more, no fewer. |
| `sources` | pattern | yes in practice | The real sentences the pattern was derived from, with `path:line`. Missing is a `no-source` warning. |
| `deprecated`, `replacedBy` | pattern | no | Retire a pattern: `deprecated: true` and the id of the pattern to use instead. |

## Slot types

| Type | Keys | Accepts |
|---|---|---|
| `concept` | `concepts: [id, ...]`, `scheme: id` (both optional) | A concept reference: its `id`, `prefLabel` or `altLabel`, case-insensitive, whitespace collapsed, a leading `the`, `a` or `an` dropped, a trailing `s` or `es` allowed. `concepts` and `scheme` narrow which concepts qualify. An `altLabel` is accepted with an `alt-label` warning, because a slot expects the `prefLabel`. A retired label resolves but the line also gets a `hidden-label` error. |
| `text` | `maxWords: n`, `pattern: regex` (both optional) | Constrained free text. `pattern` must match the whole value (case-insensitive). Use it for measurable values (`\d+ (seconds|minutes)`), commands in backticks or citation keys. |

A slot never holds a definition. A term the slot needs that is missing from the vocabulary goes to `knowledge-organization-system` first.

## How the linter reads a doc

- **Doc type.** Front matter `cnl: <doc type id>` wins. Otherwise the first doc type, by id, whose `paths` glob matches the doc's path relative to the working folder or to the rules file's folder. A doc with no doc type is ungoverned and only counted.
- **Governed text.** Front matter, fenced code, inline code and HTML comments are skipped. Headings, table rows and quote lines are checked for words only. Paragraphs and list items are split into sentences at `.`, `!` or `?` followed by a space and a capital, digit, quote or bracket; each sentence must match a pattern.
- **Matching.** A sentence matches a pattern when the whole sentence fits the template (literal words case-insensitive, spaces flexible) and every slot passes. Active patterns are tried before retired ones, in file order. The linter never parses grammar; the template is the grammar.
- **Words.** Banned words and retired labels match whole words, case-insensitive, with a trailing `s` or `es`, the way the KOS validator matches labels. Retired labels are every `hiddenLabel`, plus every label of a deprecated concept (the fix names its `replacedBy` concept's `prefLabel`).

## Linter

`python3 scripts/lint_cnl.py RULES VOCABULARY [DOC_OR_FOLDER ...] [--strict]`

Each finding is one line, `SEVERITY RULE FILE:LINE: problem Fix: fix`, sorted errors first, then by file and line. Rules-file findings point at the line in `rules.yaml`. The last line counts errors, warnings, governed docs and ungoverned files. Exit 0 with no errors, 1 with errors (or warnings under `--strict`), 2 when an input is missing or the vocabulary cannot be read. With no docs it checks the rules file alone.

| Rule | Severity | Fires when | Usual fix |
|---|---|---|---|
| `schema` | error | The rules file is not YAML, a key is unknown, a pattern names an undeclared doc type, template and slots disagree, a retired pattern lacks a valid `replacedBy`, or front matter names an undeclared doc type. | Correct the shape against the tables above. |
| `unknown-concept` | error | A slot's `concepts` names an id, or its `scheme` a scheme, that the vocabulary does not have. | Add the concept to the vocabulary first, or correct the id. |
| `hidden-label` | error | A retired label appears in governed prose. | Write the `prefLabel` the message names. |
| `banned-word` | error | A banned word or phrase appears in governed prose. | Apply the word's `fix`. |
| `unresolved-slot` | error | A sentence fits a template but a concept slot's value resolves to no concept. | Use a vocabulary label, or add the term to the vocabulary first. |
| `no-pattern` | error | A governed sentence fits no pattern (the message names a text-slot limit it broke, if any). | Rewrite it to a listed template. Add a pattern only through Stage 2. |
| `alt-label` | warning | A concept slot holds an `altLabel`. | Write the `prefLabel`. |
| `deprecated-pattern` | warning | A sentence fits only a retired pattern. | Rewrite it to the `replacedBy` pattern; delete the retired pattern once no doc uses it. |
| `no-source` | warning | A pattern records no source sentence. | Record the sentence it came from, or remove the pattern. |

`fixtures/violations.md`, with `fixtures/rules.yaml` and `fixtures/vocabulary.yaml`, trips every rule once; `fixtures/clean.md` passes with `templates/rules.yaml` and the KOS template vocabulary.

## Catalog by doc type

Each entry is a pattern as it would appear in `rules.yaml`, a source sentence it could come from, and a sentence it rejects. Take a pattern from here only when your own docs show its shape; copy the shape, then record your own sentence in `sources`.

### Software codebase: requirements

The five EARS forms ship in `templates/rules.yaml`: ubiquitous (`The {system} shall {response}.`), event-driven (`When {trigger}, ...`), state-driven (`While {state}, ...`), unwanted behavior (`If {condition}, then ...`) and optional feature (`Where {feature}, ...`). Each has a concept slot for the system and text slots for the rest.

- Source: "When a webhook delivery fails, the delivery service shall retry it 3 times."
- Rejected: "The system should handle failures gracefully." (`should` is a banned word, and the sentence fits no `shall` template.)

A response that names a limit can be tightened with a second pattern rather than a looser one:

```yaml
  - id: ears-latency
    docType: requirement
    template: "The {system} shall {response} within {limit}."
    slots:
      system: {type: concept}
      response: {type: text, maxWords: 12}
      limit: {type: text, pattern: '\d+ (milliseconds|seconds|minutes)'}
    sources: ["requirements/search.md:8: The search service shall return results within 300 milliseconds."]
```

### Software codebase: decision log

ADR bodies (context, options, consequences) stay ungoverned narrative. Govern the one-line decision log that indexes them, where ambiguity costs most:

```yaml
  - id: decision
    docType: decision-log
    template: "{adr}: We will {decision} because {reason}."
    slots:
      adr: {type: text, pattern: 'ADR-\d{3}'}
      decision: {type: text, maxWords: 15}
      reason: {type: text, maxWords: 20}
    sources: ["docs/decisions.md:4: ADR-012: We will store sessions in Redis because restarts drop in-memory sessions."]
```

- Rejected: "ADR-013: We might move to Postgres later." (no pattern; a possibility is not a decision).

### Operations or policy corpus: runbook steps

One instruction per sentence (STE). The step names the action and its object; conditions come first.

```yaml
  - id: step-run
    docType: runbook
    template: "Run {command}."
    slots:
      command: {type: text, pattern: '`[^`]+`'}
    sources: ["runbooks/db-failover.md:6: Run `pg_ctl promote`."]
  - id: step-conditional
    docType: runbook
    template: "If {condition}, page the {role}."
    slots:
      condition: {type: text, maxWords: 12}
      role: {type: concept, scheme: ops}
    sources: ["runbooks/db-failover.md:9: If replication lag exceeds 60 seconds, page the database on-call."]
```

- Rejected: "Run the promote command and then check replication and page someone if needed." (three instructions; split it).

### Operations or policy corpus: compliance statements

```yaml
  - id: obligation
    docType: policy
    template: "The {role} shall {action} within {period}."
    slots:
      role: {type: concept}
      action: {type: text, maxWords: 15}
      period: {type: text, pattern: '\d+ (hours|days|business days)'}
    sources: ["policies/privacy.md:22: The privacy officer shall answer each data subject request within 30 days."]
```

- Rejected: "Requests are answered promptly." (no actor, no period).
- The slot `role` resolves "privacy officer" against the vocabulary. "DSAR" in the action text is fine as an `altLabel`; "privacy ticket" there is a `hidden-label` error, as in the `knowledge-organization-system` model example.

### Research or notes corpus: claims and findings

A claim names what was found, in whom, and the evidence, so a reader can check it.

```yaml
  - id: finding
    docType: findings
    template: "In {sample}, {result} ({evidence})."
    slots:
      sample: {type: text, maxWords: 8}
      result: {type: text, maxWords: 20}
      evidence: {type: text, pattern: '(interview|survey|log) [A-Z]?\d+(, (interview|survey|log) [A-Z]?\d+)*'}
    sources: ["findings.md:3: In 9 of 12 participants, onboarding took longer than one week (interview P3, interview P7)."]
```

- Rejected: "Most users struggle with onboarding." (no sample, no evidence).

### Research or notes corpus: method statements

```yaml
  - id: method
    docType: methods
    template: "We {procedure} each {unit} using {instrument}."
    slots:
      procedure: {type: text, pattern: '(interviewed|surveyed|coded|observed)'}
      unit: {type: concept, scheme: study}
      instrument: {type: text, maxWords: 8}
    sources: ["methods.md:14: We interviewed each participant using the semi-structured guide in appendix A."]
```

- "We interviewed each subject using ..." resolves `subject` to `participant` (its `hiddenLabel` in the KOS research example), so the shape passes and the line gets a `hidden-label` error naming `participant`.
