---
name: controlled-natural-language
description: >
  Write and review high-stakes statements in a controlled natural language (CNL): a small,
  evidence-gated set of sentence patterns per document type, checked by a linter against
  the corpus vocabulary. Use for requirements, specs, ADRs, acceptance criteria, runbooks,
  SOPs, policies, compliance language, prompts and system prompts, and style guides for
  them; for questions written for a decision model (choice options, score levels, yes/no
  propositions); for ambiguous, vague or inconsistent phrasing; and for "make this precise",
  "testable" or "unambiguous". Not for casual prose or one-off chat answers, marketing or
  narrative copy, code comments, or naming questions (which term to use belongs to
  knowledge-organization-system).
---

# Controlled Natural Language

Make statements that humans can read and tools can check. A governed document type allows only a few sentence patterns, each slot of a pattern points at the corpus vocabulary, and a linter reports every sentence that does not fit. The rule set starts with a handful of patterns for one document type and grows only when real usage demands it.

It draws on three traditions:

- **ASD-STE100 (Simplified Technical English):** one word, one meaning; approved vocabulary; short sentences; active voice; one instruction per sentence.
- **EARS (Easy Approach to Requirements Syntax):** templates by requirement type: ubiquitous ("The `<system>` shall `<response>`"), event-driven ("When `<trigger>`, ..."), state-driven ("While `<state>`, ..."), unwanted behavior ("If `<condition>`, then ..."), optional feature ("Where `<feature>`, ...").
- **Attempto Controlled English:** deterministic interpretation; each sentence has exactly one reading.

## Hand-off: terms belong to knowledge-organization-system

The `knowledge-organization-system` skill and its `vocabulary.yaml` are the single source of truth for terms. This skill references concepts by `id` or label and never defines, redefines or aliases them. Hand off whenever the problem is what a term means or which term to use:

- a slot value that resolves to no concept (`unresolved-slot`), or a rule naming a missing concept (`unknown-concept`);
- two words in governed prose that may name one thing;
- a request to add a synonym, a definition or a retired label.

Add the term there with evidence, then come back. A term never goes into `rules.yaml`.

## The model

- A **governed document type** is a kind of document whose sentences must fit patterns: requirements, a runbook's steps, a policy's obligations, a findings list. A doc belongs to a type through a `paths` glob in `rules.yaml` or front matter `cnl: <doc type id>`.
- A **pattern** is a template with typed slots, for example `When {trigger}, the {system} shall {response}.` Literal words are fixed; slots vary.
- A **slot** is either a `concept` reference, resolved against the vocabulary by `id`, `prefLabel` or `altLabel` (optionally narrowed to listed concepts or a scheme), or constrained `text` (`maxWords`, a whole-value `pattern` regex).
- Each pattern records `sources`: the real sentences it was derived from, with `path:line`.
- A **banned word** list names words and phrases that caused misreadings, each with its fix.
- A retired pattern keeps `deprecated: true` and `replacedBy` until no governed doc uses it.

Start from `templates/rules.yaml`, or `templates/decision-question.rules.yaml` for questions a decision model answers. Field tables, slot rules, how the linter reads a doc, and a pattern catalog for requirements, decision logs, runbooks, compliance statements, findings, methods and decision questions are in [references/patterns.md](references/patterns.md).

## Stages

Every change happens at one stage, for one doc type. Never skip a stage and never write a pattern for content that does not exist yet.

| Stage | Entry criterion | Allowed change |
|---|---|---|
| 0 Seed | One document type has caused errors or ambiguity | `rules.yaml` with 3 to 5 patterns for that single type, plus a short banned-word list |
| 1 Enforce | Stage 0 patterns exist | Run the linter on that doc type; rewrite violations; refine patterns from real failures |
| 2 Extend patterns | The same unpatterned sentence shape appears 3 or more times | Add one pattern per observed shape, with source examples recorded |
| 3 Extend doc types | The current doc type passes the linter cleanly | Govern one additional doc type, starting again at Stage 0 for it |

Allowed artifacts, the gate to leave each stage, and the add, promote, retire and rename rules are in [references/growth.md](references/growth.md), which ends with a walkthrough from an ungoverned doc type through Stage 0 and Stage 1.

## Procedure

1. **Find the rules.** Look for `rules.yaml` next to the corpus's `vocabulary.yaml`. If the vocabulary is missing, start it with `knowledge-organization-system`: slots have nothing to resolve against without it.
2. **Name the evidence.** For a new doc type: the failure it caused (a defect, a dispute, a misread step) with a link or `path:line`. For a new pattern: three sentences of one shape. No evidence, no rule change: rewrite the sentence at hand to the nearest existing pattern, say what evidence would justify a new rule, and stop.
3. **Pick the stage** whose entry criterion the evidence meets, for that doc type only. Make only the change that stage allows.
4. **Seed (Stage 0).** Copy `templates/rules.yaml`. Keep one doc type; keep only the patterns whose shapes the docs show (3 to 5), and record each source sentence. Keep the banned words that caused the failure. Every concept slot must resolve: missing terms go to the vocabulary first.
5. **Enforce (Stage 1).** Run the linter on the doc type. Rewrite each violation to a pattern. When a failure shows a rule is too loose or a word misleads, refine the rule and record the failure.
6. **Check.** Run `python3 scripts/lint_cnl.py rules.yaml vocabulary.yaml <governed docs>`. Fix every error; fix or explain every warning. Ship rules and rewritten docs in one change.
7. **Report** the doc type, stage, patterns added or retired with their sources, the sentences rewritten, any term handed to the vocabulary, and the linter's last line.

When you only write or review a statement and no rule set exists, still apply the traditions: one statement per sentence, an actor, active voice, measurable values, vocabulary labels. Offer Stage 0 only when the user names a failure.

## Rules

- **Evidence before rules.** Every pattern records at least one real source sentence it was derived from.
- **Reference, don't define.** Slots point to vocabulary concepts. A term missing from the vocabulary goes to the vocabulary first, never into `rules.yaml`.
- **Retire, don't delete.** A deprecated pattern keeps a pointer to its replacement until no governed doc uses it.
- **Drift is a defect.** If governed prose and the rules disagree, fix one of them in the same change.
- **One reading per sentence.** A pattern that admits two readings of one sentence is split or tightened, not documented.
- **Govern statements, not narrative.** Context, rationale and discussion stay ungoverned prose; govern the statements a reader must act on or test.

Anti-patterns to name when you see them:

- rules that redefine terms
- patterns written before any example exists
- governing every doc type at once
- catch-all patterns that accept any sentence
- style preferences disguised as rules

How to spot and fix each is in [references/growth.md](references/growth.md).

## Linter

```bash
python3 scripts/lint_cnl.py RULES VOCABULARY [DOC_OR_FOLDER ...] [--strict]
```

Standard library plus PyYAML, Python 3.9 or later. It reads the vocabulary by the field names `knowledge-organization-system` publishes and does not validate it (run that skill's `validate_kos.py` for that). Output is deterministic, one finding per line with file, line, rule id and fix; a label swap names the `prefLabel` to use. Exit 1 on any error, so it can run in CI; warnings fail only with `--strict`.

Errors: `hidden-label` (a retired label in governed prose), `no-pattern` (a governed sentence fits no pattern), `unresolved-slot` (a concept slot resolves to nothing), `banned-word`, `unknown-concept` (a rule names a concept id the vocabulary lacks), and `schema`. Warnings: `alt-label` (an `altLabel` where a `prefLabel` is expected), `no-source` (a pattern with no recorded source), `deprecated-pattern`. Rule details are in [references/patterns.md](references/patterns.md).

## Out of scope

Full grammar parsers and NLP-based semantic analysis; machine translation; governing casual or narrative writing.

## References

- [references/patterns.md](references/patterns.md): load when writing or changing `rules.yaml`, choosing a pattern for a doc type, or reading a linter message.
- [references/growth.md](references/growth.md): load before moving a doc type to a new stage, adding, promoting or retiring a pattern, or when an anti-pattern is suspected. It ends with the Stage 0 to Stage 1 walkthrough.
- [evals/trigger-activation.suite.yaml](evals/trigger-activation.suite.yaml): run when changing this skill's description or scope; the suite format belongs to `evaluation-system`.
