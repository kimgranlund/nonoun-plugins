---
name: context-routing-review
description: Review and test repository context routes for reusable-component authors and application consumers, including fresh-agent planning or implementation trials. Use after guidance reorganizations or demonstrated discovery gaps; not for ordinary UI implementation alone.
---

# Author & Consumer Context Routing Review

Determine whether an agent starting at the repository entry can discover enough current authority to do the requested work. Author means reusable capability ownership; Consumer means composition of existing APIs (often called prototype or creator locally). Discover the repository's names rather than introducing parallel personas.

## Select the scope

- **Static review:** follow representative routes and compare governing content with implementation. No fresh-agent success claim.
- **Fresh planning:** independent agents discover a route and produce actionable plans. No implementation or visual-success claim.
- **End-to-end:** independent agents implement scoped tasks; independently verify artifacts, behavior and applicable browser views.

Honor the requested mode. For unspecified reviews, start static; do not launch implementation trials merely because agents are available. Read [briefs and acceptance](references/briefs-and-acceptance.md) when preparing a trial. Read [evidence and repairs](references/evidence-and-repairs.md) when evaluating or reporting any mode. These resources are templates to adapt, not a requirement for extra infrastructure.

The skill operator is the evaluator. Fresh repository participants receive only the extracted neutral brief, not this skill, its worked examples or the grading rubric. Fresh agents testing the skill itself may read it; label those as skill-execution checks, not uncontaminated repository-discovery benchmarks.

## Run the review

1. Identify entry, source ownership, mode, editable boundaries and verification environment. Freeze representative briefs and observable acceptance criteria before seeing results. Record entry/source revision or hashes; keep evaluator criteria and prior answers outside participant discovery.
2. Follow downward routes to governing content and upward routes for missing APIs, exceptions and ownership. Treat manifests and focused lookup results as locators, not substitutes for linked documents. Read in bounded calls; recover omitted sections before acting. Use returned paths and declared package scripts before guessing filenames. Assess retrieval cost separately from route correctness; use the retrieval guidance in evidence and repairs rather than optimizing for the fewest reads.
3. For requested fresh trials, use clean agents with no conversation inheritance (`fork_turns=none` where supported). Give each only the neutral task, actual entry path, edit/output boundaries and necessary environment facts. Do not give the expected route, suspected gaps or previous answers. Tell agents to record actual reads, failed lookups, truncation/recovery and assumptions. Exclude historical evaluations/shared task logs from discovery; if an entry directs there, record the edge without loading prior answers. If isolation is unavailable, label the run assisted rather than fresh.
4. Assign disjoint ownership. Serialize shared builds/generated output. An author and consumer can explore independently; integrating a newly delivered API afterward is an explicitly labeled integration phase. Do not count that coaching as autonomous discovery of the API. A missing API found by the consumer routes back to its reusable owner; do not invent a local substitute to make the trial pass.
5. Independently inspect actual artifacts and targeted behavior, not just agent summaries. Use existing type/build/test/registry/browser tooling. For UI implementation, inspect the real consumer at narrow and desktop widths in light/dark when applicable, plus meaningful pending, error, retry and disabled states. Numerical tests alone do not establish visual quality or accessibility. Preserve user tabs/preferences and keep generated files in the declared output location. Coordinate a final source-ready handoff and tie final results to that source; see the final-source guidance in evidence and repairs.
6. Classify failures before repairing: discovery/delivery, stale authority/metadata, implementation, integration or verification environment. Correct the earliest demonstrated cause within authorized scope. Preserve archived evidence; do not create a new registry, copied UI manual or generic test runner to fix a local stale pointer.
7. Recheck affected behavior. To claim improved *fresh discovery*, rerun the same frozen brief with a new clean agent after repairs. Otherwise label repairs source-checked or integration-verified. Default to one initial pair and at most one affected fresh rerun; stop and report remaining gaps if that bound is reached, unless the user requested a broader evaluation.

## Deliver

Report Author and Consumer outcomes separately: route correctness, delivered artifact quality, retrieval overhead, repairs and remaining uncertainty. Include evidence links, verification results and whether each phase was static, fresh, assisted or integration-directed. Update repository shared notes through its existing route. A passing build, a self-reported read trace or a reachable link alone cannot establish a successful end-to-end route.

This skill carries review mechanics, not repository-specific component rules. Current local contracts and source remain authoritative over old examples or bundled domain-skill snapshots. Do not copy tested geometry constants or component inventories into this skill.
