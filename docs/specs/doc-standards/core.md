# Core rules for every document

These rules hold for every row of [the registry](README.md). A card adds the rules for its family; where a card and this file disagree, the card wins for its family. The prose authority is the user-level `doc-writing-rules` skill (harness and docs plugins); this file names what it applies and copies none of it.

## Sentences

Simplified Technical English (STE) rules, not its dictionary, except in runbooks and reproduction steps:

- One instruction per sentence. Put the action first, in the imperative.
- One topic per paragraph.
- Use the active voice. Name the actor.
- Keep a procedural sentence to 20 words or fewer, a descriptive sentence to 25 or fewer.
- Use one word for one thing. Take terms from [the glossary](../../references/glossary.md); an unapproved alias is a defect.
- Write numbers, units, and commands exactly. Put a command, path, or key in a code span.

Plain Language (ISO 24495) rules for narrative: state who the reader is and what they must do, lead with the answer, use headings a reader scans, and cut words that carry nothing.

## Requirements: EARS

Write each requirement in one EARS template. Give it a stable ID and an `Acceptance:` line (docs_check S-2 for a file with `doc-type: requirements`).

| Pattern | Template |
|---|---|
| Ubiquitous | The `<system>` shall `<response>`. |
| Event-driven | When `<trigger>`, the `<system>` shall `<response>`. |
| State-driven | While `<state>`, the `<system>` shall `<response>`. |
| Unwanted behavior | If `<condition>`, then the `<system>` shall `<response>`. |
| Optional feature | Where `<feature is present>`, the `<system>` shall `<response>`. |

## Normative words: RFC 2119

In a policy or a requirement, the upper-case keywords carry the RFC 2119 meanings (RFC 8174: only the upper-case form is normative).

| Keyword | Meaning |
|---|---|
| MUST, SHALL, REQUIRED | An absolute requirement. |
| MUST NOT, SHALL NOT | An absolute prohibition. |
| SHOULD, RECOMMENDED | Required unless a stated reason justifies an exception. |
| SHOULD NOT, NOT RECOMMENDED | Prohibited unless a stated reason justifies an exception. |
| MAY, OPTIONAL | Truly optional. |

A file with `doc-type: policy` writes these words in upper case only (docs_check S-5).

## Stable IDs

An ID never changes and is never reused. Retire an item; do not renumber it.

| Item | Form | Home |
|---|---|---|
| Goal | `G-NNN` | `docs/goals/NNN-slug.md` |
| KPI | `K-NNN` | `docs/kpi/NNN-slug.md` |
| Ticket | `T-NNNN` | `.sdlc/NNNN-slug/handoff.md`, stamped by `tickets.py new` |
| Requirement | `REQ-NNN` | the requirements document that states it |
| Decision | `NNNN` | `docs/decisions/NNNN-slug.md` |

## Evidence marks

Mark each claim that rests on evidence:

- `[V]` verified: a command, file, or run in this repository shows it, and the line cites that source.
- `[U]` unverified: stated, inferred, or reported, but not checked against a source.

A report keeps claims, evidence, and inference apart, so a reader weights them.

## Status words

Use only the status words of the record's own schema:

- Tickets: proposed, ready, claimed, paused, blocked, done, dropped ([ticket.json](../../assets/schemas/ticket.json)).
- Goals: proposed, active, achieved, dropped. KPIs: proposed, active, retired (docs_check G-5).
- Planning documents: proposed, accepted, rejected, superseded. Decisions: proposed, accepted, superseded.
- Role results: the key values that `results.py` defines ([prompts.md](prompts.md)).

## Status verbs

A status line about work uses one verb from this closed list, and `report.py` refuses any other verb:

built, verified, merged, closed, filed, released, blocked, deferred, stopped, queued, waiting

The tense is the status. Past tense says the work finished (`recent`), present progressive says it runs now (`now`), and future tense with a trigger says it comes next (`next`), for example "will verify step 2 after the build".

## Controlled handoff words

A clarify handoff takes its Do verbs and its banned hedge words from two closed lists, `CLARIFY_VERBS` and `CLARIFY_HEDGE`. Their one home is `plugins/sdlc/scripts/plan_check.py`, whose `clarify` lint enforces them. This file copies neither list.

## Document type key

A file opts into the type rules with one front matter key, `doc-type:`. The key takes one of four values:

| Value | Rule | What it checks |
|---|---|---|
| `requirements` | docs_check S-2 | each `shall` line starts with a stable ID and a colon, and each requirement has an `Acceptance:` line |
| `runbook` | docs_check S-4 | the file has at least one numbered step line |
| `policy` | docs_check S-5 | normative words are upper case |
| `report` | docs_check S-6 | in `reports/`, each relative link and path code span resolves |

A file without the key gets no type rule. Add the key only to a file that meets its rule.
