---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "NN/g — Journey Mapping 101 (nngroup.com/articles/journey-mapping-101)."
  - "NN/g — Customer Journey Maps: When and How to Create Them (nngroup.com/articles/customer-journey-mapping)."
  - "NN/g — 7 Ways to Analyze a Customer-Journey Map (nngroup.com/articles/analyze-customer-journey-map)."
  - "G. Lynn Shostack, “Designing Services That Deliver,” Harvard Business Review (Jan 1984) — origin of the service blueprint."
  - "Jan Carlzon, *Moments of Truth* (Ballinger, English ed. 1987) — the term popularized for frontline customer interactions; phrase originally introduced by SAS strategy consultant Richard Normann."
---

# Journeys & Maps (mapping as architecture)

This is the working method for using a journey map as an _architecture_ artifact, not a workshop souvenir. A journey map is "a visualization of the process that a person goes through in order to accomplish a goal" (NN/g). Treated as architecture, it is the document that lays out the temporal structure of an experience — the stages a user passes through, the moments where the experience is won or lost, the emotional arc, and the gaps where the product fails the user. It answers a question the screen inventory (`surfaces-and-screens.md`) and the state model (`states-and-continuity.md`) cannot: **over time, end to end, what does this person actually go through, and where does it break?** The output that earns its keep is not the map — it is the prioritized list of opportunities the map exposes.

## The anatomy NN/g converges on

A journey map has a stable structure. NN/g's Journey Mapping 101 frames it in three bands. Learn the bands, because a map missing one of them is incomplete.

| Band | Contains | Why it's load-bearing |
| --- | --- | --- |
| **Zone A — the lens** | A specific **actor** (one persona, not "users") and a specific **scenario + goal** | Constrains the map to one realistic journey; a map for "everyone doing everything" maps nothing |
| **Zone B — the experience** | **Phases/stages** across the top, and under each: **actions**, **thoughts/mindsets**, and **emotions** (the emotion curve) | The narrative core — what the user does, thinks, and feels at each stage |
| **Zone C — the takeaways** | **Opportunities**, insights, and **internal ownership** (who acts on each) | Converts the map into action; without ownership, nothing changes |

The four elements that recur in every credible journey map: **(1) the actor** (the persona whose journey it is), **(2) the scenario and expectations** (the situation and what the user hopes for), **(3) the journey phases with actions/thoughts/emotions**, and **(4) the opportunities** with ownership and metrics.

## Stages: the temporal skeleton

Stages are the high-level phases that organize everything else. They are domain-shaped, not generic — NN/g's own examples vary by context:

- **E-commerce:** discover → try → buy → use → seek support
- **Considered/luxury purchase:** engagement → education → research → evaluation → justification
- **B2B / internal tool rollout:** purchase → adoption → retention → expansion → advocacy

The discipline: **derive stages from research, in the user's terms, not from your funnel or your org chart.** A common failure is labeling stages with internal process names ("lead", "MQL", "onboarding ticket") — that maps your operations, not the user's experience. Stages should read as a story the user would recognize as their own.

## Moments of truth: where the experience is decided

A **moment of truth** is a point in the journey where a key event occurs and the user forms a lasting opinion — the touchpoint where they "fall in love or leave." The term comes from **Jan Carlzon's _Moments of Truth_** (1987), describing his SAS turnaround: an airline's reputation is decided not in headquarters but in thousands of daily frontline encounters. (Carlzon popularized it; the phrase was introduced by SAS consultant Richard Normann.) For architecture purposes, moments of truth are where you concentrate effort — they are the journey's pivotal points, the equivalent of Richard R.'s "source of power" applied to experience. Not every touchpoint is a moment of truth; the skill is identifying the few that disproportionately shape the relationship (a first successful use, a failed payment, a support recovery, a renewal decision).

## The emotion curve

Emotions are plotted as a single line tracing the highs and lows across the stages — "a contextual layer of emotion that tells us where the user is delighted versus frustrated" (NN/g). It is not decoration; it is a diagnostic. The shape of the curve tells you where to act:

- **A trough at a moment of truth** is the highest-priority opportunity — a low point precisely where opinion is being formed.
- **A sharp drop between two adjacent stages** signals a transition the product handles badly (a hand-off, a context switch, an unexplained wait).
- **A flat-low stretch** signals a tedious passage users endure; a flat-high stretch you should protect and avoid "improving" into novelty.

Plot the curve from evidence — quotes, observed behavior, support tickets — not from how you imagine the user feels. A curve invented at a whiteboard reflects the team's assumptions, which is exactly what mapping is supposed to test.

## How to build one from research (not from a workshop alone)

A map's authority comes entirely from its inputs. The procedure:

1. **Set the lens.** Pick one actor and one scenario. Resist the urge to combine personas; make multiple maps instead.
2. **Gather qualitative + quantitative evidence.** Interviews, diary studies, session recordings, support logs (qual) plus analytics, drop-off rates, time-on-task (quant). NN/g's stance: hypothesis maps built only from internal assumptions are a starting point to be _validated_, never the finished artifact.
3. **Extract stages from the data.** Let the phases emerge from how users actually describe their process, then name them in their words.
4. **Populate actions/thoughts/emotions per stage** with cited evidence — attach real quotes and data points to each cell so the map is auditable.
5. **Mark touchpoints and moments of truth**, including off-product ones (an email, a phone call, a delivery, packaging) — the journey doesn't pause when the user leaves your screen.
6. **Plot the emotion curve** from the evidence.
7. **Derive opportunities and assign ownership.** Every low point and gap becomes a candidate opportunity with a named owner and, ideally, a metric. This Zone-C output is the deliverable.

## Journey map vs. experience map vs. service blueprint

These three are routinely confused, and using the wrong one wastes the effort. They differ on **scope** and on **whose machinery they expose.**

| Artifact | Scope | Whose perspective | When to reach for it |
| --- | --- | --- | --- |
| **Customer / user journey map** | One actor, one product/service, end-to-end goal | The user's, across _your_ touchpoints | You need to find where _your product_ fails a user over time |
| **Experience map** | A general human behavior or goal, **product-agnostic** | A person's, independent of any one company | You're entering a new domain and need to understand the broad human experience _before_ designing a product into it |
| **Service blueprint** | One service, **both sides of the stage** | The user _and_ the organization's internal delivery | You need to fix _why_ a journey fails — by exposing the backstage operations that cause front-stage pain |

The **service blueprint** is the deepest of the three and the one architects most under-use. It originates with **G. Lynn Shostack's "Designing Services That Deliver"** (HBR, 1984). Its defining feature is the **line of visibility**: the horizontal divider separating what the customer can see (front-stage) from the internal reality (backstage). The canonical five-component structure (Bitner, Ostrom & Morgan, 2008) stacks: **(1) physical evidence → (2) customer actions → [line of interaction] → (3) front-stage / onstage actions → [line of visibility] → (4) backstage actions → [line of internal interaction] → (5) support processes.** The architectural insight: **most service failures don't originate where the user feels them — they originate one or more layers below the line of visibility,** in backstage processes or support systems a journey map never captures. The journey map's customer-action row _is_ the top row of the blueprint, so the two compose: map first to find _where_ it hurts, blueprint to discover _why._

```text
   physical evidence  │ app screen │  email   │  package   │   ...
   ───────────────────┼────────────┼──────────┼────────────┼─────
   CUSTOMER ACTIONS   │  orders    │  waits   │  receives  │        ← the journey map lives here
   ─── line of interaction ──────────────────────────────────────
   FRONTSTAGE         │ confirm UI │ status   │  courier   │        ← what the user sees
   ─── line of VISIBILITY ───────────────────────────────────────  ← failures usually originate BELOW here
   BACKSTAGE          │ fulfilment │ warehouse pick/pack    │
   ─── line of internal interaction ─────────────────────────────
   SUPPORT PROCESSES  │ inventory db · payment gateway · 3PL │
```

## What to check (good vs. bad)

| Dimension | Bad | Good |
| --- | --- | --- |
| **Lens** | "All users" doing many things on one map | One named actor, one scenario, one goal |
| **Stages** | Internal process / funnel labels (MQL, ticket) | Phases in the user's words, derived from research |
| **Evidence** | Invented at a whiteboard from team assumptions | Each cell cites quotes/data; hypothesis maps are validated, not shipped |
| **Emotion curve** | A smooth arc that flatters the product | A jagged curve with troughs at real moments of truth |
| **Touchpoints** | Only on-screen moments | Includes off-product touchpoints (email, delivery, call) |
| **Moments of truth** | Every touchpoint treated as equal | The pivotal few identified and prioritized |
| **Output** | A pretty poster with no actions | Opportunities with owners and metrics (Zone C) |
| **Right artifact** | A journey map used where a blueprint was needed (failure cause stays hidden) | Journey map to locate pain; blueprint to expose its backstage cause |

The fastest single test: ask what the team _will do differently_ because of the map. If the answer is "we understand the user better," it's a poster. If the answer is a ranked list of changes with owners, it's architecture.

## One labeled caveat

The journey-map anatomy (the three zones, actions/thoughts/emotions, the emotion curve, stages-from-research) and the journey/experience-map/blueprint distinctions are drawn from NN/g's articles cited above and are consistent across the field. The service-blueprint origin (Shostack, HBR 1984) and the five-component model (commonly attributed to Bitner, Ostrom & Morgan, 2008) are well established; the exact component count and labels vary slightly by author, so verify against the specific source if a canonical list is needed. "Moments of truth" is correctly attributed to Carlzon's 1987 book with the phrase originating from Richard Normann; this is well documented but was cross-checked against secondary summaries here rather than the print editions.
