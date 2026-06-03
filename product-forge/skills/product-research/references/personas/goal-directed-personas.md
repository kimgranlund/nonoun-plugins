---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Alan C., Robert Reimann, David Cronin. *About Face 3: The Essentials of Interaction Design*. Wiley, 2007. ISBN 978-0-470-08411-3."
  - "Alan C.. *The Inmates Are Running the Asylum: Why High-Tech Products Drive Us Crazy and How to Restore the Sanity*. Sams, 1999/2004. ISBN 978-0-672-32614-1."
  - "Alan C.. \"Defending Personas.\" Medium, 2018. https://mralancooper.medium.com/defending-personas-2657fe26dd0f"
  - "Hugh Dubberly. \"Alan C. and the Goal Directed Design Process.\" Gain: AIGA Journal of Design for the Network Economy, vol. 1, no. 2, 2001. https://www.dubberly.com/articles/alan-cooper-and-the-goal-directed-design-process.html"
  - "Alan C. et al., \"Users, Personas and Goals\" (book chapter excerpt, hosted CMU). https://www.cs.cmu.edu/~jhm/Readings/cooper_personas.pdf"
---

# Goal-Directed Personas (Cooper)

Personas were introduced by Alan C. — first in practice at his consultancy, then in print in _The Inmates Are Running the Asylum_ (1999) and formalized in _About Face_. A persona, in Cooper's sense, is a **precise descriptive model of a user, synthesized from research, defined by goals**. It is the foundation of his _Goal-Directed Design_ process. The point of the method is to stop designing for an elastic, self-serving abstraction ("the user," who conveniently wants whatever the team wants to build) and instead design for a small number of specific, named archetypes whose goals are fixed and known. Cooper calls personas "the single most powerful design tool that we use" and "the foundation for all subsequent goal-directed design."

## Personas are synthesized from research, not invented

The defining discipline: personas are **composite archetypes built from qualitative field research** — interviews with and observation of real users — not made up at a whiteboard. In "Defending Personas," Cooper is explicit that his firm "did our field research and then synthesized personas as a tool for understanding and communicating the goals, motivations, and desired end-states of our real-world users." A persona is a _pattern found in data_, given a name and a face so the team can reason about it; the photo and the name are communication devices wrapped around researched behavior.

Cooper's sharpest warning is that the easy thing "is to do 'personas' without really doing personas" — the "bowdlerized versions, while easier to create and use, didn't actually work." A persona unbacked by research is not a lightweight persona; it is a different (and dangerous) object: the team's assumptions wearing a stock photo. (This is the central anti-pattern; the persona-antipatterns reference in this axis develops it.)

## Goals, not demographics, not tasks

Two distinctions carry the whole method.

- **Goals over demographics.** What defines a persona is its **goals and motivations**, not its age, gender, or income. Demographics may be _correlated_ with behavior but they don't _cause_ it or explain it, and they tempt teams into stereotype. A persona's demographic details exist only to make the archetype believable and memorable, never as the substance.
- **Goals over tasks.** Cooper: "Goals are not the same thing as tasks. A goal is an end condition, whereas a task is an intermediate process needed to achieve the goal… The goal is a steady thing. The tasks are transient." You design _to_ goals (which are stable across technology) and treat tasks as the changeable means. Optimizing tasks without knowing the goal produces faster ways to do the wrong thing.

Cooper's framework names **three kinds of goals**:

- **Life goals** — the persona's broad personal aspirations ("retire comfortably," "be respected in my field"). Rarely addressed directly by a product, but they set the backdrop.
- **End goals** — what the persona wants to accomplish _by using the product_ ("clear my inbox," "find a place to stay tonight"). These are the primary target of design.
- **Experience goals** — how the persona wants to _feel_ while using it ("not feel stupid," "feel in control," "have fun"). These shape tone, feedback, and interaction quality.

## The persona set: primary, secondary, and the rest

A project produces a small **cast of personas**, classified by their role in the design. _About Face_ defines six types:

- **Primary** — the principal focus of the design for one interface. The test: a primary "must be satisfied, but cannot be satisfied with an interface designed for any other persona." There is **exactly one primary per interface** (a product with multiple interfaces may have one each). The primary is who you design _for_.
- **Secondary** — mostly satisfied by the primary's interface, but with a few additional needs. You may add to the interface to serve them, **as long as it doesn't compromise the primary's experience.**
- **Supplemental** — neither primary nor secondary; their needs are already fully covered by the primary's interface. (Often political stakeholders or edge users you note but don't design specifically for.)
- **Customer** — addresses the needs of _buyers_ rather than _users_ (e.g. an IT manager purchasing for staff). Considered, but not allowed to override the end-user primary.
- **Served** — not users of the product at all, but **affected** by its use (a patient affected by the nurse's use of a medical device). Their well-being is a design consideration.
- **Negative** — an explicit **anti-target**: who you are _not_ designing for, used to keep the team honest (e.g. "a tech-savvy early adopter" for a mainstream-consumer product). Designing for nobody is impossible; naming who you're _not_ serving sharpens who you are.

The load-bearing rule of the whole set is the **single-primary principle**: design each interface to fully satisfy its one primary persona. Trying to satisfy everyone equally — "the elastic user" — is how you satisfy no one. Cooper's narrowing of focus is the point: at his firm "narrowing the focus was the key to good design, so we tightly restricted the number of personas we used," in contrast to teams that built "hundreds of personas, one for each feature they wanted to inflict on their users."

## How to build a goal-directed persona (the working sequence)

```text
1. Do qualitative field research.    Interview + observe real users in context. No research → no personas.
2. Find behavioral patterns.         Map interviewees along behavioral variables (not demographic ones);
                                       look for subjects who cluster on the same behaviors.
3. Synthesize archetypes.            Each cluster becomes a candidate persona; name its goals + motivations.
4. Add just enough detail.           A name, a photo, a role, a representative quote — to make it real,
                                       not to add fictional precision. Demographics are flavor, not substance.
5. Articulate the goals.             Life / end / experience goals — especially END goals (design targets).
6. Classify the cast.               Designate ONE primary per interface; mark secondary / supplemental /
                                       customer / served / negative.
7. Design for the primary.          Make every interaction satisfy the primary; serve secondaries only
                                       without harming the primary.
```

## Mistakes to avoid

- **Personas with no research behind them.** The cardinal error — "doing personas without really doing personas." If you cannot point to interviews or observation, you have a stereotype, not a persona.
- **Demographic personas.** Building the archetype around age/gender/income/lifestyle instead of goals and behavior. Produces "Sarah, 34, loves brunch" — vivid, useless, and bias-prone. (See persona-antipatterns.)
- **No primary, or many co-equal primaries.** Refusing to choose. Designing for everyone equally collapses back into "the elastic user" and yields a diffuse, compromised interface.
- **Too many personas.** A persona per feature or per stakeholder defeats the narrowing that makes the tool work. Keep the cast small.
- **Personas as feature justification.** Cooper's own example: Microsoft "invented personas to defend the features that the engineers cooked up in their ivory towers" — a "180 degree inversion of reality." A persona is an input to design, not a rhetorical shield for decisions already made.
- **Confusing tasks for goals.** Listing what the persona does step-by-step without stating the end condition they're after. You'll optimize the steps and miss the point.
- **Static decoration.** Printing personas, framing them, and never consulting them in a design decision. A persona that doesn't change a decision is theater.

## Scoring guide: good vs. bad personas

A strong goal-directed persona is **researched, goal-defined, behaviorally specific, and prioritized**; a weak one is invented, demographic, generic, and unranked.

| Dimension | Bad (low score) | Good (high score) |
| --- | --- | --- |
| **Evidentiary basis** | Made up in a workshop; no field research | Synthesized from interviews/observation; patterns traceable to data |
| **Defining axis** | Demographics ("34, urban, foodie") | Goals + motivations + behaviors |
| **Goals stated** | None, or only tasks ("clicks export") | Life / end / experience goals, with end goals explicit |
| **Specificity** | Could describe anyone in the market | A distinct behavioral pattern that excludes other patterns |
| **Prioritization** | A flat list, all "important" | One designated primary per interface; cast classified |
| **Use in design** | Filed and forgotten | Cited to resolve real design decisions ("would the primary want this?") |
| **Role in process** | Justifies pre-decided features | Drives the design before features are chosen |

### Worked contrast

```text
BAD  (demographic, invented, goalless)
  "Jessica, 29, marketing manager in Austin. Loves yoga, oat-milk lattes, and weekend hikes.
   Tech-comfortable. Owns an iPhone."
  → Vivid persona of nobody in particular. No goal, no behavior, no research, no design implication.
   You cannot design a single decision from this.

GOOD (researched, goal-defined, behaviorally specific — and classified)
  Primary persona: "The reluctant bookkeeper" (synthesized from 14 interviews with solo founders)
    Behavior:  does the books once a month, late at night, dreads it, has abandoned 2 tools that
               assumed accounting fluency she doesn't have.
    End goals:        "close the month without errors I'll regret at tax time"
    Experience goal:  "never feel like the app assumes I'm an accountant"
    Life goal:        "spend my time on the business, not on admin"
  → Every part implies a design decision: plain-language flows, forgiving defaults, a guided month-close.
   Secondary persona ("the founder's accountant") is served only where it doesn't complicate her path.
```

## Note on the persona debate (labeled)

Personas have a live critical literature — that they can ossify into stereotype, drift from data over time, or get faked. Cooper's "Defending Personas" is a direct response to that debate; his position is that the criticism is almost always of _misused_ personas, and the remedy is to return to research and goals, not to abandon the tool. The Nielsen Norman Group similarly insists personas "must always be rooted in a qualitative understanding of users." This file presents the Cooper-canonical method; the persona-antipatterns reference in this axis treats the failure modes directly. (Labeled as an active practitioner debate, not a settled consensus.)
