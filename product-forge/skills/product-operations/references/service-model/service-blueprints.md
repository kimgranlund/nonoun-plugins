---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "G. Lynn Shostack, 'Designing Services That Deliver,' Harvard Business Review 62, no. 1 (Jan–Feb 1984): 133–139. The origin of service blueprinting and the 'line of visibility.'"
  - "NN/g — 'Service Blueprints: Definition' (Sarah Gibbons). https://www.nngroup.com/articles/service-blueprints-definition/"
  - "Valarie A. Zeithaml, Mary Jo Bitner & Dwayne D. Gremler, *Services Marketing* — the four-line blueprint convention (line of interaction, line of visibility, line of internal interaction, line of implementation)."
  - "Marc S., Markus Edgar Hormess, Adam Lawrence & Jakob Schneider, *This Is Service Design Doing* (O'Reilly, 2018, ISBN 9781491927182) — blueprinting as a core service-design method."
---

# Service Blueprints

A journey map shows what the user experiences; a **service blueprint** shows everything the organization must do — across people, systems, and back-of-house process — to make that experience happen. NN/g calls the blueprint "a part two to customer journey maps": same horizontal time axis, but it extends downward through the layers the customer never sees. This is the load-bearing artifact for treating a product as a _service_ rather than a screen — it makes the invisible machinery visible, which is the only way to find where the promise and the delivery diverge. The technique is not new fashion: it was introduced by **G. Lynn Shostack, a bank executive, in HBR in 1984** ("Designing Services That Deliver"), specifically to take service delivery — then dismissed as intangible and ephemeral — and make it "documented, measured, controlled, and improved upon."

> Shostack's original purpose is the one to hold onto: a blueprint is a **planning tool for "What if?"** — management could reconfigure the service on paper, rerouting steps and stress-testing failure points, "without causing major disruptions in real time." A blueprint that only documents the current state, and is never used to redesign it, has been filed, not used.

## The layers: what stacks below the customer

A blueprint is read top-to-bottom as a stack of horizontal swimlanes, each separated from the next by a named line. NN/g's four elements, in order of depth:

| Layer | What lives here | Example (a refund request) |
| --- | --- | --- |
| **Physical evidence** (optional top band) | The tangible/digital touchpoints the customer encounters at each step | The app screen, the confirmation email, the SMS |
| **Customer actions** | "Steps, choices, activities, and interactions that customers perform" to reach a goal | Opens order, taps "Request refund," uploads photo |
| **— line of interaction —** |  |  |
| **Frontstage actions** | "Actions that occur directly in view of the customer" — human-to-human or human-to-computer | Agent greets in chat; the refund form renders and validates |
| **— line of visibility —** |  |  |
| **Backstage actions** | "Steps and activities that occur behind the scenes to support onstage happenings" | Agent checks fraud flags; warehouse confirms item not shipped |
| **— line of internal interaction —** |  |  |
| **Support processes** | "Internal steps and interactions that support the employees in delivering the service" | Payment-gateway API, fraud-scoring service, finance reconciliation batch |

The two diagnostic lines do the real work. The **line of visibility** is Shostack's original contribution — it cleaves what the customer can see from what they cannot, and most "experience" defects are really things gone wrong _below_ it that bled upward. The **line of interaction** sits one band higher, at the customer's own boundary: above it is what the user does, below it is what the organization does in response.

## NN/g's three lines vs. the four-line convention

There is a citation trap here worth naming precisely. **NN/g names three lines** — interaction, visibility, internal interaction. The older marketing-academic convention (Zeithaml, Bitner & Gremler, building on Shostack and Kingman-Brundage) names **four**, adding a **line of implementation** that separates day-to-day management/supervision from the deep support infrastructure. Both are legitimate; pick one and be consistent within a single blueprint. For most product work the three-line model is sufficient — reach for the fourth line only when management/governance activity is itself part of what you're redesigning (e.g., an escalation-approval layer).

## Canonical form

```text
PHYSICAL    | app screen  | refund form | confirmation email |
EVIDENCE    |             |             |                    |
============|=============|=============|====================|
CUSTOMER    | open order  | request     | upload photo       |  ← what the user does
ACTIONS     |             | refund      |                    |
------------+-------------+-------------+--------------------+  ← LINE OF INTERACTION
FRONTSTAGE  | chat greets | form        | "refund issued"    |  ← visible to customer
            |             | validates   | message            |
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .  ← LINE OF VISIBILITY
BACKSTAGE   | agent reads | fraud flags | agent triggers     |  ← hidden, human/internal
            | order data  | checked     | payment reversal   |
------------+-------------+-------------+--------------------+  ← LINE OF INTERNAL INTERACTION
SUPPORT     | order DB    | fraud-score | payment gateway +  |  ← systems & infrastructure
PROCESSES   | lookup      | service     | finance reconcile  |
```

Read a column top-to-bottom and you see the **full chain behind one moment**; read a row left-to-right and you see one actor's sequence. The diagnostic move is to find a column where a single customer action triggers a long, fragile descent through backstage and support — that depth is where the experience is most likely to break and slowest to recover.

## How to draw a blueprint from a journey

The blueprint is downstream of a journey map — never start it from scratch. The working sequence:

1. **Fix the scope and the actor.** One blueprint, one journey, one primary customer. "Returns" and "onboarding" are different blueprints. A blueprint that tries to cover every path becomes unreadable.
2. **Lay the customer-actions row first, from the journey.** Lift the steps straight off the journey map's stages — this row is the time axis everything else hangs from.
3. **Add physical evidence above each action.** What does the customer actually see/touch at this step? This anchors the abstract steps to real touchpoints.
4. **Drop the line of interaction, then map frontstage.** For each customer action, what does the org do _in view_? Name the channel (chat, IVR, screen) — frontstage actions are human-to-human or human-to-computer, and the distinction matters for who owns the step.
5. **Drop the line of visibility, then map backstage.** What has to happen out of sight for the frontstage step to succeed? This is where hidden dependencies surface.
6. **Drop the line of internal interaction, then map support processes.** Which systems, third parties, and internal teams does each backstage action call? These are the things that, when they fail, the customer feels but can't see.
7. **Draw the vertical dependency arrows.** Connect each customer action down through the column. A step with a long descent and many cross-team arrows is a fragility hot-spot.
8. **Annotate fail points and time.** Mark where steps commonly break (the "fail points" from Shostack's original method) and where the clock runs long. These annotations are what turn a diagram into a redesign brief.

## What a blueprint reveals (and a journey map can't)

- **Orphaned moments** — a customer action with no frontstage response, or a frontstage promise with no backstage capability to fulfill it. That gap is the literal shape of an unkept promise.
- **Cross-team handoff seams** — every place a backstage arrow crosses from one team's lane to another is a coordination risk; these seams are where context gets dropped (see `handoffs-human-system.md`).
- **Single points of failure** — a support process that many customer actions depend on. When it degrades, multiple journeys fail at once.
- **Channel discontinuities** — where the same journey jumps channels and the backstage doesn't carry state across (see `cross-channel-continuity.md`).
- **Cost concentration** — columns thick with human backstage labor are where assisted-channel cost piles up; these are the candidates for self-serve deflection (see `support-paths.md`).

## Anti-patterns

| Anti-pattern | Why it fails | The fix |
| --- | --- | --- |
| **Blueprint as documentation, never used to redesign** | Violates Shostack's whole purpose — it was a "What if?" tool | Use it to reroute steps and pre-mortem failure points on paper |
| **Boiling the ocean** — one mega-blueprint for the whole product | Becomes an unreadable wall; no one can trace a single path | One blueprint per journey per primary actor |
| **Skipping the journey map** and blueprinting from imagination | The customer-actions row becomes the org's assumptions, not real behavior | Build the journey from research first; lift the top row from it |
| **No vertical dependency arrows** | You get four parallel lists, not a system; dependencies stay hidden | Connect each column top-to-bottom; the arrows _are_ the insight |
| **Mixing the 3-line and 4-line conventions** in one diagram | Readers can't tell what a line separates | Choose three or four lines up front; label every line |
| **Frontstage with no backstage to support it** left unflagged | The exact location of a broken promise, silently filed | Mark it as a fail point — it is a finding, not a cell to fill in |
| **No fail points or timings annotated** | A pretty diagram with no redesign signal | Mark where it breaks and where it's slow; that's the brief |

## Good vs. bad (for scoring)

| Dimension | Good — a working blueprint | Bad — a wall-decoration diagram |
| --- | --- | --- |
| **Provenance** | Customer-actions row lifted from real journey research | Invented from internal assumptions |
| **Layering** | All four NN/g elements present, separated by named lines | Flat list of steps; lines absent or unlabeled |
| **Line of visibility** | Drawn explicitly; used to locate where defects originate | Missing — frontstage and backstage blurred together |
| **Dependencies** | Vertical arrows trace each moment's full chain | Four disconnected swimlanes |
| **Scope** | One journey, one actor, readable in one view | Everything at once; unreadable |
| **Diagnosis** | Fail points, hot-spots, and timings annotated | No annotations; no redesign signal |
| **Purpose** | Drives a "What if?" redesign | Filed after the workshop, never reopened |

The single test: **pick the customer's most painful moment and follow its column straight down.** If you can name every frontstage action, every backstage step, and every support process that moment depends on — and point to the line where it breaks — the blueprint is doing its job. If the column dead-ends at the line of visibility with "and then somehow it works," you've found the unmanaged gap the blueprint exists to expose.
