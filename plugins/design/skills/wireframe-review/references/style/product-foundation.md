# Product component foundation

Read this compact contract for every new build. Use the existing token index for exact names; the family vocabulary does not imply an API exists. These classes are implemented in wireframe.css; use assets/recipes/product-primitives.html as anatomy, adapting content and IDs. Classes are applied explicitly, not automatically. For new artifacts, use the matching primitive or verify equivalent behavior; opting out of a class does not waive its requirement. Read the linked menu recipe before building an account menu.

| Purpose | Implemented primitive | Responsibility |
| --- | --- | --- |
| Sequential groups | flow__root or stack__root | Own sibling gaps; clear direct-child margins; nest groups for distinct rhythm |
| Product typography | product__root | UI heading/body context; editorial sections can remain outside it |
| Enter a value | field__root, field__label, field__help | Label/value/help hierarchy; control geometry from local g context |
| Group related values | field-group__root + native legend, options__root | Explicit native fieldset styling and option spacing |
| Toggle or choose | label.choice__root + native input + content | Fixed control slot, multiline alignment, label activates control |
| Explained option | choice__root choice__card, choice__body, choice__description | Title and supporting explanation stay in one content column |
| Navigate | nav__item with icon/label/trailing slots | Minimum height, multiline padding, current-page pairing; not an action button |
| Sidebar | sidebar__root, sidebar__header/body/footer | Identity, flexible destinations, footer; parent provides available height |
| Contextual message | notice__root | Wrapping content and coherent surface; review metadata belongs in shell |
| Menu | navigation-menu.html + native auto popover/CSS anchors | Single indicator, top-layer panel, containment, Escape/focus/outside dismissal |
| Inverse surface | surface__inverse | Rebinds main, supporting and label foregrounds together |

Within `.surface__inverse`, consume `--ui-ink`, `--ui-muted` and `--ui-label`; do not assign neutral palette foregrounds directly to descendants or override only its background. A custom surface must pair its background, text, supporting text, labels, controls and borders in both schemes. Token existence is not pairing evidence. Do not remove visible focus to make screenshots quieter. Icons remain fixed geometry slots using Phosphor; .ph-icon[data-ph] is compiled from bundled regular-weight assets at build time. Missing glyph names fail the build; do not substitute a decorative block. Text-only navigation rows span the available label area without dummy icon nodes. A component with no icon need not invent one. Field labels and values have separate roles; avoid using a small caption as the universal label scale.

Menus are contained within their preview iframe, not permitted to cover the review shell. Top-layer popover support escapes clipping ancestors inside that document. The fixed-position fallback on older engines does not guarantee escape from transformed/clipped ancestors; record that browser limitation. Oversized menus scroll internally. Test open state at all four edges, long labels and actual ancestor clipping.

Spacing expresses grouping using the local geometry margin `u = --g-margin`: tight content relationships use `u`, separate fields/content use `2u`, major groups use `3u`, and card padding uses `3u`; contextual notices use `2u`. Content clusters use the same relationship scale in either direction. Fixed control internals such as icon-to-label gaps keep their compact half-margin geometry; do not enlarge controls to increase content breathing room. `flow__root`/`stack__root` own sibling gaps and reset direct-child margins; default is content, `data-spacing="tight"` is related content, `loose` separates major groups. Nested parents reset to content spacing. `field__root` owns label/control/help; `options__root` owns compact choice rows; `cluster__root`/`actions__root` own inline gaps. Minimum choice height preserves the click target independently of its external gap.

Card margin and major group gap are each 3u, fields use 2u and related content 1u: at the installed product default, 24 / 24 / 16 / 8px. Do not derive every spacing role as a fraction of card padding. Choose the semantic groups first; a flat stack with larger gaps does not establish hierarchy. Use `card__root flow__root data-spacing="loose"` for heading/body/footer separation; nest a default flow for fields and a tight stack for related content. A native `field-group__root` needs a flow wrapper after its legend; use `data-surface="plain"` for nested semantic groups such as Allowed collections, without another border/margin. The [spacing recipe](../../assets/recipes/spacing.html) demonstrates these relationships. Do not place flow on the fieldset itself or use child margins to patch a missing parent. Custom compositions can vary relationships with a stated purpose and measured evidence. Geometry height is the minimum frame for actions and textual controls; enlarged or wrapping text may grow it. In a bounded scrolling region, preserve intrinsic content heights: shared grid flows use max-content rows and vertical stacks do not shrink children. The region owns scrolling; do not compress actions to their minimum frame to fit all content inside it. Fixed dimensions remain appropriate for icon/mark geometry, not for clipping text.

A menu trigger requires a working panel; a raw details disclosure or unbound account button is not equivalent to the [menu recipe](../../assets/recipes/navigation-menu.html). Use Phosphor indicators, not text chevrons. For disabled native controls, set `disabled`; if an unavailable choice remains inspectable, keep selection operable and block the consequential action instead.

For interactive simulations, read [prototype-runtime.md](prototype-runtime.md). Do not append scripts by replacing closing HTML tags. For new component families, add a recipe only after a concrete repeated need; do not expand the vocabulary speculatively.

For styled checkbox/radio marks, switches, sliders, tables and related reusable anatomy, use the [component-family contract and catalog](components/README.md). These opt-in classes consume the same geometry roles; they do not replace the core engine or spacing hierarchy. Custom native marks embed Phosphor glyphs and retain native input semantics.

## Page-level rhythm

Choose semantic groups before assigning spacing. `.page__flow` separates top-level page sections by 3u, matching the card margin. `.section__flow` separates a section heading group from its body by 3u. `.heading-group__root` keeps a heading and its description together at 1u. At product/md/md these are 24 / 24 / 8px. Card internals remain 3u card margin, 3u major groups, 2u content/fields and 1u related content. Page spacing is a consumption-profile default, not a new engine invariant; an exception must identify the relationship it changes.

Each layout parent owns its immediate sibling gaps and resets direct-child block margins. Wrap the heading and introduction together, then place the content group beside that header within the section. Do not apply one larger gap to every child of a flat main element. Do not rely on the global heading bottom margin to establish a preceding section boundary. Avoid stacked margin and gap ownership. These classes are opt-in; ordinary prose outside them keeps its default rhythm.

Use the [page rhythm recipe](../../assets/recipes/page-rhythm.html) for structural guidance. Long paragraphs wrap without changing their spacing role. Native details require a content wrapper after summary: the shared disclosure__body assigns 2u padding inside the enclosing details border, and the sheet template uses 3u internal groups, with heading/example clusters at 1u. Do not put flow directly on fieldset or assume native disclosure layout behaves like an ordinary grid container.

Verification must measure both sides of headings, including the previous section's final content. Check narrow/wide widths, inherited sizes, open disclosures and nested cards. Numerical consistency is necessary but insufficient: inspect whether the heading is perceptually attached to its own content. The authored recipe verifies implementation, not future agent uptake.


## Heading context

Cards, dialogs, popovers and notices automatically use product UI headings; apply `product__root` or `data-type-context="product"` to other application containers, including each standalone specimen document. Use the installed heading role mapping and the [shared typography formulas](../../../../../Projects/ui-kit/docs/system/geometry-contract.md#typography--adopted); do not substitute a fixed pixel heading table. Heading sizes depend on the content context, not spacing density. Preserve semantic heading ranks; do not choose h4 merely to make a title smaller.

Use `data-type-context="content"` on an intentional editorial section to restore the content heading scale. Nested product cards establish their own compact context again. Arbitrary div wrappers inherit context; they do not imply editorial typography. Sheet cards and embedded specimens must consume these same contexts.

Nested semantic sections do not automatically become cards. Within one task surface, reuse `flow__root` and plain field groups so only the outer card owns padding; see [nested surfaces](composition.md#nested-surfaces) and its three-level recipe. Keep meaningful interactive boundaries, then verify the innermost reading width at mobile sizes.

Focus replaces the component boundary: set border color to transparent, retain its width, and restore state paint on blur. Apply this to the ring owner (including input-group and switch track), not unrelated ancestor containers. Clear the boundary only while its replacement ring is displayed. Ordinary pointer focus without a ring retains the boundary; keyboard focus-visible replaces it. Input-group focus-within already paints a ring, so its owner remains transparent. Checked and invalid semantics remain intact. For an affected focus-boundary change, use [the focused pointer/keyboard check](../../../wireframe-review/scripts/check-focus-replacement.mjs); this does not replace component behavior or accessibility checks.

Default surface geometry: cards use 3u padding, contextual notices 2u, and page-flow separates sections by 3u. The page outer margin stays 4u. Disclosure summary/body share a 2u inline margin. These are distinct ownership rules, not a single padding applied to every container.

Font stacks: display/editorial headings use Bricolage Grotesque, system-ui, sans-serif; body and UI (including compact product headings) use system-ui, sans-serif; code/mono roles use IBM Plex Mono, ui-monospace, monospace. Existing role names and product/content hierarchy are preserved. Bricolage Grotesque and IBM Plex Mono are bundled offline by getAssetBundle/build.mjs; see `references/bundled-fonts.md`. Wait for document.fonts.ready before geometry verification.
