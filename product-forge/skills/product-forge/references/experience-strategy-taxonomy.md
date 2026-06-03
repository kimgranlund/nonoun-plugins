---
date: 2026-06-03
coverage: foundational
primary_sources:
  - product-forge v0.2 ROADMAP (this plugin)
  - Jesse G., *The Elements of User Experience* (New Riders, 2002; 2nd ed. 2010)
---

# Product Experience Strategy — the taxonomy

The canonical frame for **what "product experience strategy" covers and who owns each part.** product-forge is organized around these twelve domains; this map routes any product / UX / PM task to the skill that holds the depth, the rubric that scores it, and the council lens that critiques it — and names the two domains a sibling plugin owns. Load this when a request is broad ("design the whole experience", "is our product experience any good") or when you need to place a sub-topic on the map.

## The twelve domains → owner

| # | Domain | Sub-topics | Owning skill | Rubric | Critic lens |
| --- | --- | --- | --- | --- | --- |
| 1 | Intent & Outcomes | user/business goals, promises, success metrics, experience principles | product-methodology | rubric-product-strategy | Richard R. · Marty C. · Melissa P. · April D. |
| 2 | Experience Architecture | journeys, flows, surfaces, navigation, wayfinding, states, continuity, enablement | product-architecture | rubric-architecture | Garrett |
| 3 | Interaction Model | inputs, commands, controls, feedback, confirmation, undo/recovery, automation boundaries | product-architecture | rubric-architecture | Norman · Nielsen |
| 4 | Information Architecture | object model, taxonomy, metadata, relationships, search, filtering, retrieval | product-architecture | rubric-information-architecture | Covert |
| 5 | Content & Communication | voice, labels, microcopy, guidance, education, empty states, help | product-patterns (`content/`) | rubric-content-design | Torrey P. |
| 6 | Interface System | layout, components, **tokens, motion**, responsive, accessibility mechanics | product-patterns (`substrate/`) — **mechanics → adia-ui / ui-\* layer** | rubric-ux-quality (a11y / pattern) | Norman · Nielsen |
| 7 | Brand & Perception | identity, tone, expressiveness, trust/quality signals, emotional affordance | **→ brand-forge** | (brand-forge) | (brand-forge council) |
| 8 | Intelligence & Adaptation | personalization, recommendations, context, memory, agentic assistance, automation | product-patterns (`ai-ux/`) | rubric-ai-product | Cat W. · Weil · Choi |
| 9 | Trust, Safety & Control | privacy, consent, permissions, explainability, reversibility, auditability, risk | product-patterns (`trust-safety/`) | rubric-trust-safety | Ann C. |
| 10 | Service & Workflow Model | handoffs, operational workflows, support, cross-channel, escalation, fulfillment | product-operations (`service-model/`) | rubric-service-model | Marc S. |
| 11 | Measurement & Learning | analytics, research, experiments, quality signals, feedback loops, iteration | product-methodology · product-research | rubric-discovery | Ron K. · Torres |
| 12 | Governance | principles, standards, ownership, decision records, review rituals, documentation | product-operations (`governance/`) | rubric-governance | Cutler |

## Cross-plugin boundaries (the frame spans three plugins)

Product Experience Strategy as drawn here is a **superset** — ten of its twelve domains are product-forge's, and two belong to sibling plugins by design:

- **Domain 7 (Brand & Perception) → `brand-forge`.** product-forge cites trust/quality _signals_ as UX, but identity, tone, expressiveness, and emotional affordance are brand-forge's domain (cultural authority, voice, the brand stack). Route brand work there.
- **Domain 6 mechanics (tokens, components, motion, layout) → the adia-ui / `ui-*` build layer.** product-forge owns the _decision_ (which pattern, is it accessible, does it fit the genre); the rendered design-system / component implementation belongs to the framework-authoring plugins. The accessibility, responsive, and pattern-fit _judgments_ stay here (rubric-ux-quality).

## How to use the frame

1. **Broad request** → name the domains in play, then route each to its owning skill (to make) or to `product-evaluate` + the matching rubric / sub-council (to judge).
2. **A sub-topic** → find its row, open the owning skill's cold-start table for the specific reference.
3. **A brand or component-rendering ask** → hand off to the boundary owner above, and say so explicitly.

The domains are a routing map, not a methodology — the depth lives in each owning skill's references, and the scoring lives in each rubric.
