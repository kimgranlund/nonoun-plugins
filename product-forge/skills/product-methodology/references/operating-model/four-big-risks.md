---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Marty C., 'The Four Big Risks', Silicon Valley Product Group (svpg.com)"
  - "Marty C., *Inspired: How to Create Tech Products Customers Love*, 2nd ed. (Wiley, 2017) — Part IV, Product Discovery"
  - "Marty C. & Chris Jones, *Empowered: Ordinary People, Extraordinary Products* (Wiley, 2020)"
---

# The Four Big Risks

In Marty C.'s product operating model, **product discovery exists to address four risks before the team commits engineering capacity to building anything.** This is the line between empowered product work and the build trap: a feature factory ships first and discovers the risks in production; a product team confronts them on cheap prototypes first. This reference defines the four risks, how to test each one quickly, and the single test for whether a team _actually_ de-risked rather than merely held a discovery-themed meeting.

> The framing to hold onto: discovery is not "deciding what to build." It is **systematically reducing four kinds of risk to an acceptable level before you spend the expensive resource — engineering time — building it.**

---

## The four risks

Marty C.'s _Inspired_ (1st edition) framed successful products as **valuable, usable, and feasible**. He later added a fourth — **business viability** — because folding business value into "valuable" let teams over-index on customer value and quietly ignore whether the solution worked for their own company. The mature taxonomy is four.

| Risk | The question | Primary owner |
| --- | --- | --- |
| **Value** | Will customers buy it, or choose to use it? | Product Manager |
| **Usability** | Can users figure out how to use it? | Product Designer |
| **Feasibility** | Can our engineers build it, with the time, skills, and technology we have? | Tech Lead / Engineers |
| **Business viability** | Does this solution work for the rest of our business? | Product Manager (with stakeholders) |

The role assignments are Marty C.'s: the **product manager owns value and viability**, the **designer owns usability**, the **engineering tech lead owns feasibility**. This is why an empowered team is cross-functional by construction — no one person can clear all four.

### Value risk — the hardest and most important

Will anyone actually buy this or choose to use it over their current alternative (including doing nothing)? Value is the risk teams are worst at and the one that kills the most products. Most "we built it and nobody came" failures are unaddressed value risk. Customer enthusiasm in a survey is not evidence of value; willingness to switch, pay, or repeatedly use is.

### Usability risk

Even a valuable, buildable thing fails if users cannot work out how to get the value. Usability risk is about comprehension and flow: can a representative user accomplish the task without coaching?

### Feasibility risk

Can _our_ engineers build _this_ with the time, skills, technology, and data actually available? Feasibility is not "is it possible in principle" but "can this team ship it within real constraints." New technology, integration with legacy systems, performance at scale, and data availability are common feasibility traps.

### Business viability risk

Does the solution work for the **rest of the business** — not just the customer? Marty C. decomposes viability across the company's other functions; the recurring list is **sales, marketing, finance, legal, and brand** (and often security, privacy, support, and partnerships besides). A solution customers love that the legal team cannot ship, sales cannot sell, or finance cannot fund has not been de-risked.

---

## How to test each risk in discovery

The point of discovery is to confront each risk with the **cheapest evidence that would change your mind**, before writing production code. Match the technique to the risk.

| Risk | Cheap discovery techniques | What counts as evidence |
| --- | --- | --- |
| **Value** | Customer interviews; demand tests (e.g. a fake-door / landing-page test); a high-fidelity user prototype put in front of real customers; concierge / Wizard-of-Oz tests | Customers act — sign up, commit, pay, return — not merely approve |
| **Usability** | Usability testing of a prototype with representative users (think-aloud) | Users complete the core task unaided and can articulate what they did |
| **Feasibility** | A technical spike / proof-of-concept by engineers; spike on the riskiest integration or scale assumption | Engineers can credibly estimate and have de-risked the unknown technology/data |
| **Business viability** | Reviews with the affected stakeholders (sales, marketing, finance, legal, security, brand) against a realistic prototype | Each affected function confirms the solution is shippable in its domain |

A reusable rule: **a prototype is the workhorse of discovery** because one artifact can test value, usability, and viability at once — for a tiny fraction of the cost of building the real thing.

---

## The ordering trap: which risk to attack first

There is no fixed order, but there is a common mistake. Teams gravitate to **feasibility** first because engineers are comfortable with technical spikes — and neglect **value** and **business viability**, which are uncomfortable and political. This is exactly backwards: spending weeks proving you _can_ build something nobody wants is the most expensive way to learn nothing.

Working heuristic: **attack the riskiest, most uncertain risk first** — usually value for genuinely new ideas. If the value risk does not clear, the other three do not matter. Sequence by uncertainty, not by comfort.

---

## How to apply it (and how it goes wrong)

| Lever | Good — risks actually addressed | Bad — risk theater |
| --- | --- | --- |
| **When risks are confronted** | In discovery, on prototypes, before build | In production, after launch, as bug reports and churn |
| **Value evidence** | Customers commit / pay / return in a test | "Stakeholders loved the demo" |
| **Usability evidence** | Real users complete the task unaided | The team finds their own design intuitive |
| **Feasibility evidence** | Engineers ran a spike on the risky part | Engineers gave a confident estimate without touching the unknown |
| **Viability evidence** | Legal, finance, sales, brand signed off on a realistic prototype | "We'll loop them in before launch" |
| **Cross-functional?** | PM, design, engineering present throughout discovery | Discovery is a PM writing a spec alone |

---

## The de-risking test: did the team actually do it?

A team can run a "discovery phase" and clear none of the four risks. The test for whether real de-risking happened:

1. **The four-named-risks test.** Ask the team to state, for this specific feature, the current status of each of the four risks. A team that has done the work can answer all four crisply; a team that cannot name them by risk has not de-risked — it has scheduled.
2. **The evidence test.** For each risk, what _evidence_ moved it from "unknown" to "acceptable"? Evidence means an observation that could have come out the other way (a user failed the task; customers did not sign up; legal flagged a blocker). "We discussed it and felt good" is not evidence.
3. **The kill test.** Did anything get changed or killed because a risk test failed? Discovery that never invalidates anything is confirmation, not discovery — the conclusion was fixed before the evidence (see `build-trap.md` and `product-operating-model.md`).
4. **The pre-build test.** Were all four addressed **before** committing engineering capacity to building the real thing? Risks confronted only after build is the build trap; the entire value of the framework is that it front-loads the learning to where it is cheap.

If the team cannot name the four risks, point to falsifiable evidence for each, show something it changed or killed, and confirm it happened before build — then it has not de-risked, regardless of how many discovery meetings it held.
