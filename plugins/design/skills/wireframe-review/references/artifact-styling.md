# Generated artifact styling

Every preview embeds the Ultimate Tokens color export and unchanged Maison geometry and layout snapshots, then `assets/wireframe.css`, then manifest CSS. The delivered file stays self-contained. Each iframe initializes product/md/md/round independently of the review shell. Nested data-tier, data-scale, data-size, and data-radius resolve independently through the shared resolver.

## Default roles

- Buttons: geometry height, text, outer inset, half-inset gaps, control radius. Explicit label/value slots add half-inset inline padding. Plain-text buttons have equivalent combined padding. Use label slots for truncation and icon composition.
- Icons: fixed g-icon containers; contextual glyphs at icon size and indicator glyphs at text size. Wrap the glyph in its slot. Mark decorative slots aria-hidden and name icon-only actions.
- Inputs/selects: geometry height, text, radius and combined outer/text inset. Selects retain native semantics with decorative Phosphor indicators. Textareas use geometry inset and inset radius, with editorial line height. Complex controls can supply their own slot-based markup.
- Borders: constant thin occupied border, transparent on focus and for ghost appearances. Focus-visible rings remain. Icon-only controls are the deliberate zero-inline-padding exception and remain square.
- Product cards: four times the local geometry inset, paired with content gaps of two insets. Tight content relationships use one inset; major-group separation uses three. See [product foundation](style/product-foundation.md) and [spacing recipe](../assets/recipes/spacing.html). Page layout and media dimensions keep their own layout roles.
- Typography: cards and application containers use the product UI heading context described in [product foundation](style/product-foundation.md#heading-context); editorial sections use the content context. Both remain independent of control geometry. Do not derive headings or prose from g-text. Semantic colors use surface__root, ink__root, muted__root, border__root, action__root, focus__root and related roles, all aliased to the exported --md-color-* foundation. The header scheme preference synchronizes previews and shell.
- Media dimensions: media-height__root, media-large-height__root, card-min-width__root and prose-width__root are explicit content-layout roles. They are not control-size aliases.
- Responsive defaults: narrow viewports adjust section insets, grid gap, heading/media roles, and stack grids. Controls retain their independent axes.
- Annotation pins: explicit product/md/sm/pill geometry. Review outlines use layout focus roles. Scrollbar chrome is hidden while scrolling remains available.

## Contextual surfaces

Use the [component foundation](style/product-foundation.md) for surface pairing. `.surface__inverse` already rebinds its contextual roles. Consume those aliases in descendants; custom backgrounds need a complete paired context and rendered contrast checks. Setting only container `color` cannot recolor paragraphs that explicitly use `--ui-muted`.

For navigation with glyphs, give rows consistent icon, text and indicator slots. Native details supplies disclosure behavior; replace its visual marker with a decorative Phosphor indicator when building the styled navigation recipe. Nested destinations are individual block/flex rows, not adjacent inline anchors. Read the navigation reference before authoring a sidebar or header.

## Authoring

Prefer the provided section__root, grid__root, grid__auto, card__root, media__root, media__large, actions__root, button__root, nav__root, center__root, eyebrow__root, stack__gap, stack__loose, section__gap and table__viewport patterns. The example manifest demonstrates label slots and spacing classes. Keep data-review-id on the semantic element, not its decorative label span.

Override semantic roles in manifest CSS for a brand or proposal. Change geometry through independent data attributes. The default styles use low specificity for controls so authored component styles can override them. Preserve accessible behavior and border occupancy when overriding. Never edit the vendored generated resolver to theme one artifact.

Shell-only edits preserve design revision IDs. Changes to reviewed design content normally require a new revision and explicit feedback migration. The starter demo retains its identity while foundations are iterated in this conversation; real reviewed artifacts should keep the previous revision package when their presentation changes materially.

## Full-width content surfaces

Section wrappers, reading layouts and agent briefing surfaces use the entire available container width. Default paragraphs do not impose a maximum width on their container. Apply `.prose__root` only to an intentional inner reading block when a shorter line length serves the content; do not use it to narrow the module surface. Internal columns, insets and gaps remain explicit.

Use [the pattern registry](design/patterns/README.md) to select composition by content purpose. Website variety and product consistency are different contextual goals; the same styling foundation supports both.

Full-width sections use fluid inline padding: `max(var(--ui-section-inset), calc((100% - var(--ui-content-width)) / 2))`. This aligns their content with navigation using the same width cap and minimum gutter while keeping backgrounds and borders full width. A `.content__root` wrapper can express the same centered limit in custom markup; do not apply the gutter twice. Use `.prose__root` (`--ui-prose-width`) for a deliberately narrower reading block inside this grid. Desktop previews grow beyond their 1200px baseline to fill a wider wrapper; narrower wrappers scale the baseline down. Mobile retains its 390px logical viewport scaled to the wrapper.

## Corner shape

Use `corner-shape: superellipse(1.5)` with a 1.5 presentation radius scale where supported. This softer curve replaces literal `squircle` (`superellipse(2)`), which remained visually tight on short controls even with increased radii. Feature detection selects the treatment; do not sniff browser names.

Fallback engines use the original foundation radius with scale 1 and factor 1. Do not reduce the fallback radius. The former 0.543214 compensation is retired. The two curves are intentionally approximate, not geometrically identical. Radius clamping means larger numeric values alone cannot guarantee softer corners.

Continue consuming foundation radius roles. Zero radius remains square, and control dimensions and insets stay unchanged. Verify rendered examples, not only computed radii. Do not edit generated foundation files. See [CSS corner shapes](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/corner-shape-value).

## Vertical rhythm ownership

Every sequential content group has one spacing owner: a `.flow__root` parent for a single-column grid, a `.stack__root` parent for a one-dimensional flex stack, or an explicit grid/flex container with a foundation gap. Do not rely on incidental paragraph bottom margins to separate cards, callouts, field groups or disclosures. Do not add child margins on top of a parent gap.

`.flow__root` and `.stack__root` clear direct-child margins and own CSS gap. Their default content gap is twice the local geometry inset; `data-spacing="tight"` uses one and `loose` uses three insets. Each nested spacing parent resets its own relationship. Field internals and option rows use tight gaps. Semantic fieldsets can be plain groups without extra padding. See product foundation for the maintained relationship contract.

Use `class="agent-panel flow__root"` as a representative pattern: heading, evidence list, boundary callout and retention field get one gap each. A callout can itself use `flow__root` for heading/body spacing. Check mixed sibling types and first/last edges, not only paragraphs. Explicit custom layouts may override this contract only with a documented content reason.

## Alignment across components

Navigation rows share one grid: inset, fixed leading icon slot, flexible label, fixed trailing indicator slot, inset. Use `--g-icon` for slots and `--g-inset` for gaps/insets. Head switchers, expandable rows, links and footer menus align to the same text column. Larger identity marks center on the leading slot without shifting text. Group captions align to the group edge; they are not expandable rows. Nested links retain the label column and replace visible leading icons with a vertical hierarchy guide. Native disclosure markers are replaced with explicit chevrons. Active backgrounds retain the same border box and inset as inactive rows. Field labels align with their control container, not a separate guessed text offset. Test bounding boxes across heterogeneous rows and text wrapping, not only individual controls.

## Icons and native selects

Use regular Phosphor icons by default from the bundled @phosphor-icons/core 2.1.1 assets. The artifact builder compiles `.ph-icon[data-ph]` to local SVG presentation before delivery; unsupported names fail the build. Standalone UI must embed the local SVG or its compiled mask. Identity text, content illustrations and review-state text are not automatically converted to icons. Accessible names remain independent from decorative glyphs. No runtime network access is required for icons.

Keep selects as actual HTML `select` elements, with native options, focus, keyboard and selection behavior. Decorate using `.select__root` with non-interactive leading icon and trailing indicator slots inside its bounds; never put a separate actionable chevron beside a partial focus ring. `data-select-icon` is build-time shorthand for a bundled leading Phosphor glyph. Authored anatomy works without JavaScript; see [the static recipe](../assets/recipes/native-select.html). The artifact builder compiles bare selects before delivery and preserves existing wrappers; copied standalone markup must contain the anatomy. Geometry supplies height, inset, icon slot and glyph size; center slot contents and reserve corresponding text padding. The control owns border/focus paint and the icons use `pointer-events: none`. Preserve the available text width and native disabled semantics.

Field labels use `--ui-label`, defaulting to `--md-color-neutral-on-surface-variant`. Override `--ui-label` locally with an exported family text role appropriate to the surface. Shell labels use `--wr-label`. Input/select values retain their own foreground. These are consumption aliases, not new exported token roles.

Editorial defaults now reference the bundled Ultimate Tokens typography.css snapshot: body MD, headline LG/SM, title MD and label SM. Control text still resolves through geometry. Preferred font files are not bundled; unavailable families use their exported fallbacks. Scenario-specific editorial overrides remain intentional specimen styling.

## Color notation

Use semantic token references for styling. When a literal color is necessary, author OKLCH with at least two decimal places per numeric channel; retain more precision where rounding changes the color (L/C six decimals and hue/alpha four are the default serialization). Preserve alpha. Legacy source excerpts remain verbatim provenance; do not silently rewrite snapshots.
