---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "S. R. Ranganathan, *Colon Classification* (Madras Library Association, 1933) — the first faceted (analytico-synthetic) classification; the PMEST facet formula."
  - "Donna Spencer, *Card Sorting: Designing Usable Categories* (Rosenfeld Media, 2009)."
  - "Heather Hedden, *The Accidental Taxonomist*, 2nd ed. (Information Today, 2016); and “Faceted Classification and Faceted Taxonomies” (hedden-information.com)."
  - "Nielsen Norman Group — “Card Sorting vs. Tree Testing” and “Open vs. Closed Card Sorting” (nngroup.com)."
---

# Taxonomy & Classification

This is the working method for the _arrangement_ layer of IA: how the agreed concepts get grouped, named, and structured into a navigable system — and, just as importantly, how you **validate** that structure with users instead of shipping the org chart. Taxonomy is where Covert's ontology (settled meanings) becomes Rosenfeld/Morville's organization system (a usable shape). Heather Hedden's working definition: a taxonomy is **a controlled vocabulary arranged to support findability** — not merely a list of approved terms, but those terms organized by their relationships. The recurring product failure here is mistaking _a tree the company likes_ for _a structure users can navigate_; this file is mostly about not doing that.

## Controlled vocabulary first

Before structure comes the **controlled vocabulary**: the finite, governed set of terms the product uses for a given concept, with the synonyms mapped _to_ the preferred term rather than competing with it. A controlled vocabulary does three jobs taxonomy depends on:

- **Collapses synonyms.** "Laptop," "notebook," and "portable" all resolve to one preferred label, so they don't fragment the categories or split search results.
- **Disambiguates homonyms.** "Mercury" the planet, the element, and the car get distinguished, usually by context or qualifier.
- **Provides entry terms.** The non-preferred synonyms still _route_ the user to the right place ("you searched 'notebook' → see Laptops"). Synonyms are kept as signposts, not discarded.

The tell of a missing controlled vocabulary: the same thing tagged three ways, search that misses obvious matches, and category labels that overlap. Settle the vocabulary, then arrange it.

## Two ways to structure: hierarchical vs. faceted

There are two fundamental structures, and the choice (or blend) is the central taxonomy decision.

**Hierarchical (enumerative) taxonomy** — a single tree of broader/narrower relationships; each item lives in **one place** ("its correct slot"). This is the model of Dewey Decimal and Library of Congress: every document has an agreed-upon location in one large tree. Strengths: simple to browse, easy to explain, gives a clear overview. Weakness: the world resists single slots. The moment an item _legitimately_ belongs in two branches, a strict hierarchy forces a wrong choice or clumsy cross-listing.

**Faceted (analytico-synthetic) classification** — instead of one tree, **multiple independent dimensions (facets)**, each describing one attribute, combined at query time to pin down an item. This is **S. R. Ranganathan's** invention: his _Colon Classification_ (1933) was the first faceted scheme, built on the **PMEST** facets — **Personality, Matter, Energy, Space, Time**. Ranganathan's argument against strict hierarchy is exactly the product-relevant one: rigid enumerative schemes are "too limiting and finite," because many items pertain to more than one subject. Facets dissolve the single-slot problem: a shirt is _Color: blue_ **and** _Size: M_ **and** _Brand: X_ **and** _Material: cotton_, all at once, with no master tree forced to rank those dimensions.

|  | Hierarchical / enumerative | Faceted / analytico-synthetic |
| --- | --- | --- |
| **Shape** | One tree, broader→narrower | N independent dimensions, combined |
| **Item placement** | One "correct" slot | Described by a _set_ of facet values |
| **Best for** | Clear overview, modest scale, naturally nested content | Multi-attribute content, large catalogs, exploratory narrowing |
| **Breaks when** | Items legitimately belong in several branches | Facets aren't truly independent, or there are too many to scan |
| **In the product** | Primary nav, sections, browse-by-category | Faceted navigation / filters (see `filtering-and-faceting.md`) |

Most real products run **both**: a shallow browsable hierarchy for orientation _over_ a faceted substrate for narrowing. They are complements — hierarchy answers "where am I?", facets answer "narrow this to what I want." (Worth distinguishing from a flat **folksonomy** — uncontrolled user tags — which scales contribution but, lacking a controlled vocabulary, fragments meaning; covered in `metadata-and-relationships.md`.)

## Validate with users: card sorting and tree testing

A taxonomy is a hypothesis about the user's mental model. Two complementary research methods test that hypothesis — **build the structure with card sorting, then verify it with tree testing.** The methods are mirror images (tree testing is often called "reverse card sorting").

**Card sorting** — _generative; builds and informs the structure._ Donna Spencer's _Card Sorting_ (2009) is the standard reference. You give participants the content items (on cards) and learn how _they_ group them:

- **Open card sort** — participants group the cards **and name the groups themselves**. Use early, when you don't yet have categories — it surfaces the user's own mental model and their _labels_ (priceless for the controlled vocabulary). Output is fuzzier and needs interpretation.
- **Closed card sort** — you supply the categories; participants sort items **into your fixed groups**. Use later, to **validate** a proposed structure — does content land where you expect? Output is cleaner, quicker to analyze.
- **Hybrid** — categories provided, but participants may add their own. A middle path when you have a draft structure but suspect gaps.

**Tree testing** — _evaluative; validates findability of the structure._ You give participants only the **bare hierarchy** (labels, no UI, no search, no visual design) and a set of "find X" tasks, then watch where they click. It isolates the _structure and labels_ from everything else, so a failure can't be blamed on visual design or a search box. Key metrics: **success** (did they reach the right node?), **directness** (did they go straight there or backtrack?), and **where they went wrong** (which sibling stole the click — a labeling or grouping defect you can pinpoint). The discipline: card sort to _generate_, tree test to _confirm_ — and tree-test the labels naked, because a beautiful UI hides a broken structure.

## The perils of org-chart taxonomies

The dominant taxonomy failure in products and intranets: **structuring content around how the company is organized rather than how users think.** It happens because internal teams own the content and name things in their own language, and because "Marketing / Sales / Operations" is the path of least political resistance. It fails because users don't know or care which department owns a feature — they have a task, and they look for it by _their_ concept, not your reporting lines. Related smells:

- **Internal jargon as labels.** Category names that are acronyms or program names meaningful only inside the building — zero information scent for outsiders.
- **Overlapping or ambiguous categories.** Two categories that could each hold the same item, so users can't predict which to open (and content gets filed inconsistently).
- **Imbalance.** One bloated catch-all category ("Other," "Resources") next to several thin ones — a sign the cuts follow ownership, not content.
- **Hierarchy that should be facets.** Forcing a multi-attribute catalog into one tree, so users must guess whether "blue cotton shirts" lives under Color, Material, or Type. That is a facet problem wearing a hierarchy costume.

The fix is procedural, not cosmetic: forage labels from research, build with an _open_ card sort (user labels, user groups), and verify with a _tree test_ — letting the evidence, not the org chart, set the structure.

## Tells of good vs. bad (for scoring)

| Dimension | Bad | Good |
| --- | --- | --- |
| **Vocabulary control** | Same concept labeled many ways; synonyms compete; homonyms collide | A controlled vocabulary: one preferred term per concept, synonyms mapped as entry terms |
| **Structure fit** | Multi-attribute catalog forced into one tree; user must guess the branch | Hierarchy for browse/overview _plus_ facets for multi-attribute narrowing — matched to the content |
| **Mutual exclusivity** | Overlapping categories; an item could plausibly sit in several | Categories users can tell apart at a glance; predictable placement |
| **Label source** | Labels written by the team in internal language | Labels foraged from users (open card sort) in the users' words |
| **Validation** | Structure shipped on the strength of internal consensus | Built with card sorting, confirmed with tree testing (success + directness, naked labels) |
| **Balance** | A giant "Other"/"Resources" bucket beside several thin categories | Reasonably balanced categories; no catch-all hiding a structural failure |
| **Mental model** | Mirrors the org chart / team boundaries | Mirrors the user's mental model, evidenced by research |

## One labeled caveat

S. R. Ranganathan's authorship of faceted (analytico-synthetic) classification, _Colon Classification_ (1933), and the **PMEST** facet formula are firmly established and confirmed across multiple references (Britannica, Wikipedia, library-science sources) in this session; the "too limiting and finite" critique of enumerative schemes is attributed to Ranganathan via those secondary summaries rather than to a page in the 1933 text. Donna Spencer's _Card Sorting: Designing Usable Categories_ (Rosenfeld Media, 2009) is the standard primary reference for card sorting; the open/closed/hybrid distinction and tree-testing-as-validation are confirmed against Nielsen Norman Group's published guidance. Heather Hedden's taxonomy/faceted-taxonomy definitions are from _The Accidental Taxonomist_ and her site. Confirm any verbatim quotation against the cited print sources before publishing.
