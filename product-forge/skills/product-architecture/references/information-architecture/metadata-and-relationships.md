---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Jeffrey Pomerantz, *Metadata* (MIT Press Essential Knowledge series, 2015)."
  - "Schema.org — the shared structured-data vocabulary (schema.org); founded 2011 by Google, Microsoft, Yahoo!, Yandex."
  - "Louis Rosenfeld, Peter Morville & Jorge Arango, *Information Architecture: For the Web and Beyond*, 4th ed. (O'Reilly, 2015) — metadata and controlled vocabularies."
  - "Heather Hedden, *The Accidental Taxonomist*, 2nd ed. (Information Today, 2016) — tags vs. categories, taxonomy vs. folksonomy."
---

# Metadata & Relationships: The Connective Layer

This is the working method for the layer that makes everything else in IA _function_: **metadata** (data about the content) and the **relationships** between objects. Taxonomy decides the categories; metadata is what actually _attaches_ content to those categories and to each other, and so it is the substrate that powers search, filtering, sorting, and recommendation. Jeffrey Pomerantz's framing in _Metadata_ (2015) is the orientation: metadata is **"a means of describing resources so they can be found"** — a statement _about_ a resource, structured enough for a machine to act on. The product lesson: features users experience as "smart" — relevant search, useful filters, good recommendations, related-content modules — are almost always **good metadata wearing a feature costume.** Thin metadata caps how good any of those can ever get, no matter the algorithm.

## What metadata is, and the kinds that matter

Metadata is structured description: the **fields and values attached to an object** beyond its primary content. Pomerantz distinguishes types that map cleanly onto product work:

- **Descriptive** — what the thing _is_ and is _about_: title, author, summary, tags, category, the facet values. This is the metadata that powers search and filtering. Most product IA work lives here.
- **Structural** — how the thing is _put together_ and related to other things: this `CHAPTER` belongs to that `BOOK`; these `STEP`s compose this `RECIPE`; this version supersedes that one. This is where metadata and _relationships_ meet.
- **Administrative** — provenance and management: created/modified dates, owner, status, permissions, rights. Powers sorting, lifecycle, and access control.

The practical move when modeling an object (per the object model): for every attribute, ask **"is this content the user reads, or metadata the system acts on?"** A recipe's step text is content; its `difficulty: easy|medium|hard`, `cuisine`, `prep-time`, and `is-vegetarian` are descriptive metadata — and _those_ are what a filter or a "more like this" can hang on. Metadata that doesn't exist can't be searched, filtered, sorted, or recommended; the IA decision is **which attributes to promote into structured, controlled metadata** versus leaving as free text.

## Tags vs. categories — not interchangeable

A persistent product confusion. They are different tools with different governance:

|  | **Categories** | **Tags** |
| --- | --- | --- |
| **Structure** | Hierarchical or a small controlled set; part of the taxonomy | Flat; many per item |
| **Governance** | Controlled — a defined, maintained list | Often _uncontrolled_ (folksonomy) or loosely controlled |
| **Cardinality** | Usually **one** primary per item (or few) | **Many** per item, freely combined |
| **Job** | "Where does this _live_?" — the spine of browse navigation | "What is this _also_ about?" — cross-cutting discovery and association |
| **Failure mode** | Forces a single slot on multi-faceted content | **Folksonomy fragmentation**: `js`, `JS`, `javascript`, `java-script` for one concept |

The taxonomist's rule (Hedden): **categories are for structure and browsing; tags are for description and cross-linking** — and tags need _some_ control (a suggested-tag autocomplete, synonym mapping) or they decay into noise. Uncontrolled tags scale contribution but, lacking a controlled vocabulary, split meaning across near-duplicate labels and quietly degrade every filter and search built on them. The fix is rarely "no tags" — it's "tags drawn from, or reconciled to, a controlled vocabulary."

## Relationships: from records to a graph

Beyond describing single items, metadata **connects them** — and the shape of those connections is the difference between a pile of records and a navigable structure. Relationships are themselves a kind of structural metadata (a typed link from one object to another), and they come in a few shapes worth naming:

- **Hierarchical / parent-child** — `FOLDER` contains `FILE`; `ALBUM` contains `TRACK`. The relationship _is_ the tree.
- **Associative / "see also"** — `ARTICLE` relates-to `ARTICLE`; `PRODUCT` is-accessory-of `PRODUCT`. Cross-cutting links that power related-content and cross-sell.
- **Equivalence** — synonym / `same-as` links (an entry term → its preferred term; a duplicate → its canonical). The plumbing behind controlled vocabularies and de-duplication.

When relationships are **typed and traversable in both directions**, the content set stops being a list and becomes a **graph** — a network of entities connected by named relationships. This is the model behind knowledge graphs: entities with attributes, linked by typed edges. Its product payoff is concrete — a graph lets you answer questions a flat list can't: "other tracks on this album," "people who also follow this cook," "articles citing this one," "accessories for this product." Every "related," "because you liked," and "people also viewed" module is a relationship traversal. The IA decision is **which relationships to model explicitly** (so they can be traversed) versus leaving implicit (so they can't).

## Schema.org and shared vocabularies: don't reinvent the entities

For public/web-facing content, **Schema.org** (founded 2011 by Google, Microsoft, Yahoo!, Yandex) is the shared, machine-readable vocabulary of common entity types — `Product`, `Recipe`, `Event`, `Person`, `Article` — with standard attributes and relationships. Marking content up with Schema.org **publishes your object model in a vocabulary external systems already understand**: search engines, voice assistants, and AI agents extract those entities and relationships to populate knowledge graphs and rich results. Two product lessons:

1. **Reuse the standard entity model where one exists.** If you're modeling a `Recipe`, Schema.org's `Recipe` (prepTime, ingredients, nutrition, rating…) is a battle-tested checklist of attributes and relationships — borrow it instead of inventing a thinner one. The same instinct that says "use the users' words for labels" says "use the web's words for entity types."
2. **Metadata has an external audience now.** In a world of LLM and agent consumption, your structured metadata is read by machines outside your product, not just your own search index. Rich, well-typed, relationship-bearing metadata is increasingly the _interface_ through which non-human consumers understand your content. Thin or absent structured data makes a product effectively illegible to that audience.

## How the connective layer powers features

Tracing the chain makes the stakes concrete — each "smart" feature is downstream of specific metadata:

- **Search** indexes descriptive metadata; controlled vocabularies and synonym (equivalence) relationships are what let a query for "notebook" find a "laptop."
- **Filtering / faceting** is _only_ possible over structured, controlled metadata fields — a facet is a metadata field surfaced as a control (see `filtering-and-faceting.md`). No field, no facet.
- **Sorting** runs on administrative/descriptive metadata (date, price, rating, popularity). "Sort by newest" is impossible without a reliable `created` field.
- **Recommendation** traverses relationships and matches on shared metadata: collaborative ("users who related to A also related to B" — a graph traversal) and content-based ("items sharing these tags/attributes").

The unifying diagnosis: when search is weak, filters are thin, or recommendations are dumb, **suspect the metadata before the algorithm.** You usually cannot out-engineer a missing field or an uncontrolled tag.

## Tells of good vs. bad (for scoring)

| Dimension | Bad | Good |
| --- | --- | --- |
| **Metadata depth** | Objects are mostly free text; few structured, queryable fields | Each object carries descriptive + structural metadata sufficient to search, filter, sort, recommend |
| **Content vs. metadata** | Acted-on attributes left as unstructured prose | The "content vs. metadata" call made per attribute; the actionable ones promoted to controlled fields |
| **Tags vs. categories** | The two conflated; tags used as structure or categories used as freeform tags | Categories for structure/browse; tags for cross-cutting description, with some vocabulary control |
| **Vocabulary control** | Folksonomy fragmentation (`js`/`JS`/`javascript`) silently degrading search and filters | Controlled (or reconciled) vocabulary; synonyms mapped via equivalence relationships |
| **Relationships** | Connections implicit; only a flat list exists; one-directional links | Typed, bidirectional relationships forming a traversable graph; "related/also" features fall out of it |
| **Standard vocabularies** | A bespoke, thin entity model for content the web already has a type for | Reuses Schema.org (or domain standards) where they exist; entities legible to external machines |
| **Feature root-cause** | "Search/recsys is dumb" treated as an algorithm problem | Weak discovery traced to thin/uncontrolled metadata and fixed at the source |

## One labeled caveat

Pomerantz's _Metadata_ (MIT Press, 2015) is a solid primary source for the descriptive/structural/administrative typology and the "describing resources so they can be found" framing, paraphrased here rather than quoted verbatim. Schema.org's founding (2011, by Google/Microsoft/Yahoo!/Yandex) and its role in populating search knowledge graphs are well documented; the specific claim that LLMs/agents increasingly consume structured data is an extrapolation of the documented search-engine behavior to the agent context — directionally well-supported but stated as a trend, not a cited measurement. The tags-vs-categories and folksonomy-fragmentation points follow Hedden's _The Accidental Taxonomist_. Confirm any verbatim quotation against the cited print sources before publishing.
