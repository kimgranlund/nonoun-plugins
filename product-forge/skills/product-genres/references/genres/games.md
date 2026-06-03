---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Tomas Hubka (updated 2025). 22 metrics all game developers should know by heart. GameAnalytics. https://www.gameanalytics.com/blog/metrics-all-game-developers-should-know"
  - "GameAnalytics. Mobile Gaming Benchmarks Report (global analysis across thousands of live mobile games). https://www.gameanalytics.com/benchmarks"
  - "Adjust. What is average revenue per daily active user (ARPDAU)? https://www.adjust.com/glossary/arpdau/"
  - "Unity. What is ARPDAU: ARPDAU Formula. https://unity.com/glossary/arpdau-formula"
  - "Nir Eyal (2014). Hooked: How to Build Habit-Forming Products. Portfolio/Penguin (variable reward; the Manipulation Matrix). https://www.nirandfar.com/how-to-manufacture-desire/"
  - "Solsten. The True Drivers of D1, D7, and D30 Retention in Gaming (practitioner analysis; observational). https://solsten.io/blog/d1-d7-d30-retention-in-gaming"
  - "Game-design lineage: the 'core loop' / 'meta loop' vocabulary is practitioner-standard (e.g. GDC talks, Deconstructor of Fun); definitions here follow common practitioner usage and are labeled observational."
---

# Games as a Genre

A game is an engagement product whose value is the experience of playing, and whose economics — especially in free-to-play (F2P) mobile — depend on keeping players in a satisfying loop for long enough that a minority choose to pay. The genre is structured as nested loops at three timescales: the **core loop** (the second-to-minute action you repeat — aim/shoot, match/clear, tap/collect), the **meta loop** (the session-to-week progression that gives the core loop a reason — leveling, base-building, collection, ranks), and the **onboarding loop** (the first-session experience, the FTUE, that decides whether a player ever reaches the other two). Retention is the master metric because in F2P you cannot monetize a player who left, and monetization rides on the same loops that produce retention.

> The loop vocabulary (core / meta / onboarding) is practitioner-standard rather than drawn from a single canonical text — it recurs across GDC talks and game-economy writing (e.g. Deconstructor of Fun). Treat the definitions here as the common practitioner usage, labeled observational.

## The three loops (the genre's architecture)

- **Core loop.** The tight, repeated action that _is_ the moment-to-moment game. It must be satisfying in isolation — good "game feel," fast feedback, low input latency — because the player does it hundreds of times per session. A weak core loop cannot be rescued by meta systems.
- **Meta loop.** The longer arc that gives the core loop stakes and forward motion: progression, unlocks, collections, social ladders, live events. The meta loop is what converts "this is fun for five minutes" into "I want to come back tomorrow," and its strength shows up specifically in mid- and long-term retention.
- **Onboarding loop (FTUE).** The first-time user experience teaches the core loop, delivers an early win, and previews the meta payoff — all before the player decides to leave. Practitioner analysis ties FTUE quality directly to D1, which then caps every downstream metric (Solsten; observational).

## Signature UX patterns

- **Tutorialized first win.** Guided early play that produces a success within the first minute or two, establishing the core loop's payoff before introducing complexity.
- **Reward schedules and variable rewards.** Loot, drops, daily rewards, and randomized outcomes — Eyal's variable-reward mechanic (Hooked, 2014) in its purest form. The unpredictability of the next reward sustains the core loop.
- **Daily-return mechanics.** Daily login bonuses, refreshing energy/lives, and time-gated events that create a reason to open the app each day (and directly target the DAU/MAU ratio).
- **Progression and meta dashboards.** Level maps, collection grids, and rank ladders that make the meta loop visible and create open loops the player wants to close.
- **F2P monetization surfaces.** Soft/hard dual currencies, energy systems, gacha/loot boxes, battle passes, ad-reward placements, and limited-time offers — the structures through which a non-paying audience funds the game via a paying minority.

## The metrics that matter

These are the genre's real, citable benchmarks. Note the source and that benchmarks vary heavily by sub-genre (hyper-casual vs. casual/puzzle vs. mid-core vs. RPG/strategy).

- **Retention — D1 / D7 / D30.** The genre's master triad (GameAnalytics; Hubka, 2025). Practitioner reading: **D1 reflects FTUE/onboarding, D7 reflects core-loop stickiness, D30 reflects meta/long-term depth** (Solsten; observational). Order-of-magnitude benchmarks from GameAnalytics' large-sample mobile data: median D1 retention sits around the low-20s percent, with top-quartile titles materially higher; D7 medians are in the low single digits with top-quartile around 7–8%; D30 typically falls to single digits. Sub-genre matters enormously — casual/puzzle and social-casino retain very differently from hyper-casual. **Cite specific cut-offs as approximate and source-bound; do not present any one figure as a universal target.**
- **DAU / MAU and stickiness.** DAU/MAU is the share of monthly players who play on a given day (GameAnalytics). Practitioner consensus (observational, cross-source): ~20% is good and ~30%+ is strong/world-class for mobile games, with top casual titles often cited at 25–30%+; treat these as observational practitioner figures, not a single controlled benchmark.
- **ARPDAU (average revenue per daily active user).** Total daily revenue ÷ daily active users, across all monetization (IAP + ads + subscriptions) — Adjust/Unity glossaries. It is the genre's most responsive monetization metric because it reacts to a live-ops change within 24–48 hours. Reported ranges vary by monetization model (ad-driven hyper-casual at the low cents end; IAP-driven mid-core/RPG substantially higher); cite ranges as observational and model-dependent.
- **ARPU vs. ARPPU.** ARPU = revenue per active user; ARPPU = revenue per _paying_ user (GameAnalytics). The gap between them, plus conversion rate (share of players who ever pay — typically low single-digit percent in F2P), describes the whale-heavy revenue distribution that defines F2P economics.
- **Session length and sessions/day.** How long a sitting lasts and how many sittings per day — core-loop quality and habit signals (GameAnalytics).
- **LTV and churn.** Lifetime value (total revenue per player over their lifetime) set against churn (players who stop playing). LTV must clear acquisition cost for the economics to work; this is where retention and monetization meet.

## F2P monetization (genre-defining economics)

- **Dual currency.** A freely-earned soft currency and a purchased hard currency, with the design tension tuned so that progression is possible free but accelerated by paying.
- **The whale distribution.** A small fraction of players (often cited at low single-digit conversion) generates most revenue; ARPPU vastly exceeds ARPU. Designing for this minority without alienating the non-paying majority — who provide the social fabric and ad inventory — is the central F2P balancing act.
- **Live ops.** Recurring events, limited-time offers, and content drops that re-engage lapsed players and create monetization moments. ARPDAU's fast responsiveness makes it the live-ops feedback metric.
- **Ads vs. IAP vs. hybrid.** Rewarded video, interstitials, in-app purchases, and increasingly hybrid models. Monetization model strongly shifts which benchmark ranges are realistic — a hyper-casual ad title and an RPG IAP title are different economic species.

## The engagement-vs-dark-pattern line

The genre runs the same ethical seam as content consumption (see `content-consumption.md`), and a rubric should score it.

- **Variable reward is the shared mechanic.** The reward schedule that makes a core loop compelling is the same mechanism that, over-tuned, becomes compulsion. Eyal's own guardrail — the **Manipulation Matrix** — applies: build hooks that improve the player's life, and provide graceful exits.
- **The recognized dark patterns.** Predatory monetization (pay-to-win paywalls that gate core enjoyment), loot-box mechanics that obscure odds (now regulated in several jurisdictions and increasingly required to disclose drop rates), artificial energy/time-gates engineered to sell relief, and FOMO-driven limited offers aimed at impulse rather than value. These are the genre's named over-the-line patterns.
- **The test.** Engagement a player would endorse on reflection (this is fun, the progression feels earned) is the product working; engagement built on obscured odds, manufactured scarcity, or pay-gated core enjoyment is the product exploiting. The same loop produces both; the genre is judged by which it engineers.

## Common pitfalls

- **A weak core loop dressed in meta systems.** No amount of progression UI rescues a moment-to-moment action that is not fun; this shows as low D7 despite a busy meta layer.
- **Onboarding that loses D1.** A long, un-fun, or unclear FTUE that delays the first win caps every downstream metric — you cannot retain, monetize, or grow a player who quit in session one.
- **Monetization that breaks the loop.** Paywalls or ad density that interrupt the core loop trade short-term ARPDAU for retention collapse — a surrogate-metric trap (the easy-to-move money metric harming the long-term outcome).
- **Benchmark misuse.** Judging a hyper-casual title by mid-core retention/ARPDAU benchmarks (or vice versa) misreads health; benchmarks are sub-genre- and model-specific.
- **Chasing DAU with mechanics that do not deepen play.** Daily-login bonuses that inflate DAU without strengthening the core or meta loop produce hollow engagement that decays.

## Good vs. bad (for a genre-fit dimension)

| Dimension | Good (high genre-fit) | Bad (low genre-fit) |
| --- | --- | --- |
| Core loop | Satisfying in isolation; fast feedback, good feel | Repetitive, sluggish, or unrewarding moment-to-moment |
| Meta loop | Gives the core loop stakes; drives D7→D30 | Thin or absent; mid-term retention collapses |
| Onboarding | Early win in the first minute; strong D1 | Long/confusing FTUE; D1 caps everything below |
| Retention shape | D1/D7/D30 healthy for the sub-genre | Steep early drop-off vs. peers; no plateau |
| Monetization | Funds the game without breaking the loop | Pay-to-win paywalls; ad density that interrupts play |
| Loot/odds | Disclosed drop rates; value-aligned offers | Obscured odds, manufactured scarcity, FOMO traps |
| Ethics posture | Engagement the player endorses on reflection | Compulsion via gates/odds; manipulation-matrix fail |
| Benchmarking | Compared to the right sub-genre and model | Judged against an unrelated sub-genre's numbers |

The single most diagnostic question for genre-fit: **does each loop earn the next — core loop fun enough to repeat, meta loop rich enough to return for, onboarding fast enough to reach both — and does monetization ride the loops without breaking them?**
