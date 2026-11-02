# Build the `knowledge-organization-system` Agent Skill

> Build order: this skill first. `controlled-natural-language` depends on its schema and validator.

## Goal

Author an Agent Skill that helps coding agents keep the **vocabulary** of any knowledge corpus consistent. That covers codebases, docs, specs, runbooks, policies, research notes and prompts. The skill governs which concepts exist, what they mean, and how they relate.

It must activate on its own when an agent touches naming, terminology or content structure. It must let a team start with almost nothing and grow the system only as real usage demands.

## Background the skill must encode

**Model.** Use a lightweight subset of SKOS. Each concept has:

- a stable `id`
- `prefLabel` (exactly one per scheme)
- `altLabel` (accepted synonyms)
- `hiddenLabel` (deprecated or misspelled forms that tools should flag)
- `definition` (required) and `scopeNote` (optional)
- `excludes` (optional): a list of `{neighbor, statement}` entries, each saying what this concept is *not* and naming the concept it gets confused with.
  - Add an entry only after a real confusion is observed, such as an evaluation run, a review dispute or a misroute.
  - Write entries by hand. Never generate them.
  - `decision-questions` compiles these into contrastive option descriptions. Measured results show that hand-written contrast is the biggest accuracy lever for decision models, while generated contrast performs worse than none.
- `broader`, `narrower` and `related` links
- `scheme` (the domain the concept belongs to)

**Spectrum.** A KOS ranges from a flat glossary, to a taxonomy (hierarchy), to a thesaurus (hierarchy plus associative links). The skill moves along this spectrum only when evidence requires it. Formal ontologies (OWL, axioms) are out of scope.

**Relationship to `controlled-natural-language`.** This skill is the single source of truth for terms. `controlled-natural-language` governs sentence patterns and references concepts here by `id`; it never redefines them. SKILL.md names that skill and says when to hand off: hand off whenever the problem is how a statement is phrased rather than what a term means.

## Deliverables

```
skills/knowledge-organization-system/
  SKILL.md                      # ≤300 lines: when to use, core model, 0→1 procedure, guardrails
  references/model.md           # full field semantics, relation rules, worked examples
  references/growth.md          # stage gates, promotion/retirement rules, anti-patterns
  evals/trigger-activation.suite.yaml   # activation suite in evaluation-system format
  templates/vocabulary.yaml     # Stage 0 starter, valid against the validator
  fixtures/broken.yaml          # deliberately invalid; one case per validator rule
  scripts/validate_kos.py
```

Use progressive disclosure. SKILL.md holds only what an agent needs on every invocation, and detail goes in `references/`. No content is duplicated across files.

## Frontmatter and triggers

`name: knowledge-organization-system`

The `description` field drives activation, so write it as concrete triggers and include the acronym "KOS".

**Trigger on:**

- glossary, terminology, naming conventions
- "what do we call X"
- the same thing named differently across files
- synonyms or ambiguous terms
- tagging, categories, taxonomy, information architecture
- documentation folder structure, domain vocabulary
- onboarding confusion about terms

**Do not trigger on:**

- casual prose and one-off answers
- marketing copy
- code changes with no naming impact
- formal ontology or RDF work

## 0→1 stages (core requirement)

Every stage defines entry criteria, allowed artifacts and a promotion gate. Agents never skip a stage and never build structure for hypothetical future content.

| Stage | Entry criterion | Allowed change |
|---|---|---|
| 0 — Seed | Any term has caused confusion or appears under conflicting names | One flat `vocabulary.yaml`, ≤15 concepts, each with a definition |
| 1 — Synonyms | A drifted or duplicate term is observed in the corpus | Add `altLabel`/`hiddenLabel`; rewrite affected docs to the `prefLabel` in the same change |
| 2 — Hierarchy | ≥3 existing concepts share an obvious parent | Add `broader`/`narrower` links for that cluster only |
| 3 — Schemes | Two domains use one label with different meanings | Split into concept schemes; disambiguate both definitions |

## Rules

- **Evidence before structure.** A concept enters only when it is used in ≥2 places or is disputed. The skill states the evidence to record when adding one, for example a file path or the conflicting usage.
- **Retire, don't delete.** A retired label moves to `hiddenLabel` so tooling can flag lingering use. A concept is deprecated with a pointer to its replacement.
- **Drift is a defect.** If a doc and the vocabulary disagree, fix one of them in the same change. One vocabulary per corpus; never one per folder.
- **Anti-patterns to name explicitly:**
  - speculative taxonomies
  - circular definitions, or definitions that restate the label
  - hierarchy deeper than the evidence supports
  - duplicate vocabularies
  - glossary entries nobody references

## Contract: `validate_kos.py`

- Uses the standard library plus PyYAML. Output is deterministic. Exits non-zero on any error, so it is usable in CI.
- **Errors:**
  - duplicate `prefLabel` within a scheme
  - a label that collides with another concept's `altLabel` or `prefLabel`
  - missing or empty definition
  - a definition that contains its own `prefLabel` as the whole definition
  - dangling `broader`/`related` ids, or an `excludes` neighbor that is not a concept id
  - an `excludes` entry with an empty statement, or one that names the concept itself
  - cycles in `broader`
  - an unknown scheme
- **Warnings:**
  - a concept unreferenced anywhere in the corpus (when given a corpus path)
  - a Stage 2+ structure present without the entry criterion being met
- Error messages name the concept id, the field and the fix.

## Domain coverage

`references/model.md` and `references/growth.md` include worked examples from three domains:

1. a software codebase (API and domain terms)
2. an operations or policy corpus (runbooks, compliance)
3. a research or notes corpus

Nothing in SKILL.md may assume software-only work.

## Process

1. Before writing files, output a one-page spec covering the YAML schema, stage gates, trigger and non-trigger lists, and assumptions. Then proceed. Stop for approval only if an assumption is irreversible.
2. Build from the center outward, in this order:
   1. the schema in `templates/vocabulary.yaml`
   2. `validate_kos.py` and `fixtures/broken.yaml`
   3. the references
   4. SKILL.md
3. Publish the schema's field names as stable. `controlled-natural-language` will reference them.

## Definition of done

- The validator passes on `templates/vocabulary.yaml`. It fails on `fixtures/broken.yaml` with one clear message per rule.
- `evals/trigger-activation.suite.yaml` lists 10 prompts that should activate the skill and 5 that should not, in `evaluation-system` suite format. Each case has `expected`, `added_because` and a `human` grader. If `evaluation-system` is not built yet, use its typed spine as written in that brief and validate once it exists.
- A documented walkthrough goes from an empty repo through Stage 0 and Stage 1, showing the exact files and diffs at each step.
- SKILL.md is ≤300 lines.

## Out of scope

- RDF/OWL and triple stores
- NLP term extraction
- generating a full vocabulary from a corpus in one pass, which contradicts evidence-driven growth
