---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Sean Ellis & Morgan Brown, *Hacking Growth* (Currency, 2017) — origin of the North Star Metric"
  - "Amplitude, 'The North Star Playbook' / 'About the North Star Framework'. https://amplitude.com/books/north-star/about-north-star-framework"
  - "Lenny Rachitsky, 'What is good retention?'. https://www.lennysnewsletter.com/p/what-is-good-retention-issue-29 — retention benchmark bands by category"
  - "Lenny Rachitsky, 'The most important marketplace metrics'. https://www.lennysnewsletter.com/p/the-most-important-marketplace-metrics"
  - "Sarah Tavel, 'The Hierarchy of Marketplaces'. https://sarahtavel.medium.com/the-hierarchy-of-marketplaces-introduction-and-level-1-983995aa218e — GMV as a vanity metric"
  - "Andrew Chen, '10 Magic Metrics' (cohort flattening, power-user curve). https://x.com/andrewchen/status/1184170125525577728"
  - "North Star examples (Spotify time spent listening; Airbnb nights booked; Facebook DAU; WhatsApp messages sent), as commonly cited. https://www.teknicks.com/blog/north-star-metric-examples/ ; https://uxcam.com/blog/north-star-metric-examples/"
  - "Mobile-game retention benchmarks & ARPDAU. https://solsten.io/blog/d1-d7-d30-retention-in-gaming ; https://www.singular.net/blog/game-analytics-dau/"
---

# Genre metrics map

This is the **index file for the genre taxonomy** — a cross-genre table of the North-Star metric, the key retention/engagement metric, and the metric _trap_ for each app genre, plus the principles that make the table cohere. It exists because the single most common product-measurement error is **importing one genre's metric into another** — judging a marketplace by MAU, a productivity tool by downloads, or an AI app by demo applause. Each genre has a number that genuinely captures value, a companion that measures durability, and a seductive number that grows while the product fails. The per-genre reference files in this directory expand each row; this file is the map.

> The one-line frame: **every genre has a metric that lies.** It is usually the easiest one to grow and the one a launch deck wants to show. Naming the trap per genre is half of measuring honestly; the other half is choosing a North Star that tracks _delivered value_, not activity.

## The North Star principle (shared across all genres)

Sean Ellis coined the **North Star Metric** — the single metric that best captures the **core value the product delivers to customers** (Ellis & Brown, _Hacking Growth_). Amplitude's framework adds that a good North Star should reflect real customer value, be a **leading indicator** of revenue (not revenue itself), and be **actionable** by teams through a handful of input metrics they can move (Amplitude). The discipline is what the North Star _excludes_: not revenue (a lagging result, not the value), and not raw activity (a proxy that detaches from value — the trap). Canonical examples, as commonly cited: **Spotify → time spent listening; Airbnb → nights booked; Facebook → daily active users; WhatsApp → messages sent** (Teknicks; UXCam — popularly reported, exact internal definitions vary).

Two cross-genre truths anchor every row below:

- **Retention-curve shape beats any single number.** Andrew Chen's product-market-fit signal is a **cohort retention curve that flattens** (users get hooked and keep returning) plus a **power-user curve that "smiles"** (a concentrated, deeply engaged core). A curve that decays toward zero is novelty regardless of how big the top-of-funnel looks (Chen). This applies to every genre.
- **The trap is almost always a top-of-funnel or aggregate count** — signups, downloads, installs, MAU, GMV, demo applause — that grows on acquisition, subsidies, or novelty while the value-delivery and retention underneath rot.

## The cross-genre table

Each genre has three metrics: the **North Star** (the value it should optimize), the **key retention/engagement metric** (does that value durably land), and the **trap** (the seductive number that grows while the product fails). Rows for genres with a dedicated reference file in this directory are the most grounded; rows marked _(convention)_ rest on widely-shared practice rather than a single cited source and should be treated as orientation, not benchmark.

| Genre | North-Star metric (value delivered) | Key retention / engagement metric | The trap (grows while failing) |
| --- | --- | --- | --- |
| **Workplace collaboration** (`workplace-collaboration.md`) | Active collaborating workspaces / seats expanded | Net dollar retention; team (workspace) cohort retention | Individual MAU / total registered users — counts logins, not collaboration |
| **Productivity** (`productivity.md`) | Habitual completion of the core job (tasks done, notes captured-and-retrieved) | Flattening cohort retention + DAU/MAU stickiness; the power-user smile | Signups / downloads / launch-week DAU — novelty that decays (the toy curve) |
| **Marketplaces** (`marketplaces.md`) | Fill rate / liquidity (matches completed); nights/rides/orders | Repeat-purchase / cohort retention; net revenue retention | **GMV** — Tavel's named vanity metric; grows on subsidies and whales while liquidity rots |
| **AI-native apps** (`ai-native-apps.md`) | Tasks completed at acceptable quality (eval pass rate × usage) | Retention after novelty wears off (flattening curve); containment/task-completion | Demo applause / sign-up spike / raw query volume — novelty and curiosity, not PMF _(emerging)_ |
| **Social / messaging** _(convention)_ | Meaningful interactions — messages sent, connections made, content shared (e.g. WhatsApp → messages sent; Facebook → DAU) | DAU/MAU stickiness; cohort retention; k-factor / invite loop | Registered users / total accounts — a huge user table with collapsing DAU/MAU and dead network density |
| **Content / media / streaming** _(convention)_ | Time spent in core consumption / completed sessions (e.g. Spotify → time spent listening) | Subscription retention; DAU/MAU; completion rate | Total catalog size / raw pageviews / impressions — inventory and traffic, not engaged consumption |
| **Games** _(convention)_ | Engaged play of the core loop (sessions, ARPDAU on a retained base) | **D1 / D7 / D30 retention** (historic rough bands ≈40 / 20 / 10%; D1 ≥50% now often cited as strong — Solsten/MAF, varies) | **Downloads / installs** and over-indexing on D1 alone — UA volume and first-day logins masking shallow content depth and D7/D30 collapse |
| **Tracking / quantified-self** _(convention)_ | Logging streak / entries recorded against the user's goal | Long-run cohort retention (does logging persist past the novelty week) | Total signups / one-time logs — the abandoned-after-January-1 curve |
| **Dashboards / analytics** _(convention)_ | Decisions or actions taken from the data (insight → action) | Recurring active analysts / query frequency; team retention | Dashboards created / charts rendered — artifacts produced, not decisions changed |
| **Fintech / finance** _(convention)_ | Funded accounts / transaction or payment volume per active user; assets under management | Funded-account retention; net revenue retention; balance growth | Sign-ups / app installs / KYC-started — funnel entries that never fund or transact |
| **Health / wellness** _(convention)_ | Sustained behavior change / completed care or activity episodes | Long-run program adherence and cohort retention | Downloads / enrollments / one-time check-ins — intent without sustained behavior |
| **Travel / booking** _(convention)_ | Completed bookings (nights / trips) — e.g. Airbnb → nights booked | Repeat-booking / cohort retention; net revenue retention | Searches / browse sessions / wishlist adds — high intent-traffic that never converts to a booking |

## How to read this table (and how it goes wrong)

| Lever | Good — honest measurement | Bad — the trap operating |
| --- | --- | --- |
| **Choice of North Star** | Tracks _value delivered_ to the customer; a leading indicator (Amplitude) | Tracks revenue (lagging) or raw activity (detached from value) |
| **Retention read** | Cohort curve _shape_ — does it flatten? is there a power-user smile? (Chen) | A single point-in-time number, or aggregate actives, with no cohorting |
| **The headline number** | The genre's value/liquidity metric (fill rate, collaborating workspaces, eval-quality × usage) | The genre's trap (GMV, MAU, downloads, demo applause) front-and-center |
| **Cross-genre hygiene** | Each genre judged by _its own_ value metric | One genre's metric imported into another (a marketplace judged by MAU; an AI app by signups) |
| **What growth is for** | Growth in service of value/happiness — "pursue happiness, growth follows" (Tavel) | Growth pursued directly via subsidies, paid acquisition, or novelty into a leaky bucket |

A reusable rule: **for any product, name its trap first.** Ask "which number here grows while the product quietly fails?" — it is almost always the easiest to grow and the one the deck leads with. Then choose a North Star that would _not_ move on subsidies, paid acquisition, or novelty alone, and read retention as a cohort curve, not a single figure.

## Scope and honesty note

The four genres with dedicated reference files in this directory (workplace-collaboration, productivity, marketplaces, ai-native-apps) carry primary-source-cited detail; the remaining rows are marked _(convention)_ because they summarize widely-shared practice (and, for several, the popularly-cited company North-Star examples) rather than a single authoritative source — and the canonical company examples are as _reported_, since firms' exact internal metric definitions are not public. Benchmark bands quoted anywhere here (retention by category from Rachitsky; D1/D7/D30 from gaming sources) are orientation, not targets: they vary by cohort, era, and definition, and Chen's point stands — the _shape_ of the curve matters more than hitting a benchmark number.
