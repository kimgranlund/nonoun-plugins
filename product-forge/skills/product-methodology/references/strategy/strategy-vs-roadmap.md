---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Shreyas D., 'Good Product Strategy, Bad Product Strategy', Medium (medium.com/@shreyashere/good-product-strategy-bad-product-strategy-826cdfe74818)"
  - "Shreyas D. (2021), 'Stages of strategy maturity' (thread, tweet 12/), x.com/shreyas/status/1399048843270901760"
  - "Shreyas D., 'Mission: Why / Vision: What / Strategy: How / Roadmap: When', x.com/shreyas/status/1460848932116844550"
  - "Shreyas D. on Lenny's Podcast, ep. 3: 'why most execution problems are strategy problems', lennysnewsletter.com/p/episode-3-shreyas-doshi"
  - "Shreyas D. on X: 'Most Execution problems are really 1) Strategy problems, or 2) Interpersonal problems, or 3) Culture problems', x.com/shreyas/status/1316573473934696449"
  - "Richard R., *Good Strategy/Bad Strategy: The Difference and Why It Matters* (Crown Business, 2011)"
---

# A Roadmap Is Not a Strategy

A roadmap, an OKR list, and a feature backlog are all answers to the question _what will we do, and when?_ A strategy answers a different question: _why will doing that win, given the obstacle in front of us?_ The first set is a plan; only the second is a strategy. This reference is the working method for telling them apart — what a real strategy contains that a plan never does, why the substitution happens, and Shreyas D.'s load-bearing reframe that **most of what we file under "execution failure" is actually strategy failure leaking downward.** It pairs with `rumelt-kernel.md` (the underlying theory of good vs bad strategy) and applies it to the artifacts product teams actually ship.

> Shreyas D.'s mnemonic for keeping the layers distinct, restated verbatim: **"Mission: Why · Vision: What · Strategy: How · Segmentation: Who · Positioning: Where · Roadmap: When."** A roadmap lives at _when_. A strategy lives at _how we win_. Confusing the two is the single most common product-strategy defect.

## The core idea: a plan tells you what; a strategy tells you why it works

Richard R.'s distinction (see `rumelt-kernel.md`) is that a strategy is _a way through a difficulty_ — it must name an obstacle and a coherent approach to overcoming it. A plan assumes the path is already clear and just schedules the steps. The tell is brutal and fast: **a strategy can be wrong; a plan cannot.** A roadmap that says "ship onboarding redesign in Q2, billing v2 in Q3" cannot be falsified — it is a list of intentions, and intentions are always achievable on paper. A strategy that says "we win by becoming the obviously-safe default for regulated buyers, so we concentrate on security surface and defer IC features" _can_ be proven wrong by reality. That falsifiability is the signature that you are holding a strategy and not a calendar.

Three artifacts routinely impersonate a strategy. None of them is one:

- **A roadmap** is a sequence of outputs over time. It encodes _order_, not _why this order beats the obstacle_. A roadmap is a downstream consequence of a strategy, not a substitute for it — you cannot derive the roadmap correctly until the strategy has named what to concentrate on and what to refuse.
- **An OKR list** is a set of targets. "Grow activation 20%, grow ARR 3x" states desired outcomes but not the _approach_ that makes those outcomes reachable. Richard R.'s name for this exact error is **mistaking goals for strategy**: a target is what you want, not how you will get it against resistance.
- **A feature list / backlog** is an inventory of solutions. It presupposes that the problems are settled and the only question is build order. It is the build trap in document form (see `build-trap.md`): outputs with no diagnosis of the obstacle they are meant to overcome.

The unifying defect across all three: they **skip the diagnosis.** They begin at "here is what we'll do" without ever establishing "here is the specific reason winning is hard, and here is our chosen way through." A document that never names an obstacle is, by Richard R.'s definition, not evaluable — and a thing you cannot evaluate is not a strategy.

## Shreyas D.: most execution problems are strategy problems

Shreyas D.'s most-cited reframe is a diagnostic lens for product orgs that feel chronically stuck. His exact framing: **"Most Execution problems are really 1) Strategy problems, or 2) Interpersonal problems, or 3) Culture problems. Good leaders execute well because they understand this. They fix the root problem. Bad leaders struggle because they are always applying band-aids."**

The mechanism: when a team has no real strategy — only a roadmap — local execution decisions have nothing to align to. Every prioritization call, every scope cut, every "should we add this field" becomes an unanchored argument, because there is no shared answer to _what are we concentrating on and what are we refusing_. The symptoms present as execution problems ("we keep missing dates," "the teams are pulling in different directions," "we ship constantly but nothing moves"), so leaders reach for execution band-aids: more standups, tighter tickets, a new planning tool, a reorg. The band-aid never holds, because the wound is one layer up.

The working diagnostic, applied to any "we have an execution problem" complaint:

1. **Is there a strategy to execute against at all?** Ask the team to state, in one sentence, the obstacle they are overcoming and the approach they chose. If they produce a roadmap or a goal instead, there is no strategy — and no roadmap-tuning will fix a missing strategy.
2. **If a strategy exists, is it _articulated_?** Shreyas D.'s stages of strategy maturity (below) make "we have a strategy but it isn't articulated" a distinct, common failure: the strategy lives in one leader's head, so teams execute against their own private guesses and diverge.
3. **Only if both pass is it really execution.** Genuine execution problems — a flaky deploy pipeline, an under-resourced team — exist, but they are the minority. Reach for them last, after ruling out the strategy and articulation gaps above.

## Shreyas D.'s stages of strategy maturity

Shreyas D.'s verbatim ladder is the fastest way to locate _which_ failure a given org has, because the fix is different at each rung:

```text
1: We don't need a strategy
2: We need a strategy but don't have one
3: We have a strategy but it isn't articulated
4: We have an articulated strategy but execution is disconnected
5: We are cohesively executing on a known & rigorous strategy
```

The two rungs product teams misdiagnose most:

- **Rung 3 (unarticulated) masquerades as rung 5.** Leadership "has a strategy" but it was never written down sharply enough to align on, so each team substitutes its own. This reads on the ground as an _execution_ problem (teams diverge, priorities clash) but the fix is articulation, not coordination tooling.
- **Rung 4 (disconnected) is where roadmaps get blamed.** There _is_ an articulated strategy, but the roadmap was built without tracing each item back to it, so the plan and the strategy have quietly decoupled. The fix is to re-derive the roadmap _from_ the strategy — every roadmap item should name the strategic bet it advances — not to rewrite the strategy.

A useful caution Shreyas D. gives upstream of the whole ladder: **do not begin strategy work by writing the mission and vision first and deriving a strategy from them.** Mission and vision should be _outputs_ of rigorous customer and market understanding, not the seed you reason forward from; treating them as the starting point is, in his telling, a reason so many "strategy" docs come out hollow. (See the worked contrast and the production caveat below — exact phrasing of this point is attributed to his LinkedIn writing.)

## How to apply it: pressure-test the document in front of you

Given any artifact labeled "strategy," run these passes in order. The first failure is usually disqualifying.

1. **The obstacle pass.** Find the sentence that names what makes winning _hard_ — the specific structural reality (a shifting buyer, a distribution choke point, a capability gap). If there is no such sentence, you have a plan. Stop; everything below is moot.
2. **The "what we won't do" pass.** A strategy concentrates force, so it always has a costly refusal baked in. Try to state what this strategy explicitly _declines_ to pursue. If it refuses nothing — if it tries to serve every segment and chase every opportunity — it is a wish list. (Shreyas D.'s tell: bad strategy "eschews trade-offs and tries to be 'all things to all people.'")
3. **The falsifiability pass.** Ask "what would have to be true in reality for this to be wrong?" A real strategy answers cleanly (e.g. "if regulated buyers still don't convert after the security bundle, the diagnosis was wrong"). A plan or goal list cannot be wrong, only unfinished — that is the tell.
4. **The derivation pass.** For each roadmap item / OKR / feature, ask "which strategic bet does this advance, and how do we know?" If items can't be traced back to a bet, the plan and strategy are decoupled (rung 4) — or there was never a strategy and the roadmap _is_ the "strategy" (the build trap).

## Key moves

- **Demand the diagnosis before the plan.** When handed a roadmap and asked to "review the strategy," refuse to evaluate order until the obstacle is named. There is nothing to review in a plan that has skipped its own premise.
- **Re-derive, don't re-decorate.** When strategy and roadmap have decoupled (rung 4), fix it by tracing each roadmap item back to a bet, cutting the ones that trace to nothing — not by adding more strategic-sounding language on top.
- **Route execution complaints up one layer first.** Treat "we have an execution problem" as a hypothesis to disprove: check for a missing or unarticulated strategy before investing in execution machinery.
- **Separate the six layers explicitly.** Use Shreyas D.'s mnemonic to label which question a sentence is answering. A document that only ever answers _what_ and _when_ has no _how-we-win_ and is therefore not a strategy, however thorough its calendar.

## Tells and anti-patterns

These are pattern-matchable smells that a "strategy" is actually a plan. Drawn from Shreyas D.'s _Good Product Strategy, Bad Product Strategy_ (which explicitly synthesizes Richard R.) and the Richard R. hallmarks in `rumelt-kernel.md`:

- **The roadmap-as-strategy swap** — the "strategy" is a Gantt chart or a quarter-by-quarter feature sequence. Order without a why.
- **The OKR-list swap** — a stack of target metrics with no approach. Goals mistaken for strategy.
- **No trade-offs / all-things-to-all-people** — the strategy "either ignores customer segmentation or attempts to cater to all customer segments" and "eschews trade-offs." A strategy that refuses nothing has not chosen.
- **Rah-Rah / visionary language** — it "tries to sound visionary and ambitious, usually by employing Rah-Rah language" and "often reads like a prayer." Inspiration substituting for an approach.
- **Fluffy or abstruse** — it "is fluffy or abstruse," impressive-sounding sentences that decode to a truism (Richard R.'s "fluff").
- **Optimizes for near-term consensus** — it "optimizes for near-term consensus" rather than making the hard, possibly-unpopular concentration call. Agreement is not strategy.
- **Mission/vision-first derivation** — it was reasoned forward from an aspirational mission statement instead of backward from customer/market reality, producing eloquence without a diagnosis.

## Good vs bad: scoring a "strategy" doc

Use this when grading any artifact that claims to be a product strategy. A bad cell on the first three rows is disqualifying — these are not averaged.

| Dimension | Real strategy | A plan wearing the label |
| --- | --- | --- |
| Names an obstacle | States the specific reason winning is hard | Jumps straight to what we'll do / ship |
| Has an approach (the "how we win") | A chosen way through that rules options in _and out_ | A sequence of outputs, or a list of target metrics |
| Falsifiable | Reality could prove it wrong; it's a bet | Cannot be wrong, only incomplete |
| Trade-offs | A clear, costly "no"; serves a chosen segment | All-things-to-all-people; serves everyone |
| Roadmap relationship | The roadmap is _derived from_ the strategy | The roadmap _is_ the strategy |
| Language | Plain; survives "restate it simply" | Rah-Rah, visionary, fluffy, prayer-like |
| Failure when absent | — | Chronic "execution problems" no tooling fixes |

The fastest single test, when time is short: **ask what the strategy refuses to do.** A plan refuses nothing — it is a list, and a list never has to choose. A strategy's refusal is the shadow cast by its concentration; if there's no shadow, there's no concentration, and without concentration there is no strategy.

## Labeled-uncertain claims

- The Shreyas D. tells of bad product strategy ("eschews trade-offs and tries to be 'all things to all people,'" "Rah-Rah language," "often reads like a prayer," "is fluffy or abstruse," "optimizes for near-term consensus") are quoted from his Medium essay _Good Product Strategy, Bad Product Strategy_, which itself names Richard R. as a source. Verified against the article text in this session.
- The **"mission and vision should be outputs, not the starting point of strategy work"** point and the claim that this is **why a majority of product-strategy docs are not real strategies** are attributed to Shreyas D.'s LinkedIn post ("Please do not begin any product strategy work by first writing down your mission and vision…"), surfaced via search snippet and not fetched in full this session — treat the _claim_ as well-supported by his body of work but confirm exact wording against the post before quoting verbatim.
- The "stages of strategy maturity" and "Mission: Why / Vision: What / …" lists are verbatim from Shreyas D.'s public X threads (tweet 12/ of his frameworks thread, and the standalone mnemonic tweet); the execution-problems quote is verbatim from his X post. These were corroborated across multiple secondary captures of the same threads.
