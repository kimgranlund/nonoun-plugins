---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Ron K., Diane Tang & Ya Xu (2020). Trustworthy Online Controlled Experiments: A Practical Guide to A/B Testing. Cambridge University Press. ISBN 9781108724265. DOI 10.1017/9781108653985"
  - "Ron K., Deng, Frasca, Longbotham, Walker & Xu (2012). Trustworthy Online Controlled Experiments: Five Puzzling Outcomes Explained. Proceedings of the 18th ACM SIGKDD (KDD '12)"
  - "Fabijan, Gupchup, Gupta, Omhover, Qin, Vermeer & Dmitriev (2019). Diagnosing Sample Ratio Mismatch in Online Controlled Experiments: A Taxonomy and Rules of Thumb for Practitioners. Proceedings of the 25th ACM SIGKDD (KDD '19), pp. 2156-2164. DOI 10.1145/3292500.3330722"
  - "experimentguide.com — companion site to Ron K., Tang & Xu (2020)"
---

# Trustworthy Online Controlled Experiments as a Working Method

An A/B test produces a number. The hard problem is not getting the number — platforms do that — it is knowing whether to _believe_ it. Ron K., Tang & Xu's _Trustworthy Online Controlled Experiments_ (Cambridge, 2020) is the field's standard reference precisely because its subject is trust, not mechanics. The authors ran experimentation at Microsoft, Google, and LinkedIn respectively, and the book's recurring argument is that most experiment results are believed too easily and the ones that look most exciting are the ones most likely to be wrong. This reference distills it into a working method for product teams: how to set up an experiment you can trust, and how to interrogate a result before you ship on it.

> The discipline in one line: a controlled experiment is the most reliable way to establish causality between a change and user behavior — but only if the experiment is _trustworthy_, and trustworthiness is something you engineer and verify, not assume.

## The OEC: decide what "better" means before you run

The **Overall Evaluation Criterion (OEC)** is the metric (or small set of metrics) you agree, _in advance_, will decide whether a variant wins. Ron K., Tang & Xu's defining property: an OEC must be "believed to causally impact long-term objectives." It is the contract that stops the post-hoc metric-shopping that quietly destroys trust — picking, after the fact, whichever of fifty metrics happened to move in your favor.

What makes an OEC usable, per the book:

- **Measurable in the short term, predictive of the long term.** It has to be computable within the experiment's window, yet stand in for the long-run goal. This is the central tension of metric design, and the source of the surrogate trap below.
- **Sensitive and timely.** It must move enough, and fast enough, to be detectable in a normal experiment duration.
- **Causal, not just correlated.** The whole point is that improving the OEC should _cause_ the long-term objective to improve.
- **Aligning.** Combining several related metrics into one OEC gives "a clear alignment mechanism to the organization" — the team optimizes one agreed thing instead of arguing over which chart to believe.

The canonical worked example pairs a goal metric with its own cost: for an email campaign, `OEC = (Revenue - Unsubscribes x Unsubscribe_Lifetime_Loss) / Number_Of_Users` — revenue per user, _net_ of the future revenue destroyed when an aggressive campaign drives unsubscribes. The structure is the lesson: a good OEC has the obvious win metric and the thing it would otherwise cannibalize, built in.

## Guardrail metrics: the things a win is not allowed to break

A win on the OEC is not a license to degrade everything else. **Guardrail metrics** are the metrics you are _not_ trying to improve but refuse to harm — and a regression on one can veto an otherwise-positive result. The book's standing examples are operational and trust-protective:

- **Latency / page-load time** — a classic guardrail, because almost any feature can be made to "win" by ignoring the performance cost it imposes; the guardrail prices that cost back in.
- **Page size, crash/error rate, and other quality metrics** — the things that protect the user experience and the business while you chase the OEC.
- **Sample Ratio Mismatch** — itself treated as a guardrail (see below): an organizational trust guardrail that catches broken experiments before their results are believed.

The working rule: a variant ships only if it wins (or holds) on the OEC **and** trips none of the guardrails. Guardrails exist precisely because optimizing a single metric hard enough will eventually break something you forgot to watch.

## Twyman's law: the more interesting the number, the more likely it's wrong

Ron K. et al. repeatedly invoke **Twyman's law** — "any figure that looks interesting or different is usually wrong." Its practical force: a surprising, too-good result is not cause for celebration, it is cause for suspicion. The bigger and more exciting the lift, the higher the prior that it's an artifact — instrumentation bug, logging error, SRM, or a novelty spike — rather than a real effect. The discipline Twyman's law imposes is to spend your scrutiny budget on exactly the results you most want to be true.

## The trust pitfalls: how good-looking results lie

These are the recurring ways an experiment produces a number you shouldn't ship on. The book's stance is that you must actively look for each one; trust is the absence of a known failure mode, established by checking, not the default.

### Sample Ratio Mismatch (SRM)

SRM is when the observed split between variants differs from the designed split (e.g. you assigned 50/50 but observe 52.1/47.9). The authors' analogy: SRM is "a symptom for a variety of data quality issues" — like a fever, it tells you _something_ is wrong without saying what. A statistically significant SRM invalidates the experiment: if the populations in the two arms aren't comparable, the comparison between them is meaningless, and the headline result cannot be trusted. The companion KDD '19 paper (Fabijan et al.) gives a taxonomy of root causes — assignment, execution, logging, interference, and analysis-stage bugs. The rule of thumb: run a chi-squared test on the counts; if SRM is present, **stop and find the cause** before reading any other metric. Not checking for SRM has been likened to a car without seatbelts.

### Novelty and primacy effects

The treatment effect measured early is not always the long-run effect, because users react to _change_ as well as to the change's merits.

- **Novelty effect** — a new feature draws inflated engagement out of curiosity; the lift decays as the novelty wears off. The early win overstates the truth.
- **Primacy effect** — users primed on the old experience need time to adapt, so a genuinely better change can _under_-perform at first and improve as people learn it. The early read understates the truth.

Both imply that some experiments must run for **multiple weeks**, and that a treatment effect trending toward zero (or up) over time is a flag, not noise. A single short read can be wrong in either direction.

### Surrogate-metric traps (short-term proxy ≠ long-term value)

Because the OEC must be measurable in the experiment window, teams reach for short-term **surrogate** metrics — and a surrogate can move the _opposite_ way from the goal it's standing in for. The book's standing example (from "Five Puzzling Outcomes," KDD '12) is click-bait: it has a positive short-term effect on click-through rate but a negative long-term effect on user retention and revenue. Optimizing the proxy actively harms the objective. The trap is structural, not careless: the proxy was chosen _because_ it's easy to move, which is exactly what makes it gameable. Guard against it by validating that the surrogate is causally linked to the long-term goal (e.g. via long-running holdouts), not merely correlated in historical data.

### Other trust hazards the book treats

- **Peeking / multiple looks** — repeatedly checking a running test and stopping at the first significant moment inflates the false-positive rate; either fix the duration in advance or use a method designed for sequential testing.
- **Multiple comparisons** — test enough metrics and some cross significance by chance alone; Twyman's law plus correction methods apply.
- **Interference / network effects** — when treatment and control units affect each other (marketplaces, social graphs), the no-interference assumption breaks and the measured effect is biased.

## The "is this result trustworthy?" checklist

Run this before shipping on any experiment number. It operationalizes the book's discipline: each item is a known way the number could be lying.

1. **Sanity first — SRM.** Did the actual traffic split match the designed split? A significant SRM means **stop** — diagnose the data-quality cause before reading anything else.
2. **Pre-registered OEC.** Was the decision metric chosen _before_ the experiment, and does it plausibly cause the long-term objective — or is this a metric found _after_ the data came in?
3. **Guardrails intact.** Did latency, errors, and other do-no-harm metrics stay within bounds? A guardrail regression can veto an OEC win.
4. **Apply Twyman's law.** Is the result surprisingly large or counter-intuitive? If so, raise the bar — suspect instrumentation, logging, or an artifact before believing it.
5. **Duration vs. novelty/primacy.** Did it run long enough that a novelty spike would have decayed and a primacy dip would have recovered? Is the effect stable over time, or trending?
6. **Surrogate vs. goal.** If the win is on a short-term proxy, is that proxy causally tied to the long-term outcome — or could you be shipping click-bait?
7. **Statistical hygiene.** Was the duration fixed in advance (no peeking)? Were multiple comparisons accounted for? Is there interference between units that violates the test's assumptions?
8. **Reproducibility.** Could the result be replicated (a re-run, or a hold-back)? The more it matters, the more a confirmation run is worth.

A result earns trust only when it clears every applicable item — in the authors' framing, trustworthiness is the absence of a _known, unchecked_ failure mode, not the presence of a low p-value.
