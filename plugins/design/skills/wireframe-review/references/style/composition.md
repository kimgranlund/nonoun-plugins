# Compact style contract

This is the wireframe-review profile of the supplied token foundations. Read contract.json plus this file when inventing components. Load recipes only when their anatomy helps. Token values and resolvers remain authoritative; this contract names relationships, not a second value table. Paths in the manifest resolve relative to its directory.

Choose families from the component's purpose. Compose surfaces, controls, collections, navigation and overlays; these categories may overlap. Slots name responsibilities, not mandatory DOM nodes. Keep native controls and appropriate semantic elements. An unseen component can introduce new structure without new decorative rules.

## Family resemblance

- Choose semantic color pairs, never a literal color because it happens to resemble a reference. Resolve scheme through the foundation. Status color expresses status; emphasis expresses priority.
- Resolve control height, margin, icon and text together from the selected geometry context. Center fixed icon slots; wrapping text must not stretch them. Editorial headings and reading measures use editorial roles independently of control geometry.
- Choose spacing by relationship using the rules in [product foundation](product-foundation.md): tight, content, section and margin share the local geometry unit. The immediate parent owns gap; semantic nesting does not automatically add another padded surface.
- Navigation and section content share a width cap and minimum margin. Backgrounds remain full width. Reading blocks can be narrower inside that alignment.
- Menus overlay rather than resize their header. Trigger-to-panel separation is half the trigger's resolved gutter. Reset generic disclosure margins locally.
- Keep borders occupied across states. Selection and focus must not shift siblings. Provide visible keyboard focus and truthful disabled/pending behavior.
- Use the supplied corner and icon treatments. Prefer Phosphor glyphs to homemade decorative symbols. Decorative glyphs are hidden from assistive technology; interactive elements need names.

## Novel components

Establish purpose and interaction, choose constituent families, assign slots and consequential states, then compose. Explain a material exception with its intent and local scope. Do not require an exhaustive rationale for routine decisions. A new visualization may need content-specific dimensions; it should still inherit surface, typography, spacing and interaction rules.

Reuse installed components when they satisfy the task. This profile does not mandate a framework or replace platform accessibility requirements. The axes in the manifest are vocabulary, not proof that every state has a ready-made recipe.

## Verification

Run the browser harness described in verification.md. Mechanical conformance does not prove aesthetic quality, task fitness, accessibility compliance or model generalization. Keep those conclusions separate.

Emphasis (primary/secondary/quiet), appearance (solid/soft/outline/ghost/link) and intent (neutral/accent/success/warning/danger) are independent vocabulary in contract version 2. They are not automatic variant APIs; inspect a recipe's implemented support. For inverse surfaces, consider `--ui-ink`, `--ui-muted` and `--ui-label` together.

## Nested surfaces

Use a padded card for a distinct surface, not for every semantic section. Within one task surface, nested sections use headings and `flow__root`; related form choices use a plain field group. This keeps semantic depth without multiplying 3u card margins. In the nesting recipe, the outer task card uses `flow__root data-spacing="loose"` for its 3u group gap; inner `flow__root` sections use 2u, and `heading-group__root` uses u. The one card retains its 3u card margin. See the [three-level nesting recipe](../../assets/recipes/nesting.html). If a nested item needs its own interactive boundary, keep that boundary and adapt the layout at narrow widths; do not shrink every card or introduce arbitrary density to recover space. Verify the innermost text measure and long labels at each supported width and density, not only document overflow.

## Collection followed by a task

Preserve 3u card margin and 3u/2u/1u group/content/related gaps; reduce repeated surfaces before reducing those relationships. A selectable collection can use flat native choice rows with a strong item name and compact related metadata. Avoid giving every metadata line a section gap. Keep the follow-on task discoverable with ordinary named anchors, and keep optional technical explanations after the task or in an optional disclosure rather than between required steps. Check both collapsed and expanded states. The [equipment-loan recipe](../../assets/recipes/collection-workflow.html) demonstrates this composition; its [local controller](../../assets/recipes/collection-workflow.js) retains draft versus saved state. It is a development example, not evidence of generation reliability.

Collection choices use `label.choice__root > input.checkbox__control + .choice__body`, with the item name and `.choice__description` inside the body. The mark-to-body gap is one full local gutter; title-to-metadata uses the related-content gutter. A flat collection row may use one margin of block padding, while the enclosing card retains its 3u card margin. Do not remove the content wrapper to compress a collection: that bypasses the related-content gap.


## Bounded selection with an adjacent task

When a long selectable collection pushes a required follow-on form far below it, consider a named native scroll region for the collection while keeping the summary, contact fields and actions in ordinary flow immediately after that region. The [bounded collection-task recipe](../../assets/recipes/bounded-collection-task.html) keeps all18 choices in one scrollable region, with the same flat row anatomy and 3u card/group, 2u content and 1u related relationships. This is an optional task composition, not the default for every list. Prefer document flow when browsing the full collection is the main task; do not hide the only item content or remove choices to shorten the page.

The region's block size combines viewport space with a minimum and maximum from local control geometry. Its footer occupies normal flow rather than overlapping the scrollport. Name the region, provide a visible scrolling cue and retain native keyboard access to every available choice. A persistent action bar must reserve space in the actual scrolling viewport; document-bottom padding alone does not prevent it from covering intermediate focused controls. Verify ordinary Tab navigation, hit-testing and wrapped/enlarged labels at short viewports before adopting any overlaid bar.

The [local controller](../../assets/recipes/bounded-collection-task.js) owns totals and save/stale/restore application state only. With scripts unavailable, selection and contact fields remain usable; totals and local saving are explicitly unavailable. Restore stays disabled until a valid draft exists. CSS owns list bounds and footer placement; the recipe adds a geometry-derived block-end scroll margin for its multiline native disclosure, verified separately from visible layout gaps. This authored recipe is not proof that generated interfaces reproduce the composition or that a shorter geometric distance lowers overall task effort.

## Page and record ownership

Use page__root on the outer product page for its 4u margin, and page__flow for 3u task boundaries. These own different relationships; repeat neither on nested groups. A non-tabular button.record-choice__root is a card option: 2u margin, 1u title/metadata gap, card radius and visible selected surface. Table-cell selectors use 1u margin and control radius; metadata is not a decorated action label. Staged collection grouping and post-render heading focus are owned by [workflow guidance](components/workflow-patterns.md#focus-and-task-grouping).

Default surface geometry: cards use outer margin3d and contextual notices2d (padding subtracts border), and page-flow separates sections by 3u. The page outer margin stays 4u. Disclosure summary/body share a 2u inline margin. These are distinct ownership rules, not a single padding applied to every container.

## Field with a related command

Use field-action__root for one labelled field plus its related button, keeping control bottoms aligned and wrapping the button below when needed. Put independent commands in a separate actions__root group. Keep field help after the pair. See [field/action recipe](../../assets/recipes/field-action.html). Do not reuse an auto-fit filter grid for this different relationship. Check intermediate widths and enlarged labels; ordinary flex wrapping does not establish intentional grouping.

## Related command and disclosure text rails

Outer edge alignment does not imply text alignment: default action and disclosure margins differ. For related secondary commands followed by evidence, use [control-rail__root](../../assets/recipes/control-rail.html). Boxed controls share2u margin. In a narrow reading-flow__root, commands adopt the same flat inline treatment as disclosures, preserving their block borders and focus targets. Apply only to this declared relationship, not every adjacent button and panel. Verify actual rendered text starts and outer edges in both modes; preserve the shared mathematical button margins.

Here spacing u means the resolved density spacing d, not the content unit n. The [shared geometry contract](../../../../../Projects/ui-kit/docs/system/geometry-contract.md) owns formula definitions.
