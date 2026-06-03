---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Jules Walter, \"How to develop product sense.\" Lenny's Newsletter, 2022. https://www.lennysnewsletter.com/p/product-sense"
  - "Shreyas D., \"PM Career Skills Map\" (Analytical / Execution / Product sense), thread. x.com/shreyas/status/1264621650663727104 (May 24, 2020)."
  - "Shreyas D., \"Key elements of Product Sense.\" x.com/shreyas/status/1270799017417437184 (June 2020)."
  - "Shreyas D., \"World-class Product Sense in Practice\" (course overview). https://maven.com/shreyas-doshi/product-sense"
---

# Product sense, execution sense, analytical sense — and how to grow taste

"Product sense" is treated, wrongly, as innate taste you either have or don't. The practitioners who teach it treat it as a **learnable skill** — pattern recognition built deliberately from exposure, feedback, and reflection, like any craft. This file covers the three "senses" Shreyas D. maps for a PM, Jules Walter's definition of product sense and his concrete program for developing it, and why this matters for prioritization: the judgment that tells a genuine Leverage task from comfortable Overhead (see `doshi-lno.md`) _is_ product sense in action. Where a specific verbatim definition isn't canonical, it is labeled below.

## The three senses (Shreyas D.'s PM skills map)

Shreyas D. maps a PM's core capability into three "senses," and observes that most PMs have a **natural bias toward one** — you must lean on your strength without neglecting the other two.

- **Product sense** — the ability to consistently make product decisions that have the intended effect on users. Shreyas D. frames it as the differentiator that takes the front seat as you grow more senior; the other two are necessary but not what separates great PMs.
- **Execution sense** — aligning people toward an objective and orchestrating complex, cross-functional projects to ship. The level most ICs default to and are measured on.
- **Analytical sense** — framing the right questions, evaluating a problem from multiple angles, simulating outcomes, and using data well.

> Single-source / paraphrase label: this three-sense map and the "natural bias toward one" observation come from Shreyas D.'s public threads and course materials (cited above), accessed here via secondary summaries because the primary posts sit behind an authenticated platform. Treat the _structure_ (three senses; product sense as the senior differentiator) as well-attested across his body of work, but treat any exact verbatim definition as paraphrase, not canonical wording.

Shreyas D. further decomposes **product sense itself** into a small set of elements — commonly summarized as **empathy, domain knowledge, and creativity** — i.e., understanding users deeply, knowing the space, and generating non-obvious solutions. _Single-source label:_ the specific three-element breakdown is attributed to Shreyas D.'s "key elements of product sense" post; the wording of the elements varies across secondary retellings, so treat the trio as a faithful paraphrase rather than a fixed quotation.

## Jules Walter: product sense is a learnable skill

The most cited primary treatment of _developing_ product sense is Jules Walter's essay (Slack and YouTube PM, in Lenny's Newsletter). His definition: product sense is **"the skill of consistently being able to craft products (or make changes to existing products) that have the intended impact on their users."** Two words do the work — _consistently_ (not a lucky hit) and _intended impact_ (measured against a goal, not aesthetic preference).

His central claim is explicit and contrarian: **"product sense is not something you need to be born with. It's a learned skill, just like any other PM skill."** He allows natural variation in starting ability but insists you don't need exceptional talent — only deliberate practice. Walter grounds product sense in **two foundational sub-skills**:

- **Empathy** — discovering meaningful, real user needs (not imagined ones).
- **Creativity** — generating solutions that actually address those needs.

Note the convergence with Shreyas D.: both root product sense in empathy + creativity (Shreyas D. adds domain knowledge as a third leg). The agreement across two independent practitioners is itself a signal that this is the stable core.

## How to know you're getting better

Walter offers observable signals that product sense is improving — useful because "taste" otherwise feels unmeasurable. You're getting better when you:

- notice subtle product details you used to miss;
- anticipate non-obvious user problems _before_ a product review surfaces them;
- form higher-quality hypotheses under ambiguity;
- contribute insights your teammates didn't have;
- predict a feature's effect on metrics more accurately;
- get unprompted feedback (e.g., from design partners) that you caught something others didn't.

These are leading indicators of judgment, not lagging outcome metrics — which is what makes them usable as a personal feedback loop while the skill is still forming.

## The practice program (deliberate, not osmotic)

Walter's contribution is that he makes "develop taste" concrete — four repeatable practices, two per sub-skill, with rough cadences:

```text
BUILD EMPATHY (discover real needs)
  1. Observe users directly.
     Attend user-research sessions ~2-4x/month. Watch faces and reactions; ask
     open-ended questions about what confused, excited, or frustrated them, and why.
     Goal: replace your imagined user with the actual one.
  2. Deconstruct everyday products.
     Spend ~1-2 hours/month trying new apps and pulling them apart — compare across
     onboarding, core flow, aesthetics, and the decisions behind them. Ask "why did
     they build it this way, and what were they optimizing for?"

IMPROVE CREATIVITY (generate solutions that fit)
  3. Learn from great product thinkers.
     Sit in on product reviews led by people whose judgment you respect. Take notes on
     the PATTERNS in their feedback and the decision principles they apply repeatedly —
     you're reverse-engineering a mental model, not memorizing verdicts.
  4. Stay curious about technology trends.
     Track what's newly possible (developer conferences, analysts, emerging capabilities)
     across macro shifts (AI, AR/VR, regulation) and micro advances — new capability is
     where non-obvious solutions come from.
```

The discipline that makes this work is **feedback and reflection**, not exposure alone. Watching a review without extracting the principle, or trying an app without articulating _why_ it works, builds hours but not sense. The program is "deliberate practice" in the technical sense: targeted reps, immediate feedback, reflection — which is exactly why it transfers from people who are "naturals" to people who simply put in the structured reps.

## Why this lives next to prioritization

Product sense is not a soft adjacency to prioritization — it is the faculty prioritization frameworks _can't_ supply. RICE and ICE rank items but can't tell you whether your Impact estimate is wise; LNO sorts effort by leverage but relies on you to recognize which task is genuinely Leverage versus Overhead dressed up as Leverage (see `doshi-lno.md`). Each of those judgments — _is this impact real, is this task high-leverage, is this "execution problem" actually a strategy problem_ — is product/analytical sense doing its job. The practical consequence: **a junior PM's mis-prioritization is usually a sense gap, not a process gap**, and it closes with the same deliberate practice above — better to coach the judgment than to add another scoring column. Taste is the input the frameworks assume and never provide.

## The "am I training taste, or just logging hours?" test

```text
Pressure-test your own development of product sense:

  - Real users, not imagined ones?  Am I deciding from observed user behavior, or from
    a persona in my head? If I can't recall the last time I watched a real user, my
    empathy input is stale.
  - Extracting principles, not verdicts?  When I watch a strong PM review work, am I
    capturing the reusable DECISION RULE, or just remembering what they approved?
  - Feedback loop closed?  Do I check my predictions (impact on metrics, where users
    will struggle) against what actually happened? Unchecked predictions don't build sense.
  - Observable improvement?  Against Walter's signals — noticing subtler details,
    anticipating non-obvious problems — am I measurably better than six months ago?
  - Intended impact, not preference?  Am I judging a decision by its effect on users
    and the goal, or by what I personally find elegant? Taste anchored to impact is
    product sense; taste anchored to preference is just opinion.
```

Failure modes to watch: mistaking _exposure_ for _practice_ (hours logged, no reflection); cultivating opinions about elegance unanchored to user impact; never closing the prediction loop, so the same misjudgments repeat; and treating product sense as innate — which removes the incentive to train it and is, per both Walter and Shreyas D., simply wrong.
