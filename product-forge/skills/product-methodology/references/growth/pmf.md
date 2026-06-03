---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Sean Ellis. Using Product/Market Fit to Drive Sustainable Growth. GrowthHackers / Medium, 2009. https://medium.com/growthhackers/using-product-market-fit-to-drive-sustainable-growth-58e9124ee8db"
  - "Sean Ellis. The Product/Market Fit Survey. pmfsurvey.com"
  - "Rahul Vohra. How Superhuman Built an Engine to Find Product/Market Fit. First Round Review. https://review.firstround.com/how-superhuman-built-an-engine-to-find-product-market-fit/"
  - "Rahul Vohra. The Superhuman Product/Market Fit Engine. https://coda.io/@rahulvohra/superhuman-product-market-fit-engine"
  - "Julie Supan. The high-expectation customer (HXC) framework, as applied by Vohra."
---

# Product-Market Fit (PMF)

Product-market fit is famously easier to recognize in hindsight than to measure in the moment — Marc Andreessen's "you can always feel when product-market fit isn't happening" is true but not operational. Sean Ellis's contribution was to make PMF **measurable while you still have time to act on it**, via a single leading-indicator survey question; Rahul Vohra's contribution was to turn that one number into a repeatable **engine** for raising it. This reference covers the 40% "very disappointed" test, the signals and fallacies around PMF, and the Superhuman PMF engine — the standard method for systematically increasing fit. Sources are Ellis's original essay and survey, and Vohra's First Round Review write-up.

> The reframe: don't wait for retention curves to mature to learn if you have PMF. Ask recently-active users one question — _how would you feel if you could no longer use this?_ — and watch the share who say **"very disappointed."** It is a leading indicator of the must-have feeling that PMF is made of.

## The 40% "very disappointed" test

Sean Ellis — who ran early growth at Dropbox, LogMeIn, and Eventbrite — looked for a metric that predicted PMF earlier than retention. The result is one question:

```text
How would you feel if you could no longer use [Product]?
  A) Very disappointed
  B) Somewhat disappointed
  C) Not disappointed (it isn't that useful)
  D) N/A — I no longer use [Product]
```

The PMF score is **the percentage of respondents who answer "very disappointed."** Ellis's benchmark, from surveying roughly a hundred startups: **a product can begin to grow sustainably once it reaches around 40% "very disappointed."** Below ~40%, companies almost always struggled to find growth; at or above it, they tended to have strong traction. In his words, "it becomes possible to sustainably grow a product when it reaches around 40% of users who try it that would be 'very disappointed'" without it.

Two methodology points Ellis is explicit about, and that make-or-break the number:

- **Survey people who have experienced real usage.** "Our goal for the survey is to get feedback from people who have recently experienced 'real usage' of the product" — typically users active in the last couple of weeks, _not_ everyone who ever signed up. Surveying tourists deflates the score; surveying only fans inflates it. The honest population is recent, genuine users.
- **It is a leading indicator, not a guarantee.** Ellis frames it as "a leading indicator to help you understand if early customers consider your product a must-have." It predicts; it does not certify.

> Calibration label: the 40% threshold is Ellis's empirical heuristic from benchmarking ~100 startups, presented in his essay as guidance from experience rather than a derived constant — his own write-up "does not explain the methodology for arriving at this specific benchmark." Treat 40% as a well-known, widely-used directional bar from a named primary source, not a law of nature; the _trend_ (below 40% struggles, above 40% has traction) is the durable claim.

## PMF signals and fallacies

PMF has real signals and seductive fakes. The honest signals tend to be _pull_ — the market taking the product from you — and the fallacies tend to be _push_ you mistake for pull.

Genuine signals:

- **Retention curves that flatten** — a cohort that decays to a stable plateau means durable value with a segment; the single strongest objective PMF signal (see `growth/retention-engagement.md`).
- **~40%+ "very disappointed"** on the Ellis survey among recently-active users.
- **Organic pull** — word-of-mouth, unsolicited demand, usage outrunning the team's ability to keep up, customers hacking around your limits to keep using it.

Common fallacies:

- **Vanity-metric PMF.** Sign-ups, downloads, total registered users, press, and a spiky launch are not PMF — they measure curiosity and marketing, not the must-have feeling. A product can post big top-of-funnel numbers and retain no one (cumulative totals only ever go up; see the vanity-metric test in `growth/retention-engagement.md`).
- **Surveying the wrong people.** Including never-activated sign-ups, or only your champions, corrupts the 40% number in opposite directions. The test only works on recent real users.
- **Treating PMF as permanent.** PMF is not a milestone you pass once. Vohra's caution: as you grow beyond early adopters to more demanding users, the score tends to **drop** — fit must be continuously re-earned, especially for non-network-effect products.
- **Founder feel as evidence.** "It feels like it's working" is exactly the unfalsifiable read Ellis's question was invented to replace.

## The Superhuman PMF engine

Rahul Vohra ran the Ellis survey on Superhuman's beta and got **22% "very disappointed"** — below the 40% bar, and "feel"-based advice ("keep iterating") gave him nothing to act on. So he built a four-step engine to systematically raise the number, taking Superhuman from 22% to **58%** over three quarters (with a jump to 33% from segmentation alone). The four steps:

### 1. Segment — find the supporters and define the high-expectation customer

Group respondents by their answer and **focus only on the "very disappointed" segment** — the people who already love it. Vohra reports that this narrowing _by itself_ raised the score by ~10 points (the broad number was dragged down by users who were never going to love the product). Then, using Julie Supan's **high-expectation-customer (HXC)** framework, study how those "very disappointed" users describe who would most benefit (a survey question: _what type of people do you think would most benefit?_) — happy customers describe themselves, revealing the profile and the language. Superhuman's HXC was "Nicole," a busy professional processing 100-200 emails a day who values responsiveness and inbox zero.

### 2. Analyze — why people love it, and what holds the fence-sitters back

Two questions drive the roadmap, asked of different segments:

- **From "very disappointed" users — why do they love it?** (_What is the main benefit you receive?_) For Superhuman, word-cloud analysis surfaced three themes: **speed, focus, keyboard shortcuts.** This is what to protect and amplify.
- **From "somewhat disappointed" users — what holds them back?** Here Vohra applies a counterintuitive cut: **ignore the somewhat-disappointed users who don't already value your core benefit** (they're "essentially a lost cause"), and **intensely study the ones who _do_ value it but are still only somewhat disappointed** — they are converts in waiting. Their answers to _how can we improve?_ revealed the decisive gap: a missing **mobile app**, plus integrations, attachments, calendaring, and better search.

His stated principle: "Politely disregard those who would not be disappointed without your product. They are so far from loving you that they are essentially a lost cause."

### 3. Build a roadmap that splits love and gaps 50/50

Vohra names the central tension precisely: **"If you only double down on what users love, your product-market fit score won't increase. If you only address what holds users back, your competition will likely overtake you."** The resolution is a **50/50 roadmap**:

- **Half — double down on what they love:** more speed, more shortcuts, more automation, more design polish (the things "very disappointed" users named).
- **Half — close the gaps holding fence-sitters back:** the mobile app, integrations, attachments, calendaring, search (the things convertible "somewhat disappointed" users named).

Prioritize within that split by a simple cost/impact pass (label each project low/medium/high cost and impact; do low-cost, high-impact first).

### 4. Repeat — and make the PMF score the company's most important metric

Continuously survey **new** users (never re-survey the same person, to avoid contamination), tracking the "very disappointed" percentage weekly/monthly/quarterly with custom tooling. Superhuman made it a single OKR whose only key result was maximizing that percentage — the organization's North Star. The engine is a loop, not a one-time diagnosis: measure → segment → build → re-measure, because as you reach more demanding users the score erodes and must be re-earned.

## The PMF working method

A short sequence for using PMF as a working metric rather than a feeling:

1. **Measure, don't intuit.** Run the Ellis survey on recently-active real users; read the "very disappointed" percentage against the ~40% directional bar.
2. **If below 40%, run the engine, not more vibes.** Segment to your lovers, find why they love it (protect that) and what holds the convertible fence-sitters back (close that), and split the roadmap ~50/50 between the two.
3. **Define and recruit toward the HXC.** Let your "very disappointed" users describe your high-expectation customer; aim the product and positioning at them rather than at the lost-cause middle.
4. **Re-measure continuously.** Treat PMF as a moving number that drops as the audience widens; keep the survey running on fresh users and re-earn fit each quarter.
5. **Cross-check with retention.** The survey is the leading indicator; **flattening retention curves** are the lagging confirmation. Trust the pair, distrust either alone (see `growth/retention-engagement.md`).
