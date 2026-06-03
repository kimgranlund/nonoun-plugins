---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Casey Winters & Lenny Rachitsky. What Is Good Retention: An Exhaustive Benchmark Study. https://www.caseyaccidental.com/p/what-is-good-retention-an-exhaustive-benchmark-study-with-lenny-rachitsky and https://www.lennysnewsletter.com/p/what-is-good-retention-issue-29"
  - "Casey Winters. Retention curves and the natural-frequency framing, https://caseyaccidental.com and the Reforge growth program."
  - "Sequoia Capital. Retention. https://articles.sequoiacap.com/retention"
  - "Andreessen Horowitz (a16z) / Andrew Chen. The Power User Curve (a.k.a. the L7/L30 engagement / smile curve)."
  - "Reforge / Brian Balfour & Casey Winters. Input vs output metrics, leading vs lagging — Reforge growth curriculum."
---

# Retention and Engagement

Retention is the closest thing product growth has to a single source of truth: a product that retains users compounds, and one that doesn't leaks faster than it can fill. Casey Winters' standing claim, from the benchmark study he ran with Lenny Rachitsky, is blunt: **"Retention is not only the primary measure of product value and product/market fit for most businesses; it is also the biggest driver of monetization and acquisition as well."** This reference covers how to read a retention curve (and the one question that matters most — does it flatten?), the DAU/MAU stickiness ratio and its traps, how the North Star metric anchors engagement, and the discipline of separating real engagement from vanity metrics. Sources are the Winters/Rachitsky benchmark study, Sequoia's retention note, and a16z's power-user-curve work.

> The one question a retention curve must answer: **does it flatten?** A curve that decays to a stable plateau means a cohort found durable value (you have product-market fit with a segment). A curve that decays toward zero means you don't — no growth tactic survives a retention curve that never flattens.

## Reading the retention curve

A retention curve plots the percentage of a sign-up cohort still active over time (week 1, week 2, …). The shape, not any single point on it, is the diagnostic.

- **Does it flatten?** This is the decisive read. Winters: for transactional businesses especially, "where the retention graph flattens is more important to me than the six-month retention rate." A curve that drops steeply at first but then **flattens to a horizontal asymptote** is healthy — the initial drop is the tourists leaving, and the plateau is the cohort that found real value. A curve that keeps sloping toward zero has no plateau, which means no durable value, no PMF.
- **Where it flattens matters more than how fast it drops.** A deep first-period drop-off is acceptable _if it flattens_; a shallow drop that never stabilizes is worse. The plateau height (and the fact that one exists) is the signal.
- **The "smile" / upward-sloping curve.** In rare, strong cases the curve bends back _up_ after the trough — the power-user / "smiling" retention curve, where surviving users use the product _more_ over time. a16z's **Power User Curve** (the L7/L30 distribution of how many days out of a window users engage) is the engagement-distribution view of the same idea: a healthy product has a fat right tail of near-daily users, not a single average that hides a hollow middle. A smiling curve is a strong PMF signal because it means the product's value grows with tenure (often via network effects or accumulated stored value).

## Choosing the measurement interval: natural frequency

A retention number is meaningless without the right time interval, and the right interval is set by the product's **natural frequency of use** — its real-world cadence. Winters' framing: "you may only look for a place to live once every few years" but "look for something to eat multiple times of day," so the two products must be measured on entirely different clocks.

- Match the interval to the offline analog. A food-delivery product measured daily looks broken; measured at its true (roughly monthly) cadence it can look excellent. Daily-active is the right denominator for a feed; monthly is right for travel; somewhere between for most SaaS.
- Forcing a daily metric onto a weekly/monthly behavior manufactures false alarms; forcing a monthly metric onto a daily behavior hides real churn. (This is the same natural-frequency logic that picks an activation cadence — see `growth/activation-aha-habit.md`.)

## DAU/MAU stickiness — and its trap

**DAU/MAU** (daily active users ÷ monthly active users) is the standard **stickiness** ratio: of the users who showed up this month, what fraction show up on an average day. It is a quick proxy for habit strength.

- A widely-cited practitioner heuristic puts **DAU/MAU above ~50% as excellent** for consumer products built on daily habits (and Lenny Rachitsky's benchmark framing treats >50% DAU/MAU _or_ >50% D30 retention as excellent). Treat these as practitioner rules of thumb from named sources, not laws.
- **The trap: DAU/MAU only makes sense for products whose natural frequency is daily.** Applying it to an inherently weekly or monthly product (most B2B tools, travel, finance) produces a low ratio that looks alarming but means nothing — the users aren't _supposed_ to come daily. Worse, DAU/MAU can be inflated by re-engagement spam (notifications that drive opens without value), so a rising ratio is not automatically good. It is a stickiness proxy, not a value metric; pair it with retention-curve flattening, never substitute it.

## Retention benchmarks (practitioner, by business model)

Winters and Rachitsky published benchmark ranges from surveying practitioners across company types. **These are venture-scale benchmarks from a practitioner survey — directional, not authoritative**; the study itself stresses "what matters is that your retention supports sustained growth," and that lower retention can be fine for low-CAC or non-explosive-growth businesses.

User retention, measured at **6 months** (share of the sign-up cohort still active):

| Category               | Good | Great |
| ---------------------- | ---- | ----- |
| Consumer social        | ~25% | ~45%  |
| Consumer transactional | ~30% | ~50%  |
| Consumer SaaS          | ~40% | ~70%  |
| SMB / mid-market SaaS  | ~60% | ~80%  |
| Enterprise SaaS        | ~70% | ~90%  |

The study deliberately separates **user retention** from **net revenue retention (NRR)** because who you sell to changes revenue dynamics — e.g. bottom-up SaaS (Slack, Figma, Zoom) can show NRR above 100% via in-organization expansion even with some user churn (their reported "good/great" bottom-up NRR is ~100% / ~120% at 12 months). Use user retention to judge product value; use NRR to judge the business model's expansion.

> Labeling: every number in this section is a reported practitioner benchmark from the Winters/Rachitsky survey, transcribed from its public write-up. They are reproduced as that study's findings, not independently verified, and not universal targets — calibrate to your business model and CAC.

## The North Star anchors engagement

The risk with engagement metrics is measuring _activity_ instead of _value_. The **North Star metric** is the anchor that keeps engagement honest: the single metric that best captures realized customer value, chosen as a **leading indicator of success rather than a lagging one like revenue** (see `experimentation/metric-design.md` for the selection method and Amplitude's criteria). Retention and engagement metrics should ladder up to it:

- The North Star is the value metric; retention-curve flattening shows whether that value is _durable_; DAU/MAU and frequency show the _shape_ of engagement underneath it.
- Reforge's input/output framing applies: the North Star and retention are **outputs (lagging)**; the **inputs (leading)** are the handful of in-product actions a team can directly move to bend them. You manage the inputs; you watch the outputs.

## Engagement vs. vanity metrics

A vanity metric goes up and to the right, looks impressive in a deck, and **changes no decision.** The distinction is not what the metric measures but whether it can be acted on and whether it reflects value.

| Vanity (avoid as a goal) | Actionable engagement / value (prefer) |
| --- | --- |
| Cumulative registered users (only ever grows) | Active users at the natural frequency; cohort retention |
| Total page views / total sessions | Retained-cohort engagement; power-user-curve shape |
| Downloads / sign-ups | Activated users (reached the aha and a habit loop) |
| Raw DAU as a headline | DAU/MAU stickiness _plus_ whether the curve flattens |
| "Time on site" celebrated unconditionally | Time on site interpreted against the job — more is good for a feed, bad for a support tool |

The vanity test, in one line: **if this metric moved, would we make a different decision?** If a number only ever rises, can't be tied to a specific input the team controls, and wouldn't change a choice, it is decoration — report it for morale if you must, but never set it as a goal. (Cumulative totals are the archetypal trap: they cannot go down, so they always look like success even as the product dies.)

## The retention-and-engagement checklist

1. **Curve before number.** Plot the cohort retention curve and ask first: **does it flatten?** A plateau means durable value (PMF with a segment); a slide to zero means no growth tactic will save it.
2. **Right clock.** Is the interval (daily/weekly/monthly) matched to the product's natural frequency / offline analog? A wrong interval invents or hides churn.
3. **Stickiness in context.** Is DAU/MAU being used only for a genuinely daily-frequency product, and read alongside the curve — not as a standalone or inflatable-by-notifications headline?
4. **Benchmarks as direction, not verdict.** Compare to the Winters/Rachitsky ranges _for your business model_, treating them as practitioner directionals, and judge against "does retention support sustained growth," not a single threshold.
5. **Engagement ladders to the North Star.** Every engagement metric connects to the value-based North Star (a leading indicator, not revenue), with the team's leverage on the **inputs** that move it.
6. **No vanity goals.** Every headline metric passes the test — _if it moved, we'd decide differently_. Cumulative totals and uninterpreted activity counts are reported, never targeted.
