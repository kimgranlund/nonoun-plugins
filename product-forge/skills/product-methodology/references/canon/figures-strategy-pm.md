---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Eight widely recognized product / strategy / experimentation practitioners (the lenses the product-forge council borrows). Each figure's real name, books, and canonical sources are recorded in the git-ignored `agents/.name-map.md` (kept out of the repo by design); this file keeps only the obscured `First L.` display and the operating lens."
---

## Why this file exists

These are the eight figures whose lenses the product-forge critic council borrows. Each capsule gives the one idea that figure is uniquely right about and — most important for a critic — the distinct angle of attack that figure brings to a product artifact. Identities are obscured to `First L.`; the real names and the canonical sources to cite live in the git-ignored `agents/.name-map.md` (kept out of the repo by design). Read these as adversarial roles, not as a hall of fame: each figure is the person in the room who will reliably catch one specific class of mistake the others miss. Where two figures overlap (and several do), the capsules say where the line is, so a review doesn't double-count.

## Marty C. — the product operating model and the four risks

**Core idea.** Great products come from empowered, durable, cross-functional teams given problems to solve, not features to build — and the team's real job is _discovery_ (figuring out what's worth building), with delivery as the output. Before committing to build anything, a team must de-risk four things: **value** (will anyone want it / buy it?), **usability** (can users figure out how to use it?), **feasibility** (can engineering build it with the time, skills, and tech available?), and **business viability** (does the rest of the business — sales, marketing, finance, legal, compliance, brand — support it?). Marty C.'s recurring line is that the two biggest, most-missed risks are value and viability, because teams over-index on usability and feasibility.

**Distinct critical lens.** _The empowerment-and-risk auditor._ Marty C. attacks the operating context: Is this a feature team taking orders, or an empowered team solving a problem? Which of the four risks did you actually test before building, and which did you assume away? He is the critic who catches "you validated that engineers can build it and that it's usable, but you never validated that anyone wants it or that the business can sell it." If the artifact is a roadmap of features handed down from stakeholders, Marty C.'s verdict is _feature factory_ regardless of how polished it looks.

## Teresa T. — continuous discovery and the opportunity solution tree

**Core idea.** Discovery is not a phase; it is a weekly habit. Teresa T.'s keystone practice is teams "interviewing customers at least weekly" while running small experiments, all anchored to a clear desired **outcome**. Her signature artifact is the **opportunity solution tree (OST)**: a visual that hangs the desired outcome at the root, branches into customer **opportunities** (unmet needs, pains, desires discovered through interviews), then into **solutions** for each chosen opportunity, then into **experiments** ("assumption tests") that validate the solutions. The tree forces a team to compare _opportunities_ against each other before falling in love with a solution, and keeps business value and customer value visibly connected.

**Distinct critical lens.** _The discovery-rigor inspector._ Teresa T. attacks the gap between opinion and evidence: When did you last talk to a customer? Is this "opportunity" an actual unmet need you heard in an interview, or a solution in disguise? Did you generate and compare multiple opportunities, or jump to the first idea? Did you test the _assumptions_ behind a solution, or just ship it? She is the critic who catches a roadmap built from stakeholder opinion and HiPPO instead of continuous customer contact — and who catches "opportunities" that are really pre-baked features wearing a problem costume.

## Melissa P. — escaping the build trap (outcomes over outputs)

**Core idea.** The **build trap** is when an organisation measures success by _outputs_ (features shipped, roadmap items completed) instead of _outcomes_ (value created for customers and the business). Trapped orgs become feature factories that ship to a schedule rather than to a need. The escape is to manage toward outcomes and to run a repeatable problem-solving loop — Melissa P.'s **Product Kata** (adapted from Toyota's improvement kata): set a goal, understand the current condition, define a target condition, then iterate experiments toward it, "doing just enough to get to the goal." Organisationally, escaping the trap requires strategy, roles, and incentives that reward outcomes.

**Distinct critical lens.** _The outcomes-vs-outputs prosecutor._ Melissa P. attacks the success metric itself: Is this initiative defined by what gets shipped or by what changes for the user and the business? What outcome is this feature accountable to, and how will you know if it worked? She is the critic who catches a "strategy" that is actually a feature list with dates, and a team congratulating itself on velocity while the business metric flatlines. Her line sharpens Marty C.'s: where Marty C. asks whether the team is empowered, Melissa P. asks whether the work is measured by impact at all.

## Clayton C. — jobs to be done

**Core idea.** Customers don't buy products; they **hire** them to make progress in a particular circumstance — to get a "job" done. A job has functional, social, and emotional dimensions, and the unit of analysis is the _circumstance of struggle_, not the customer demographic or the product category. The canonical illustration is the McDonald's milkshake: segmenting by demographics and "improving" the shake did nothing, because the real job (a thick, one-handed, long-lasting companion for a boring morning commute) only became visible once researchers asked what customers were _hiring the shake to do_. Understand the job and innovation stops being luck.

**Distinct critical lens.** _The demand-side interrogator._ Clayton C. attacks the framing of the customer: What job is this product hired for, in what circumstance? What does the customer "fire" to hire it? Are you innovating on attributes nobody is hiring for? He is the critic who catches a feature justified by a persona's demographics rather than by a real struggling moment, and a roadmap that improves the product along dimensions no job actually demands. His lens complements Teresa T.'s: Teresa T. supplies the _method_ (weekly interviews, the opportunity space); Clayton C. supplies the _unit_ (the job, the circumstance) that those interviews should be excavating.

## Richard R. — the strategy kernel

**Core idea.** Real strategy is a **kernel** of three linked parts: a **diagnosis** that names the crux of the challenge, a **guiding policy** that chooses an overall approach to that challenge (and rules options out), and **coherent actions** that reinforce each other in carrying it out. Most "strategy" is **bad strategy**, identifiable by four tells: **fluff** (jargon masking emptiness), **failure to face the challenge** (no diagnosis, so nothing to evaluate), **mistaking goals for strategy** (aspirations restated as a plan), and **bad strategic objectives** (a dog's-dinner list of priorities). Good strategy concentrates force on a pivotal point and "draws upon sources of power" such as leverage and feasible proximate objectives.

**Working method.** Applied as a working method in the sibling reference `../strategy/strategy-kernel.md`.

**Distinct critical lens.** _The strategy-integrity judge._ Richard R. attacks the document calling itself a strategy: Where is the diagnosis? Does the guiding policy actually rule anything _out_, or does it try to do everything? Do the actions cohere, or compete? Can this strategy be wrong — is it falsifiable? He is the critic who catches a vision statement or a revenue target posing as strategy, and the laundry list of fifteen co-equal priorities that proves no priority was set. A single tell from him is disqualifying.

## April D. — positioning

**Core idea.** Positioning is "the context that makes your product obviously awesome" to a well-defined set of customers — and it is deliberate, not a default you inherit from however the product was first built. April D.'s method has five interlocking components: **competitive alternatives** (what customers would do if you didn't exist — often a spreadsheet or the status quo, not a named rival), **unique attributes** (what you have that the alternatives don't), **value** (the benefit those attributes uniquely enable, and the proof of it), **target market characteristics** (the buyers who care most about that value), and **market category** (the frame of reference that primes customers to understand and want it), with **relevant trends** as a careful sixth lever. The components flow from each other: value depends on unique attributes, which are only unique relative to the competitive alternatives.

**Distinct critical lens.** _The frame-of-reference challenger._ April D. attacks the context the product is presented in: What does the customer compare this to — and is that the comparison that makes your strengths obvious, or one that buries them? What market category are you implicitly competing in, and is it the right one? Have you confused _features_ with _value_? She is the critic who catches a brilliant product positioned in a category where its differentiators look like table stakes, and a value claim untethered from any genuinely unique attribute. Her lens is the market-facing complement to Clayton C.'s demand-side job: the job tells you what customers want; positioning tells you the frame in which to make your answer obvious.

## Shreyas D. — leverage, the three levels, and product sense

**Core idea.** Two operating frameworks. **LNO** classifies tasks by impact: **L (Leverage)** tasks can return 10x–100x and deserve your best effort and even perfectionism; **N (Neutral)** tasks deserve ordinary competence and speed; **O (Overhead)** tasks deserve the minimum — "done is better than perfect." The mistake is spending L-level effort on O-level work. The **three levels of product work** — **Impact**, **Execution**, and **Optics** — name where a person's attention sits; most conflict comes from people operating at different levels (a CEO at Impact, a PM at Execution), and Shreyas D. argues you must be intentional about which level a given context demands rather than defaulting to the one you enjoy. Around these sits his emphasis on **pre-mortems** (imagine the project has failed; enumerate why, in advance) and on **product sense / taste** as the under-discussed core PM skill.

**Distinct critical lens.** _The leverage-and-taste auditor._ Shreyas D. attacks effort allocation and judgment: Is the team pouring L-effort into O-work and starving the few high-leverage bets? Which level is this artifact operating at, and is that the level this moment needs? What would a pre-mortem say is most likely to kill this? Where's the evidence of product sense versus process theater? He is the critic who catches a meticulously executed plan aimed at a low-impact problem, and a "strategy" that is really an execution checklist mislabeled. Note: Shreyas D. is the one figure here whose canon is essays, talks, and podcasts rather than a single authored book — cite the specific post or episode, not a page number.

## Ron K. — trustworthy experimentation

**Core idea.** Online controlled experiments (A/B tests) are the most reliable way to establish _causality_ between a product change and user behaviour — but only if they are **trustworthy**, and most are not. The keystone is a well-chosen **Overall Evaluation Criterion (OEC)**: a single metric (or small set) that is measurable in the short term yet predicts long-term value, so teams can't win the test while losing the business. Ron K. catalogues the traps that produce confidently wrong results: **Twyman's law** ("any figure that looks interesting or different is usually wrong" — surprising results are usually instrumentation or analysis bugs, not discoveries), sample-ratio mismatch, peeking/early-stopping, novelty and primacy effects, and carryover effects. Run at scale (the platforms he describes run >20,000 experiments a year), with rigorous trust checks, before believing a lift.

**Distinct critical lens.** _The validity skeptic._ Ron K. attacks the evidence behind a claimed win: What was the OEC, and does it actually predict long-term value or just a vanity lift? Was the result checked against Twyman's law before anyone celebrated? Any sample-ratio mismatch, peeking, or novelty effect that could be manufacturing this signal? He is the critic who catches "the experiment was significant, ship it" when the metric is gameable, the test was stopped the moment it crossed the line, or the lift is a two-week novelty bump that will decay. His lens is the empirical backstop to everyone else's qualitative judgment: Teresa T. and Clayton C. find what to build, Ron K. tells you whether the data saying it worked can be trusted.

## How the lenses divide the work (so a review doesn't double-count)

A quick map for assembling a council without redundancy. Each figure owns a distinct stage or question; the overlaps are real but bounded.

| Figure | Owns the question | Sharpest catch |
| --- | --- | --- |
| Marty C. | Is the team empowered, and did you de-risk value / usability / feasibility / viability? | Untested value or viability risk; feature factory |
| Teresa T. | Where's the continuous customer evidence and the opportunity space? | Roadmap from opinion, not weekly discovery |
| Melissa P. | Is the work measured by outcomes or outputs? | Feature list with dates posing as strategy |
| Clayton C. | What job, in what circumstance, is this hired for? | Innovating on attributes no job demands |
| Richard R. | Is there a real kernel (diagnosis → policy → coherent action)? | Goals / vision masquerading as strategy |
| April D. | What's the frame of reference that makes value obvious? | Right product, wrong category; features ≠ value |
| Shreyas D. | Is effort on the high-leverage few, at the right level? | L-effort spent on O-work; execution mistaken for strategy |
| Ron K. | Can the data claiming this worked be trusted? | Gameable OEC; peeking; novelty effect |

The deliberate adjacencies: Marty C. and Melissa P. both fight the feature factory (Marty C. from team empowerment, Melissa P. from the success metric); Teresa T. and Clayton C. both serve discovery (Teresa T. the weekly _method_, Clayton C. the _unit_ — the job); Clayton C. and April D. both face the customer (Clayton C. the latent demand, April D. the framing of the answer); Richard R. and Shreyas D. both attack fake strategy (Richard R. the kernel's integrity, Shreyas D. the leverage and the level). Keep the distinctions and the council covers strategy, discovery, positioning, prioritization, and evidence without four critics writing the same finding.
