---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Richard R., *Good Strategy/Bad Strategy: The Difference and Why It Matters* (Crown Business, 2011)."
  - "Richard R., “The perils of bad strategy,” McKinsey Quarterly (June 2011)."
---

## Why this file exists

This is the working method for writing and scoring a product strategy. It encodes Richard R.'s _Good Strategy/Bad Strategy_ (2011) as a procedure, not a précis: how to build the kernel, how to spot the four tells of bad strategy on sight, and what separates a passing strategy from a failing one. When product-forge evaluates a strategy doc, this is the spine the critics measure against. Richard R.'s central claim is blunt and load-bearing: most documents that call themselves "strategy" are not strategy at all — they are a mash-up of ambitions, vision statements, and financial targets that "skip over the annoying fact" of the actual obstacle.

## The kernel: the only three parts that matter

Richard R. strips strategy down to a "kernel" of three elements. Everything else (slides, OKRs, vision posters) is decoration on top of these three, and decoration without a kernel is bad strategy.

1. **Diagnosis** — a definition of the nature of the challenge. It "simplifies the often overwhelming complexity of reality by identifying certain aspects of the situation as critical." A diagnosis is a judgment call: it names what is really going on and, by implication, what to ignore. It often replaces a fuzzy problem with a metaphor or analogy that makes the structure of the situation graspable.
2. **Guiding policy** — the overall approach chosen to cope with or overcome the obstacles named in the diagnosis. It is not a goal and not a plan; it is a "method of grappling with the situation" that rules whole classes of action in and out. A good guiding policy "draws upon sources of power" and creates advantage by concentration and coherence.
3. **Coherent actions** — the coordinated steps, resource commitments, and policies that carry out the guiding policy. The word that earns its keep is _coherent_: the actions must be "coordinated and support each other," not a list of independently sensible initiatives that fight for the same resources or pull in different directions.

The kernel is causal and ordered. Diagnosis constrains the guiding policy; the guiding policy constrains the coherent actions. If you can reorder the three without anything breaking, you don't have a kernel — you have three disconnected sections.

## Sources of power and leverage

Richard R.'s guiding policy is only good if it "draws upon some source of power." A guiding policy that applies effort evenly across everything is just a budget. Good strategy concentrates force where the situation is most "pivotal." Two of Richard R.'s named mechanisms are the ones product strategy abuses most by omission:

- **Leverage** — anticipation plus concentration on a pivotal point, so that a focused application of resources produces an outsized result. Strategy finds the one place where pushing hardest pays off, rather than pushing everywhere a little.
- **Proximate objectives** — a goal "close enough at hand to be feasible." Good strategy sets a target the organisation can actually hit with the resources and knowledge it has, which converts ambiguity into a solvable problem. A proximate objective is the bridge between an abstract guiding policy and concrete action; a strategy whose nearest objective is "win the market" has skipped this rung.

When scoring, treat "what is the source of power?" as a direct question to the strategy. If the guiding policy names no concentration, no leverage point, and no feasible near-term objective, the kernel is hollow even if all three sections are present.

## The four tells of bad strategy

Richard R. names four hallmarks. They are pattern-matchable, which makes them the front line of any strategy review. The first one, in particular, is mechanizable as a lint.

- **Fluff** — "a form of gibberish masquerading as strategic concepts," built from inflated words, abstruse jargon, and apparent depth. His canonical example: a bank describing its strategy as "customer-centric intermediation," which decodes to "we are a bank." Tell: if you can delete a sentence and lose no information, or restate it in plain words and reveal a truism, it's fluff.
- **Failure to face the challenge** — strategy is "a way through a difficulty, an approach to overcoming an obstacle." If the document never names the actual obstacle, there is nothing for the strategy to be a response to, and "you cannot evaluate it or improve it." Tell: scan for the diagnosis; if it's missing, vague, or flattering, the rest is unanchored.
- **Mistaking goals for strategy** — a strategy that is just a restatement of desired outcomes ("grow 20%," "be the market leader") with no account of _how_. "If you fail to identify and analyze the obstacles, you don't have a strategy. Instead, you have a stretch goal or a budget or a list of things you wish would happen." Tell: count the verbs of method versus the verbs of aspiration.
- **Bad strategic objectives** — objectives that fail to address critical issues, or a "dog's dinner" long list of "things to do" mislabeled as strategies (Richard R. calls these "blue-sky objectives" and "dog's dinner" objectives). A scramble of 20 priorities is the absence of priority. Tell: a long undifferentiated list, or objectives that restate the mission rather than confront the obstacle.

A single tell is enough to fail a strategy. Bad strategy is not the absence of strategy; it is an active substitution of these patterns for the hard work of the kernel.

## Applying it to a product strategy

A product strategy passes through the kernel like this. The diagnosis names the specific structural reality the product faces — a shifting buyer, a distribution choke point, a wedge a competitor opened, a capability the org lacks — not "users want a better experience." The guiding policy is the chosen wedge: where this product concentrates to win, and therefore what it refuses to do. The coherent actions are the roadmap bets, sequencing, and resourcing that all reinforce that wedge.

The most common product-strategy failure is the build trap dressed as strategy: a roadmap (a list of outputs) presented as the strategy, with no diagnosis of the obstacle the roadmap is supposed to overcome. That is "mistaking goals for strategy" plus "bad strategic objectives" at once. The second most common is the vision-as-strategy swap — an inspiring end-state with no account of the barrier between here and there.

A concrete worked contrast, in the kernel's own shape:

```text
BAD (goals-as-strategy, no diagnosis):
  "Our strategy is to become the #1 collaboration tool for engineering teams
   by delivering a world-class, AI-powered, customer-centric experience and
   growing ARR 3x in 18 months."
  -> No obstacle named. "World-class / AI-powered / customer-centric" = fluff.
     "Grow 3x" = a goal, not a method. Nothing here could be wrong, so nothing
     here can be evaluated.

GOOD (kernel intact):
  Diagnosis:      "Adoption stalls because we sell to individual engineers, but
                   the buying decision sits with platform leads who evaluate on
                   security and admin control — a surface we under-built while
                   chasing IC delight."
  Guiding policy: "Win the platform lead. Concentrate the next two quarters on
                   becoming the obviously-safe default for regulated orgs, and
                   explicitly defer net-new IC features."
  Coherent action:"(1) Ship SSO + audit log + role admin as one bundle.
                   (2) Re-aim sales motion at platform leads, not ICs.
                   (3) Reprice to a per-seat floor that platform leads expect.
                   (4) Freeze the IC-feature backlog this half."
  Source of power: concentration on the pivotal buyer; a feasible proximate
                   objective ("be the safe default for regulated orgs") rather
                   than the abstract "be #1."
```

The good version is falsifiable — if platform leads still don't convert after the bundle ships, the diagnosis was wrong, and you can say so. That testability is the signature of a real strategy.

## Scoring rubric: good vs. bad at a glance

Use this when grading a product strategy. Bad on any single row is disqualifying, not averaged away.

| Dimension | Good strategy | Bad strategy |
| --- | --- | --- |
| Diagnosis | Names a specific, structural obstacle; simplifies to what's critical | Absent, generic, or flattering ("users want more value") |
| Guiding policy | A chosen approach that rules options in _and out_; draws on a source of power | A goal or aspiration restated; tries to do everything |
| Coherent actions | Mutually reinforcing; concentrated; sequenced | A laundry list; initiatives compete for the same resources |
| Focus | Concentrates force on a pivotal point; says no | Spreads effort evenly; 15+ undifferentiated priorities |
| Proximate objective | Feasible near-term target the org can actually hit | "Win the market" with no nearer rung |
| Falsifiability | Could be proven wrong by reality; testable | Cannot be wrong, therefore cannot be evaluated |
| Language | Plain; survives the "restate it simply" test | Fluff, jargon, buzzwords masking absence of substance |

The fastest single test, when time is short: try to state what the strategy refuses to do. A good strategy has a clear, costly "no" baked into the guiding policy. A bad strategy refuses nothing, because a list of wishes never has to choose.

## One labeled caveat

The exact phrasings quoted above ("simplifies the often overwhelming complexity of reality," "a form of gibberish masquerading as strategic concepts," "a stretch goal or a budget or a list of things you wish would happen," "customer-centric intermediation," "dog's dinner") are attributed to Richard R.'s _Good Strategy/Bad Strategy_ (2011) and his 2011 McKinsey Quarterly article "The perils of bad strategy," cross-checked against multiple secondary summaries of the book rather than against the page-numbered print edition in this session. The concepts (kernel, four hallmarks, sources of power, proximate objectives, leverage) are unambiguous across every source; if a verbatim quote is needed for publication, confirm wording and page against the print edition.
