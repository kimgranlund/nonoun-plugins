---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Marc S., Markus Edgar Hormess, Adam Lawrence & Jakob Schneider, *This Is Service Design Doing: Applying Service Design Thinking in the Real World* (O'Reilly, 2018, ISBN 9781491927182). The six principles and the research → ideate → prototype arc."
  - "Marc S. & Jakob Schneider, *This Is Service Design Thinking* (BIS Publishers, 2011) — the earlier five-principle formulation that the 2018 book revised."
  - "Service Design Network (SDN) — book record for *This Is Service Design Doing*. https://www.service-design-network.org/books-and-reports/this-is-service-design-doing-applying-service-design-thinking-in-the-real-world"
---

# Service Design Method

Service design is the discipline of designing the _whole_ service — every touchpoint, every channel, the people who deliver it, and the back-of-house that supports them — as one coherent thing, rather than designing screens and hoping the rest follows. The canonical practitioner reference is **Marc S., Hormess, Lawrence & Schneider's _This Is Service Design Doing_ (O'Reilly, 2018)**, which deliberately emphasizes _doing_ — facilitation, methods, and embedding in an organization — over theory. This file encodes its working spine: the six principles that gate whether you are actually doing service design, and the research → ideate → prototype arc that produces a blueprint you can act on (see `service-blueprints.md` for the blueprint itself).

> The orienting shift: a product team instinctively asks "what should this screen do?" Service design forces the prior question — "what is the whole sequence of interactions this person moves through, across every channel and every human, to get the job done, and what has to be true backstage for it to work?" The screen is one touchpoint in that sequence, not the unit of design.

## The six principles (the gate)

The 2018 book revised the earlier five principles (the 2011 _This Is Service Design Thinking_ listed user-centered, co-creative, sequencing, evidencing, holistic) into **six**. Treat them as a checklist: if a process violates one, it is product design wearing service-design vocabulary.

| Principle | What it demands | The tell it's being faked |
| --- | --- | --- |
| **Human-centered** | "Consider the experience of all the people affected by the service" — customers _and_ staff | Only the end-customer is studied; the agent/operator is ignored |
| **Collaborative** | Stakeholders of varied backgrounds and functions are "actively engaged" in the process | A designer works alone and presents a finished artifact |
| **Iterative** | An "exploratory, adaptive, and experimental approach," iterating toward implementation | One pass, big reveal, ship — no learning loop |
| **Sequential** | The service is "visualized and orchestrated as a sequence of interrelated actions" | Designed as isolated features, not as a journey over time |
| **Real** | Needs are "researched in reality," ideas "prototyped in reality," intangibles made physical/digital | Personas and ideas invented in a room; nothing tested with real people |
| **Holistic** | "Sustainably address the needs of all stakeholders through the entire service and across business" | One channel optimized; the rest of the service left to fend for itself |

The two principles product teams most often drop are **human-centered (staff included)** and **holistic**. Optimizing one channel while starving the others, or delighting customers on a foundation of broken internal tooling, fails both — and the failure is visible to the customer even though its cause is backstage (see `fulfillment-and-ops.md`).

## The core artifacts

Service design's vocabulary is concrete; these are the nouns you produce.

- **Touchpoints** — the discrete moments of contact between person and service (a screen, an email, a phone call, a parcel, a store counter). The atomic unit.
- **Stages / journey** — touchpoints arranged in the sequence a person moves through over time. The journey map is the primary canvas; the blueprint extends it downward (see `service-blueprints.md`).
- **Personas** — research-grounded archetypes of the people affected. Service design demands personas for **staff and back-of-house actors too**, not only end-customers — the agent is a user (see `fulfillment-and-ops.md`).
- **Channels** — the media a touchpoint lives in (web, app, email, phone, in-person). Continuity _across_ channels is its own design problem (see `cross-channel-continuity.md`).
- **Service ecosystem / stakeholder map** — the wider web of actors (partners, suppliers, regulators) the service depends on. Forces the holistic view.
- **Evidence** — the tangible/digital artifacts that make an intangible service perceivable (a confirmation, a receipt, a status). The "real" principle in object form.

## The working arc: research → ideate → prototype → implement

The book's method is a loop, not a line. Each phase iterates, and you re-enter earlier phases as you learn.

```text
   ┌─────────────────────────────────────────────────────────┐
   │                                                         │
   ▼                                                         │
RESEARCH ──────────▶ IDEATE ──────────▶ PROTOTYPE ──────────▶ IMPLEMENT
"in reality"        co-create          "in reality"          embed in org
journeys,           options with       test touchpoints      operations,
interviews,         stakeholders,      & whole sequences     staff, systems
shadowing,          not in a vacuum    with real people,     — and keep
service safaris                        cheaply               iterating
   ▲                                       │
   └───────────────────────────────────────┘
        each prototype sends you back to research
```

**Research — "in reality."** Go where the service happens. The book's signature methods: contextual interviews, **shadowing** (following a real customer or staff member through the actual journey), **service safaris** (experiencing competitors' and your own service as a customer), and diary studies. The output is evidence of the _real_ sequence and its breakpoints — not a stakeholder's idealized version. This research is what populates the customer-actions row of a blueprint with truth rather than assumption.

**Ideate — collaboratively.** Generate options _with_ the people who deliver and depend on the service, in facilitated workshops. The point of co-creation is not democracy; it's that frontline staff know where the service actually breaks, and partners know what's actually feasible. Ideas that survive contact with the people who'll execute them are the ones worth prototyping.

**Prototype — "in reality," cheaply.** Service prototypes are not just screens. Methods include **service walkthroughs / desktop walkthroughs** (acting the journey out on a table-top with props and personas), **investigative rehearsal** and **bodystorming** (physically role-playing a touchpoint to feel where it's awkward), and the **Wizard of Oz** (a human secretly performs what will eventually be automated, so you can test the experience before building the machinery). Prototype whole _sequences_, not isolated moments — the seams between touchpoints are where services fail.

**Implement — embed in the organization.** A service design dies if it never reaches operations. Implementation means changing staff workflows, internal tools, scripts, and systems — the backstage and support layers of the blueprint — so the new design is what actually gets delivered. The book is explicit that embedding service design in the organization is itself a design problem, not an afterthought.

## How this composes with the rest of the cluster

- The journey and research from this method **feed the blueprint** (`service-blueprints.md`) — the blueprint is the downstream artifact, not a parallel one.
- The "holistic" and "human-centered (staff)" principles are what make **fulfillment and ops** (`fulfillment-and-ops.md`) part of the design, not an externality.
- The "sequential" principle is what surfaces **handoffs** (`handoffs-human-system.md`), **cross-channel continuity** (`cross-channel-continuity.md`), and **escalation** (`escalation-and-exceptions.md`) as first-class design objects rather than gaps.

## Anti-patterns

| Anti-pattern | Which principle it violates | The fix |
| --- | --- | --- |
| **Designing the screen, calling it the service** | Sequential, holistic | Map the whole journey across channels; design the sequence |
| **Personas invented in a conference room** | Real, human-centered | Research in reality — shadow, interview, safari real people |
| **Customer studied, staff ignored** | Human-centered | Build staff/back-of-house personas; the operator is a user |
| **Designer works solo, presents a finished deck** | Collaborative | Co-create with frontline staff and partners who'll execute it |
| **One channel polished, the rest neglected** | Holistic | Design for continuity across every channel the journey touches |
| **Prototype is only hi-fi screens** | Real | Walkthroughs, bodystorming, Wizard of Oz — test the sequence |
| **Design handed off, never reaches ops** | (Implement) | Treat embedding in operations as part of the design work |

## Good vs. bad (for scoring)

| Dimension | Good — service design done | Bad — product design in disguise |
| --- | --- | --- |
| **Scope** | The whole service: every touchpoint, channel, and the staff | A screen or feature in isolation |
| **Evidence** | Grounded in research "in reality" (shadowing, safaris) | Assumptions and invented personas |
| **Stakeholders** | Co-created with staff, partners, back-of-house | Designed solo and handed down |
| **Sequence** | Orchestrated as interrelated actions over time | Disconnected features |
| **Staff as users** | Frontline and ops personas designed for explicitly | Only the end-customer considered |
| **Prototyping** | Sequences tested cheaply with real people before build | Hi-fi screens reviewed in a meeting |
| **Implementation** | Embedded in operations, tools, and workflows | Stops at a design artifact; ops left to cope |

The single test: **name every channel and every human the user touches to complete one core job, then ask whether each was researched, co-created, and prototyped as part of one sequence.** If the answer is "we designed the app and assumed the phone line, email, and the agent would sort themselves out," you have product design with a service-design label — and the seams between those untreated touchpoints are exactly where the experience will fail.
