---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Marty C., 'Vision vs. Strategy', Silicon Valley Product Group (svpg.com/vision-vs-strategy/)"
  - "Marty C., 'Product Strategy - Overview / Focus / Insights / Actions / Management', Silicon Valley Product Group (svpg.com/product-strategy-overview/ and the four linked parts)"
  - "Marty C., 'Changing How You Decide Which Problems To Solve', Silicon Valley Product Group (svpg.com/changing-how-you-decide-which-problems-to-solve/)"
  - "Marty C., *Inspired*, 2nd ed. (Wiley, 2017) and *Transformed: Moving to the Product Operating Model* (Wiley, 2024)"
  - "Gibson Biddle, '#1 The DHM Model' and '#2 From DHM to Product Strategy', Medium (gibsonbiddle.medium.com)"
  - "Marty C. on The Product Experience podcast, 'Product vision and strategy', Mind the Product (mindtheproduct.com)"
---

# The Product Strategy Stack

Product work has a natural altitude: a long-range _destination_, a chosen _way to get there_, the _bets and objectives_ that carry the approach, and the _roadmap_ of concrete work. This reference is the working method for the stack — vision → strategy → bets/objectives → roadmap — using Marty C.'s definitions of each layer and his insight-driven account of how strategy is actually made, with Gibson Biddle's DHM model as a concrete lens for what a good strategy concentrates on. It is the constructive companion to `strategy-vs-roadmap.md` (which diagnoses the failure of collapsing the stack) and `strategy-kernel.md` (the underlying good/bad-strategy theory).

> Marty C.'s one-line framing of the two top layers, paraphrased from _Vision vs. Strategy_ and his Product Experience interview: **the product vision describes the destination — how you will make customers' lives better — and the product strategy is how you decide which problems to solve now in order to get there.** Vision is the _what/where we're going_; strategy is the _how we'll get there_. Collapse them and you get an inspiring poster with no path, or a path to nowhere in particular.

## The layers, top to bottom

Each layer constrains the one below it. The connection is causal: you cannot set the right objectives without the strategy, and you cannot build the right roadmap without the objectives. Read top-down to plan; read bottom-up to audit (every roadmap item should trace all the way back to the vision).

| Layer | The question it answers | Time horizon (Marty C.) | Owned by |
| --- | --- | --- | --- |
| **Vision** | Where are we going, and how does that make customers' lives better? | ~2–5 yrs (5–10 for hardware); changes rarely | Leadership; shared across all teams |
| **Strategy** | Which few problems do we solve now to get there, and why those? | "A living thing," reviewed ~quarterly | Product leadership |
| **Bets / objectives** | What outcomes will each team pursue this period? | Per quarter / cycle (OKRs) | Leadership assigns; teams own the how |
| **Roadmap** | What concrete work, in what order? | Rolling; derived, not primary | The empowered team |

The discipline is that **the roadmap is the output, never the input.** A healthy stack produces the roadmap last, as a consequence of the bets; an unhealthy one starts with a roadmap and reverse-rationalizes a "strategy" to justify it (the failure dissected in `strategy-vs-roadmap.md`).

### Vision — the destination

The product vision describes the future you are trying to create and, crucially, how it improves customers' lives. Marty C.'s load-bearing properties: it is **emotional and inspiring** (its job is to recruit and align people for years), spans roughly two-to-five years (longer for hardware/device companies), and is **updated infrequently** — on the order of once every few years. The vision is deliberately not actionable on its own; that is the strategy's job. The test of a vision is whether people would willingly work on it for years, not whether it tells you what to build Monday.

### Strategy — the way to the destination

Where the vision is the destination, **the product strategy is how you decide which problems to solve now to get there.** Marty C.'s sharpest framing: strategy is "brass tacks" — it answers "okay, that vision sounds great; how in the world are we going to do that?" It is **a living thing**, revisited at least quarterly as teams surface new learnings. Strategy's product is a short, prioritized set of _problems worth solving this cycle_, which leadership then assigns to teams as objectives — never a list of features.

### Bets / objectives — the strategy made assignable

Strategy becomes executable by being converted into **outcome-based objectives for each team** (OKRs are Marty C.'s preferred instrument). Leadership supplies each team a problem to solve plus the strategic context; the team owns the solution (see `product-operating-model.md` and `empowered-teams.md`). The objective is an _outcome_ ("raise activation from A to B"), not an output ("ship the redesign") — encoding an output here re-introduces the build trap one layer up (`build-trap.md`).

### Roadmap — the concrete work, derived last

The roadmap is the sequence of work the empowered team chooses to pursue its objective. Marty C. is explicit that **a roadmap handed _down_ from leadership is command-and-control**, and that it lets teams confuse shipping features with actually moving the outcome. In a healthy stack the roadmap is the team's own, downstream artifact — falsifiable against the objective it serves — not the org's strategy.

## Insight-driven strategy: how the strategy layer is actually built

Marty C.'s most useful contribution at the strategy layer is _how_ a real strategy is generated, not just what it contains. In _Changing How You Decide Which Problems To Solve_ and the SVPG strategy series, he frames product strategy as four sequential moves:

1. **Focus.** Choices mean focus — "deciding what few things you really need to do, and therefore all the things you won't do." Most companies fail here by trying to do too much at once and diluting effort. (This is Richard R.'s concentration of force in product clothing; see `strategy-kernel.md`.)
2. **Leverage insights.** Once focused, strategy "depends on insights," and "insights come from study and thought." Marty C.'s three principal sources: **data** (where most product insights come from — quantitative analysis of how the product is actually used), **qualitative learning** from talking directly to customers, and **new enabling technologies** that change what's now possible. A strategy with no insight is just a reshuffled opinion.
3. **Convert insights into action.** Translate the chosen insights into **objectives assigned to specific teams**, each with the strategic context they need to solve the problem. This is the seam where the strategy stack meets the operating model.
4. **Manage the work.** Active management of the strategy "without resorting to micro-management" — keeping the bets coherent and adjusting as learnings arrive, since the strategy is a living thing.

The decisive principle underneath all four: in strong product companies, **what drives the strategy is the pursuit of the vision (and the insights about customers), not the queue of sales asks, competitor features, and customer requests.** They _care about_ those inputs but are not _driven by_ them. A strategy that is just a prioritized stakeholder request list has inverted this — it is driven by the queue, not by insight toward the vision.

## DHM: a concrete lens for what a good strategy concentrates on

Gibson Biddle (former VP/CPO at Netflix) gives the focus step a sharp, testable shape with the **DHM model**, which complements Marty C.'s process by specifying the _criteria_ a good strategic bet should satisfy. His canonical definition: a product strategy answers, **"How will your product delight customers in hard-to-copy, margin-enhancing ways?"**

- **D — Delight customers.** The bet must measurably make customers' lives better, now and in the future (Netflix examples Biddle cites: personalized recommendations, instant streaming, original content).
- **H — Hard-to-copy.** The bet should build or draw on a durable advantage a competitor can't trivially replicate — Biddle maps these to Hamilton Helmer's seven powers (brand, network effects, scale economies, counter-positioning, unique technology, switching costs, process power). Delight that is trivially copyable evaporates as advantage.
- **M — Margin-enhancing.** The bet must improve the business model so the company can fund the _next_ round of delight. Delight that loses money is not a strategy, it's a subsidy.

Biddle frames strategies as **hypotheses**, not fixed plans — "think of product strategy as hypotheses about how you hope to delight customers in hard-to-copy, margin-enhancing ways" — and argues the strongest strategies hit **two or three DHM objectives at once** ("achieving two or three objectives with a single strategy is at the heart of an effective product strategy"). Netflix's personalization is his showcase: it delights (better matches), is hard-to-copy (built on knowledge of an enormous member base), and is margin-enhancing (it improves content-investment forecasting) — all three at once.

How DHM sits in the stack: it is a **quality bar for the strategy layer**, not a fourth layer. When Marty C. says "focus," DHM gives you three questions to focus _toward_; a candidate bet that delights but is trivially copyable, or is hard-to-copy but margin-destroying, is a weak bet and the model flags it before it reaches the roadmap.

## How to apply it

- **Build top-down, audit bottom-up.** Set vision → strategy → objectives → roadmap in order. Then audit by reversing: pick any roadmap item and trace it up to an objective, the objective to a strategic bet, the bet to the vision. A break in the chain is a defect — usually a roadmap item that exists for no strategic reason.
- **Run the strategy layer through Marty C.'s four moves.** Force the sequence: have you actually _focused_ (named what you won't do)? Which specific _insight_ — from data, customers, or new tech — does each bet rest on? Has each bet been _converted into a team objective with context_? A strategy missing the insight step is opinion; missing the focus step is a wish list.
- **Score each bet against DHM.** For every strategic bet, ask all three DHM questions. Prefer bets that hit two or three. Treat a bet that hits only "delight" with suspicion — copyable, unfunded delight is not durable strategy.
- **Keep horizons honest.** If the "vision" changes every quarter, it's a strategy mislabeled; if the "strategy" never changes, it's an unrevisited vision. Vision is stable for years; strategy is revisited quarterly as insights arrive.

## Key moves

- **Refuse to ship a roadmap that can't trace upward.** The roadmap is derived; if an item traces to no objective, cut it or surface the missing bet.
- **Make the insight explicit per bet.** Write the literal sentence: "We bet on X because [this data / this customer learning / this new technology]." A bet with no nameable insight behind it is the tell of an opinion-driven strategy.
- **Use DHM to kill weak bets early.** A bet that fails "hard-to-copy" or "margin-enhancing" gets downgraded before it consumes a quarter of team time.
- **Assign problems, not features, at the objective layer.** Convert each surviving bet into an outcome objective and hand the _problem_ (plus context) to a team — the seam into the operating model (`empowered-teams.md`).

## Tells and anti-patterns

- **Stack collapse** — "strategy" and "roadmap" are the same document. No layer between the destination and the dated work; nothing to derive the roadmap _from_. (Full treatment in `strategy-vs-roadmap.md`.)
- **Vision-as-strategy** — an inspiring multi-year picture presented as the strategy, with no account of which problems to solve now or why. Destination, no path.
- **Roadmap-as-strategy** — a feature sequence presented as the strategy, with no destination and no insight. Path, no reason.
- **Insight-free strategy** — focus and bets exist but rest on no data, customer learning, or new technology — just reshuffled stakeholder opinion. Driven by the request queue, not by insight toward the vision.
- **DHM-incomplete bets** — bets chosen only for delight, with no durable advantage (trivially copied) or no business model (loses money). Delight alone is not a strategy.
- **Objectives stated as outputs** — the bets layer lists features-with-dates instead of outcomes-to-move, re-importing the build trap one rung up.

## Good vs bad: scoring a strategy stack

| Layer / property | Healthy stack | Broken stack |
| --- | --- | --- |
| Vision | Stable multi-year destination tied to customer benefit | Missing, or rewritten every quarter |
| Strategy | A focused, insight-backed choice of which problems to solve now | A reshuffled stakeholder request queue, or absent |
| Insight | Each bet names its data / customer / technology source | Bets rest on opinion; no insight cited |
| Focus | Names what it will _not_ do | Tries to do everything; effort diluted |
| Bets / objectives | Outcomes assigned to teams with context | Features-with-dates handed down |
| Roadmap | Derived by the team, traces up to an objective | _Is_ the strategy; nothing to trace to |
| DHM quality | Best bets hit 2–3 of delight / hard-to-copy / margin | Bets deliver copyable or unfunded delight |
| Direction of build | Top-down to plan, traceable bottom-up to audit | Bottom-up rationalization of a pre-set roadmap |

The fastest single test: **pick a roadmap item at random and walk it up the stack.** If you can name its objective, the bet that objective serves, the insight the bet rests on, and the slice of vision it advances — the stack is intact. If the walk dead-ends, you've found exactly where the stack collapses.

## Labeled-uncertain claims

- The SVPG four-part structure of strategy (**Focus → Leverage Insights → Convert Insights into Action → Manage the Work**) and the three insight sources (data, customers, new technology) are attributed to Marty C.'s SVPG _Product Strategy_ series and _Changing How You Decide Which Problems To Solve_. The svpg.com pages returned HTTP 403 to direct fetch this session; the framing and the quoted phrases ("deciding what few things you really need to do," "insights come from study and thought," "without resorting to micro-management") were corroborated across multiple independent secondary captures of those SVPG pages. Confirm exact wording against svpg.com before quoting verbatim.
- The vision/strategy definitions and horizons (2–5 yrs vision, "living thing" strategy, "brass tacks," "how in the world are we going to do that") are attributed to Marty C.'s _Vision vs. Strategy_ and his Mind the Product / Product Experience interview; the interview quotes were fetched and verified this session, the SVPG page via secondary capture.
- The DHM definition, the "hypotheses" framing, the "two or three objectives with a single strategy" line, and the Helmer seven-powers mapping are from Gibson Biddle's Medium essays (_The DHM Model_ and _From DHM to Product Strategy_), fetched and verified this session. The specific Netflix metrics Biddle cites (e.g. cancel-rate and recommendation-share figures) are _his_ illustrative claims about Netflix and are reproduced as such, not independently audited here.
