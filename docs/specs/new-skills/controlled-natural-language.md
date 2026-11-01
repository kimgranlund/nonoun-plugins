# Build the `controlled-natural-language` Agent Skill

> Build order: after `knowledge-organization-system`. This skill reads that skill's vocabulary schema and never redefines terms.

## Goal

Author an Agent Skill that helps coding agents write **statements** that humans can read and tools can check. It applies across specs, requirements, ADRs, acceptance criteria, runbooks, policies and prompts. The skill governs which sentence patterns are allowed in governed document types, and how those sentences use vocabulary terms.

It must activate on its own when an agent writes or reviews high-stakes prose. It must let a team start with a handful of patterns and grow the rule set only as real usage demands.

## Background the skill must encode

Draw on three traditions:

- **ASD-STE100 (Simplified Technical English).** One word, one meaning. Use approved vocabulary, short sentences, active voice, and one instruction per sentence.
- **EARS (Easy Approach to Requirements Syntax).** Use templates for requirement types:
  - ubiquitous: "The `<system>` shall `<response>`"
  - event-driven: "When `<trigger>`, …"
  - state-driven: "While `<state>`, …"
  - unwanted behavior: "If `<condition>`, then …"
  - optional feature: "Where `<feature>`, …"
- **Attempto Controlled English.** Deterministic interpretation: each sentence has exactly one reading.

A pattern is a template with typed slots. A slot is either a concept reference (resolved against the vocabulary by `id` or label) or a constrained free-text field.

**Relationship to `knowledge-organization-system`.** That skill is the single source of truth for terms. This skill references its concepts and never defines, redefines or aliases them. SKILL.md names that skill and says when to hand off: hand off whenever the problem is what a term means or which term to use.

## Deliverables

```
skills/controlled-natural-language/
  SKILL.md                      # ≤300 lines: when to use, pattern model, 0→1 procedure, guardrails
  references/patterns.md        # pattern catalog by document type, with examples
  references/growth.md          # stage gates, pattern promotion/retirement, anti-patterns
  evals/trigger-activation.suite.yaml   # activation suite in evaluation-system format
  templates/rules.yaml          # Stage 0 starter rule set, valid against the linter
  fixtures/violations.md        # prose with one violation per linter rule
  scripts/lint_cnl.py
```

Use progressive disclosure. SKILL.md holds only what an agent needs on every invocation, and detail goes in `references/`. No content is duplicated across files.

## Frontmatter and triggers

`name: controlled-natural-language`

The `description` field drives activation, so write it as concrete triggers and include the acronym "CNL".

**Trigger on:**

- writing or reviewing requirements, specs, ADRs, acceptance criteria
- runbooks, SOPs, policies, compliance language
- prompts and system prompts
- style guides
- ambiguous, vague or inconsistent phrasing
- "make this precise / testable / unambiguous"

**Do not trigger on:**

- casual prose and one-off chat answers
- marketing or narrative copy
- code comments
- naming questions (hand off to `knowledge-organization-system`)

## 0→1 stages (core requirement)

Every stage defines entry criteria, allowed artifacts and a promotion gate. Agents never skip a stage and never write patterns for hypothetical content.

| Stage | Entry criterion | Allowed change |
|---|---|---|
| 0 — Seed | One document type has caused errors or ambiguity | `rules.yaml` with 3–5 patterns for that single type, plus a short banned-word list |
| 1 — Enforce | Stage 0 patterns exist | Run the linter on that doc type; rewrite violations; refine patterns from real failures |
| 2 — Extend patterns | The same unpatterned sentence shape appears ≥3 times | Add one pattern per observed shape, with source examples recorded |
| 3 — Extend doc types | The current doc type passes the linter cleanly | Govern one additional doc type, starting again at Stage 0 for it |

## Rules

- **Evidence before rules.** Every pattern records at least one real source sentence it was derived from.
- **Reference, don't define.** Slots point to vocabulary concepts. A term missing from the vocabulary goes to the vocabulary first, never into `rules.yaml`.
- **Retire, don't delete.** A deprecated pattern keeps a pointer to its replacement until no governed doc uses it.
- **Drift is a defect.** If governed prose and the rules disagree, fix one of them in the same change.
- **Anti-patterns to name explicitly:**
  - rules that redefine terms
  - patterns written before any example exists
  - governing every doc type at once
  - catch-all patterns that accept any sentence
  - style preferences disguised as rules

## Contract: `lint_cnl.py`

- Uses the standard library plus PyYAML. Output is deterministic. Exits non-zero on any error, so it is usable in CI.
- **Inputs:** `rules.yaml`, the vocabulary file from `knowledge-organization-system`, and paths to governed docs. Doc type is resolved by path glob or frontmatter.
- **Errors:**
  - a `hiddenLabel` used in governed prose
  - a sentence in a governed doc type that matches no pattern
  - a slot whose value fails to resolve to a vocabulary concept
  - a banned word
  - a rule referencing a concept id missing from the vocabulary
- **Warnings:**
  - an `altLabel` used where a `prefLabel` is expected
  - a pattern with no recorded source example
- Messages give file, line, rule id and the suggested fix. Where the fix is a label swap, include the `prefLabel` to use.

## Domain coverage

`references/patterns.md` and `references/growth.md` include worked examples from three domains:

1. a software codebase (requirements, ADRs)
2. an operations or policy corpus (runbook steps, compliance statements)
3. a research or notes corpus (claims, findings, method statements)

Nothing in SKILL.md may assume software-only work.

## Process

1. Read the `knowledge-organization-system` schema and use its field names exactly.
2. Before writing files, output a one-page spec covering the rule schema, slot types, stage gates, trigger and non-trigger lists, and assumptions. Then proceed. Stop for approval only if an assumption is irreversible.
3. Build from the center outward, in this order:
   1. the schema in `templates/rules.yaml`
   2. `lint_cnl.py` and `fixtures/violations.md`
   3. the references
   4. SKILL.md

## Definition of done

- The linter passes on a clean sample doc using the template rules and template vocabulary. It fails on `fixtures/violations.md` with one clear message per rule.
- `evals/trigger-activation.suite.yaml` lists 10 prompts that should activate the skill and 5 that should not, in `evaluation-system` suite format. Each case has `expected`, `added_because` and a `human` grader. If `evaluation-system` is not built yet, use its typed spine as written in that brief and validate once it exists.
- A documented walkthrough goes from an ungoverned doc type through Stage 0 and Stage 1, showing the exact files and diffs at each step.
- SKILL.md is ≤300 lines.

## Out of scope

- full grammar parsers and NLP-based semantic analysis
- machine translation
- governing casual or narrative writing
