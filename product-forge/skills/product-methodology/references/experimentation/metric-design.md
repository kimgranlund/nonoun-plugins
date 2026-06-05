---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Ron K., Diane Tang & Ya Xu (2020). Trustworthy Online Controlled Experiments: A Practical Guide to A/B Testing. Cambridge University Press, ch. 6-7. ISBN 9781108724265. DOI 10.1017/9781108653985"
  - "Ron K., Deng, Frasca, Longbotham, Walker & Xu (2012). Trustworthy Online Controlled Experiments: Five Puzzling Outcomes Explained. Proceedings of the 18th ACM SIGKDD (KDD '12)"
  - "Amplitude / John C. The North Star Playbook. https://amplitude.com/books/north-star and https://info.amplitude.com/rs/138-CDN-550/images/Amplitude-The-North-Star-Playbook.pdf"
  - "Amplitude. Every Product Needs a North Star Metric: Here's How to Find Yours. https://amplitude.com/blog/product-north-star-metric"
  - "Reforge / Brian Balfour & Casey Winters. Input metrics vs output metrics (leading vs lagging) — Reforge growth curriculum, summarized at https://www.reforge.com/blog/north-star-metric-growth"
---

# Metric Design as a Working Method

A product team drowns in numbers; the discipline is deciding, in advance, which few numbers are allowed to make decisions — and how they relate. This reference is the working manual for designing that metric set: the goal / driver / guardrail roles a metric can play, the surrogate-metric trap that quietly inverts a team's incentives, how to construct an Overall Evaluation Criterion (OEC), and how to select a North Star metric. The experimentation backbone is Ron K., Tang & Xu's _Trustworthy Online Controlled Experiments_ (Cambridge, 2020), whose chapters 6-7 are the standard treatment of metrics for experimentation; the North-Star material is from Amplitude's _North Star Playbook_ and the Reforge input/output framing. (For the trust mechanics of reading a single experiment result — SRM, Twyman's law, novelty effects — see the sibling `experimentation/trustworthy-experiments.md`; this file is about designing the metrics themselves.)

> The one-line discipline: you do not get to pick which metric "won" after the data arrives. You define the roles each metric plays — what you are trying to move, what moves first, and what you refuse to break — before the experiment runs.

## The metric taxonomy: goal, driver, guardrail

Ron K., Tang & Xu sort metrics by the _job each one does_ in a decision, not by what it measures. The three load-bearing roles:

- **Goal metrics** (also "success" or "true-north" metrics) — what you ultimately want to move: the metric that captures the long-term value of the change to the business and the user. They tend to be the _right_ thing to optimize and the _hardest_ to move in a single experiment's window, because long-term value is slow.
- **Driver metrics** (also "indirect," "surrogate," or "proxy" metrics) — faster-moving, more sensitive metrics that are hypothesized to _cause_ the goal metric. The book's standing requirement is that a driver metric be **aligned with the goal, actionable, sensitive, and resistant to gaming.** Drivers exist because goal metrics are often too slow and too insensitive to decide an experiment; a driver is a bet that "if this moves, the goal will follow."
- **Guardrail metrics** — the metrics you are _not_ trying to improve but refuse to harm. A guardrail is not a target; it is a veto. The team's classic operational guardrails are latency / page-load time, crash and error rates, and page size — the do-no-harm metrics that any feature can quietly degrade while it "wins" on the thing you were watching.

The working move is to assign every metric a role explicitly. A metric with no role is noise that will be mined for a flattering story after the fact. (A complementary distinction from the Reforge / Balfour-Winters curriculum: **input metrics are leading indicators — actions you can directly influence; output metrics are lagging indicators — results.** Driver/goal maps onto input/output: you act on inputs/drivers and hope the output/goal follows.)

## The surrogate-metric trap: when the proxy inverts the goal

Because the goal metric is slow, teams reach for a driver as a **surrogate** — a short-term proxy standing in for long-term value. The trap, set out in Ron K. et al.'s "Five Puzzling Outcomes Explained" (KDD '12) and revisited in the 2020 book, is that **a surrogate can move the opposite way from the goal it stands for.**

The canonical example is click-bait. Optimizing click-through rate (an easy, sensitive proxy) can produce a _positive_ short-term effect on clicks and a _negative_ long-term effect on user retention and revenue — the proxy improves while the goal it was supposed to represent degrades. The trap is structural, not careless: the surrogate was chosen _because_ it is easy to move, which is exactly the property that makes it gameable. Optimizing the proxy hard enough actively harms the objective.

Defenses, per the book:

- **Validate the causal link, don't assume it.** A surrogate earns its place only if moving it _causes_ the goal to move — established via long-running holdouts or holdback experiments, not merely a historical correlation. Correlation between proxy and goal in past data is the weakest possible evidence and the most common justification.
- **Watch for the inversion directly.** Track the goal metric over a longer horizon (a long-term holdout) even while deciding on the surrogate, so a proxy/goal divergence shows up rather than being assumed away.
- **Treat sensitivity as a warning, not a virtue.** The easiest metric to move is the one most likely to be a gameable proxy. Sensitivity is necessary for a driver but is also the property that makes click-bait-style failures possible.

> Caveat (single-source on the statistical fix): a 2021 WSDM paper (Duan et al., "Online Experimentation with Surrogate Metrics") proposes accounting for the surrogate model's prediction error when computing p-values to control the inflated false-positive rate. Treat that specific statistical correction as one team's published method, not settled canon; the _conceptual_ surrogate trap is firmly Ron K.-canonical.

## Constructing an OEC

The **Overall Evaluation Criterion (OEC)** is the metric — or a small, weighted set of metrics — agreed _in advance_ to decide whether a variant wins. Its defining property, per Ron K., Tang & Xu: an OEC must be **"believed to causally impact long-term objectives."** It is the contract that stops post-hoc metric-shopping, the practice of picking — after the data arrives — whichever of fifty metrics happened to move your way.

What makes an OEC usable:

- **Measurable in the short term, predictive of the long term.** It must be computable inside the experiment window yet stand in for the long-run goal — the central tension that creates the surrogate trap above.
- **Sensitive and timely** — it must move enough, fast enough, to be detectable in a normal experiment duration.
- **Causal, not merely correlated** — improving the OEC should _cause_ the long-term objective to improve.
- **Aligning** — combining related metrics into one OEC gives the organization a single agreed thing to optimize instead of an argument over which chart to believe.

A worked construction couples the obvious win metric with the thing it would otherwise cannibalize. The book's email-campaign example:

```text
OEC = (Revenue − Unsubscribes × Unsubscribe_Lifetime_Loss) / Number_Of_Users
```

The structure is the lesson: revenue per user, _net_ of the future revenue destroyed when an aggressive campaign drives unsubscribes. A good OEC builds the cannibalization in, so a variant cannot "win" by borrowing against the future. In practice the OEC sits on top of the taxonomy: it is the (possibly combined) **goal/driver** the experiment decides on, evaluated **only when the guardrails hold** — a guardrail regression can veto an OEC win outright.

## Selecting a North Star metric

Where the OEC decides a single experiment, the **North Star metric** is the organization-level metric that aligns everyone's work over quarters. Amplitude's _North Star Playbook_ (John C., former Amplitude product evangelist) frames it as the single metric that **best captures the value customers derive from your product**, sitting between three "languages" — customer, product, and business — and made operational by a small set of **inputs**: the handful of factors that together produce the North Star and that teams can directly influence with day-to-day work.

Amplitude's three stated characteristics of a good North Star metric:

1. **Aligns to customer value** — it "should spring from a deep understanding of the actions within your product that provide realized value to your customer." Not what your team produces; what the customer gets.
2. **Represents product strategy** — "someone should be able to read it and understand your company's product strategy and your vision."
3. **Is a leading indicator of success** — "a critical aspect of a good North Star Metric is that it's a leading indicator of future success," _rather than_ a lagging indicator like revenue. A North Star predicts the money; it is not the money.

Amplitude's illustrative examples (note these are stated as patterns, and the playbook stresses that two companies "playing the same game" can have radically different North Stars):

- **Facebook** — number of users adding seven friends in the first ten days.
- **A Dropbox-style SaaS** — trial accounts with more than three users active in week 1.
- **A Fortune-100 retailer (eCommerce)** — number of mobile orders delivered.

### The North-Star selection method

1. **Start from realized customer value, then find the action that proxies it.** The metric is a measurable user action that means "the customer got the value." Work backward from the value, not forward from what is easy to log.
2. **Demand a leading indicator of revenue, not revenue.** Revenue is the lagging outcome; the North Star is the in-product behavior that reliably precedes it. (Choosing revenue itself as the North Star is the most common error — it tells you what happened, not what to do.)
3. **Name the inputs.** Decompose the North Star into 3-5 inputs the team can move directly. The inputs _are_ the framework: they connect daily work to the one metric. (This is the same input/output, leading/lagging split as the driver/goal taxonomy above.)
4. **Pass the value test, not the vanity test** — see below.

> Caveat (blocked-source label): Reforge's "Don't Let Your North Star Metric Deceive You" argues a North Star can mislead when it is mistaken for a complete strategy, gamed, or conflated with revenue, and recommends pairing it with inputs and counter-metrics. We could not fetch the full Reforge article in this pass (HTTP 403); the input-vs-output / leading-vs-lagging framing attributed to Reforge here is taken from its publicly summarized growth curriculum, and the specific "deceive" failure modes are reported as Reforge's claim, not independently verified against the full text.

## The metric-design checklist

Run this before an experiment metric set or a North Star is allowed to make decisions. Each item is a known way a metric set lies.

1. **Every metric has a declared role.** Goal, driver, or guardrail — assigned in advance. A metric with no role will be mined for a flattering story after the data lands.
2. **The OEC is pre-registered and causal.** The decision metric was chosen _before_ the data, and it is believed to causally drive the long-term objective — not picked because it moved.
3. **Surrogate links are validated, not assumed.** Any short-term proxy standing in for a slow goal has been checked (holdout / holdback) to move the _same_ direction as the goal. Beware the most sensitive metric — it is the most gameable.
4. **Guardrails can veto.** Latency, errors, and other do-no-harm metrics are explicitly tracked, with thresholds that can overturn an OEC "win."
5. **Cannibalization is priced in.** The OEC nets out the cost the win imposes (the unsubscribe term), so a variant cannot win by borrowing from the future.
6. **The North Star is a leading indicator of value, not revenue.** It measures realized customer value, predicts the money, and decomposes into a few inputs the team can directly move.
7. **No metric in the set is a vanity metric.** Each one, if it moved, would change a decision (see the engagement-vs-vanity test in `growth/retention-engagement.md`). A metric that only ever goes up and never changes a choice is decoration.

A metric set earns the right to decide only when each metric's role is named, the decision criterion was fixed in advance, and every proxy has been shown to move with — not against — the value it stands for.
