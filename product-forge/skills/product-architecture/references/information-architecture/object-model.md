---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Sophia V. Prater, “Introducing ORCA: The Third Diamond in Your UX Process” (ooux.com, 2021) and ooux.com/what-is-ooux."
  - "Sophia V. Prater, interview on *The Informed Life* podcast, ep. 63 (theinformed.life, 2021-06-06)."
  - "Jorge Arango, *Living in Information: Responsible Design for Digital Places* (Two Waves Books, 2018) — environments built from places/objects, not pages."
---

# The Object Model: Nouns Before Screens

This is the working method for the single most leverage-rich move in product IA: **identify the objects before you design a single screen.** Sophia Prater's Object-Oriented UX (OOUX) and its **ORCA** process formalize an old engineering instinct — model the domain first — for UX. The thesis: every product is, underneath the pixels, **a set of objects with attributes, related to each other, that users act on.** Design the screens first and you bake the model's mistakes into the layout, the URLs, the API, and the analytics, where they are expensive to dig out. Model the objects first and the screens, navigation, and even the database tend to fall out of the structure almost mechanically. For product-forge, this is the bridge between IA-as-language (Abby C.) and IA-as-structure (the polar bear book): the **object model is the shared spine** both layers hang on.

## ORCA: the four questions, answered before any screen

Prater's process is **ORCA** — **Objects, Relationships, CTAs, Attributes.** (Note the C: it is **Calls-to-action**, not "actions" — the order O→R→C→A is the deliberate sequence.) It answers four questions, in order, _before_ designing a screen:

1. **Objects** — _What are the objects in the user's mental model?_ The real-world things that have value to both the user and the business: the connected people, places, and things the product is actually about (a `RECIPE`, a `PATIENT`, an `INVOICE`, a `PLAYLIST`). Objects are the nouns the user would point to.
2. **Relationships** — _How do the objects relate to each other?_ The connections and their cardinality: a `PATIENT` has zero-to-many `APPOINTMENTS`; a `PLAYLIST` contains many `TRACKS`; a `TRACK` belongs to one `ALBUM` and many `PLAYLISTS`.
3. **CTAs (calls-to-action)** — _What does each object call various users to do?_ Every action in a digital product is done _to an object_; OOUX insists you attach each CTA to the object it operates on (`book` an `APPOINTMENT`, `add` a `TRACK` to a `PLAYLIST`). This is where flows get derived — from objects and their actions, not invented screen-first.
4. **Attributes** — _What content elements make up each object?_ The fields and properties that define it (`RECIPE`: title, image, prep-time, ingredients, steps, rating). Attributes include _metadata_ and _nested objects_ — distinguishing "a plain field" from "a reference to another object" is itself a finding.

The ordering is the discipline. Objects constrain relationships; relationships and objects constrain CTAs; all three constrain attributes. Jumping to attributes (fields on a form) before settling objects is the screen-first mistake in disguise.

## Noun foraging: how to find the objects

The first concrete activity Prater teaches is **noun foraging** — extract the candidate objects from the raw material instead of inventing them at a whiteboard:

- **Gather the source text**: user-interview transcripts, stakeholder interviews, competitive teardowns, support tickets, existing copy, analytics labels.
- **Highlight every noun.** Literally mark the nouns. The recurring, weight-bearing nouns are your object candidates; the modifiers and one-offs are usually attributes.
- **Cluster synonyms, split homonyms.** "Customer" and "client" referring to one thing collapse into one object; "report" used for both a document and an action splits — the document is an object, the action is a CTA. (This is Abby C.'s ontology work, done with a highlighter.)
- **Separate objects from attributes from actions.** The test for an object: _does it have its own attributes, can it be acted on, and would a user expect a "detail" view of it?_ "Author" with just a name is an attribute of `BOOK`; "Author" with a bio, a photo, and a list of works is its own `AUTHOR` object. Promoting an attribute to an object (or demoting an object to an attribute) is the highest-stakes modeling call you make.

The tell of a good object set: each object is a thing a user could point to and say "show me that one," has attributes of its own, and offers actions. The tell of a bad set: "objects" that are really screens (`DASHBOARD`, `SETTINGS`), features (`CHECKOUT`), or UI controls (`MODAL`) — those are _views onto_ objects, never objects themselves.

## The object map: make the model visible and falsifiable

OOUX externalizes the model as an **object map** — typically a grid of sticky notes or cells, one column per object, color-coded by what each cell _is_:

```text
        RECIPE              COOK                 INGREDIENT
core →  title               name                 name
attrs   image               avatar               quantity-unit
        prep-time           bio
        rating
nested→ ⟶ COOK (author)     ⟶ RECIPE[] (authored) ⟶ RECIPE[] (used in)
object  ⟶ INGREDIENT[]      ⟶ COOK[] (follows)
refs    ⟶ STEP[]
metadata difficulty (enum)  member-since         is-allergen (bool)
CTAs    save · cook · rate  follow · message      (—)
```

The color-coding is load-bearing: **plain attributes, nested-object references (relationships), metadata, and CTAs are visually distinct.** A single object map makes three things checkable at a glance that prose hides: (1) every relationship appears on _both_ objects it connects (a missing reciprocal is a bug); (2) cardinality is explicit (`[]` = many); (3) objects with no CTAs and no inbound relationships are probably not objects. Because the map is concrete, stakeholders can disagree with it precisely — "no, a `STEP` isn't its own object, it's an attribute of `RECIPE`" — which is exactly the argument you want _before_ the screens exist.

## Why model-first pays: the structure propagates

The payoff is that a sound object model **propagates downstream almost for free**:

- **Screens fall out of objects.** Most products need, per object, roughly: a _collection_ view (the list of all `RECIPE`s), a _single_ view (one `RECIPE` detail), and the _CTAs_ as the buttons on those views. Navigation is largely "browse the top-level objects." You stop inventing screens and start _deriving_ them.
- **The model lines up with the database, the API, and the URL.** Objects ↔ tables/resources; attributes ↔ fields; relationships ↔ foreign keys / nested resources; CTAs ↔ endpoints. `/recipes/{id}` and `/cooks/{id}/recipes` write themselves. When UX and engineering share one object model, the costly UX-vs-data-model mismatch never opens up.
- **Consistency is structural, not enforced by review.** If `RECIPE` has a canonical single-view defined once, every place a recipe appears inherits it. Drift ("a recipe looks different on the search page than on the profile") becomes a model violation you can spot, not a taste argument.

Arango's _Living in Information_ (2018) reinforces the same shift from a different angle: design digital products as **environments built from places and objects**, not as stacks of pages. "Page-thinking" produces a pile of one-off layouts; "object-thinking" produces a coherent place a user can build a mental model of.

## Tells of good vs. bad (for scoring)

| Dimension | Bad | Good |
| --- | --- | --- |
| **Order of work** | Screens/wireframes drawn first; the data model reverse-engineered from layouts | Objects modeled first (ORCA); screens _derived_ from objects and their CTAs |
| **What counts as an object** | "Objects" are screens, features, or UI controls (`DASHBOARD`, `CHECKOUT`, `MODAL`) | Objects are user-meaningful nouns with their own attributes, actions, and a detail view |
| **Object sourcing** | Objects invented in a workshop, untethered from evidence | Nouns foraged from research, support, copy, and competitors; synonyms merged, homonyms split |
| **Relationships** | Relationships implicit or one-directional; cardinality unstated | Every relationship on both objects, with explicit cardinality (one / zero-to-many / many-to-many) |
| **Attribute vs. object** | A rich thing buried as a flat attribute (or a trivial field promoted to an object) | The promote/demote call made deliberately, by the "has its own attributes + actions + detail view?" test |
| **Model visibility** | The model lives only in someone's head or scattered across mockups | A single, color-coded object map anyone can challenge precisely |
| **Propagation** | UX model and data model diverge; screens and URLs inconsistent across the app | One object model spans UX, API, URLs, and DB; consistency is structural |

## One labeled caveat

The ORCA process and its expansion — **Objects, Relationships, Calls-to-action, Attributes** — and the "noun foraging" activity are Sophia Prater's, confirmed across her ooux.com writing and _The Informed Life_ interview in this session; OOUX is her named framework. The cardinality example (`PATIENT` → zero-to-many `APPOINTMENTS`) is hers. The downstream-propagation claims (object map ↔ API/URL/DB, screens derived from objects) and the object-map cell taxonomy are faithful to OOUX practice but stated here as the working method rather than quoted from a single page; OOUX practitioners structure the map this way but exact templates vary. Arango's place/object framing is from _Living in Information_ (2018). Confirm any verbatim phrasing against the cited primary sources before publishing.
