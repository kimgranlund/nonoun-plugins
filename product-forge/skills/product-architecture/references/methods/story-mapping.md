---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Jeff Patton, *User Story Mapping: Discover the Whole Story, Build the Right Product* (O'Reilly, 2014). https://www.jpattonassociates.com/user-story-mapping/"
  - "Jeff Patton, “The new user story backlog is a map” (jpattonassociates.com/the-new-backlog/) — the origin essay for the backbone/body and the walking-skeleton slice."
method: story-mapping
phase: structure
domains: [2]
timebox: "½-day workshop"
cadence: one-off
participants: [facilitator, pm, designer, engineer, "a domain/user voice"]
inputs: ["a validated direction or problem to build", "one or two specific user types + their goal", "the team that will build it in the room"]
produces: "a story map — the activity backbone + prioritized tasks, sliced into releases"
rubric: rubric-architecture
---

# Story Mapping — turn a flat backlog into a sliced, walkable plan

A **½-day collaborative workshop** (Patton) that lays a product's work out as a two-dimensional map — a left-to-right **backbone** of the activities a user moves through, a top-to-bottom **body** of the tasks under each, prioritized — and then **slices** the body horizontally into releases, where the first slice is a viable end-to-end **walking skeleton**. The point is not to enumerate stories; it is to **make scope and release sequencing a decision the whole team can see and argue with**, replacing the flat priority list that hides the narrative.

## When to run it · when NOT

**Run it** once you have a validated direction and need to turn it into buildable, sequenced work — a new product, a major feature area, an MVP whose scope is contested, or a flat backlog nobody can reason about as a whole. It earns its keep precisely when the team is about to over-build the first release and needs a shared way to cut it. **Do NOT run it** when the direction itself is unvalidated (map nothing until discovery has answered the bet — that is a Design Sprint's job, not this), when the work is a handful of unrelated tickets with no user narrative to lay out (a list is fine; a map is overkill), or when the people who will build it aren't in the room — a map authored by one person and handed down is a backlog with extra steps, and loses the shared understanding that is the actual product of the session.

## The run (backbone → body → slices)

| # | Step | Who | Timebox | Output |
| --- | --- | --- | --- | --- |
| **1 — Frame** | State the user(s), their goal, and the validated direction being built; agree the map is for _one_ narrative | facilitator + pm | 20 min | a named user + goal scoping the map |
| **2 — Build the backbone** | Write the **user activities / big steps** on cards, left→right in the order the user does them — the narrative flow ("the spine"), not features | everyone | 45 min | the activity backbone across the top |
| **3 — Fill the body** | Under each activity, brainstorm the **tasks** that accomplish it; one card per task, placed beneath its activity | everyone | 60 min | tasks hanging under each backbone step |
| **4 — Prioritize vertically** | Within each column, drag the most essential tasks **up**, the optional/elaborate ones **down** — height = necessity | everyone | 30 min | each column ranked top→bottom by priority |
| **5 — Walk it & find gaps** | Read the backbone left→right aloud as a story; surface missing steps, alternatives, and exception paths the happy line skipped | everyone | 30 min | a validated, gap-checked narrative |
| **6 — Slice into releases** | Draw a horizontal line across the whole map; everything above it = **release 1**. The top slice must reach end-to-end across the _whole_ backbone — a **walking skeleton**, thin but complete | facilitator + pm | 30 min | a sliced map: a viable first release + later slices |

## Roles

A **Facilitator** keeps the map a narrative (defends left→right flow against feature-listing and keeps the group from rat-holing on one column), the **PM/product owner** owns the user, the goal, and ultimately where the slice line falls, and a cross-functional **team** — design, engineering, plus a domain or user voice — builds the body and tests feasibility live. The team being present _is_ the deliverable: the shared understanding outlasts the cards. Keep it small enough that everyone touches the wall.

## Failure modes (mapping theater)

- **A feature list turned sideways** → the backbone reads as system functions ("login", "settings", "dashboard") instead of user activities; you've drawn a sitemap, not a journey, and lost the narrative the method exists to expose.
- **No slice, or a vertical slice** → you map but never cut, so it's just an organized backlog; or release 1 is one whole activity done deeply (a leg, not a skeleton) and the product can't be walked end-to-end. The first slice must span the _entire_ backbone thinly.
- **Authored solo and presented** → one person makes the map and shows it to the team; the shared understanding — the real output — never forms, and you have a backlog with prettier formatting.
- **Mapping an unvalidated bet** → laying out the build for a direction discovery hasn't confirmed; you've sequenced work that may not be worth doing.
- **Cards = exhaustive specs** → treating every card as a finished, estimated story up front; the map is a conversation tool, and over-documenting it freezes it before the body is even prioritized.

## A good run vs. a bad run

|  | Bad run | Good run |
| --- | --- | --- |
| Backbone | system features laid sideways | user activities in narrative order |
| Body | unranked pile of tasks | each column prioritized by necessity, top→bottom |
| Gaps | only the happy path on the wall | alternatives and exceptions surfaced by walking it |
| First slice | one activity built deep (a vertical leg) | a thin end-to-end walking skeleton across the whole backbone |
| Authorship | one person's map, handed down | built together; shared understanding is the product |

**The single test:** can you trace the top slice left-to-right across the _entire_ backbone and tell one complete (if minimal) user story end to end? If the slice covers some activities richly but skips others, it isn't a walking skeleton — it's a leg, and the product won't stand up.

## Hand-off

The map is the architecture artifact that sequences the build. The backbone composes with the journey it implements — derive or sanity-check it against the user's `../experience-architecture/journeys-and-maps.md` (the journey supplies the stages and moments of truth the backbone narrates) — and each non-trivial task card hands off to `../experience-architecture/flows-and-task-design.md`, where its happy path, branches, and dead-ends get designed before any screen is drawn. The slice line feeds release planning: the walking skeleton becomes release 1's scope, lower slices become the next increments. Score the resulting structure with `rubric-architecture` (plane coherence · journey/flow integrity · state coverage) — the map should make a coherent first slice obvious, not hide an over-scoped one.

## Sourcing

Jeff Patton, _User Story Mapping_ (O'Reilly, 2014), and his origin essay "The new backlog is a map" (jpattonassociates.com). The backbone/body two-dimensional structure, the narrative left→right flow, vertical prioritization, and the horizontal release slice with the first slice as a viable walking skeleton are all Patton's. "Walking skeleton" is an Agile term Patton adopts (originating with Alistair Cockburn) for a thin end-to-end implementation; it is noted here as borrowed, not coined by the book. The ½-day timebox is a common workshop length for a single product area, not a fixed prescription from the text — larger products map over longer sessions.
