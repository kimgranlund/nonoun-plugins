# Vocabulary model

Load this when you add or change a field, a label or a link, when a validator message is unclear, or when another tool reads the vocabulary file. It is the authority for the file shape, field semantics, relation rules and validator rules. Stage rules live in [growth.md](growth.md).

## File shape (stable contract)

One YAML file per corpus, usually `vocabulary.yaml` at the corpus root. The top level has three keys:

| Key | Required | Content |
|---|---|---|
| `title` | no | A name for the vocabulary. |
| `schemes` | yes | A list of `{id, definition, scopeNote}`; at least one. A scheme is the domain a concept belongs to. |
| `concepts` | yes | A list of concepts (may be empty). |

The concept field names below are published as stable. `controlled-natural-language` and any other consumer read them by these exact names. Rename or add a field only with a versioned change to every consumer.

| Field | Type | Required | Meaning |
|---|---|---|---|
| `id` | string | yes | Stable identifier. Lowercase kebab-case by convention (`change-request`). Never reused, never changed after anything references it; labels can change, the id cannot. |
| `prefLabel` | string | yes | The preferred label. Exactly one per concept, unique within its scheme. |
| `altLabel` | list of strings | no | Accepted synonyms and abbreviations. Using one is not drift. |
| `hiddenLabel` | list of strings | no | Retired, deprecated or misspelled forms. Tools flag any use of them. |
| `definition` | string | yes | What the concept means in this corpus, in words other than its label. |
| `scopeNote` | string | no | What the concept includes and excludes; the boundary with a neighbor. |
| `broader` | list of ids | no | Parent concepts (Stage 2). |
| `narrower` | list of ids | no | Child concepts; the inverse of `broader` (Stage 2). |
| `related` | list of ids | no | Associative links between concepts that are neither parent nor child. |
| `scheme` | string | yes | The id of a declared scheme. |
| `evidence` | list of strings | no | Where the concept is used or disputed: `path:line`, a review link, or the conflicting usage. Record it whenever a concept or label is added. |
| `deprecated` | boolean | no | `true` retires the concept. It stays in the file so old references resolve. |
| `replacedBy` | id | with `deprecated` | The concept to use instead. Required when `deprecated` is true. |

Any other key is a `schema` error, so a typo such as `synonyms` or `preflabel` cannot silently drop data.

## Labels

- Labels compare case-insensitively with whitespace collapsed: `Change  Request` equals `change request`.
- Label rules apply within one scheme. The same label in two schemes is the Stage 3 case and is valid.
- Within a scheme, a `prefLabel` belongs to one concept (`duplicate-preflabel`), and no `altLabel` or `hiddenLabel` may equal another concept's `prefLabel` or `altLabel` (`label-collision`). A label that means two things in one scheme is the ambiguity this file exists to remove.
- A deprecated concept's labels are retired labels. It is left out of the two label rules, so its `prefLabel` may also sit in the replacement's `hiddenLabel`.
- Corpus matching is whole-word and case-insensitive and accepts a trailing `s` or `es`, so `change requests` counts as a use of `change request`. Matching is literal: it does not stem, translate or resolve pronouns.

## Definitions

- Name the kind of thing, then what distinguishes it from its neighbors: "A recorded proposal to alter production that names its risk, owner and rollback."
- The validator rejects only the extreme case, a definition that is the label itself (`A pager.`). Also avoid definitions that lean on the label ("A change request is a request for a change"), and pairs that define each other (A uses B, B uses A). Both pass the validator and still fail a reader.
- Write the definition for this corpus, not the dictionary. If a reader could swap in the general meaning without losing anything, the concept may not need an entry.
- Use `scopeNote` for exclusions ("Excludes emergency fixes, which follow the incident runbook").

## Relations

- `broader` and `narrower` express "is a kind of" or "is a part of" as the corpus uses it. Write one direction, preferably `broader` on the child; the validator reads `narrower` as the inverse and does not require both. A concept may have several parents.
- The `broader` chain must not loop back to a concept (`broader-cycle`).
- `related` is symmetric and associative ("see also"): `incident` related to `postmortem`. It arrives with Stage 2, when evidence shows readers confuse or consult two distinct concepts together. Do not use it for a parent or child, and do not use it to express sameness. Two concepts that mean the same thing are one concept with an `altLabel`.
- `replacedBy` points from a deprecated concept to its successor. Every link target must be an existing id (`dangling-link`).

## Validator

`python3 scripts/validate_kos.py VOCABULARY [--corpus PATH ...] [--strict]`

Each finding is one line, `SEVERITY RULE CONCEPT FIELD: problem. Fix: fix.`, sorted errors first, then by rule and concept. The last line counts errors and warnings and prints the inferred stage. Exit 0 with no errors, 1 with errors (or with warnings under `--strict`), 2 when the file or a corpus path cannot be read. `--corpus` takes a file or folder and skips hidden folders, dependency folders, binary files and the vocabulary file itself.

| Rule | Severity | Fires when | Usual fix |
|---|---|---|---|
| `schema` | error | The file is not YAML, a required key is missing, a field is unknown or has the wrong type, an id repeats, or `deprecated` lacks `replacedBy`. | Correct the shape against the tables above. |
| `duplicate-preflabel` | error | Two active concepts in one scheme share a `prefLabel`. | Merge them (deprecate one) or give one a distinct label. |
| `label-collision` | error | An `altLabel` or `hiddenLabel` equals another concept's `prefLabel` or `altLabel` in the scheme. | Keep the label on one concept. |
| `missing-definition` | error | `definition` is absent or blank. | Write it. |
| `circular-definition` | error | The definition is only the `prefLabel` (ignoring case, a leading article and a final period). | Define it in other words. |
| `dangling-link` | error | A `broader`, `narrower`, `related` or `replacedBy` target is not a concept id. | Correct the id or add the concept with evidence. |
| `broader-cycle` | error | The hierarchy loops. | Remove the link that makes a concept its own ancestor. |
| `unknown-scheme` | error | `scheme` is missing or not declared under `schemes`. | Use a declared scheme. |
| `stage-gate` | warning | A parent has fewer than three children, or several schemes are declared but no label is used in two of them. | Remove the structure until its entry criterion holds. |
| `unreferenced` | warning | With `--corpus`: no file uses the concept's id, `prefLabel` or any `altLabel`. | Deprecate or drop it, or point `--corpus` at where it is used. |
| `retired-label-used` | warning | With `--corpus`: a `hiddenLabel`, or any label of a deprecated concept, appears in a file. | Rewrite the line to the `prefLabel` (of the replacement, for a deprecated concept). |

`fixtures/broken.yaml` trips every rule once; `fixtures/corpus/` supplies the two corpus warnings.

## Worked examples

### Software codebase (API and domain terms)

The API says `workspace`, the UI says `project`, the database table is `orgs`. They name one thing.

```yaml
schemes:
  - id: product
    definition: Domain and API terms of the billing service and its web app.
concepts:
  - id: workspace
    prefLabel: workspace
    altLabel: [project]          # the UI label, kept until the UI copy changes
    hiddenLabel: [org, orgs]     # the legacy table name; flagged in new docs and code comments
    definition: The billable container that owns members, API keys and invoices.
    scopeNote: Excludes personal accounts, which have no members.
    scheme: product
    evidence: [api/openapi.yaml:88, web/src/nav.tsx:12, db/schema.sql:4]
  - id: invoice
    prefLabel: invoice
    definition: A monthly statement of charges issued to one workspace.
    scheme: product
    evidence: [api/openapi.yaml:140, docs/billing.md:3]
```

### Operations or policy corpus (runbooks, compliance)

A policy says "data subject request", the runbook says "DSAR", support macros say "privacy ticket".

```yaml
schemes:
  - id: compliance
    definition: Privacy policy, its runbooks and the support macros that apply it.
concepts:
  - id: data-subject-request
    prefLabel: data subject request
    altLabel: [DSAR]
    hiddenLabel: [privacy ticket]
    definition: A person's formal request to access, correct or erase the personal data held about them, with a legal response deadline.
    scopeNote: Excludes general privacy questions, which have no deadline.
    scheme: compliance
    evidence: [policies/privacy.md:22, runbooks/dsar.md:1, "support macro 'privacy ticket' (2026-10 audit)"]
```

### Research or notes corpus

Notes use "participant", "subject" and "respondent" for people in a study; the methods chapter uses "participant".

```yaml
schemes:
  - id: study
    definition: Notes, protocols and drafts for one interview study.
concepts:
  - id: participant
    prefLabel: participant
    altLabel: [respondent]       # survey sections; same people, same consent
    hiddenLabel: [subject]       # the ethics board asked us to stop using it
    definition: A person who consented to take part in the study and supplied data.
    scopeNote: Excludes people screened out before consent.
    scheme: study
    evidence: [methods.md:14, notes/2026-09-03.md:2, "ethics review letter, item 3"]
```
