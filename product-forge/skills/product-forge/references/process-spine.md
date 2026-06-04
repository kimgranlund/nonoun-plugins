---
date: 2026-06-03
coverage: foundational
primary_sources:
  - "Design Council — The Double Diamond (2004; refreshed as the 'Framework for Innovation', 2019). https://www.designcouncil.org.uk/our-resources/the-double-diamond/"
  - "product-forge v0.3 ROADMAP (this plugin)"
---

# The Process Spine — methodologies across the taxonomy

The companion to `experience-strategy-taxonomy.md`. The taxonomy maps the **surfaces** of an experience (the _what_); this maps the **motion** through them (the _how_) — the repeatable methodologies a team runs, sequenced on the Double Diamond. Load this when the question is "how do we actually _do_ this," or to pick the right method for where you are.

## The spine — Double Diamond

Two diamonds, four moves, alternating divergent (open up) and convergent (narrow down): **Discover** (explore the problem) → **Define** (frame the one problem worth solving) → **Develop** (explore solutions) → **Deliver** (narrow to one, build, validate). product-forge expands the two diamonds into **seven phases**, so each methodology has a home: `discover · frame · decide · structure · make · measure · govern`. Human-Centered Design (IDEO / d.school: empathize, define, ideate, prototype, test) is the same rhythm with an empathy emphasis — treat them as one spine, not two.

## The method index

Each methodology carries a **method card** (frontmatter: `phase · domains · timebox · participants · produces · de_risks · rubric`) and a runnable body (steps · roles · failure modes · hand-off). It lives in its owning skill's `references/methods/` cluster; the depth is there, this frame only sequences and routes.

**playbook** = a dedicated runnable card under the owning skill's `references/methods/`; _concept_ = run from its framework reference in the owning skill (a dedicated playbook may follow). `product-research/methods/` additionally cards the research primitives — `interviewing` · `survey-design` · `research-ops` · `behavioral-vs-attitudinal`.

| Method | Phase | Domains | Timebox | Produces | Home · form |
| --- | --- | --- | --- | --- | --- |
| Double Diamond / HCD | _spine_ | all | — | the process arc itself | this frame |
| Build–Measure–Learn (Lean) | frame | 1·11 | continuous | validated learning per loop | product-methodology · _concept_ |
| Continuous Discovery + OST | discover | 1·11 | weekly | opportunities → tested assumptions | product-methodology · _concept_ |
| JTBD switch interview | discover | 1·11 | ~1 hr | the real job + forces of progress | product-research · **playbook** |
| Design Sprint | decide | 1·2·11 | 5 days | tested prototype + go/no-go | product-methodology · **playbook** |
| Riskiest-Assumption Test | decide | 1·11 | hours–days | the killer assumption, tested | product-methodology · _concept_ |
| Working Backwards / PR-FAQ | frame | 1·5 | days | the launch artifact, written first | product-methodology · _concept_ |
| Journey mapping | structure | 2 | ½–1 day | the end-to-end map + the gaps | product-research · _concept_ |
| Story mapping | structure | 2 | ½ day | the backbone + a sliced plan | product-architecture · **playbook** |
| OOUX / ORCA | structure | 4 | 1–2 days | the object model | product-architecture · **playbook** |
| IA validation (card sort + tree test) | structure | 4 | hours | a validated (or failed) IA | product-architecture · **playbook** |
| Service blueprinting | structure | 2·10 | ½–1 day | front-stage + back-stage + support | product-operations · **playbook** |
| Usability testing | make | 2·3·5·6 | ½ day | the top usability problems | product-research · **playbook** |
| A/B test (controlled experiment) | measure | 11 | weeks | a measured causal effect + guardrails | product-methodology · _concept_ |
| ADR cadence + RAPID/DACI | govern | 12 | per-decision | a durable, owned decision | product-operations · _concept_ |

## How to use it

1. **"Where are we?"** → find the phase, run its method(s). Discovery is _continuous_ (it never fully closes); the rest are episodic.
2. **"Which method?"** → filter the card by what you actually _have_: a week + a Decider → Design Sprint; an hour + no users → a card sort, not a sprint. `timebox` + `participants` + `produces` are the selection signals.
3. **"Did we run it well?"** → each card names the `rubric` that scores its output; the maker runs the method, `product-evaluate` + the council judge the run.

A methodology is a procedure, not a guarantee. This frame sequences and routes; the steps, roles, and failure modes live in each playbook under `references/methods/`.
