---
date: 2026-06-03
coverage: expanded
primary_sources:
  - "Nathan Curtis (EightShapes), “Team Models for Scaling a Design System” (medium.com/eightshapes-llc/team-models-for-scaling-a-design-system-2cf9d03be6a0, 2015)."
  - "Nathan Curtis (EightShapes), “The Fallacy of Federated Design Systems” (medium.com/@nathanacurtis/the-fallacy-of-federated-design-systems-23b9a9a05542)."
  - "Jina Anne, “The Salesforce Team Model for Scaling a Design System” (medium.com/salesforce-ux, 2017)."
  - "Brad Frost, *Atomic Design* (2016) — design systems as living products, not deliverables."
---

# Standards & Design-System Governance

A standard is a principle with a check attached: a principle says "prefer reuse over bespoke," a standard names the exact component, token, or pattern you reuse and how. Governance is the answer to one question — **who gets to change the standard, and how does a change get in?** Get that wrong and the system either ossifies (a central team becomes a bottleneck nobody routes around) or fragments (everyone forks, and "the system" is a museum). Nathan Curtis's team-model taxonomy is the canonical map of the options, and his own later correction is the load-bearing lesson: centralized vs. federated is **not** a binary.

> **Curtis's correction:** positioning central versus federated as a mutually exclusive choice "was a mistake." Successful design systems "always have a central team and always seek participation from a federated community." The real question is not _which_ model but _how much of each_, and how the two are wired together.

## The team models (Curtis)

Curtis names three production shapes plus the hybrid most mature systems converge on. Pick from the org's real shape, not the org chart you wish you had.

| Model | Who owns the system | Fits when | Failure mode |
| --- | --- | --- | --- |
| **Solitary ("Overlord")** | One team builds it primarily for _its own_ needs; others adopt what's there | Early days; one dominant product | "Overlords don't scale" — other teams' needs go unserved, so they fork |
| **Centralized** | A dedicated central team produces and supports the system as its full-time job | Strong consistency mandate; resourced team; many consumers | Bottleneck; backlog of requests; central team can't keep up with product velocity |
| **Federated** | Designers/engineers from multiple product teams decide the system together, part-time | Distributed expertise; no budget for a standing team | "Fallacy" — part-time contributors deprioritize system work when their product is on fire; quality and velocity sag |
| **Hybrid (cyclical)** | A small central team owns the core and the process; a federated community contributes patterns from real product work | Most systems past the first year | Under-investment in either half: a central team with no community drifts from product reality; a community with no center produces incoherence |

Curtis's "Fallacy of Federated Design Systems" is the warning most relevant to product orgs that try to do a system "for free": pure federation assumes people will steward shared infrastructure on the margins of their day jobs, and **they reliably won't** when their own product deadline competes. The fix is not to abandon federation — it is to fund a center that owns the spine and runs the intake, then invite the community to contribute against a defined process. Salesforce (per Jina Anne) ran an explicitly cyclical model: the central team and product teams trade off who drives, so the system stays both coherent and grounded in real use.

## Contribution / federation as a pipeline, not a vibe

"We accept contributions" is meaningless until the path is mechanized. A live system publishes the route from "a team needs something" to "it's in the system," with a gate the central team owns.

- **Three tracks, not one.** A request is either (a) **use what exists** (the answer is already in the system — close it, point at the doc), (b) **extend an existing component** (a new variant/prop against the current API), or (c) **propose net-new** (no existing pattern fits). Most healthy intake resolves as (a); a system where everything is (c) has either thin coverage or a routing problem.
- **A contribution has a contract.** Define up front what "done" means: the component plus its tokens, states, accessibility behavior, documentation, and a usage example — "the deliverable is not the design file." A contribution missing the doc or the a11y states is not a contribution; it is a liability the central team inherits.
- **The center owns the merge bar; the community owns the proposal.** This mirrors DACI cleanly (see `ownership-and-raci.md`): the contributing team is the _Driver_, reviewers are _Contributors_, and the system lead is the single _Approver_. One approver keeps the system coherent; many approvers reproduce the federated fallacy at the PR level.
- **Make the easy path the cheap path.** Adoption is a governance outcome, not a mandate. If using the system is slower than hand-rolling, teams hand-roll and your standard is fiction. Invest in scaffolding, codemods, and copy-paste-ready snippets so the standard-compliant option is the path of least resistance.

## How a standard stays alive

Standards rot by default. Brad Frost's framing — a design system is a "living product serving other products," not a finished deliverable — is the operative stance: an unmaintained system is worse than none, because teams trust it and inherit its staleness. Keep it alive with explicit mechanisms, not goodwill.

- **Versioning with a changelog.** Treat the system as released software: semantic versions, a public changelog, and migration notes per breaking change. Consumers must be able to read "what changed and what I have to do." (This is the same discipline as docs-as-code — see `documentation-as-system.md`.)
- **A coverage and adoption metric.** Track what fraction of shipped UI uses system components vs. one-offs. Falling adoption is the leading indicator that the system has drifted from product needs; rising one-off counts name the gaps the roadmap should close.
- **A standing intake cadence.** A weekly or biweekly system review where the central team triages requests, accepts contributions, and decides deprecations. Without a cadence, requests pile in a backlog and teams route around the system. (See `review-rituals.md`.)
- **An office-hours / advisory channel.** The cheapest governance is a fast answer. A place where a product team can ask "is there a pattern for X?" and get a same-day reply prevents most accidental forks.

## Deprecation: the part everyone skips

Adding to a system is easy and feels productive; removing from it is the hard, unglamorous work that keeps it coherent. A system that only grows accretes contradictory patterns until "use the system" stops meaning anything.

- **Deprecate explicitly, never silently.** Mark the component `deprecated` in code and docs, state the replacement, and give a removal version. A pattern that is "discouraged" but undocumented as such is a trap — teams keep adopting it.
- **Pair every deprecation with a migration path.** "Don't use this" without "use that instead, here's the codemod" generates exceptions, and exceptions are how standards die. The replacement must exist and be at least as easy before you deprecate the old thing.
- **Set a sunset, then enforce it.** A deprecation with no removal date is permanent; the old component lives forever beside its replacement, doubling the surface. Announce the version it disappears in, and hold the line.
- **Audit for orphans on a cadence.** Components no shipped product uses are dead weight — find them (usage telemetry, codebase grep) and retire them. Coverage works both ways: undocumented patterns in the wild are gaps; unused patterns in the system are bloat.

## Tells of good vs. bad standards governance

| Dimension | Bad | Good |
| --- | --- | --- |
| **Model fit** | Pure federation "on the side," or a lone overlord serving only itself | Funded center owning the spine + a defined federated contribution path |
| **Intake** | "Send us a Figma" with no contract; everything becomes net-new | Three tracks (use/extend/propose); a contribution contract incl. a11y + docs |
| **Decision rights** | Many approvers; coherence erodes at the PR level | One approver owns the merge bar; community drives proposals |
| **Adoption** | Mandated by memo; using the system is slower than hand-rolling | Measured; the compliant path is the cheapest path |
| **Liveness** | No versioning, no changelog, no cadence | Semantic versions, changelog, standing intake review, office hours |
| **Deprecation** | Components only ever added; old patterns linger silently | Explicit deprecation + migration + enforced sunset + orphan audits |
| **Drift signal** | Nobody tracks one-offs; gaps invisible | One-off rate watched; rising bespoke usage routes work to the roadmap |

The fastest single test: ask to see the system's **deprecation list and its last three merged contributions.** A system with neither is not governed — it is a component dump that happens to have a logo. A system with both has a living pipeline and a center willing to do the unglamorous half of the job.

## One labeled caveat

The Curtis taxonomy (solitary/overlord, centralized, federated), the "Overlords don't scale" line, and his explicit correction that central-vs-federated "was a mistake" / that successful systems "always have a central team and always seek participation from a federated community" are attributed to his EightShapes essays "Team Models for Scaling a Design System" and "The Fallacy of Federated Design Systems," cross-checked against multiple secondary summaries in this session rather than re-read in full. The Salesforce cyclical model is attributed to Jina Anne's "The Salesforce Team Model" article; the "living product, not a deliverable" framing to Brad Frost's _Atomic Design_. Verify exact phrasing against the originals before quoting.
