---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Marty C., 'Dual-Track Agile', Silicon Valley Product Group (svpg.com/dual-track-agile)"
  - "Marty C., *Inspired: How to Create Tech Products Customers Love*, 2nd ed. (Wiley, 2017) — Part IV, Product Discovery; the Customer Letter technique (svpg.com/the-customer-letter)"
  - "Jeff Patton, *User Story Mapping: Discover the Whole Story, Build the Right Product* (O'Reilly, 2014)"
  - "Jeff Patton, 'Dual Track Development is not Duel Track' (jpattonassociates.com/dual-track-development)"
  - "Jeff Patton & Comakers LLC, 'Story Map Concepts' / 'Story Map Process' handout (jpattonassociates.com, ©2013)"
---

# Dual-Track Discovery and Delivery

Dual-track is the answer to a single question: if discovery is a continuous habit (see `continuous-discovery.md`) and delivery is also continuous, how do the two streams coexist on one team without becoming a relay? The answer Jeff Patton and Marty C. converged on around 2012 — first as **dual-track scrum**, later **dual-track agile** — is that they run **in parallel, on the same team**, with discovery feeding validated work into delivery and delivery feeding fresh questions back into discovery. This reference defines the two tracks precisely, kills the two-teams misreading, and adds two artifacts that make a team's discovery legible: Patton's **story map** and Marty C.'s **customer letter**.

> Patton's correction is the load-bearing one: dual track is **not "duel track."** _"Discovery and development are shown in two tracks because they're two kinds of work, and two kinds of thinking"_ — not two kinds of people. The tracks are concurrent _activities_ owned by one cross-functional team, never two staffed groups handing artifacts across a fence.

---

## The two tracks

Each track produces a different output and runs to a different standard of done. The discipline is holding both, every week, on one team — not finishing one before starting the other.

|  | Discovery track | Delivery track |
| --- | --- | --- |
| **The work** | _"the work that we do to decide what to build"_ (Torres) — interviews, assumption tests, prototypes | The work to build, ship, and maintain production-quality software |
| **Output** | Validated backlog items — ideas that have cleared the riskiest assumptions | Releasable, instrumented software |
| **Standard of done** | "We have enough evidence to commit / kill / iterate" | Production quality: tested, performant, scalable, reliable |
| **Speed posture** | _"validate our ideas the fastest, cheapest way possible"_ (Marty C.) | Predictable, frequent, reliable shipping |
| **Primary artifact** | Prototypes (see `idea-to-prototype.md`), the opportunity solution tree, the story map | Working software in front of users |

The flow between them is the point: **discovery's output is delivery's input.** Validated items move from discovery onto the backlog; only ideas that survived a cheap test get the expensive resource — engineering time. Patton's framing of the team's job: _"minimize output, and maximize outcome and impact."_

---

## Parallel, not sequential

The model exists to defeat one specific failure: the **mini-waterfall**, where even an "agile" team runs discovery as a phase that exits into a delivery phase. Dual track _"captures the parallel nature of Discovery and Delivery,"_ so the two progress simultaneously rather than in sequence.

```text
        ┌──────────────── DISCOVERY (continuous) ────────────────┐
week →   interview · prototype · assumption test · interview · …  │
        └────────────┬──────────────┬─────────────────────────────┘
                     │ validated     ▲ fresh questions
                     ▼ items         │ from what shipped
        ┌──────────────────────────────────────────────────────────┐
week →   build · ship · build · ship · build · ship · …             │
        └────────────────────────── DELIVERY (continuous) ──────────┘
```

Two correcting loops run at once. Discovery pushes validated work _down_ into delivery; delivery pushes _up_ the questions that only contact with real shipping surfaces (a metric that did not move, an edge case users hit). Neither track waits for the other to "finish," because neither finishes. The cadence — not a phase gate — is what keeps bets honest.

A caution that follows directly: dual track is **not a license for infinite research before any build.** The discovery track is sized to small weekly activities precisely so it keeps pace with shipping. A team that runs months of discovery before delivery starts has rebuilt the waterfall with new labels.

---

## The two-teams anti-pattern

The most common and most damaging misreading: staffing a "discovery team" (product + design) and a separate "delivery team" (engineering). This was never the intention, and it reintroduces the relay the model was built to remove.

| Lever | Dual track (one team, two tracks) | Two-teams anti-pattern |
| --- | --- | --- |
| **Who discovers** | The whole cross-functional team; PM/designer/engineer lead but _"involve the whole team in discovery tasks wherever possible"_ (Patton) | Product/design discovers; engineering only delivers |
| **Engineering's role** | In discovery — surfacing feasibility, killing infeasible ideas cheaply, spotting "build it in a day" shortcuts | Receives a validated spec; first sees the idea at delivery time |
| **Accountability** | _"The whole team is responsible for product outcomes, not just on-time delivery"_ (Patton) | Discovery owns the idea; delivery owns the date — split accountability |
| **Failure mode** | — | Engineers de-risk feasibility too late; designers/PMs validate things that cannot be built affordably |

> The test: **could the engineer recount the customer story behind the thing they are building?** If discovery happened on another team, the answer is no — and feasibility was never on the table when it was cheap to change. One team, two tracks; not two teams.

---

## The story map (Jeff Patton)

A story map is Patton's antidote to the **flat backlog** — the prioritized list that loses the shape of the user's journey the moment it is sorted. It is a two-dimensional arrangement of the work around the order a user actually experiences it, and its first job is **shared understanding**, not documentation: _"shared documents aren't shared understanding."_ The map is the conversation's residue, not a substitute for the conversation.

The structure has named parts:

- **The backbone** — the top row. _"Activities and tasks at a higher goal level give the story map its structure. The backbone is arranged in a narrative flow."_ These are the high-level user activities, the spine the rest hangs from.
- **Narrative flow** — the left-to-right axis. _"The left to right axis in a story map is organized in the order you'd tell the story about your user to someone else."_ You read the backbone like a sentence: the user does this, then this, then this.
- **The body / ribs** — beneath each backbone activity, the stack of smaller tasks, alternatives, exceptions, and details that fulfill it, hanging down vertically. _"Smaller sub-tasks, details and variations hang down to form the ribs."_
- **Release slices** — horizontal cuts across the map. _"Use a tape line to identify slices of tasks that users might use your software for to reach their goals."_ Each slice spans the whole journey at a thinner level of completeness.

A practical naming rule Patton stresses: **"User Tasks make great story titles"** — write tasks as short verb phrases, and the backbone reads as the story.

### The walking skeleton

The first, thinnest release slice is the **walking skeleton**: _"the smallest number of tasks that allow your specific target users to reach their goal"_ — a _"functional walking skeleton, the simplest possible functional version of the product."_ It crosses the entire backbone end-to-end at minimum depth, so the user can complete the whole journey, just barely. The contrast is the **horizontal layer-cake** trap: building all of one activity to full depth before any of the next, which produces a half-product no user can walk through. Slice _across_ the backbone (a thin end-to-end path), never _down_ one column.

```text
backbone →   [ Browse ]   [ Choose ]   [ Pay ]   [ Track order ]   ← narrative flow, left→right
            ┌──────────┬────────────┬─────────┬───────────────┐
 skeleton   │  list    │  see price │  card   │  email status │  ← thin slice across ALL activities
            ├──────────┼────────────┼─────────┼───────────────┤
 release 2  │  search  │  reviews   │  PayPal │  live map     │  ← next slice adds depth everywhere
            ├──────────┼────────────┼─────────┼───────────────┤
 later      │  filters │  compare   │  wallet │  notifications│
            └──────────┴────────────┴─────────┴───────────────┘
```

### Patton's five-step process

Patton's canonical handout lays the build sequence out as five steps; the order is the method.

1. **Frame.** Write a short product/feature brief first — _what_ (the product/problem), _who_ (the user types and the chooser), and _why_ (the benefit to the business). Constrain before you map.
2. **Map the big picture.** _"Focus on getting the whole story"_ — go _"mile-wide, inch-deep."_ Start with the most critical user type; walk a typical day left to right; add other user types as they enter the story.
3. **Explore.** Fill the body. Think _"blue sky"_ — play _"wouldn't it be cool if…,"_ look for variations and exceptions, consider other users, _"and don't worry that your ideas are 'in or out of scope.' You'll deliberately move things out of scope later."_ Involve developers here; they _"find holes"_ and _"point out risky or expensive areas."_
4. **Slice out viable releases.** Cut horizontal slices, each a _"minimal viable product release."_ For each release, **name the target outcome and the success metric** — _"what would we measure to determine if this product was successful?"_ Releases are defined by outcomes, not by feature counts.
5. **Slice out a development strategy.** Within the first release, split into delivery phases — _opening / mid / end game_ — to learn fast and reduce risk early, workshopping each story's detail with developers and testers.

> The map's purpose statement, in Patton's words: it is for _"understanding now, and imagining later."_ It exists so a team can **plan to build less** — slice out the thin viable path and consciously defer the rest, rather than committing to a flat list with no shape.

---

## The customer letter (Marty C.)

The customer letter is Marty C.'s variation on Amazon's "working backwards" press release. Where Amazon drafts a launch press release and a PR/FAQ before building, Marty C. reframes it as a **letter from an imagined, already-happy customer to the CEO**, written from the perspective of one of the product's well-defined personas, explaining why they are grateful for the product and how it changed their experience — paired with the **CEO's congratulatory reply** describing the business impact.

It is a discovery artifact with two jobs:

- **A forcing function on value and clarity.** Writing as a delighted customer forces the team to articulate the actual benefit in human terms, _before_ a line of production code — the same discipline as Amazon's press release ("a forcing function to ensure the creator is focused on the customer"). If the letter is vague or unconvincing, the value risk is unaddressed.
- **An alignment artifact for the trio and stakeholders.** The letter (customer) plus the reply (CEO) makes both halves of Marty C.'s frame visible at once: **customer value** in the letter, **business value** in the CEO's response. A letter that thrills the customer but has no plausible CEO reply has not closed the business-viability risk (see `four-big-risks.md`).

> Read alongside the story map, the two artifacts cover complementary gaps. The customer letter pins down **why** — the value, in the customer's own imagined voice. The story map pins down **what and in what order** — the journey, sliced into a walking skeleton. Discovery that produces both has stated the benefit and the path; discovery that produces neither is running on opinion.

---

## The "are you actually running two tracks?" test

Dual track is easy to claim (any team that does some research and some building can say it). Run this against the **last few weeks**:

- [ ] **Both tracks ran, concurrently.** Did discovery _and_ delivery both produce output recently — or did one stall while the other ran (a phase, not a track)?
- [ ] **One team, not two.** Was discovery done by the same cross-functional team that ships — engineer included — or handed over from a separate discovery group?
- [ ] **Validated in, questions out.** Did at least one item enter the backlog because a test cleared it, and did at least one shipped thing raise a question that re-entered discovery?
- [ ] **Discovery stayed small.** Were the discovery activities week-sized, keeping pace with delivery — or a multi-month study that put delivery on hold?
- [ ] **The shape survived.** Is the work organized by the user's journey (a story map / backbone) or flattened into a priority list that lost the narrative?
- [ ] **A walking skeleton, not a layer cake.** Is the first release a thin end-to-end path the user can complete — or one activity built to full depth with the journey still broken?

If discovery and delivery are sequential, or staffed as two teams, or discovery has swelled into a phase, the team has the dual-track vocabulary and the single-track reality. The fix is structural: one team, both kinds of work every week, sliced thin enough that neither track waits on the other.
