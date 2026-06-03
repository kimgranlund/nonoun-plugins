---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Marty C., *Inspired: How to Create Tech Products Customers Love*, 2nd ed. (Wiley, 2017) — Part IV, Product Discovery (prototype types; Ch. 48, the Live-Data Prototype Technique)"
  - "Marty C., 'Product Discovery with Live-Data Prototypes' and 'High-Fidelity Prototypes', Silicon Valley Product Group (svpg.com)"
  - "Marty C., 'The Four Big Risks', Silicon Valley Product Group (svpg.com)"
  - "Teresa T., 'Assumption Testing: Everything You Need to Know to Get Started' (producttalk.org/assumption-testing) — prototypes as single-assumption tests"
---

# From Idea to Prototype

The fastest path from an idea to a decision is not a document — it is a prototype that asks a question. Marty C.'s framing of discovery is built on this: _"our goal in discovery is to validate our ideas the fastest, cheapest way possible,"_ and the instrument for that is a prototype, because _"the overarching purpose of any form of prototype is to learn something at a much lower cost in terms of time and effort than building out a product."_ This reference defines prototype-first discovery, the four prototype types and the risk each one attacks, the "demos over docs" posture, and the disciplines that keep a prototype cheap. It is the build-side companion to `assumption-testing.md`: assumption testing tells you _which question to ask_; the prototype is _how you ask it_.

> The reframe that organizes everything: **a prototype is the question, not the answer.** It is not a small version of the product you intend to ship; it is a disposable instrument sized to extract one piece of evidence. Marty C.'s operational version of this: _"the primary purpose of a prototype is to tackle one or more product risks — value, usability, feasibility, or viability — in discovery."_ Build it to learn, then throw it away. _(The "question, not the answer" phrasing is a synthesis of Marty C.'s prototype-to-learn principle, not a verbatim quotation.)_

---

## Why prototype-first beats spec-first

The default a prototype displaces is the **spec**: a written description of the solution, reviewed and signed off, then handed to engineering to build. Marty C.'s objection is economic and epistemic at once. A spec describes a solution as if the risks were already resolved; a prototype confronts them while they are still cheap to be wrong about.

|  | Spec-first (document the answer) | Prototype-first (build the question) |
| --- | --- | --- |
| **What it asserts** | "Here is what we will build" — the answer, pre-committed | "Here is what we want to learn" — the question, still open |
| **When risk surfaces** | In production, after build, as churn and bug reports | In discovery, on a throwaway artifact, before build |
| **Cost of being wrong** | A built feature nobody wanted | Hours of prototyping |
| **Evidence it yields** | Stakeholder sign-off on a description | Customer _behavior_ against something they can touch |
| **Reversibility** | Low — code is written, sunk | High — the prototype was always disposable |

The size discipline makes the economics real: a discovery prototype should take _"at least an order of magnitude less time and effort as the eventual product."_ If a "prototype" approaches the cost of the product, it has stopped being a question and become an unhedged bet.

---

## The four prototype types (Marty C.)

Marty C. distinguishes four kinds of prototype, each matched to a different risk. The skill is reaching for the _right_ one — not defaulting to whatever the team is most comfortable building. Teams gravitate to feasibility prototypes (engineers like code) and neglect value, which is exactly backwards (see `four-big-risks.md`).

| Prototype | What it is | Primary risk it attacks |
| --- | --- | --- |
| **Feasibility** | Engineers write _"just enough code"_ to prove a technical unknown — algorithm, performance, new technology, data availability. Usually throwaway. | Feasibility |
| **User** | A simulation of the experience, from low-fidelity (paper / wireframe) to high-fidelity (looks and behaves real), tested face-to-face with target users. | Usability — and, at high fidelity, value |
| **Live-data** | _"A very limited implementation"_ that sends real traffic to real data and collects analytics, to see _"how this live-data prototype is being used."_ | Value (behavioral evidence at scale) |
| **Hybrid / Wizard-of-Oz** | A real front end with a human manually performing the backend the product will eventually automate — _"behind the product's front-end user experience, an engineer manually performs the tasks."_ | Value and usability, without building the engine |

### User prototypes test the experience — not whether it sells

A user prototype, even a beautiful high-fidelity one, _"cannot prove whether a product will actually sell."_ It can prove that a representative user understands the flow and can complete the task (usability), and it can gather qualitative signal on value when put in front of real customers — but a person saying "I'd use this" in a session is not the same as a person actually using it. This is the boundary between a user prototype and the next type.

### Live-data prototypes get behavioral evidence

When the question is _"does anyone actually use this, at scale, with their real data?"_ — a question a simulation cannot answer — Marty C. reaches for a **live-data prototype**: a stripped implementation lacking _"automated tests, full analytics, internationalization, performance optimization, and SEO,"_ whose entire purpose is _"to collect some actual usage data"_ by sending _"some limited amount of traffic"_ to it and instrumenting how it is used. It deliberately skips the 90–95% of work that productization requires, because that work is irrelevant to the question being asked. Its evidence is behavioral — what users _do_ with live data — which is why it is Marty C.'s tool for hard **value** questions like search relevance, funnels, and game dynamics.

### Wizard-of-Oz fakes the engine, not the experience

When the front end is cheap but the backend is expensive (a recommendation engine, a matching algorithm), a **Wizard-of-Oz** prototype puts the real experience in front of users while a human secretly performs the backend by hand. Users get a fully working-feeling product; the team gets value and usability evidence without building the costly automation. The "wizard" is hidden behind the curtain, doing manually what the product will one day do automatically.

---

## Demand testing: the fake door

The cheapest value test of all asks only "does anyone care enough to try?" Marty C.'s **fake-door / demand test** _"involves adding a product idea to the company's already live system without making it functional"_; when a customer clicks the new button, _"they're taken to a landing page that says the company is looking for test subjects for the idea."_ The click is the evidence — measured demand, before a single feature exists behind the door.

The discipline here is **honesty and proportion.** A fake door must lead somewhere truthful (an invitation to test, a "coming soon," a way to register interest), never a dead end that wastes the customer's trust. Run small, measure the click-through against a real baseline, and treat a low rate as the cheap "no" it is — the answer you came for, delivered before the build.

---

## The prototype-first / "demos over docs" posture (emerging practice)

Beyond Marty C.'s canon sits a fast-emerging working culture — often labeled **"prototype-first"** or **"demos over docs"** — in which AI-assisted tooling has collapsed the cost of a working prototype so far that, for some classes of product, building a rough functional demo is now _cheaper than writing the spec that describes it._ When that inequality flips, the spec stops being the efficient artifact: the team shows a working thing in a review instead of arguing over a written description, and the demo becomes the unit of shared understanding.

This extends, rather than overturns, the principles above:

- It is still **prototype-to-learn** — the demo is the question, sized to extract evidence, not the shippable product. The throwaway discipline is _more_ important when prototypes are this easy to generate, because the temptation to ship the demo (carrying its unhedged risk and disposable-grade code into production) is correspondingly greater.
- The risk taxonomy is unchanged. A slick AI-generated demo can still leave **value** and **viability** untested — a working prototype proves you _can_ make the thing, which is the feasibility/usability corner, not the value corner. "It demos well" is not "customers will switch and pay."

> **Label: this is an emerging, single-source-thin practice, not established canon.** "Demos over docs" reflects a real and growing 2024–2026 shift in AI-assisted product teams, but it is documented mainly in practitioner posts and talks rather than a primary methodological text, and its boundaries are still being worked out. Treat it as a directional lens to apply with Marty C.'s discipline attached — not as a verified method on par with the four prototype types above.

---

## Keeping the prototype cheap (and disposable)

The failure mode of prototype-first discovery is the prototype that stops being cheap — it accretes scope, gets polished, and slides toward production, taking the economics of discovery with it. Four guardrails:

- **Size to the question.** Build only enough to produce the one piece of evidence you came for. A feasibility spike needs no UI; a usability test needs no real backend; a demand test needs no functionality behind the door.
- **Pick the type that matches the risk.** Do not run a feasibility prototype to answer a value question. The most expensive way to learn nothing is to prove you _can_ build something nobody wants.
- **Plan to throw it away.** Discovery code is disposable by design; it lacks the tests, performance, and hardening of production precisely because that work is orthogonal to the question. Reusing it in production smuggles unhedged risk and discovery-grade quality into the shipped product.
- **Demand behavior, not approval.** A prototype's job is to make customers _act_ — click, complete, sign up, return — not to make stakeholders nod. "The demo went well" is not evidence; an observed behavior that could have gone the other way is.

---

## The "did the prototype actually answer something?" test

Run this against a prototype the team has built or is about to build:

- [ ] **There was a question.** Can the team state, in one sentence, the specific risk this prototype exists to reduce (value / usability / feasibility / viability)?
- [ ] **The type fits the question.** Is it the _right_ kind — a feasibility spike for a tech unknown, a user prototype for flow, a live-data prototype or fake door for value — not just the kind the team likes to build?
- [ ] **It's an order of magnitude cheaper.** Did it cost dramatically less than the real thing — or has it quietly grown into a near-product?
- [ ] **Evidence is behavioral.** Will the result come from what users _do_ (complete, click, pay, return), or only from what they _say_ in a session?
- [ ] **It's disposable.** Is the team prepared to throw the prototype away — or is there pressure to ship the discovery code into production?
- [ ] **A result would change something.** Is there an outcome that would kill or reshape the idea — or is the prototype a demo built to win approval for a decision already made?

If the prototype has no question, costs as much as the product, gathers opinions, or cannot fail, it is not discovery — it is a head start on building the wrong thing. The fix: name the riskiest assumption first (see `assumption-testing.md`), pick the cheapest prototype type that tests it, and build only enough to make a customer act.
