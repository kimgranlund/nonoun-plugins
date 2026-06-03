---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Abby C., *How to Make Sense of Any Mess: Information Architecture for Everybody* (self-published, 2014). abbycovert.com/make-sense"
  - "Abby C., “Understanding Information Architecture” and collected essays — abbycovert.com/writing (esp. “What do we mean?”, “How to Make Meaning”, “Information, Meaning, Perception & Truth”)"
---

# Covert: Making Sense of Any Mess

This is the working lens for the deepest, most-skipped layer of information architecture: **language**. Abby C.'s _How to Make Sense of Any Mess_ (2014) reframes IA away from sitemaps and screens toward a prior question — what do the words mean, and to whom? Her definition is load-bearing: information architecture is "the practice of deciding how to arrange the parts of something to be understandable," and more sharply, **"the structural design of shared information environments."** Most products that feel "confusing" are not suffering a navigation defect or a visual-design defect; they are suffering a **language defect** that no amount of UI polish can fix. Covert's contribution to product-forge is to put that diagnosis first.

## The one idea that changes everything: you can't make information

Covert's most disorienting and most useful claim: **"We can't actually make information — our users do that for us."** What you ship is _content_ arranged in a _structure_; **information is the interpretation a person forms** when they encounter that arrangement. You author content and structure; the user authors the meaning. This splits every IA decision into two halves that are easy to conflate:

- **Intent** — what _you_ mean the arrangement to communicate. This is yours to set, and you must set it explicitly. "The organization of things is only correct in so far as it helps you reach the intention you have set."
- **Interpretation** — what the _user_ actually understands from it. This is not yours to control; it is yours to _anticipate, test, and respect_.

The gap between intent and interpretation is where products fail silently. A label is "right" not when it satisfies the org chart but when it is interpreted as intended by the audience. The working move: for any contested label, taxonomy node, or screen title, write down the intended interpretation in one sentence, then go find out what users actually infer. A divergence is a finding, not an opinion.

## The three layers: ontology, taxonomy, choreography

Covert (crediting Dan Klyn's framing) stacks IA into three layers. They are ordered by depth — **ontology is bedrock, choreography is surface** — and a product can only be as coherent as its lowest unsettled layer.

| Layer | The question it answers | The product failure when it's skipped |
| --- | --- | --- |
| **Ontology** | _What do we mean?_ The act of deciding what words and concepts mean **in this specific context** — and what they explicitly do not mean. | The same word means three things across the app ("project," "workspace," "board"); teams argue past each other; the model is never agreed. |
| **Taxonomy** | _How is it arranged?_ How the agreed concepts are grouped, ordered, and related into categories. Covert: taxonomy is "a tool of rhetoric, not an exact science." | Categories that mirror departments, overlap, or split things users see as one. The arrangement persuades the wrong thing. |
| **Choreography** | _How does it flow over time?_ The rules for how the structure behaves as a person moves through it across screens, states, and sessions. | Each screen is locally sensible but the path between them contradicts itself; the system "forgets" what the user just did. |

The discipline: **do not negotiate taxonomy until ontology is settled.** Two people sorting cards into "Marketing" vs. "Growth" are not having a taxonomy fight; they have an unresolved ontology — they don't agree what those words mean. Naming the layer the disagreement actually lives in is half the fix.

## Ontology in practice: pin the words before the pixels

Ontology work is unglamorous and decisive. Covert's stance — "the goal is not simplifying… it is to know what you mean when you say what you say" — argues against premature wireframing. Concrete moves:

- **Build a controlled vocabulary for the contested terms.** For each core noun, write one sentence: what it _is_, what it is _not_, and one example. This is the product's dictionary, and it is an IA deliverable, not a glossary afterthought. (Covert distinguishes _lexicography_ — compiling the dictionary — from _ontology_ — deciding the meanings that go in it.)
- **Hunt synonyms and homonyms.** Synonyms (two words, one concept: "client" / "customer") bloat the model and split search. Homonyms (one word, two concepts: "report" the document vs. "report" the action) are worse — they fracture meaning silently. Resolve each: pick one word per concept, one concept per word.
- **Use the users' words, not the company's.** Covert: "Language matters… the hardest lesson for most organizations to turn into practice." The org's internal name for a thing is frequently the worst possible label because it encodes politics, not user mental models.
- **Make the disagreement visible.** When stakeholders can't agree on a word, that is the finding. Surfacing it early is cheaper than discovering it after the taxonomy, the URLs, the API field names, and the help docs have all hard-coded the ambiguity.

## "The things we make people understand" — IA is bigger than digital

Covert deliberately de-couples IA from screens: it is "any method of order applied to the pieces of something to make the whole more understandable to someone" — a reorganized pantry, a chore chart, and a checkout flow are the same discipline. For product work this matters because **the IA you are responsible for spans every surface that uses the words**: the UI, yes, but also notifications, emails, error messages, the API, the docs, the sales deck, and the support macros. If "project" means one thing in the app and another in the billing email, you have an ontology leak across surfaces, and the user — who experiences all of them as one product — pays for it.

## Tells of good vs. bad (for scoring)

| Dimension | Bad | Good |
| --- | --- | --- |
| **Intent stated** | Labels and structure chosen by feel; no one can say what a given arrangement is _meant_ to communicate | The intended interpretation of each contested label/grouping is written down and can be tested against it |
| **Layer diagnosis** | Taxonomy debated while the underlying words are still ambiguous; people argue past each other | Disagreements are placed at the right layer; ontology settled before taxonomy is negotiated |
| **Vocabulary** | Synonyms split the model; homonyms fracture it silently; org jargon used as labels | One word per concept, one concept per word; a controlled vocabulary in the users' language |
| **Interpretation respected** | Designer's intent assumed to equal user understanding; never validated | Intent vs. interpretation treated as two things; the gap is measured (card sort, tree test, comprehension check) |
| **Surface coherence** | A term means different things in the app, the email, the API, and the docs | The same concept carries the same word and meaning across every shared surface |
| **Sequence as content** | Order/flow treated as a layout afterthought | Choreography designed deliberately; the path between screens reinforces, not contradicts, the model |

## One labeled caveat

The verbatim phrasings attributed above — "the structural design of shared information environments," "we can't actually make information — our users do that for us," "any method of order applied to the pieces of something to make the whole more understandable to someone," and "the goal is not simplifying… it is to know what you mean when you say what you say" — are drawn from Covert's _How to Make Sense of Any Mess_ (2014) and her published essays at abbycovert.com, cross-checked across multiple summaries and her own site in this session rather than against a page-numbered print copy. The ontology / taxonomy / choreography stack is Covert's, with the three-part framing credited by Covert to Dan Klyn (The Understanding Group). The concepts are unambiguous across sources; confirm exact wording and page against the print edition before publishing a direct quote.
