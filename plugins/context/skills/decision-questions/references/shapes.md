# Shapes

Load this when you pick a shape for a new question set, when one big question is not working, or when you need the eval cases a shape requires. Field names are in [model.md](model.md); the numbers behind each choice are in [evidence.md](evidence.md).

## Choosing a shape

| The decision | Shape | Mode |
|---|---|---|
| One label from a small, domain-scoped set | `single-choice` | threshold |
| One label from a large set | `retrieve-then-choose` or `hierarchical-walk` | threshold |
| Several values may apply at once | `per-value-propositions` | compare, per value |
| Does this item fall on one side of a stated boundary? | `boundary-pair` | compare |
| Is the current label right, or is a neighbor better? | `verify-against-rival` | compare |

A joint label (a usage plus a state plus a property) is never one question and never a set of independent questions trusted together. Ask each part, then combine them in code with a named `assemble` validator that enforces the label grammar.

Every shape's suite carries standard cases tagged with the question id, each with a `basis`. The rows below add what each shape needs on top; `scripts/make_eval_cases.py` generates the variants.

## single-choice

One Choice over a domain-scoped option set: the values the domain's concepts actually use, plus a general option with examples when items can fall outside. Up to about 12 options (`compile_questions.py --max-options`).

Support triage, the Stage 0 template (`templates/question-set.yaml`): one question `team` over `billing`, `outage`, `account-access` and `none`, a boundary case in the instructions, and a threshold decision with `bands: {act: 0.85, review: 0.5}` and `outcome: flag`.

Eval cases: option-order invariance (reversed and rotated orders; a changed answer fails), at least one case per option, and the boundary cases the instructions state.

## retrieve-then-choose

A ranker produces the top k candidates, then one Choice among them. The ranker may be deterministic (string match on labels), per-facet probabilities, or search. The question's `options` hold the full candidate pool; the adapter sends only the k the ranker kept.

Design tokens to concepts (the evidence-base project): rank the registry's concepts for a token by its name, then one Choice among the top 20. Report two numbers, never one: the list hit rate (the right concept was among the 20) and the pick accuracy (the Choice picked it, given it was listed). A low hit rate is a ranker problem; a low pick accuracy with a high hit rate is a question problem.

Eval cases: standard cases with the right concept, invariance over the candidate order, and cases where the right answer is missing from the list, expecting the general option.

## hierarchical-walk

One Choice per KOS level: the top concepts first, then the children of the one picked, optionally keeping a beam of K paths. On low confidence at a level, return the `broader` concept already picked instead of abstaining. A partly right answer is still useful.

Policy library: choose among `privacy`, `security` and `finance` first, then among the children of `privacy`. Below the review band at the second level, the answer is `privacy`.

Eval cases: one slice per level, so a weak level is visible; cases whose right answer is a parent, expecting the walk to stop there.

## per-value-propositions

For a multi-valued facet: one proposition per value, each in compare mode against a rival, combined in code.

Design tokens: "This token is used for text." and "This token is used for borders." are separate propositions. Code collects every value that fired and validates the combination.

Eval cases: balanced true and false cases per value, scored in both directions.

## boundary-pair

A boundary statement compared against its positive complement in compare mode, with a minimum margin. The strongest shape in the evidence base.

Support triage, `fixtures/needs-human.question-set.yaml`: `needs-human` ("Answer yes when the message needs a person to decide.") against `self-serve` ("Answer yes when a help center article answers the message."), `margin: 0.2`, `outcome: flag`. A near-tie defers.

Eval cases: balanced true and false seeds, plus a `negation` variant of each (the rival asked, the answer flipped), tagged with the base question so its gate reads both directions; invariance with the answer options presented as `no, yes`.

## verify-against-rival

"This item means `<concept>`" compared against the same statement for its nearest neighbors. Used as an audit: the flag fires only when a neighbor outscores the current label by the margin.

Compliance review: each contract clause carries a label such as `retention-limit`. Ask "This clause sets a retention limit." and "This clause sets a deletion duty." for the clause; the decision's input is the neighbor's statement and its rival the current label's, `margin: 0.2`, `outcome: flag`. Flags are leads for a second look, never verdicts: in the evidence base about 1 in 11 was a real error and 2 more needed evidence.

Eval cases: known-good labels (expecting no flag) and seeded mislabels (expecting a flag), balanced, with the margin tuned on dev.
