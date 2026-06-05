---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Anthony W. Ulwick. *Jobs to be Done: Theory to Practice*. IDEA BITE PRESS, 2016. ISBN 978-0-9907360-0-8."
  - "Anthony W. Ulwick. \"What Customers Want: Using Outcome-Driven Innovation to Create Breakthrough Products and Services.\" McGraw-Hill, 2005."
  - "Strategyn, \"Jobs to be Done: The Original Framework by Tony Ulwick.\" https://strategyn.com/jobs-to-be-done/"
  - "Tony Ulwick, \"Mapping the Job-to-be-Done.\" *JTBD + Outcome-Driven Innovation* (Medium). https://jobs-to-be-done.com/mapping-the-job-to-be-done-45336427b3bc"
  - "Strategyn, \"What is Outcome-Driven Innovation (ODI)?\" (PDF). https://innovationroundtable.com/summit/wp-content/uploads/2014/05/Strategyn_what_is_Outcome_Driven_Innovation.pdf"
---

# Outcome-Driven Innovation (Ulwick / ODI)

Outcome-Driven Innovation (ODI) is Tony Ulwick's method for turning Jobs-to-be-Done from a lens into an operating procedure. Where Clayton C.'s JTBD is a _theory_ — customers hire products to make progress (see `jobs-to-be-done.md`) — Ulwick's claim is that the theory is not actionable until you make the job _measurable_. ODI is the bridge: it decomposes a job into a stable process and then attaches a fixed set of quantified "desired outcomes" to that process, so a team can survey customers and learn precisely which outcomes are under-served (the opportunities) and which are over-served (the waste). Ulwick developed ODI at Strategyn beginning in 1991; the canonical text is _Jobs to be Done: Theory to Practice_ (2016).

## ODI's premise: a job is a stable process, and needs are metrics

Ulwick's move is to treat a functional job-to-be-done not as a fuzzy motivation but as a **process that stays stable over time even as the solutions that execute it churn**. Listening to music, getting a meal, preparing a tax return — the _job_ persists for decades while the products that serve it (cassette, CD, MP3, streaming) come and go. This stability is the whole point: if you anchor on the job-process rather than the solution, your customer-needs data does not expire when technology shifts.

From that premise follows ODI's most distinctive commitment: **customer needs are not vague preferences — they are the metrics customers use to measure success when getting a job done.** Ulwick calls these metrics _desired outcomes_. Because they are framed as metrics, they are measurable, solution-independent, and stable, which is exactly what makes them survey-able at scale. This is the formal difference between the Ulwick lineage and the Clayton C./Moesta lineages: Ulwick converts "the job" into a quantified needs-list; the others keep it qualitative (see `jtbd-variants-map.md`).

## The desired-outcome statement (the rigid syntax)

The engine of ODI is a deliberately rigid statement format. Ambiguity is the enemy — two people must read the same outcome statement the same way for survey data to mean anything — so Ulwick standardizes the grammar into four parts:

```text
[direction of improvement] + [unit of measure] + [object of control] + [contextual clarifier]

  direction of improvement : minimize / maximize / reduce / increase  (a verb of change)
  unit of measure          : time, effort, number, likelihood, frequency ...
  object of control        : the thing being acted on in the job process
  contextual clarifier     : the circumstance that makes the metric meaningful

Example (pet nutrition):
  "Minimize the time it takes to determine what nutrition is needed
   to address the pet's existing health problems."
    direction  = Minimize
    unit       = the time it takes
    object     = determine what nutrition is needed
    context    = to address the pet's existing health problems

Example (listening to music):
  "Minimize the time it takes to get the songs in the desired order for listening."
```

Two disciplines make a statement valid. First, it must be **solution-free** — no product, feature, or technology may appear; "minimize the time to reorder the playlist on the app" smuggles in a solution and is therefore not an outcome but a feature request in disguise. Second, it must be a **metric the customer can rate twice** — once for _importance_ and once for current _satisfaction_ — because those two ratings are what the method runs on. If a statement can't be scored for importance and satisfaction, it isn't a desired outcome.

## The job map: eight universal steps

Before you can enumerate outcomes you need the job's process. Ulwick's _job map_ deconstructs any core functional job into discrete steps describing **what the customer is trying to accomplish, independent of any solution.** ODI uses a universal eight-step template (with two optional steps — _prepare_ and _modify_ — that not every job needs):

```text
1. Define   — determine objectives, plan the approach
2. Locate   — gather the inputs / information needed
3. Prepare  — set up and organize the inputs and environment
4. Confirm  — verify everything is ready before executing
5. Execute  — carry out the job; do the central task
6. Monitor  — assess whether execution is going correctly
7. Modify   — make adjustments when something is off
8. Conclude — finish, clean up, store or dispose
```

The map is the scaffold: you walk each step and ask what the customer is trying to get done there, then attach desired-outcome statements to each step. Ulwick's rule of thumb across his cases: **most jobs have 8–12 process steps, with roughly 6–12 outcomes per step, totaling on the order of 50–150 desired outcomes for a complete job.** This is why ODI is a quantitative method — that many metrics demand surveying rather than intuition.

## The opportunity algorithm: importance and satisfaction

The payoff step. Once you have the outcome list, you field a large quantitative survey asking customers to rate **each outcome on two scales: how important it is, and how satisfied they are with current solutions.** ODI then plots every outcome on an importance/satisfaction landscape and ranks opportunity with Ulwick's _opportunity algorithm_:

```text
Opportunity = Importance + max(Importance − Satisfaction, 0)

  high importance + low satisfaction  -> UNDER-served  = the real opportunity
  high importance + high satisfaction -> appropriately served (don't over-invest)
  low importance  + high satisfaction -> OVER-served    = wasted investment / cost to cut
```

The two failure regions are the actionable insight. **Under-served outcomes** (important, unsatisfied) are where unmet need lives — invest there. **Over-served outcomes** (satisfied beyond what their importance warrants) are where you are gold-plating and can disrupt with something cheaper or simpler. This is the same over-served/under-served logic that Clayton C.'s disruption theory predicts, now made measurable at the level of individual needs. ODI's segmentation also falls out of this data: clusters of customers with _different unmet-outcome patterns_ become outcome-based segments — a segmentation built on needs, not demographics or firmographics.

## How ODI operationalizes JTBD theory

The clean way to hold the relationship: **JTBD theory says _what_ to anchor on (the job); ODI says _how_ to measure it (outcomes) and _where_ to act (the opportunity landscape).** Ulwick frames ODI as putting the theory into practice — the title _Theory to Practice_ is the thesis. The chain:

1. Pick the **core functional job** (solution-free, process-stable).
2. **Map** the job into its ~8 steps.
3. Enumerate **desired outcomes** per step in the rigid four-part syntax (~50–150 total).
4. **Survey** customers for importance and satisfaction on every outcome.
5. Rank with the **opportunity algorithm**; act on under-served, cut over-served, segment by unmet-outcome pattern.

Strategyn markets ODI on a success-rate claim — that ODI-guided launches succeed at a far higher rate than the industry baseline. Treat that figure as the vendor's own marketing metric rather than an independently audited result; the _method_ stands on its logic regardless of the headline number.

## The "is this a measurable outcome, or a smuggled solution?" test

ODI lives or dies on outcome-statement hygiene. Run this before any statement enters the survey:

```text
For each candidate "desired outcome":

  - Direction?  Does it start with a verb of change (minimize / maximize)? If it
    states a feature or a state of being, it's not an outcome.
  - Solution-free?  Strip every product, app, feature, and technology name. If the
    statement collapses without them, it was a feature request, not a need.
  - Rate-able twice?  Can a customer score it for IMPORTANCE and for SATISFACTION?
    If either rating is meaningless, it isn't a metric and ODI can't use it.
  - Process-stable?  Would this outcome still be true ten years ago / ten years
    from now, across whatever solution is in fashion? If it churns with the
    solution, you've anchored on the solution, not the job.
  - Tied to a job step?  Which of the 8 map steps does it attach to? An outcome
    that maps to no step is probably about a different job.
```

Failure modes to watch: the **smuggled solution** ("maximize the speed of the dashboard refresh" — dashboard is a solution); the **un-rateable wish** ("delight the user" — can't score importance vs. satisfaction); the **moving-target metric** that's really about today's product and will expire when the product changes; and **outcome sprawl** where teams generate hundreds of near-duplicate statements instead of a clean, de-duplicated set per step.

## Relationship to the other JTBD lineages (pointer)

ODI is the most quantitative of the three commonly-conflated JTBD schools. Its "job-as-process-with-measurable-outcomes" differs sharply from Clayton C.'s "job-as-progress-in-a-circumstance" and from Moesta's switch-interview, demand-side practice. Those are genuine, partly-contradictory differences, not stylistic ones — the honest comparison and the unresolved disagreements live in `jtbd-variants-map.md`.
