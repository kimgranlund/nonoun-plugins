---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "G. Lynn Shostack, 'Designing Services That Deliver,' Harvard Business Review 62, no. 1 (Jan–Feb 1984): 133–139. The origin of service blueprinting, the line of visibility, and the 'What if?' planning purpose."
  - "Marc S., Markus Edgar Hormess, Adam Lawrence & Jakob Schneider, *This Is Service Design Doing* (O'Reilly, 2018, ISBN 9781491927182). Blueprinting as a facilitated, collaborative method — the workshop, not just the artifact."
  - "Nielsen Norman Group — 'Service Blueprinting' (Alita Joyce / Sarah Gibbons). https://www.nngroup.com/articles/service-blueprinting/ — running the workshop and the line-of-visibility convention."
method: service-blueprinting
phase: structure
domains: [2, 10]
timebox: "½–1 day workshop"
cadence: one-off
participants: [facilitator, service owner, frontline staff, ops, designer, pm]
inputs: ["one chosen journey (ideally a researched journey map)", "the frontline staff and ops who actually run the steps", "a wall or shared canvas", "a named operational question to answer"]
produces: "a service blueprint — customer actions · frontstage · backstage · support, with the line of visibility"
de_risks: [feasibility]
rubric: rubric-service-model
---

# Service Blueprinting (workshop) — build the blueprint in a room with the people who run the service

A **facilitated half-to-full-day workshop** that produces a service blueprint by getting the customer-facing and behind-the-scenes people into one room and walking a single journey together, lane by lane, until the invisible machinery is on the wall. The artifact's anatomy — the swimlanes, the line of visibility, what each lane holds — is the CONCEPT, documented in `../service-model/service-blueprints.md`; the method it sits inside is `../service-model/service-design-method.md`. **This file is the RUN**: how to facilitate the session that yields the blueprint, and how to drive it toward a real operational decision rather than a wall decoration. The technique originates with **G. Lynn Shostack (HBR, 1984)**; the modern collaborative facilitation follows **Marc S. et al., _This Is Service Design Doing_ (2018)** and **NN/g's "Service Blueprinting."**

## When to run it · when NOT

**Run it** when a service spans several teams and systems and nobody in the room can describe the whole chain behind a customer's moment — when frontstage and backstage are owned by different people, when a promise the front end makes keeps breaking somewhere out of sight, or when you're about to redesign, automate, or staff a journey and need to see the operation before you change it. The strongest trigger is a **named operational question** ("can we honor a same-day refund?", "where does the handoff to the warehouse drop context?", "what breaks when the payment gateway is slow?").

**Do NOT run it** when you don't yet know the customer's real journey — blueprint without a researched journey and the customer-actions row becomes the org's assumptions, not behavior (build the journey first; see `../service-model/service-design-method.md`). Don't run it for a single screen with no backstage to speak of (overkill — it's a journey-spanning tool). And **don't run it without the backstage and ops people in the room**: a blueprint drawn only by frontstage staff and designers is a guess about the half of the service they can't see, which is precisely the half the method exists to expose.

## The run

A blueprint is built in lanes, top of the visible band down into the machinery. The session moves left-to-right along one journey and top-to-bottom through the lanes, and the discipline is to keep asking _"and then what has to happen below this for it to work?"_ until the column bottoms out in a real system or team.

| # | Step | Who leads | Timebox | Output |
| --- | --- | --- | --- | --- |
| 1 | **Prep & scope a single journey** — pick one journey, one primary customer, one goal ("request a refund," not "support"); confirm the researched journey map is on hand; write the operational question the blueprint must answer on the wall; recruit the people who actually run each lane | facilitator + service owner | before the session | a scoped journey, a named question, the right people invited |
| 2 | **Assemble the swimlanes** — draw the empty lanes on the wall/canvas: customer actions, frontstage, backstage, support processes (plus the optional physical-evidence band on top); leave the customer-actions row's time axis spanning the width | facilitator | 15 min | empty lanes ready to fill |
| 3 | **Lay the customer-actions row first** — lift the steps straight off the journey map onto the top lane; this is the time axis everything hangs from, and using research keeps the column honest | pm + designer | 20–30 min | the journey's spine, left to right |
| 4 | **Draw the line of visibility (and line of interaction)** — name the two diagnostic lines explicitly before filling the lanes, so every later card lands above or below them deliberately: interaction at the customer's own boundary, visibility cleaving what the customer can see from what they can't | facilitator | 10 min | the lines drawn and labeled (line of internal interaction added when support processes go in) |
| 5 | **Walk the journey step by step, filling the lanes** — take each customer action in turn and ask, column by column: what does the org do _in view_ (frontstage)? what happens _out of sight_ to make that work (backstage)? which systems, teams, third parties does it call (support)? Frontline staff own the frontstage cards; ops and backstage staff own theirs — write what _is_, not what should be | facilitator + frontline + ops | 90–150 min | every column populated, sourced from the people who run it |
| 6 | **Hunt the backstage gaps and failure points** — re-walk each column top-to-bottom drawing the vertical dependency arrows; mark where a column dead-ends ("and then somehow it works"), where one customer action triggers a long fragile descent, where a handoff crosses team lanes, and where it commonly breaks or runs slow; annotate fail points and timings | facilitator + whole room | 30–45 min | dependency arrows, marked fail points / hot-spots / timings — the redesign brief |

Close by answering the **named operational question from step 1** against the wall, and naming the one or two redesign moves the blueprint surfaced — the point of the session, per Shostack, is the "What if?", not the diagram.

## Roles

A neutral **facilitator** (runs time and the lane-by-lane walk; never fills cells with content — that's the room's job). A **service owner** (chose the journey, owns the operational question, can act on the outcome). **Frontline staff** — the people who actually face customers in this journey; they own the frontstage lane and know where it really breaks. **Ops / backstage** — fulfillment, internal-tools, the people behind the line of visibility; without them the lower lanes are fiction. A **designer** (holds the journey and the customer's reality) and a **PM** (holds scope and the downstream decision). The non-negotiable seat is **the people who run the backstage** — they are the only ones who can populate the half of the blueprint the customer never sees.

## Failure modes (blueprint theater)

- **No backstage people in the room** → the lower lanes are designers guessing; you've drawn the frontstage twice and called it a service. The session needs the people who run the machinery.
- **Blueprinting from imagination, no journey** → the customer-actions row becomes internal assumptions; everything below inherits the lie. Lift the top row from research (see `../service-model/service-design-method.md`).
- **Boiling the ocean** → one mega-journey for the whole product becomes an unreadable wall nobody can trace. One journey, one primary customer, one session.
- **Drawing what _should_ happen** → an idealized blueprint of the intended process hides exactly the gaps you came to find. Map what _is_; the gap between is-and-should is the finding.
- **No line of visibility / no vertical arrows** → you leave with four parallel lists, not a system; the dependencies that _are_ the insight stay invisible.
- **Filed, never reopened** → a beautiful diagram photographed and forgotten violates Shostack's whole purpose. Leave with the operational question answered and a redesign move named, or you ran a documentation exercise, not a workshop.

## A good run vs. a bad run

|  | Bad run | Good run |
| --- | --- | --- |
| Scope | "support," the whole product | one journey, one primary customer, one goal |
| Room | designers + frontstage only | frontline _and_ ops/backstage in the room |
| Top row | invented in the session | lifted from a researched journey map |
| The walk | each lane listed in isolation | walked column-by-column with vertical arrows |
| Content | the idealized intended process | what actually happens, named by who runs it |
| Output | a photographed diagram, filed | fail points marked + the operational question answered |

**The single test:** at the end, take the customer's most painful moment and follow its column straight down — can the room name every frontstage action, every backstage step, and every support process it depends on, and point to the line where it breaks? If the column bottoms out in a real system or team and a fail point is marked, the workshop built a blueprint. If it dead-ends at the line of visibility with "and then somehow it works," the people who own that gap weren't in the room — and that absence _is_ the finding.

## Hand-off

The blueprint is a redesign brief, not an end state. Marked **fail points and hot-spots** flow into the operational design work — handoff seams to `../service-model/handoffs-human-system.md`, the unhappy path to `../service-model/escalation-and-exceptions.md`, neglected ops tooling to `../service-model/fulfillment-and-ops.md`, channel jumps to `../service-model/cross-channel-continuity.md`, and self-serve vs. assisted routing to `../service-model/support-paths.md`. The answered **operational question** flows back to the service owner as a go / change / staff decision. Score the resulting blueprint with `rubric-service-model` — its **whole-journey blueprint `[gate]`** dimension and the column-descent hard test are the same test this workshop is built to pass.

## Sourcing

Shostack, "Designing Services That Deliver" (Harvard Business Review, 1984) — the blueprint, the line of visibility, fail points, and the "What if?" planning purpose. Marc S., Hormess, Lawrence & Schneider, _This Is Service Design Doing_ (O'Reilly, 2018) — blueprinting as a collaborative, facilitated method run with frontline staff and ops, not a designer working alone. NN/g, "Service Blueprinting" (nngroup.com) — running the workshop and the three-line (interaction / visibility / internal-interaction) convention. The lane anatomy and the four-line variant are the CONCEPT — see `../service-model/service-blueprints.md`; this file deliberately does not restate them. The ½–1-day timebox is a common practitioner range, not a figure from any single source — treat it as a default to fit the journey's size, not a rule.
