---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Andrew Chen, *The Cold Start Problem: How to Start and Scale Network Effects* (Harper Business, 2021)"
  - "Andrew Chen, 'On Marketplaces' (Stripe Atlas guide). https://stripe.com/guides/atlas/andrew-chen-marketplaces"
  - "Sarah Tavel, 'The Hierarchy of Marketplaces — Introduction and Level 1'. https://sarahtavel.medium.com/the-hierarchy-of-marketplaces-introduction-and-level-1-983995aa218e"
  - "Sarah Tavel, 'Hierarchy of Marketplaces — Level 2'. https://sarahtavel.medium.com/hierarchy-of-marketplaces-level-2-f1c44ed4a39"
  - "Lenny Rachitsky, 'The most important marketplace metrics'. https://www.lennysnewsletter.com/p/the-most-important-marketplace-metrics"
  - "Lenny Rachitsky, 'What is good retention?' (transactional-marketplace benchmark band). https://www.lennysnewsletter.com/p/what-is-good-retention-issue-29"
---

# Marketplaces

Marketplaces — Airbnb, Uber, eBay, Etsy, DoorDash, Upwork, Vinted — connect two distinct populations (supply and demand: hosts/guests, drivers/riders, sellers/buyers) and make money by facilitating transactions between them, typically via a **take rate** on each. They are governed by network effects: each side's value rises with the size of the _other_ side. That same property is the genre's central curse — an empty marketplace is worthless to both sides, so getting the first transactions to happen is structurally hard. This reference covers the conventions that make a marketplace function (liquidity, trust, the take-rate model), the metrics that track real health versus the seductive vanity number, and the two problems that define the genre: the chicken-and-egg cold start, and the perpetual balancing of supply against demand.

> The one-line frame: a marketplace is a **liquidity machine**, not a transaction counter. The job is to make it reliable that a buyer who shows up finds supply and a seller who shows up finds demand — fast. Liquidity is the product; GMV is a lagging byproduct that can lie (Tavel).

## Conventions: what these apps have in common

- **Two-sided structure with cross-side network effects.** Two populations with opposite needs; more supply makes the platform more valuable to demand and vice-versa. This is the engine and the trap.
- **A take rate.** The platform's cut of each transaction, expressed as a percentage of GMV (gross merchandise value). Take rate is the core monetization lever and is bounded by the value the platform adds versus the ease of going around it (disintermediation): too high and both sides transact off-platform; too low and the business doesn't fund itself.
- **Liquidity as the core product.** Liquidity is the probability that a posted listing sells (supply side) or that a searching buyer finds a match (demand side) within an acceptable time. Chen and Tavel both treat liquidity — not catalog size, not GMV — as the thing the marketplace actually sells.
- **Trust and safety machinery.** Strangers transacting money and goods/services need a trust substitute for the reputation a local relationship would provide: **ratings and reviews**, verification/identity, escrow or held payments, insurance/guarantees, and dispute resolution. Trust infrastructure is not a feature bolted on; it is what makes transactions between strangers possible at all.
- **Search, match, and discovery.** The mechanism that pairs the right demand with the right supply (search, ranking, recommendations, or active dispatch as in ride-hail). Match quality directly drives liquidity.
- **Payments and disbursement.** Collecting from demand, paying out supply, holding funds in between — the financial plumbing that also enforces the take rate.

## Signature patterns

- **Seed the hard side first.** Chen's central cold-start move: identify the **"hard side" of the network** — the smaller group that creates most of the value and is hardest to attract (often supply) — and win it first with disproportionate effort and incentives (Chen, _Cold Start_). A marketplace with no supply has nothing to offer demand.
- **Find the atomic network.** Don't try to launch the whole market — find the smallest network that delivers real value on its own (one city, one category, one campus) and make _it_ liquid before expanding. Chen calls this the **atomic network**; Tavel's Level-1 equivalent is to "pick the thimble" — a narrow segment where you can saturate and create real happiness (Chen; Tavel).
- **Subsidize, guarantee, or fake the cold start.** Common bootstraps: guarantee supply-side income early to pull providers in (predictable pay de-risks joining an empty platform — Chen, via Stripe Atlas), single-player utility that has value before the network exists, concierge/manual matching, or seeding one side yourself.
- **Constrain geography/category to concentrate liquidity.** Going deep in one market beats going thin across many; liquidity is local and does not average across a sparse map.
- **Build trust as a growth lever, not a cost center.** Reviews, guarantees, and verification reduce the perceived risk of a first transaction, which is the conversion gate; better trust → higher fill rate → more liquidity.

## Key metrics

The genre's metric discipline is unusually well-developed _because_ its headline number (GMV) is so misleading. Track liquidity and happiness; treat GMV as a lagging byproduct.

| Metric | What it measures | Why it matters here |
| --- | --- | --- |
| **Fill rate (match rate)** | Share of demand intent that results in a completed transaction (or supply listings that sell) | Lenny argues fill rate is "the ultimate measure of marketplace health, because it's the essence of what a marketplace is" — it _is_ liquidity made measurable (Rachitsky). Absolute values vary wildly by stage; track relative improvement |
| **Net dollar / revenue retention** | Revenue retained and expanded from existing cohorts | Tavel's pick for the best _single_ proxy for marketplace "happiness" — durable value, not accumulated volume (Tavel) |
| **Repeat / cohort retention** | Whether buyers and sellers come back and transact again | Distinguishes a real marketplace from a one-time-transaction funnel; the flattening cohort curve is the health signal |
| **Take rate** | Platform revenue ÷ GMV | The monetization lever; its ceiling is set by added value vs. disintermediation risk |
| **Supply/demand balance** | Ratio and growth of each side; geographic/temporal coverage | An imbalance starves liquidity on the short side (see below); a healthy marketplace tracks both sides, not the aggregate |
| **Time to first / second transaction** | How fast a new participant transacts, and returns | Activation gates for each side; the second transaction is the retention signal |

A reusable rule: **measure liquidity and happiness; treat GMV as a lagging byproduct.** A marketplace can grow GMV while liquidity rots (low fill rate masked by a few whales, or by buying volume that won't repeat).

## Pitfalls

- **Chasing GMV — the genre's signature vanity metric.** Tavel is explicit: "GMV is a vanity metric for marketplaces," the marketplace analogue of MAU for social, because it "does not get to the heart of whether you are creating enduring value." Her thesis: "the ultimate success of your marketplace will depend on your ability to create meaningfully more happiness in the average transaction than any substitute, _not_ how many transactions you accumulate" — and "by pursuing happiness, you'll achieve growth. But not vice-versa" (Tavel). GMV grows on subsidies, whales, and one-time buyers while the marketplace fails; it is the number that most reliably misleads (see `genre-metrics-map.md`).
- **Launching too broad / failing the cold start.** Spreading thin across many cities or categories so no single one reaches liquidity. The fix is the atomic network / "pick the thimble" — saturate one before expanding (Chen; Tavel).
- **Solving the easy side first.** Pouring acquisition into demand when supply is the hard, value-creating side (or vice-versa) — you fill the platform with frustrated users who find no match (Chen).
- **Take rate set wrong.** Too high invites disintermediation (both sides transact off-platform once trust exists); too low starves the business. The take rate must track the value the platform genuinely adds.
- **Trust under-built.** Skimping on reviews, verification, guarantees, or dispute resolution caps the first-transaction conversion rate — the liquidity gate for strangers.
- **Averaging away an imbalance.** Reporting one aggregate GMV / one match rate hides that supply is glutted in one segment and starved in another; liquidity is local and per-side.

## Cold start and supply-vs-demand balance (the two defining problems)

**The cold-start (chicken-and-egg) problem.** Neither side will join an empty platform: demand won't come without supply, supply won't come without demand. This kills most marketplaces before they start. Chen's resolution is the **Cold Start Theory** — don't try to fill the whole market; find the **atomic network** (the smallest network that delivers real value on its own), and win the **hard side first** (the smaller, value-creating side, usually supply) with concentrated effort and incentives. Common bootstraps: guarantee supply-side earnings early to make joining an empty platform rational (Chen, via Stripe Atlas), provide single-player utility that has value pre-network, or seed/concierge one side manually. Tavel's complementary Level-1 advice — saturate a narrow segment to "minimum viable happiness" before expanding — is the same instinct from the happiness angle.

**Supply-vs-demand acquisition balance.** Once liquid, the work is never finished: a marketplace must continuously keep the two sides in balance, because liquidity is set by the **short side**. Over-acquire demand and buyers churn from unmet searches (no supply to match); over-acquire supply and providers churn from idle inventory (no demand to absorb it). Either imbalance destroys liquidity on the starved side and, with it, retention on _both_ sides. The operational discipline is to steer acquisition spend toward whichever side is currently constraining liquidity — and to read the two sides as separate funnels with separate cohort retention, never as one aggregate (Chen; Rachitsky). A single blended GMV number is exactly the report that hides a balance problem until churn surfaces it.

## Good vs. bad

| Dimension | Good | Bad |
| --- | --- | --- |
| **Headline metric** | Fill rate / liquidity + net revenue retention (happiness) | Aggregate GMV — the genre's vanity metric (Tavel) |
| **Launch strategy** | Atomic network / "pick the thimble" — saturate one segment first | Broad launch across many cities/categories, none liquid |
| **Which side first** | The hard, value-creating side (usually supply), seeded with incentives | The easy side, leaving the platform full of unmatched users |
| **Take rate** | Tracks genuine added value; resilient to disintermediation | Too high (invites off-platform) or too low (starves the business) |
| **Trust** | Reviews, verification, guarantees, disputes built as a growth lever | Under-built; first-transaction conversion capped by perceived risk |
| **Balance** | Two sides tracked as separate funnels; spend steers to the short side | One blended GMV number; imbalance hidden until churn appears |
| **Growth philosophy** | Pursue happiness/liquidity; growth follows (Tavel) | Pursue GMV directly via subsidies and whales; liquidity rots underneath |
