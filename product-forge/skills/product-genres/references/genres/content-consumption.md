---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Tim Neusesser (2022). Infinite Scrolling: When to Use It, When to Avoid It. Nielsen Norman Group. https://www.nngroup.com/articles/infinite-scrolling-tips/"
  - "Bryan Kim (2023). Do You Have Lightning In a Bottle? How to Benchmark Your Social App. Andreessen Horowitz (a16z). https://a16z.com/do-you-have-lightning-in-a-bottle-how-to-benchmark-your-social-app/"
  - "Sequoia Capital Data Science. Retention. https://articles.sequoiacap.com/retention"
  - "Lenny Rachitsky (2020). What is good retention? (Issue 29; benchmark survey of 20+ growth experts). https://www.lennysnewsletter.com/p/what-is-good-retention-issue-29"
  - "Nir Eyal (2014). Hooked: How to Build Habit-Forming Products. Portfolio/Penguin (variable-reward model; engagement-vs-manipulation 'Manipulation Matrix'). https://www.nirandfar.com/how-to-manufacture-desire/"
  - "Federico Maggi et al. / academic literature on Attention-Capture Damaging Patterns and infinite scroll as variable reward (ACM CHI 2022, dl.acm.org/doi/fullHtml/10.1145/3491101.3519829)"
---

# Content-Consumption Apps as a Genre

Feeds, media libraries, news readers, and streaming services share one job: keep a stream of content flowing past a user who did not arrive with a specific item in mind. Unlike a single-purpose task app (see `single-purpose-task.md`), the consumption genre has **no terminal "done" state by design** — the experience is open-ended, and its core loop is _surface something worth attending to → hold attention → surface the next thing._ Discovery and ranking are the product; the catalog is only the raw material. This is also the genre where the engagement-vs-ethics line is sharpest, because the same mechanic that makes the product good (always something relevant next) is the mechanic that, pushed too hard, becomes an attention trap.

> The genre's defining tension: the metric that proves the product is working (sustained, voluntary session time) is one keystroke away from the metric that proves it is exploiting the user (compulsive, regretted session time). Designing this genre well means optimizing engagement that the user would endorse on reflection — and being able to tell the difference.

## Conventions: what the genre takes for granted

- **The feed/library is the home.** The default surface is a ranked stream, not a search box. The user is browsing without a goal, so the system must propose; "homogeneous content browsed without a specific goal" is exactly the case NN/g identifies as the home turf of infinite scroll (Neusesser, 2022).
- **Recommendation is the engine.** Ranking, personalization, and "next item" prediction are not features bolted on — they are the product. Netflix's own widely cited figure is that over 80% of viewing originates from personalized recommendation rather than search (observational, company-reported; treat the exact percentage as a vendor claim, not an independent measurement).
- **Continue / resume.** A "Continue watching / reading / listening" surface is a genre staple, because re-entry friction is churn. State is carried across sessions and devices.
- **Variable reward is structural.** The next item's value is unpredictable, which is precisely what sustains scrolling — academic work characterizes infinite scroll as a variable-reward mechanism: "the illusion that new interesting content will flow forever, while the quality of the next item cannot be predicted" (CHI 2022 literature on attention-capture patterns).

## Signature UX patterns

- **Infinite scroll vs. pagination vs. load-more.** The defining interaction decision. Per NN/g (Neusesser, 2022): infinite scroll fits goal-less browsing of homogeneous content, but fails when users must find a specific item, compare distant items, reach the footer, or are on low bandwidth. Its signature defect is **pogo-sticking** — tapping an item and returning via back resets the user to the top, forcing them to "scroll down through screenfuls and screenfuls of already-seen content." NN/g's stance is that no option is universally superior: a **Load More** button restores user control and footer access; integrated pagination adds landmarks for re-finding.
- **Autoplay and previews.** Auto-advancing video, hover previews, and post-play countdowns reduce the cost of the next item to zero. This is the most powerful engagement lever and the one most prone to crossing into dark-pattern territory.
- **Personalized entry points.** Per-user artwork/thumbnails, micro-genre rows, and reordered shelves shape what the first impression surfaces. (Netflix-reported figures of ~20–30% CTR lift from personalized artwork are company claims; cite as observational.)
- **Algorithmic + chronological toggles.** Offering the user a chronological or "following" view alongside the ranked feed is the genre's main concession to user control and freedom (NN/g heuristic #3) — and increasingly a regulatory expectation.

## The metrics that matter

This genre's north stars are engagement and retention, not task completion. The benchmarks below are real and citable; note which framework they come from, since "good" varies by product type.

- **DAU, MAU, and DAU/MAU stickiness.** The headline engagement ratio. a16z's social-app benchmarks (Bryan Kim, 2023): DAU/MAU of **25% is OK, 40% good, 50%+ great**. The L-ness curve (L5+, users active 5+ days/week) runs 30% OK / 40% good / 50%+ great. These are consumer-social benchmarks; media/streaming products with weekly rather than daily cadence should be judged on weekly-active analogues, not forced onto a daily ratio.
- **Retention curves (the real PMF test).** Sequoia's framing: plot cohort retention over time; a healthy product's curve **flattens to a plateau** rather than declining to zero — "the higher the level at which the curve flattens, the higher the long-term retention." a16z's consumer-social N-day benchmarks: D1 50/60/70%, D7 35/40/50%, D30 20/25/30% (OK/good/great), with the curve expected to flatten by roughly days 7–14 and plateau near day 20. Lenny Rachitsky's expert survey puts good 6-month consumer retention at ~25–40% and great at ~45–70% (Lenny, Issue 29).
- **Session length and sessions per day.** For this genre these are _legitimate_ north stars (the opposite of `single-purpose-task.md`). Average session duration and session frequency measure whether the stream holds attention. Streaming-specific practitioner metrics include completion rate and "binge velocity" (how fast a season is finished); company-reported correlations with lower churn are observational.
- **Discovery / catalog reach.** What fraction of the catalog actually gets surfaced and consumed — a long-tail health metric that distinguishes genuine discovery from re-serving the same hits.
- **CTR and play-rate on surfaced items.** The ranking system's local quality signal; useful but dangerous as a sole target (see surrogate-metric traps below).

## The infinite-scroll-ethics line (engagement vs. dark pattern)

This is the genre's defining design-ethics question, and a rubric should score it explicitly.

- **The bright line is reflective endorsement.** Engagement the user would endorse on reflection (found the next great show, caught up on the news they wanted) is the product working. Engagement the user regrets (an hour gone, "why am I still here?") is an attention-capture damaging pattern. The mechanic — variable reward, autoplay, infinite stream — is identical; only the alignment with the user's own goals differs.
- **CTR/dwell as a surrogate trap.** Optimizing raw click-through or dwell-time can actively harm long-term value — the canonical example is clickbait, which lifts short-term CTR while degrading retention and trust. (This is the surrogate-metric trap from the experimentation literature; see the methodology skill's experimentation references.) Engagement metrics must be paired with a guardrail that prices in the harm.
- **Nir Eyal's own guardrail.** Eyal, who literally wrote the variable-reward playbook (Hooked, 2014), pairs it with the **Manipulation Matrix**: build only hooks that materially improve the user's life, disclose persuasive patterns, and provide graceful exits (controls, limits, stopping cues). A consumption product with no stopping cue is failing its own designer's ethical test.
- **User control and freedom (NN/g heuristic).** Stopping cues ("you're all caught up"), digestible chunking, chronological options, time/usage controls, and a reachable footer are the genre's concrete countermeasures. Their presence or absence is the most observable proxy for which side of the line a product sits on.

## Common pitfalls

- **Pogo-sticking on infinite scroll.** Losing scroll position on back-navigation is the genre's most common, most fixable usability defect (NN/g, 2022).
- **Optimizing a surrogate (CTR/dwell) into clickbait.** Chasing the easy-to-move proxy degrades the long-term outcome it was standing in for.
- **Filter-bubble collapse / discovery starvation.** Over-tuning relevance re-serves the same content, starving the long tail and making the catalog feel smaller than it is — measurable as falling catalog reach.
- **No stopping cue.** An endless stream with no "caught up" state, no chunk boundaries, and aggressive autoplay is the structural signature of an attention trap.
- **Forcing daily metrics onto a weekly product.** Judging a weekly-cadence media product against daily DAU/MAU benchmarks (or vice versa) misreads health; match the metric's period to the genre's natural cadence.

## Good vs. bad (for a genre-fit dimension)

| Dimension | Good (high genre-fit) | Bad (low genre-fit) |
| --- | --- | --- |
| Discovery | Personalized + diverse; healthy catalog reach | Same hits re-served; long tail starved |
| Scroll/paging | Position preserved on return; Load-More option | Pogo-sticking resets to top; no footer access |
| Engagement metric | Session/frequency paired with a quality guardrail | Raw CTR/dwell optimized into clickbait |
| Retention | Cohort curve flattens to a high plateau (PMF) | Curve declines toward zero (leaky bucket) |
| Stopping cues | "Caught up" states, chunking, time controls | Endless autoplay, no boundary, no controls |
| Ethics posture | Engagement the user endorses on reflection | Compulsive, regretted use; manipulation-matrix fail |
| User control | Chronological/following toggle offered | Algorithmic feed only; no escape from ranking |

The single most diagnostic question for genre-fit: **would the user, looking back at this session, say the product served their goal — or that it captured their attention against it?** The mechanics are the same on both sides; the genre is judged by which one it is engineered to produce.
