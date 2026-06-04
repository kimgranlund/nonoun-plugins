---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Jake Knapp, John Zeratsky & Braden Kowitz, *Sprint: How to Solve Big Problems and Test New Ideas in Just Five Days* (Simon & Schuster, 2016). https://www.thesprintbook.com/"
  - "Google Ventures (GV) — The Design Sprint. https://www.gv.com/sprint/"
method: design-sprint
phase: decide
domains: [1, 2, 11]
timebox: "5 days (modern variants compress to 4)"
cadence: one-off
participants: [decider, facilitator, pm, designer, engineer, "5 target users (Friday)"]
inputs: ["one high-stakes question or bet", "a Decider who attends all week", "a week of the team's time"]
produces: "a realistic prototype + 5 user tests + a validated or invalidated decision"
de_risks: [value, usability]
rubric: rubric-discovery
---

# Design Sprint — de-risk a big bet in a week

A **time-boxed five-day process** (Knapp / GV) that takes one high-stakes question from idea to a tested prototype — compressing months of discover → design → debate → build → test into a single week, _without building the real thing_. The point is not to build; it is to **buy a shortcut to validated learning** before committing engineering.

## When to run it · when NOT

**Run it** when there is one big, expensive, ambiguous bet (a new product, a risky flow, a pivot) — a high cost of being wrong and genuine disagreement about the answer. **Do NOT run it** when the answer is already known (just ship), when the problem is small (overkill), when there is no Decider who will attend all week (it will not stick), or when you cannot recruit 5 real target users for Friday — you lose the only validation step and it degrades into a workshop, not a sprint.

## The run (Mon → Fri)

| Day | Leads | Timebox | The move | Output |
| --- | --- | --- | --- | --- |
| **Mon — Map** | facilitator | 1 day | Set the long-term goal + sprint questions; map the problem; the Decider picks one target moment; "Ask the Experts" interviews | a map + a chosen target |
| **Tue — Sketch** | everyone (alone) | 1 day | Lightning demos (steal good ideas), then individual detailed sketching (notes → ideas → Crazy 8s → solution sketch) | competing solution sketches |
| **Wed — Decide** | Decider | 1 day | Critique sketches ("art museum" + heat-map dots), straw poll, then the Decider's **supervote**; storyboard the winner | a storyboard to prototype |
| **Thu — Prototype** | designer + a "stitcher" | 1 day | Build a realistic _façade_ (not real code) — just enough fidelity to test the storyboard | a clickable / Wizard-of-Oz prototype |
| **Fri — Test** | one interviewer | 1 day | Five 1:1 think-aloud interviews with target users; the team watches live and notes patterns together | a validated / invalidated answer + the next step |

## Roles

The **Decider** (the one who can actually commit — owns the supervote; attendance is non-negotiable), a **Facilitator** (runs time and process, stays neutral on _content_), and a small cross-functional **team** (PM, design, engineering, plus whoever holds key knowledge). Five **target users** on Friday. Seven people in the room is the ceiling — more and decisions stall.

## Failure modes (sprint theater)

- **No Decider, or one who skips days** → no real decision; the week yields a deck, not a commitment.
- **No real users on Friday** → you tested nothing; it was an internal workshop wearing a sprint's clothes.
- **Prototyping the real thing** → you spent the budget the sprint exists to protect; the disposable façade _is_ the method.
- **Solving an already-answered question** → expensive theater.
- **Consensus-seeking** → the supervote exists precisely to avoid design-by-committee; if the team votes instead of the Decider, you get mush.

## A good run vs. a bad run

|  | Bad run | Good run |
| --- | --- | --- |
| Question | vague, or already answered | one sharp, high-stakes bet |
| Decider | absent / a committee | present all week; owns the supervote |
| Friday | demoed to stakeholders | tested with 5 real target users |
| Output | a polished deck | a clear go / no-go + what was learned |

**The single test:** by Friday evening, can you name the decision the sprint _made_ and the user evidence that made it? If the answer is "we aligned the team," it was a workshop, not a sprint.

## Hand-off

A **validated** bet flows into delivery (→ story mapping for the build backbone, → `product-architecture` for the structure). An **invalidated** bet flows back to discovery (→ continuous discovery, → the opportunity-solution tree) — which is the cheap win: a week spent instead of a quarter built. Score the run with `rubric-discovery` (evidence strength · assumption testing · decision-readiness).

## Sourcing

Knapp, Zeratsky & Kowitz, _Sprint_ (Simon & Schuster, 2016) and the GV Design Sprint materials (gv.com/sprint). The five-day structure, the Decider and supervote, Crazy 8s, and the Friday five-user test are from the book; the 4-day and fully-remote variants are widely practised and noted here as variants, not the canonical book process.
