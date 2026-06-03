---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Teresa T., 'Assumption Testing: Everything You Need to Know to Get Started' (producttalk.org/assumption-testing)"
  - "Teresa T., *Continuous Discovery Habits: Discover Products that Create Customer Value and Business Value* (Product Talk LLC, 2021)"
  - "David J. Bland & Alexander Osterwalder, *Testing Business Ideas* (Wiley, 2019) — the assumptions map (importance × evidence). Torres adopts this two-axis model."
  - "Marty C., *Inspired: How to Create Tech Products Customers Love*, 2nd ed. (Wiley, 2017) — Part IV, Product Discovery; 'The Four Big Risks' (svpg.com)"
---

# Assumption Testing

Assumption testing is the discipline that turns a solution from a bet into a sequence of cheap, falsifiable questions. The core move, in Teresa T.'s framing, is to stop testing whole ideas and start testing the **single riskiest assumption** behind an idea — because _"assumption tests make it clear that we're testing a single assumption and not the whole idea. These tests are faster and take less work."_ This reference defines what an assumption is, how to enumerate the assumptions inside a solution, how to find the riskiest one with the assumption map, and how to test it with the smallest prototype that could change your mind. It is the solution-space companion to `opportunity-solution-tree.md`, whose bottom row is exactly these tests.

> The reframe that makes everything cheap: an idea has many assumptions, and most are safe. Torres's definition — _"an assumption is a belief that may or may not be true… the assumptions that need to be true for your idea to succeed."_ You do not test the idea. You find the few beliefs that are both **critical** and **unproven**, and you test those, one at a time, before committing engineering capacity.

---

## What an assumption is — and the five categories

An assumption is any belief that **must be true for the idea to work**. The skill is enumerating them, and the trap is that teams list only the assumptions they already believe (which are, by definition, the ones least worth testing). Torres uses five categories as a generator — _"the point is to generate assumptions across the categories, increasing the likelihood that you uncover the riskiest assumptions"_ — and they map cleanly onto Marty C.'s four big risks (see `four-big-risks.md`), with **ethical** added as a fifth lens.

| Category | The question Torres asks of the solution | Maps to Marty C.'s risk |
| --- | --- | --- |
| **Desirability** | _"Why do we think our customers want this solution and why do we think they'll be willing to do what we need them to do to get value from it?"_ | Value |
| **Viability** | _"Why do we think this solution will be good for our business?"_ | Business viability |
| **Feasibility** | _"Why do we think we can build this solution?"_ | Feasibility |
| **Usability** | _"Why do we think the customer will be able to use this solution?"_ | Usability |
| **Ethical** | _"Is there any potential harm in building this solution?"_ | (Torres's addition) |

The categories are a checklist against blind spots, not a taxonomy to file neatly. A single solution will spawn many assumptions per category; the goal of the enumeration step is **breadth** — surface more than feels comfortable — because you cannot prioritize a risk you never wrote down.

---

## Generating assumptions: simulate the experience step by step

The most reliable generator Torres gives is **story mapping the solution** — walking through each step the customer would take to get value, and asking at every step "what has to be true here?" Mapping the experience _"is an effective way to generate different types of assumptions, including desirability and usability assumptions, while also surfacing feasibility, viability, and ethical assumptions as well."_

The mechanism: a flat description of a solution ("a setup wizard") hides its assumptions; a **step-by-step simulation** ("the user lands here → sees this → clicks this → expects that → receives this") exposes a separate belief at every transition. Each arrow is a place the idea can fail. Walking the steps converts one vague bet into a row of specific, checkable beliefs.

```text
 user step:   discovers it  →  understands it  →  acts on it  →  gets value  →  comes back
 hidden       "they'll        "the value is      "they'll      "it actually   "the value
 assumption:   notice the      obvious without     complete       solves their   recurs enough
               entry point"    a tutorial"         all 5 steps"   problem"        to retain"
 category:     desirability    usability           usability      desirability    desirability
                                                                  + value         + viability
```

This is why story mapping appears in both discovery references: in `dual-track.md` it shapes the build; here it is a **risk-finding instrument**, used to mine a solution for the beliefs hiding between its steps.

---

## The assumption map: importance × evidence

Enumerating assumptions produces too many to test. The prioritization tool Torres uses is the **assumption map**, a two-axis model from David Bland and Alex Osterwalder's _Testing Business Ideas_ that plots each assumption on **how important it is** (critical → less critical to the idea's success) against **how much evidence** you already have (strong → weak). The combination, not either axis alone, locates risk.

```text
              IMPORTANT (critical to the idea)
                        ▲
                        │
   known & critical     │     RISKIEST — test first
   (safe; monitor)      │     critical + little evidence
   ─────────────────────┼─────────────────────────────→
   STRONG evidence      │      WEAK evidence
                        │
   trivial & known      │     trivial & unknown
   (ignore)             │     (defer; cheap to be wrong)
                        │
              UNIMPORTANT (peripheral to the idea)
```

> The whole map exists to find one quadrant. Torres: _"Our riskiest assumptions are the assumptions that are critical to the success of our idea where we have little evidence that suggests that they are safe."_ That is the **top-right** — important **and** unproven. These are the **leap-of-faith assumptions**; they are the only ones worth a test right now.

The map disciplines three reflexes:

- **Important but well-evidenced (top-left):** do **not** spend a test here. You already know it. Testing the obvious is the most common way discovery wastes a week feeling productive.
- **Unimportant, any evidence (bottom row):** ignore or defer. If being wrong costs nothing, learning costs too much by comparison.
- **Important and unproven (top-right):** **test first.** This is where a failed test would actually change the decision — the definition of a worthwhile experiment.

A test that cannot change a decision is not a test. Prioritizing by this map is how a team ensures every experiment it runs is one whose outcome it does not already know and genuinely cares about.

---

## Prototypes to learn, and discovery sprints

Once the riskiest assumption is named, the job is to confront it with the **smallest artifact that produces evidence** — a prototype built **to learn**, not to keep. Match the test to the assumption; do not reach for a single default method.

| Assumption type | A cheap test that produces evidence | What counts as a result |
| --- | --- | --- |
| **Desirability / value** | Demand test (fake-door / landing page); a high-fidelity prototype put in front of real customers; concierge / Wizard-of-Oz | Customers _act_ — sign up, commit, pay, complete — not merely approve |
| **Usability** | Think-aloud usability test on a prototype with representative users | Users complete the core task unaided and can say what they did |
| **Feasibility** | Engineering spike / proof-of-concept on the risky integration or scale assumption | Engineers de-risk the unknown and can credibly estimate |
| **Viability** | Stakeholder review (sales, finance, legal, brand) against a realistic prototype | The affected function confirms it is shippable in its domain |
| **Ethical** | Pre-mortem on harms; review of misuse / edge-population cases | A named harm is surfaced and either mitigated or accepted deliberately |

Two operating ideas keep this honest:

- **The prototype is built to be thrown away.** Its only product is evidence about one assumption. Reusing prototype code in production smuggles the cheapness out of discovery — the artifact was sized to answer a question, not to ship. (See `idea-to-prototype.md` for the prototype-first practice and the four prototype types.)
- **A discovery sprint is time-boxed risk reduction, not a build phase.** When several leap-of-faith assumptions cluster around one important bet, a team can concentrate a short, fixed-length burst of discovery — interviews, prototypes, and assumption tests aimed squarely at the riskiest beliefs — to decide _build / iterate / kill_ before committing delivery capacity. The fixed box is the safeguard against discovery quietly becoming a phase.

---

## Good assumption test vs. risk theater

The structure of a test is easy to mimic; the rigor is not. If the right-hand column describes your test, you ran a ritual, not an experiment.

| Dimension | Real assumption test | Risk theater |
| --- | --- | --- |
| **Scope** | One assumption, isolated | The whole idea at once ("let's validate the feature") |
| **Which assumption** | Top-right of the map — critical _and_ unproven | One you already had strong evidence for, or one that doesn't matter |
| **Falsifiability** | Could come out the other way; a failing result is defined in advance | Designed so it can only confirm; no result would change the plan |
| **Evidence type** | Observed behavior (acted / completed / paid) | Stated opinion ("users said they'd love it") |
| **Cost** | Sized to the question — minutes to days, throwaway | A near-production build dressed as a "test" |
| **Consequence** | Sometimes kills or reshapes the idea | Always greenlights the predetermined idea |

> The disqualifying tell, in one line: **if no possible outcome would have changed the decision, it was not a test.** A test you cannot fail is a confirmation, and confirmation is the thing assumption testing exists to replace.

---

## The "did you actually test the riskiest assumption?" check

Run this against a specific solution the team is about to build:

- [ ] **Enumerated across categories.** Did the team generate assumptions across all five (desirability, viability, feasibility, usability, ethical) — or only list the few it already believed?
- [ ] **Mapped by importance × evidence.** Were assumptions plotted to find the critical-and-unproven ones — or was a test chosen by which was easiest to run?
- [ ] **Tested the top-right, one at a time.** Did the test target a single leap-of-faith assumption — not the whole idea, and not a belief already well-evidenced?
- [ ] **Built to learn, sized to the question.** Was the artifact a throwaway prototype proportional to the risk — or a near-production build in disguise?
- [ ] **Evidence was behavior, and falsifiable.** Did the result rest on what users _did_, with a failing outcome defined beforehand — or on what they _said_, with only confirmation possible?
- [ ] **Something could have died.** Was the team genuinely willing to kill or reshape the idea on a bad result — or was the conclusion fixed before the test?

If the team tested the whole idea, picked the easy assumption, gathered opinions, or could not have failed, it did not run assumption tests — it ran reassurance. The fix is upstream: enumerate wider, map by importance _and_ evidence, and aim the next cheap test at the one belief that is both critical and unproven.
