# Intent-led design corpus

Use this corpus to decide what an experience needs to accomplish before choosing its structure. These are authored design heuristics and example decision spaces, not empirical claims that a pattern increases conversion or satisfies a standard. Read only the relevant profiles and capability sections.

## Routing

A project can combine several dimensions. Name its purpose, platform, primary surfaces, and operating conditions rather than forcing it into one category.

| Entry point | Read when | Main unit of reasoning |
| --- | --- | --- |
| [Marketing websites](profiles/marketing.md) | Explaining an offering and supporting a qualified next step | Audience decision and persuasion journey |
| [Platform websites](profiles/platform.md) | Explaining an ecosystem, its participants, and adoption paths | Role-specific route into capabilities and participation |
| [Content websites](profiles/content.md) | Publishing, finding, understanding, and connecting information | Content object, taxonomy, discovery and reading journey |
| [Mobile apps](profiles/mobile.md) | Designing device-constrained, interruptible sessions | Task flow, session continuity, device capability |
| [Product UI](profiles/product.md) | Creating, managing, collaborating on or administering objects | Object lifecycle, task surface and permission boundary |
| [Dashboard UI](profiles/dashboard.md) | Turning measurements into understanding and action | Analytical question, comparison and intervention |

Marketing, platform and content describe purposes; mobile describes a platform; product and dashboard describe modes of work. Combine them when appropriate. A mobile operations dashboard may need mobile, product, dashboard and operational guidance. An ecosystem's public website and its signed-in console usually need separate briefs.

## Shared references

- [Content and task pattern registry](patterns/README.md): intent-led module selection, website rhythm, product consistency and full-width composition.

- [Bidirectional reasoning](bidirectional-reasoning.md): the general principle connecting desired outcomes and available means, at any design scale.
- [Intent contract](intent-contract.md): describe goals, content responsibilities, KPI candidates, constraints and variant hypotheses.
- [Capability briefs](capabilities.md): commerce, search, support, operations, collaboration, learning, AI assistance and lifecycle.
- [Conditions and foundations](conditions.md): accessibility, responsive behavior, permissions, recovery, privacy, localization and state coverage.
- [Worked examples](examples.md): show how different intents produce different briefs and alternatives.
- [Brief scaffold](../../assets/intent-brief.template.md): optional authoring aid; omit irrelevant fields and deepen consequential ones.

## How to reason with the corpus

The following are useful considerations, not a mandatory sequence. Use the two reasoning lenses to decide what needs attention and at what depth.

1. Identify the user's intended outcome and the organization's legitimate objective. State where they conflict or remain uncertain.
2. Select one primary profile plus only relevant overlays. Derive the needed surface/flow inventory from tasks, content and transitions. The profile tables are candidate families, not a required sitemap.
3. Write a concise intent brief. Label each constraint as a requirement, heuristic, example or assumption with its source. Do not silently upgrade recommendations to requirements.
4. Identify the consequential unknown. Choose three alternative hypotheses that could resolve it. Keep content truth, access rules and evaluation conditions comparable.
5. Sketch enough entry, working, completion and recovery states to assess each hypothesis. Do not triple every trivial control or mechanically add capabilities outside the request.
6. Evaluate against the brief, explain tradeoffs, and make unresolved evidence visible. A polished screen is not evidence that a KPI improved.

## Contemporary practice without trend mandates

Prefer patterns whose purpose and costs can be explained. Command entry, contextual workspaces, adaptive disclosure, conversational assistance, personalization and automation are possibilities, not a definition of modernity. Ask which task they improve, whose effort they reduce, how users understand the result, and how people recover when they fail. A conventional interaction may be the best hypothesis.

When a task needs claims about current platform behavior, standards, products or performance, research current primary sources. Record source, access date, supported claim, limits and recheck trigger alongside that task's brief. Do not label undated examples as current best practice or copy observed product patterns without analyzing their context.

## Artifact mapping and scope

The shell has page, section and component units. Treat an application screen/state as a page unit when useful; use stable state-specific IDs and explain that naming convention. Record flow transitions in the brief. The runtime supports static composition and navigation, not application state machines, real authentication, network requests, transactions, analytics or AI execution. State which behavior is simulated or needs implementation. No new runtime fields are implied by this corpus.

Choose decision boundaries appropriate to the project. Website sections often compose independently; onboarding steps, editing modes and permission flows may need a coherent flow-level alternative. Do not permit mixed choices to create impossible journeys. Document compatible combinations or adapt the renderer before promising enforced compatibility.

- [Experience reasoning lenses](experience-lenses.md): shared prompts with local narrative, native, product, analytical and delegation perspectives.
- [Agentic workspaces](profiles/agentic.md): direction, supervision, evidence and authority.

- [Navigation patterns](patterns/navigation.md): website, mobile web, SaaS/dashboard and native families with global, local and task defaults.
