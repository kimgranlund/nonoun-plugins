# Navigation patterns

Use the [machine-readable navigation registry](navigation.json) when selecting an experience shell or navigation structure. It contains four composable families and 17 global, local and task patterns. These are authored defaults and variant hypotheses, not a fixed template inventory or claims of platform compliance.

## Reason from the work

Establish destination count and hierarchy, frequency, user familiarity, object and workspace scope, device constraints and consequences of leaving work. Select global, local and task navigation independently, then check that their relationship is understandable. A breadcrumb explains ancestry; back returns through a defined context; neither substitutes automatically for the other.

Use the four family defaults as starting points. A native task with no peer destinations may not need a bottom bar. A small SaaS product may not need a persistent sidebar. Combine families locally where a marketing website leads into an authenticated workspace.

## Labels and shared alignment

Default destination labels to one familiar word; use two or three short words when they improve recognition or distinguish peers. Author labels separately from descriptive page titles, goals and editorial headlines. Preserve stable route IDs. Never truncate a title mechanically to invent a label, and avoid vague single words when a short phrase is clearer. Keep vocabulary consistent across global navigation, mobile menus and local links.

Use the same `--ui-content-width` and `--ui-section-inset` for navigation and page content. Section backgrounds and borders fill the wrapper; their content aligns to the centered navigation container. Narrow reading measures belong inside that shared grid. Test at widths above and below the content limit, including mobile, rather than aligning only one screenshot.

## Defaults and variants

Each pattern describes intent, fit, a default, three candidate variant directions, tradeoff, adaptation and an evaluation question. Shared review dimensions cover anatomy, behavior, states, access and measures. Variant directions are possibilities, not a requirement to render every combination.

Changing logo alignment or menu side is configuration. Changing direct links into a mega menu or a sidebar into a top-level route system changes navigation structure and deserves a hypothesis. For A/B/C proposals, prioritize consequential structural uncertainties; do not manufacture three architectures when the task only needs a placement adjustment.

Persistent bottom destinations and contextual bottom actions have different semantics. Keep them distinct, avoid covering content and explain when each appears. Preserve navigation vocabulary and ordering through responsive adaptation. Overflow must remain discoverable without relying on visible scrollbars.

## Behavior and review

Consider active location, expansion and dismissal, focus return, keyboard operation, unavailable destinations, deep links and refresh, unsaved work, notifications and switching scope when relevant. Avoid an exhaustive state checklist for a trivial menu. Define which context is preserved on return and how users resolve pending changes.

Record conclusions in existing intent, rationale and tradeoff fields, with flow/state details in the companion brief. Keep tightly related navigation alternatives coherent across screens. The current shell does not enforce cross-screen compatibility or implement native gestures and routing. A static navigation picture does not establish working keyboard behavior, persistence or accessibility.

Use foundational geometry, color and inset roles for authored controls. Sections fill their wrapper; navigation content can use an intentional centered inner container. Research current primary platform guidance before implementing native behavior or asserting standards conformance.

Related: [experience lenses](../experience-lenses.md), [pattern selection](README.md), [conditions](../conditions.md).

## Marketing header composition

The registry separates `headerCompositions` from destination patterns. Four useful compositions are brand-led discovery, minimal conversion, independently centered destinations, and enterprise grouped discovery. Direct links, dropdowns and mega menus describe information architecture; they can combine with a suitable composition without becoming a new pattern for every placement permutation.

Use explicit identity, destination and utility/action regions. Balance the header across these regions: a relevant primary action for a public experience, or a user/workspace menu for a signed-in experience. Do not add a fake operational action just to fill space. For centered destinations use equal flexible side tracks and place the utility at the trailing edge; collapse the destination group before those tracks collide. Center their visible controls vertically, use tighter gaps within a region than between regions, and align the inner container with the page content. For true centered navigation, equal flexible side tracks accommodate unequal brand/action widths. Switch to a compact arrangement before groups collide; exercise realistic long labels and narrow widths. Typography and branding in supplied screenshots are references, not required measurements or permission to copy identity assets.

Use only actions justified by the offering. A search box or sign-in button is not mandatory because a reference contains one. Relay has no live account or search experience, so its rendered examples retain a truthful pilot action and destination links. Its minimal variant preserves secondary access through Explore.

Account dropdowns overlay content without changing header height. Anchor the panel to the trigger with a gap of `calc(var(--g-inset) / 2)`. Reset disclosure-summary margins in this component so general accordion spacing cannot move the trigger or its panel. Verify closed/open header height and the actual trigger-to-panel gap at desktop and mobile widths.

## Rendered coverage and boundaries

`assets/demos/marketing-navigation.mjs` implements reusable markup for all four compositions. Marketing A/B/C compare brand-led, centered and focused-conversion strategies. `marketing-headers.html` demonstrates all four, including categorized disclosures. The gallery links to the review artifact; it does not promise direct routing into a selected review page via URL fragments. Native details menus operate; these are not production mega menus or an accessibility certification.

The product demo uses its distinct sidebar contract: context-switching head, searchable navigation body, expandable link groups and a user-menu footer. Platform, content and agent demos retain their earlier header experiments; those are not prescribed marketing defaults. In All pages, preview interactions select design context; use Inspect/Browse to exercise menus and navigation. The runtime does not implement all registry patterns or application workflows.

Verify alignment at the intended logical viewport as well as the scaled preview. Check actual group centers, collision/overflow, active context, keyboard disclosure, destinations and shared text columns. Preference or static render checks do not establish conversion impact.
