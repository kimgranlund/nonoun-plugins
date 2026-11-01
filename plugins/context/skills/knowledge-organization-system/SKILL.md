---
name: knowledge-organization-system
description: >
  Keep a corpus's vocabulary consistent with a lightweight KOS (knowledge organization
  system, a SKOS subset): one vocabulary.yaml of defined concepts, labels and links that
  grows only on evidence, plus a validator. Use for glossaries, terminology, naming
  conventions, "what do we call X", the same thing named differently across files,
  synonyms or ambiguous terms, tagging, categories, taxonomy, information architecture,
  documentation folder structure, domain vocabulary, or onboarding confusion about terms,
  in code, docs, runbooks, policies, research notes or prompts. Not for casual prose,
  one-off answers, marketing copy, code changes with no naming impact, or formal
  ontology and RDF/OWL work.
---

# Knowledge Organization System

Decide which concepts a corpus has, what each one means, which label to use for it, and how concepts relate. The vocabulary file is the single source of truth for terms. Everything else in the corpus (code, docs, specs, runbooks, policies, notes, prompts) uses its labels.

Grow the vocabulary only when the corpus shows a need. Start with almost nothing; never build structure for content that does not exist yet.

## The model

One `vocabulary.yaml` per corpus, with `schemes` (the domains) and `concepts`. Each concept has:

- `id`: stable, never reused; labels may change, the id does not
- `prefLabel`: the one preferred label, unique within its scheme
- `altLabel`: accepted synonyms; `hiddenLabel`: retired or misspelled forms that tools flag
- `definition` (required) and `scopeNote` (optional boundary)
- `broader`, `narrower`, `related`: links to other concept ids
- `scheme`: the declared scheme it belongs to
- `evidence`: where it is used or disputed; `deprecated` and `replacedBy` to retire it

These field names are a stable contract that other tools read. Start from `templates/vocabulary.yaml`. Field semantics, label and relation rules, the validator's rules and examples from three domains are in [references/model.md](references/model.md).

## Stages

The vocabulary moves along a spectrum: flat glossary, then taxonomy (hierarchy), then thesaurus (hierarchy plus associative links). Move one stage at a time, and only when that stage's entry criterion is observed in the corpus.

| Stage | Entry criterion | Allowed change |
|---|---|---|
| 0 Seed | A term has caused confusion or appears under conflicting names | One flat `vocabulary.yaml`, at most 15 concepts, each defined |
| 1 Synonyms | A drifted or duplicate term is observed in the corpus | Add `altLabel` or `hiddenLabel`; rewrite affected docs to the `prefLabel` in the same change |
| 2 Hierarchy | Three or more existing concepts share an obvious parent | `broader`/`narrower` links for that cluster only |
| 3 Schemes | Two domains use one label with different meanings | Split into schemes; disambiguate both definitions |

Allowed artifacts and the gate to leave each stage are in [references/growth.md](references/growth.md), with the rename, merge and retire rules.

## Procedure

1. Look for an existing `vocabulary.yaml` (or a glossary, terms file or wiki page that plays its role). There is one per corpus. If several exist, merging them is the first change. If none exists, Stage 0 starts from `templates/vocabulary.yaml` once step 2 finds evidence.
2. Name the term, where it is used (`path:line`, at least two places) or where it was disputed (a review comment, a question, two docs that contradict). No evidence, no change: say what evidence would justify one and stop.
3. Run the validator; its last line prints the inferred stage. Check which entry criterion the evidence meets. Make only the change that stage allows. If the evidence meets a later stage's criterion, still finish the earlier stage's cleanup first.
4. Make the change the stage allows:
   - New concept: `id`, `prefLabel`, a `definition` in words other than the label, `scheme`, `evidence`.
   - Drift: choose the `prefLabel`; record the other form as `altLabel` (still acceptable) or `hiddenLabel` (must stop), then rewrite the docs that use a hidden form in the same change.
   - Rename: change `prefLabel`, keep `id`, move the old label to `hiddenLabel`, rewrite the corpus.
   - Merge or retire: `deprecated: true` and `replacedBy`; keep the entry.
5. Run `python3 scripts/validate_kos.py vocabulary.yaml --corpus <corpus root>`. Fix every error. Fix or explain every warning.
6. Report the concepts and labels changed, the evidence for each, the docs rewritten, and the validator's last line.

## Rules

- **Evidence before structure.** A concept enters only when it is used in two or more places or is disputed. Record that evidence in the concept's `evidence` field when you add it.
- **Retire, don't delete.** A retired label moves to `hiddenLabel` so tooling can flag lingering use. A concept is deprecated with `replacedBy` pointing to its replacement, and its entry stays.
- **Drift is a defect.** When a doc and the vocabulary disagree, fix one of them in the same change.
- **One vocabulary per corpus**, never one per folder, team or document type. Schemes separate meanings, not files.
- **Never skip a stage** and never add structure for hypothetical future content.
- **Definitions explain.** Name the kind of thing and what distinguishes it. A definition that restates the label explains nothing.
- **Use the vocabulary's labels everywhere** you write in the corpus, including file and folder names, headings, tags and identifiers that readers see.

Anti-patterns to name when you see them:

- speculative taxonomies
- circular definitions, or definitions that restate the label
- hierarchy deeper than the evidence supports
- duplicate vocabularies
- glossary entries nobody references

How to spot and fix each is in [references/growth.md](references/growth.md).

## Validator

```bash
python3 scripts/validate_kos.py VOCABULARY [--corpus PATH ...] [--strict]
```

Standard library plus PyYAML. Deterministic output, one finding per line naming the rule, concept id, field and fix. Exit 1 on any error, so it can run in CI; warnings fail only with `--strict`. Without `--corpus` it checks the file alone; with it, it also reports unreferenced concepts and uses of retired labels. Rule meanings are in [references/model.md](references/model.md).

## Hand-off

This skill decides what a term means and which label to use. When the problem is how a statement is phrased (sentence patterns for requirements, specs, runbook steps, policies or prompts), hand off to the `controlled-natural-language` skill. It references concepts here by `id` and never redefines them; a term it needs that is missing here comes back to this skill first.

## Out of scope

RDF, OWL, axioms and triple stores; automatic term extraction; generating a full vocabulary from a corpus in one pass.

## References

- [references/model.md](references/model.md): load when adding or changing fields, labels or links, reading a validator message, or building a tool that reads the vocabulary.
- [references/growth.md](references/growth.md): load before moving to a new stage, renaming, merging or retiring, or when an anti-pattern is suspected. It ends with an empty-repo to Stage 1 walkthrough.
- [evals/trigger-activation.suite.yaml](evals/trigger-activation.suite.yaml): run when changing this skill's description or scope; the suite format belongs to `evaluation-system`.
