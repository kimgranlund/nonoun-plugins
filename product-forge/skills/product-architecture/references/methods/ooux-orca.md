---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Sophia V. Prater, “Introducing ORCA: The Third Diamond in Your UX Process” and “What is OOUX?” (ooux.com, 2021). https://www.ooux.com/"
  - "Sophia V. Prater, interview on *The Informed Life* podcast, ep. 63, “Sophia Prater on Object-Oriented UX” (theinformed.life, 2021). https://theinformed.life/2021/06/06/episode-63-sophia-prater/"
  - "Sophia V. Prater & Rewired UX Studio, *The OOUX Launch Guide* / ORCA process documentation (ooux.com). https://www.ooux.com/orca"
method: ooux-orca
phase: structure
domains: [4]
timebox: "1–2 days (the four rounds)"
cadence: one-off
participants: [facilitator, pm, designer, engineer, content]
inputs: ["raw domain material — research transcripts, support tickets, existing copy, competitor teardowns", "a real feature or system to model", "a cross-functional team in one room (or one board)"]
produces: "an object model — objects + relationships + CTAs + attributes, color-coded"
de_risks: [usability, feasibility]
rubric: rubric-information-architecture
---

# OOUX / ORCA — model the nouns before the screens

A **time-boxed four-round process** (Prater) that turns raw domain material into a shared, color-coded **object model** — the objects a product is about, how they relate, what they call users to do, and what content each carries — _before anyone draws a screen_. The output is not a deliverable for its own sake; it is the **named decision about the data and content structure** that screens, navigation, URLs, and the API will all inherit. This file is the RUN. For _why_ object-first is the highest-leverage move in IA, and what an object actually is, read the CONCEPT `information-architecture/object-model.md`; for where the object model sits among the four polar-bear systems, read `information-architecture/polar-bear-foundations.md`. This page does not restate that theory — it executes it.

## When to run it · when NOT

**Run it** when you are about to design a content-rich or data-rich system (or a substantial new feature) and the structure is genuinely unsettled — multiple object types, real relationships, and disagreement about "what is this thing." Run it when UX and engineering are about to diverge on the data model, or when an existing product's screens are inconsistent because no shared model was ever named. **Do NOT run it** for a single throwaway screen or a thin marketing page (no objects to model — overkill); when the object model is already well-established and stable (just design against it); when you have no raw domain material to forage from (you'll invent objects at a whiteboard, which is the failure the process exists to prevent); or when there is no engineer and no content person in the room — without them the model floats free of the data and the real content, and ORCA degrades into a sticky-note exercise that nobody downstream honors.

## The run (the four ORCA rounds)

ORCA = **O**bjects → **R**elationships → **C**TAs → **A**ttributes. The letters are an ordering, not a menu: each round constrains the next, and the C is **Calls-to-action** (not "actions"). Work the rounds in sequence on a shared grid — one column per object — color-coding each cell by what it _is_ (plain attribute · nested-object reference · metadata · CTA), so the map stays falsifiable at a glance.

| # | Round | Who leads | Timebox | The move | Output |
| --- | --- | --- | --- | --- | --- |
| **1** | **Objects** (noun-forage) | facilitator + everyone | ~½ day | **Noun-forage** the source material: highlight every noun in transcripts, tickets, copy, competitor teardowns; cluster synonyms, split homonyms; keep only nouns that pass the test — _has its own attributes, can be acted on, deserves a detail view_. Demote screens/features/controls (`DASHBOARD`, `CHECKOUT`, `MODAL`) — they are views _onto_ objects, never objects. | the **object inventory** — one column per real object |
| **2** | **Relationships** | designer + engineer | ~½ day | Connect the objects: for each pair that relates, draw the link and state its **cardinality** (one · zero-to-many · many-to-many). Enforce reciprocity — every relationship must appear on _both_ objects it joins (a missing return edge is a bug). | a **relationship map** with cardinality on every edge |
| **3** | **CTAs** (calls-to-action) | pm + designer | ~¼ day | For each object, list what it **calls various users to do** — every CTA attached _to the object it operates on_ (`book` an `APPOINTMENT`, `add` a `TRACK` to a `PLAYLIST`). Flows get _derived_ here, from objects and their CTAs — not invented screen-first. | **CTAs per object** (the future buttons / endpoints) |
| **4** | **Attributes** | content + engineer | ~½ day | For each object, enumerate the **content elements and metadata** it carries (`RECIPE`: title, image, prep-time, rating, difficulty-enum). Mark which "attributes" are really **nested-object references** (a relationship in disguise) and which are sortable/filterable **metadata** — distinguishing a plain field from a reference is itself a finding. | each object's **attributes + metadata + nested refs**, color-coded |

### The color-coded object map

The four rounds converge on one artifact: a grid, **one column per object**, every cell color-coded by what it is. The color-coding is load-bearing — it makes three things checkable at a glance that prose hides: (1) every relationship appears on **both** objects (a missing reciprocal is visible); (2) **cardinality** is explicit (`[]` = many); (3) an object with no CTAs and no inbound relationships is probably not an object. Build the map structure and read the worked example in the CONCEPT `object-model.md` — do not duplicate the template here; ORCA's job is to _fill it in_, in order.

### Iterate (round-trip, don't waterfall)

The four rounds are a **loop, not a one-way pour.** Attributes routinely promote to objects (an "author" with a bio, a photo, and a list of works is no longer a field on `BOOK` — it's an `AUTHOR` object), which sends you back to Objects → Relationships. CTAs surface missing objects ("`export` — to what? there's a `REPORT` object we missed"). Expect at least one return trip; a model that never round-tripped probably wasn't interrogated. The promote/demote call — attribute ⇄ object — is the highest-stakes decision in the run; make it deliberately, by the three-part test, not by reflex.

## Roles

A **Facilitator** (runs the rounds and the timebox, holds the order O→R→C→A, stays neutral on the model's _content_), a **PM** (owns the domain truth — which objects matter to the business and the user), a **Designer** (drives relationships and CTAs; will derive the screens from this map), an **Engineer** (keeps the model honest against the real data model and API — objects ↔ resources, attributes ↔ fields, relationships ↔ foreign keys), and **Content** (knows what each object actually carries and how it's really referred to — the source of the foraged nouns). The engineer and content roles are what keep ORCA tethered to reality; omit them and the model floats.

## Failure modes

- **Skipping the foraging** → objects invented at a whiteboard, untethered from evidence; you model the team's assumptions, not the user's domain.
- **"Objects" that are screens, features, or controls** (`DASHBOARD`, `SETTINGS`, `CHECKOUT`, `MODAL`) → these are _views onto_ objects; modeling them as objects bakes screen-thinking back into the model the process exists to prevent.
- **Breaking the O→R→C→A order** — jumping to attributes (fields on a form) before objects are settled is the screen-first mistake in disguise; the ordering _is_ the discipline.
- **One-directional or cardinality-free relationships** → the model looks done but the reciprocals and the "how many" are missing, and those are exactly what the database and the screens need.
- **Reading the C as "actions" and detaching it from objects** → free-floating actions, no object to hang them on, and flows invented screen-first instead of derived.
- **No engineer / no content in the room** → the model diverges from the real data and the real content the day it's finished; nobody downstream honors it.
- **Waterfalling the four rounds** (never round-tripping) → the promote/demote calls never get made; rich things stay buried as flat attributes.

## A good run vs. a bad run

|  | Bad run | Good run |
| --- | --- | --- |
| Objects | invented at a whiteboard; screens/features/controls listed as objects | **foraged** from research/tickets/copy/competitors; each passes the noun test (attributes + actions + detail view) |
| Order | jumped to fields/screens first | **O→R→C→A** held; each round constrains the next |
| Relationships | implicit, one-directional, cardinality unstated | every edge on **both** objects, with explicit cardinality |
| CTAs | a list of screens, or actions with no object | each CTA attached **to its object**; flows _derived_, not invented |
| The map | lives in someone's head or scattered across mockups | one **color-coded object map** anyone can challenge precisely |
| Iteration | waterfalled once, never revisited | **round-tripped** — at least one attribute promoted to an object |

**The single test:** point at any named "object" on the map and apply the noun test — does it have its own attributes, can it be acted on, would a user expect a detail view of it? If `CHECKOUT` (a flow), `SETTINGS` (a screen), or `MODAL` (a control) survived as "objects," the run produced a sitemap wearing an object model's clothes, not an object model.

## Hand-off

A sound object model **propagates downstream almost for free** (see `object-model.md` for the full mechanism): screens fall out of objects (per object: a collection view, a single view, and the CTAs as buttons); the model lines up with the database, API, and URLs (`/recipes/{id}` writes itself); consistency becomes structural, not a review argument. From here the work flows to **`product-patterns`** for the screen-level units the map implies (the form that edits one object, the list pattern for a collection), and the model feeds the rest of the IA layer — `taxonomy-and-classification.md`, `metadata-and-relationships.md`, `search-systems.md`, and `filtering-and-faceting.md` all run off these objects and their metadata. Score the run with **`rubric-information-architecture`** — D1 (object model) is a hard gate, and ORCA is exactly the process that earns the 5: objects modeled first, foraged with synonyms merged and homonyms split, every relationship reciprocal with cardinality, the promote/demote call made by test, screens/URLs/API derived from the model.

## Sourcing

The **ORCA** process and its expansion — **Objects, Relationships, Calls-to-action, Attributes** — the **noun-foraging** activity, and the **color-coded object map** are Sophia Prater's Object-Oriented UX (OOUX), from her ooux.com writing (the "third diamond"/ORCA articles and the ORCA documentation) and her _The Informed Life_ ep. 63 interview. The four-round sequence, the within-round role split, the per-round timeboxes, and the iterate/round-trip discipline are stated here as the **working run** faithful to OOUX practice; OOUX practitioners structure ORCA this way, but exact round counts, sub-step names, and templates vary between Prater's materials and her training cohorts. The downstream-propagation claims (object map ↔ API/URL/DB; screens derived from objects) are faithful to OOUX but are the working method, not a single quoted page. **Caveat:** confirm any verbatim ORCA sub-step names, the precise round breakdown, and the _The Informed Life_ ep. 63 publication date against the cited primary sources before publishing — the timeboxes here are a practical default, not Prater's fixed numbers, and OOUX's canonical ORCA is sometimes taught as more than four discrete rounds (e.g., a distinct prioritization/synonyms step).
