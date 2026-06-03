---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Gartner — 'Gartner Survey Finds Only 14% of Customer Service Issues Are Fully Resolved in Self-Service' (Aug 2024); earlier 2019 figure was 9%. https://www.gartner.com/en/newsroom/press-releases/2024-08-19-gartner-survey-finds-only-14-percent-of-customer-service-issues-are-fully-resolved-in-self-service"
  - "Gartner — benchmark median cost per contact: ~$1.84 self-service vs ~$13.50 assisted (live/phone/chat). Widely cited Gartner contact-center benchmark; confirm current figure before quoting."
  - "U.S. Federal Trade Commission — 'Click-to-Cancel' rule / negative-option guidance: cancellation/contact must be as easy as sign-up (hard-to-reach contact treated as a deceptive practice). https://www.ftc.gov/"
  - "Industry practice on deflection rate vs. abandonment rate as distinct support metrics (contact-center / CX literature, 2024–2026). Practitioner consensus; verify specific benchmarks before citing."
---

# Support Paths

Support is not a fallback bolted onto the product — it is **a designed path that is part of the product**, and for many users it is the moment that decides whether they stay. This file is the _operations_ view of help: support as a routed journey from self-serve to assisted to human, the economics that make the routing matter, and the experience of being supported as a first-class design surface. (For the _in-product UI_ layer — tooltips, contextual panels, help-center content patterns — see the product-patterns reference on in-product help; this file picks up where the UI layer hands off, at the support _organization_ and its paths.) The defining tension is **deflection vs. abandonment**: routing a user to self-serve is a win only if the user actually resolves their problem there — and a hidden loss if they merely give up.

> The reframe that fixes most support design: a support path has two very different success states that look identical in a naive metric. **Deflection** = the user intended to contact support but resolved it themselves. **Abandonment** = the user intended to contact support, couldn't find or reach help, and quit unresolved. Both reduce ticket volume. Only one is good. A support strategy optimized for "fewer tickets" without distinguishing the two is optimizing for customers giving up.

## The economics that make routing worth designing

Two numbers from Gartner anchor why this is an operations problem and not just a UX nicety:

- **Self-serve is roughly an order of magnitude cheaper per contact** — Gartner benchmarks median cost per contact near **$1.84 for self-service vs. ~$13.50 for assisted channels**. The pull toward deflection is real and rational.
- **But self-serve resolution is low** — Gartner found only **14% of issues are fully resolved in self-service (2024; it was 9% in 2019)**. So the cheap channel frequently _doesn't actually resolve the issue_ — it just pushes the user to another channel, often after burning their patience.

The design consequence: **measure resolution, not deflection.** Cost savings from a channel the user abandons are illusory — the user comes back angrier through a more expensive channel, or churns. The right metric for an AI/self-serve layer is **cost per resolution**, not cost per contact, precisely because the latter rewards pushing volume around without solving anything.

## The path: self-serve → assisted → human

Support is a staircase the user climbs only as far as they need to. Each rung is cheaper and faster than the next; each must resolve what it can and **hand off cleanly when it can't** (warm handoff — see `handoffs-human-system.md`).

```text
Rung 0  Prevent the question     Clear product, good defaults, contextual help at point of need
Rung 1  Self-serve answer        Searchable docs / help center / FAQ — scannable, task-focused, with steps
Rung 2  Assisted self-serve      AI assistant / bot grounded in the docs, citing sources, with a human escape
Rung 3  Async human              Ticket / email / message — pre-filled with context (page, account, error)
Rung 4  Synchronous human        Live chat / call — for blocking, account-specific, or high-stakes issues
```

Two laws govern the staircase, and they are in tension by design:

- **Don't skip rungs upward by default.** Don't throw a "contact support" button at a user who hasn't been offered a self-serve answer first — it's expensive for both sides and trains escalation. _Route the cheap rung first._
- **Don't trap the user at a rung.** A self-serve layer with no visible escape to a human is the support equivalent of a maze. The FTC treats hard-to-reach contact/cancellation as deceptive-by-omission — and operationally it manufactures abandonment. _Always leave a visible door up._

The art is calibrating these two: route to self-serve _and_ keep the human door visible. A path that does only the first creates abandonment; a path that does only the second wastes the cheap rung.

## Deflection vs. abandonment: telling them apart

Because both states reduce tickets, you have to instrument the difference deliberately. Tells of healthy deflection vs. hidden abandonment:

| Signal | Healthy deflection | Hidden abandonment |
| --- | --- | --- |
| After self-serve, the user… | leaves and does not return on the same issue | returns via another channel, or churns |
| Search behavior | finds a relevant result, stops | searches repeatedly, refines, then quits |
| Path to a human | visible and used when needed | absent or buried — user gives up looking |
| Sentiment / re-contact | no re-contact; CSAT holds | re-contact on the same issue; CSAT drops |
| What the metric rewards | resolution at the lowest rung | volume reduction regardless of outcome |

The diagnostic instrument is the **"contact us" path on a failed self-serve action**: a search that returns nothing useful should offer an escape to a human, **pre-filled with what was searched.** If your zero-result page is a dead end, you are converting deflection attempts into abandonment, and your ticket-volume drop is partly customers quitting.

## The support experience is part of the product

Treat the support path with the same design rigor as the core flow, because to the user it is the same product:

- **Continuity of context across rungs.** Each step up the staircase must carry the user's context forward — the failed search, the bot transcript, the account state — so they never repeat themselves (see `handoffs-human-system.md`). Context dropped between rungs is the most common support-experience defect.
- **Honesty about wait and capability.** State the expected wait and what each channel can actually do. A "we'll respond in 24h" that takes a week is worse than an honest "2 business days."
- **At least two channels at the human rung.** Don't force everyone into one contact mode; NN/g-style guidance and basic accessibility both argue for offering a choice (e.g., chat _and_ email) so users with different constraints can reach help.
- **The escape hatch is sacred.** The path to a human must be findable from the point of frustration, not buried in a footer. Burying it is both a dark pattern and an abandonment factory.
- **Close the loop back into the product.** High-volume support topics are unshipped product fixes or missing contextual help. A support path that never feeds its top issues back into Rung 0 is treating symptoms forever (see `fulfillment-and-ops.md`).

## Anti-patterns

| Anti-pattern | Why it fails | The fix |
| --- | --- | --- |
| **Optimizing for deflection / ticket volume** | Rewards customers giving up; abandonment counts as a "win" | Measure resolution and cost-per-resolution, not contacts avoided |
| **Hidden / buried "contact a human"** | Manufactures abandonment; FTC-style deceptive omission | Visible human escape from the point of frustration; ≥2 channels |
| **Zero-result search with no next step** | Converts a deflection attempt into a dead end | Offer "still stuck? contact us," pre-filled with the query |
| **Self-serve maze with no exit** | Traps users at a rung; resolution rate is already only ~14% | Always leave a visible door up the staircase |
| **Skipping straight to "contact us"** | Wastes the cheap rung; trains escalation | Route a self-serve answer first, human door still visible |
| **Context dropped between rungs** | User re-explains; the warm-handoff failure | Carry search/transcript/account state forward at each step |
| **Dishonest wait/SLA promises** | Erodes trust more than an honest long wait would | State real expected times; meet them (see `escalation-and-exceptions.md`) |
| **Support topics never fed back to the product** | Treats symptoms forever; volume never structurally drops | Route top issues into product fixes and Rung-0 prevention |

## Good vs. bad (for scoring)

| Dimension | Good — a designed support path | Bad — a support dead end |
| --- | --- | --- |
| **Success metric** | Resolution / cost-per-resolution | Deflection / ticket volume alone |
| **Routing** | Cheap rung first, human door always visible | Either no self-serve, or a self-serve trap |
| **Deflection vs. abandonment** | Instrumented and distinguished | Conflated — abandonment counts as success |
| **Escape to a human** | Findable from the frustration; ≥2 channels | Buried, absent, or single forced channel |
| **Failed self-serve** | Hands off to a human, context pre-filled | Zero-result dead end |
| **Continuity** | Context carries up every rung | User repeats themselves at each step |
| **Honesty** | Real wait times and channel capabilities stated | Optimistic promises that aren't met |
| **Feedback loop** | Top issues fed back into the product | Same tickets recur forever |

The single test: **trace a user whose self-serve attempt fails — can they reach a human in one obvious, context-carrying step, and does your metric record their original self-serve attempt as resolved or abandoned?** If the failed-self-serve user hits a dead end, and your dashboard quietly logs it as a deflected (saved) contact, you are designing for abandonment and calling it efficiency.
