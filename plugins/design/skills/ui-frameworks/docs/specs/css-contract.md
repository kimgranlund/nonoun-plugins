# CSS contract

Spec 4 of 4. Accepted on 2026-11-13.

How a kit's styles are organised: which stylesheets exist and how they reach the page, what `tokens.css` is made of, the shape every recipe follows, and how one recipe serves all four targets and Panda.

Terms such as recipe, root, part, component token, condition and cascade layer are defined in the [vocabulary](vocabulary.md). The conditions themselves are in the [state matrix](state-matrix.md).

## How to read the rules

Each rule has an id, a basis and a check. "Built" means the check runs today; "planned" names what the spike must add. Fourteen rules went beyond the decisions that existed when this spec was written. They were confirmed as D49 to D62 and are listed [at the end](#decisions-this-spec-introduced).

The recipe pattern in this spec was tested on 2026-11-12 in Chromium 156, Firefox 157 and WebKit 27.2, together with the patterns it rules out. See [Check 7](../checks.md#check-7--the-recipe-pattern).

## Stylesheets

| File | Cascade layer | Where it comes from |
|---|---|---|
| `reset.css` | `reset` | Hand-written and small |
| `tokens.css` | `tokens` | Generated from the three sibling skills |
| `<id>.css` | `recipes` | One hand-written recipe per component or style-only item |
| `kit.css` | none of its own | The index: one `@import` per file above, kept by the skill |

| # | Rule | Basis | Check |
|---|---|---|---|
| C1 | Every kit stylesheet shall begin with `@layer reset, base, tokens, recipes, utilities;` and shall put every other rule inside one of those cascade layers. | D11, D27, D28 | Built: the cascade pages of check 3, the recipe lint, and a test of every kit stylesheet |
| C2 | The kit shall put rules only in `reset`, `tokens` and `recipes`. `base` and `utilities` belong to the project and to Panda. | D50; check 3 | Built: a test of every kit stylesheet |
| C3 | A page shall load `kit.css` with a `<link>` ahead of any kit script. No kit script shall import or inject a stylesheet. | D11, D43, D49 | Built: a test that no kit script loads a stylesheet |
| C4 | `kit.css` shall import `reset.css`, `tokens.css` and the recipe of each component the project has, and nothing else. The skill updates it when it copies a component in. | D3, B14, D49 | Built: a test that the imports and the recipes on disk match |

C3 and C4 are how "components load with their CSS" (B14) is met without a script loading CSS. Adding a component adds its recipe and one line in `kit.css`. Because every file starts with the same statement (C1), the order of the imports does not matter.

## tokens.css

Three generated sections, each inside the `tokens` cascade layer.

| # | Rule | Basis | Check |
|---|---|---|---|
| T1 | The colour section shall be the `system.css` that ui-colors generates, unchanged except for being wrapped in the `tokens` cascade layer. | B5; ui-colors emits it unlayered | Built: `node scripts/tokens.mjs --check` regenerates the file and compares |
| T2 | The material section shall be ui-materials' base block: its palette inputs and its material tokens at their Flat values. It shall be declared on every scope where the colour mode changes, not on the root alone. | D4, D51 | Built: the same check. Planned: a comparison with ui-materials' token catalogue |
| T3 | The geometry section shall be generated from `ui-geometry`'s `derive.mjs --json`. Each variable shall be named after the row's id, with dots as hyphens: `controls.control.h` becomes `--controls-control-h`. | B5, D52; ui-geometry emits no CSS | Built: the same check |
| T4 | The geometry section shall hold exactly the rows that some recipe reads. | context-system: closure both ways | Built: a closure test, and the recipe lint refuses a variable `tokens.css` does not declare |
| T5 | Each geometry variable shall be a literal length. The rows that change with density shall be repeated, with their own values, under `[data-density="compact"]` and `[data-density="loose"]`. | gen-ui-kit: a custom property that uses `calc()` resolves where it is declared | Built: the same check, and a browser test at three densities |
| T6 | The kit shall not compute a colour in the browser. | ui-colors: generated, not derived | Built: the recipe lint |

What the siblings give, as found on 2026-11-12:

- **ui-colors** writes `--colors-<role>` variables on `:where(:root)`, with modes as the classes `.light`, `.dark`, `.dim` and `.contrast-more` plus the matching media queries. A default system is about 300 KB; its `minimal` preset is smaller.
- **ui-materials** lists 33 material tokens in its catalogue, such as `--raised-face`, `--solid-face`, `--on-solid`, `--recessed-face`, `--field-shadow` and `--ink`. Each reads a ui-colors role through a palette input.
- **ui-geometry** returns 200 rows at one font size, each with an id, a symbol and a length in px. Density changes six of the control rows.

## The shape of a recipe

A recipe is one `@scope` block inside the `recipes` cascade layer, with its contents in this order:

1. **The token block**, `:where(:scope)`: every private token the recipe reads.
2. **Variant blocks**, `:where(:scope[variant="…"])`: private tokens only.
3. **The root rule**, `:scope`, and the rule that keeps `hidden` working.
4. **Part rules**.
5. **Condition rules**, in the fixed order of C13, with the hover rule inside `@media (hover: hover)`.
6. **Environment blocks**: motion, forced colours, coarse pointer.

```css
@layer reset, base, tokens, recipes, utilities;

@layer recipes {
  @scope (ui-button) {
    :where(:scope) {
      --_face: var(--button-face, var(--raised-face));
      --_face-hover: var(--button-face-hover, var(--button-face, var(--colors-bg-muted-hover)));
      --_face-active: var(--button-face-active, var(--button-face, var(--pressed-face)));
      --_ink: var(--button-ink, var(--ink));
      --_ink-disabled: var(--button-ink-disabled, var(--ink-faint));
      --_height: var(--button-height, var(--controls-control-h));
      --_inset: var(--button-inset, var(--controls-control-t));
      --_radius: var(--button-radius, var(--controls-curvature-r));
    }
    :where(:scope[variant="primary"]) {
      --_face: var(--button-face, var(--solid-face));
      --_face-hover: var(--button-face-hover, var(--button-face, var(--colors-primary-solid-hover)));
      --_face-active: var(--button-face-active, var(--button-face, var(--colors-primary-solid-hover)));
      --_ink: var(--button-ink, var(--on-solid));
    }

    :scope {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      block-size: var(--_height);
      padding-inline: var(--_inset);
      border-radius: var(--_radius);
      background-color: var(--_face);
      color: var(--_ink);
    }
    :scope:where([hidden]:not([hidden="until-found"])) { display: none; }

    @media (hover: hover) {
      :scope:where(:is(:hover, [data-hover]):where(:not(:is(:disabled, [disabled], [aria-disabled="true"]), :is(:checked, [aria-checked="true"], [checked]:not(input, option)), :is(input[type="checkbox"]:indeterminate, [aria-checked="mixed"], [indeterminate]), :is([aria-pressed="true"], [pressed]), :is([aria-selected="true"], [selected]:not(option)), :is([aria-current]:not([aria-current="false"], [aria-current=""]), [current]), :is([aria-expanded="true"], [expanded]), :is([open], :popover-open)))) { background-color: var(--_face-hover); }
    }
    :scope:where(:is(:focus-visible, [data-focus-visible])) {
      outline: var(--controls-focus-ring-width-w) solid var(--colors-primary-solid);
      outline-offset: var(--controls-focus-ring-offset-o);
    }
    :scope:where(:is(:active, [data-active]):where(:not(:is(:disabled, [disabled], [aria-disabled="true"])))) { background-color: var(--_face-active); }
    :scope:where(:is(:disabled, [disabled], [aria-disabled="true"])) { color: var(--_ink-disabled); }

    @media (prefers-reduced-motion: no-preference) {
      :scope:where([data-ready]) { transition: background-color 100ms; }
    }
    @media (forced-colors: active) {
      :scope { border: var(--unit-border-b) solid ButtonBorder; }
      :scope:where(:is(:focus-visible, [data-focus-visible])) { outline-color: Highlight; }
      :scope:where(:is(:disabled, [disabled], [aria-disabled="true"])) { color: GrayText; border-color: GrayText; }
    }
  }
}
```

This is an illustration of the shape, not the button's final recipe. The spike writes that.

### Component tokens

| # | Rule | Basis | Check |
|---|---|---|---|
| C5 | The kit shall never declare a public component token. It shall only read one, as the first argument of `var()`, when it sets a private token. | D10 | Built: check 7 for the pattern, and the recipe lint on every recipe |
| C6 | A root rule, a part rule and a condition rule shall read private tokens only. | D10 | Built: the recipe lint |
| C7 | A private token for hover, for active or for a variant shall fall back first to its own public token, then to the base public token, then to the kit's value: `var(--button-face-hover, var(--button-face, <kit value>))`. Where the component has no such base token, as a tab has no face at rest, it shall fall back to the kit's value alone. | D54, D73; check 7 | Built: check 7 for the pattern, the recipe lint, and a browser test in three engines |
| C30 | A private token for any other state shall fall back to its own public token, then to the kit's value: `var(--checkbox-face-checked, <kit value>)`. It shall read no other public token and no private token. | D54 as amended: the base fallback erases a state that carries meaning | Built: the recipe lint, and a browser test in three engines that sets only the base token |
| C8 | A recipe shall declare, in its token block, every private token it reads. | A private token would otherwise be inherited from an enclosing component | Built: the recipe lint |
| C31 | A recipe shall make its root and its parts border boxes, in one rule of no specificity: `:where(:scope, [data-part]) { box-sizing: border-box; }`. A recipe that sizes other elements, such as table cells, shall add them to the list. It shall not include `::before` or `::after`: a pseudo-element keeps the content box the recipes were written for, which the reset never changed, because `:where()` takes no pseudo-element. | D102: a kit loaded without the reset, or under a project's own, keeps its sizes | Built: the recipe lint with two negative controls; `checks/review/css-loading.mjs` compares every family with and without `reset.css` |
| C9 | A variant block shall set private tokens and nothing else. | D58 | Built: the recipe lint |
| C10 | A kit value shall be a material token, a geometry variable or a ui-colors role. A recipe shall contain no literal colour and no literal length other than `0`. | B5, T6, D51, D59 | Built: the recipe lint |
| C11 | The property words of a public token shall be `face`, `ink` and `line` for paint, and `height`, `inset`, `gap` and `radius` for geometry, with the state or variant as a suffix: `--button-face`, `--button-ink-disabled`. | N8, D60 | Built: the recipe lint |

C7 has a visible consequence. A consumer who sets only `--button-face` gets that colour at rest, on hover and when pressed, in every variant. To keep a hover change they also set `--button-face-hover`.

C10 has one exception today. ui-materials has no token for hover: it describes hover as the face moved one step along its ramp. Recipes therefore read ui-colors' hover roles, such as `--colors-primary-solid-hover`, directly.

### Conditions and their order

| # | Rule | Basis | Check |
|---|---|---|---|
| C12 | A recipe shall write a condition inside `:where()`, after `:scope` or after a part, and shall take the condition unchanged from the state matrix. | S1, D55; check 7 | Built: check 7 for the pattern, and the recipe lint compares each condition with the matrix |
| C13 | Condition rules shall appear in this order, so that a later one wins: hover, focus-visible, active, then checked, indeterminate, pressed, selected, current, expanded and open, then invalid, loading, read-only, and disabled last. | D55; check 7 | Built: the recipe lint |

| C28 | A recipe shall write every hover rule inside `@media (hover: hover)`. | D64; ui-interaction-dev `hover.media` | Built: check 7 and the real recipes under touch emulation in Chromium, and the recipe lint |
| C29 | A hover rule shall change paint only, and shall set no property that changes a box. Its paint shall differ from the paint of the active condition. | D63; ui-interaction-dev `hover.face-only` | Built: the recipe lint for the properties, and a test that the box does not change |

C30 was added on 2026-11-13, when D54 was amended; C7 held both cases before. The last sentence of C7, the tray clauses of C20 and C21, and the limits of the lint under C19 and C20 came with the tabs. They were confirmed on 2026-11-13 as D73 and D74. C28 and C29 were added on 2026-11-13, when the kit adopted two rules of the sibling skill `ui-interaction-dev`. The hover condition itself already refuses a disabled root and a root that holds a state, so a recipe needs no extra selector for that.

The conditions differ in specificity: the checked condition ranks above the disabled one. Without `:where()`, a checked and disabled root would keep its checked look however the rules were ordered. Check 7 shows exactly that failure, and shows that with `:where()` the order alone decides.

### Parts

| # | Rule | Basis | Check |
|---|---|---|---|
| C14 | A recipe shall select a part as a child of the root, or of another part of the same component, with the child combinator: `:scope > [data-part="mark"]`. | D30, D56; check 7 | Built: check 7 for the pattern, and the recipe lint on every recipe |
| C15 | A part that holds no content and takes no events should be a pseudo-element of the root, not an element. The manifest records which kind each part is. | D40, D43, D57 | Judgement, reviewed with each manifest |
| C16 | A recipe whose root sets `display` shall restate that a hidden root is not displayed. | agent-ui: an author's `display` rule defeats `hidden` | Built: the recipe lint |

C14 is what keeps a part rule from reaching a part of the same name in a component nested inside. Check 7 shows the leak when a part is selected as any descendant.

C15 serves two earlier decisions at once. A pseudo-element exists before the component is defined, so it cannot cause a layout shift (D43), and it is never in the author's way (D40). A checkbox's mark is the usual case.

### Before the component is defined

| # | Rule | Basis | Check |
|---|---|---|---|
| C17 | A recipe shall size and place the root from its tag and its author attributes alone, never from a managed attribute or from a part the component creates. Where the component will create an element part, the recipe shall reserve its space. | D43; foundation rule U1 | Built: the layout test of U1, in three engines |

### Motion, forced colours, pointer and direction

| # | Rule | Basis | Check |
|---|---|---|---|
| C18 | A recipe shall declare a transition or an animation only inside `@media (prefers-reduced-motion: no-preference)` and only for a root that is ready: `:scope:where([data-ready])`. | D61; state matrix: ready, reduced-motion | Built: the recipe lint |
| C19 | A recipe that paints a part shall have a `@media (forced-colors: active)` block. In it, an operable boundary shall be drawn with a system colour, an on state with `Highlight`, and a disabled part with `GrayText`. | D15 | Built: the recipe lint for the block, and a computed-style test under forced-colours emulation in three engines |
| C20 | A root that takes focus shall draw its focus ring as an outline on the focus-visible condition, with its width and offset from ui-geometry's focus rows, the same in every recipe. An item inside a tray, such as a tab, shall draw the ring inside itself: the offset is the ring's width, negated. The ring is never painted over: the reset raises a part on the focus-visible condition (`z-index: 1`, zero specificity), and a root whose focus is on a part, such as a text field, raises itself with `:scope:where(:focus-within) { z-index: 1; }`. A root that sets its own `z-index` keeps the ring above its neighbours itself. | D74; ui-materials: the ring is identical in every material. ui-geometry: a hosted item uses the inset ring, because an outer ring would overlap its neighbours; a later sibling in a flex or grid row paints over an earlier one's outline wherever they overlap | Built: the recipe lint, for every recipe whose manifest says the root takes focus, a keyboard test of the ring on a button, a checkbox, a tab and a tab panel, and `checks/focus-on-top/run.mjs`, which reads the ring's pixel over a joined neighbour for a button and a text field, with `--negative` removing the rules that raise them |
| C21 | Under `@media (pointer: coarse)`, a control's hit area shall be at least ui-geometry's touch target, without changing the root's box. An item inside a tray shall take the pointer over the tray's padding at every pointer, and its hit area shall never cover a neighbouring item. | D74; ui-geometry: a target never shrinks the box; an item and its padding make the height of a control | Built: hit tests in three engines and on an emulated touch screen in Chromium |
| C22 | A recipe shall use logical properties. It shall not use `left`, `right`, or a property whose name contains them. | gen-ui-kit: physical properties in 24 sheets | Built: the recipe lint |

## One recipe, four targets

A recipe is written once, for the Web Components target: the root is a tag and a variant is an author attribute. The other three targets render a native element as the root (D17), which has neither.

| # | Rule | Basis | Check |
|---|---|---|---|
| C23 | In the React, Svelte and Solid targets, a root shall carry `data-<prefix>="<component id>"`, and a variant shall be the attribute `data-<variant name>`. | D17, D62 | Built: a browser test in three engines that paints native elements carrying the root attribute with the rewritten recipes. Planned: the parity script of D17, with the first real second target |
| C24 | When the skill copies a recipe for one of those targets, it shall rewrite the tag in `@scope (…)` to that root attribute, and each variant attribute selector to its `data-` form. It shall rewrite nothing else. | D62 | Built: `scripts/rewrite-recipe.mjs`, with a test that undoes the two rewrites and compares every recipe character for character |

So `@scope (ui-button)` becomes `@scope ([data-ui="button"])`, and `:scope[variant="primary"]` becomes `:scope[data-variant="primary"]`. Conditions need no rewrite, because each one already covers the author attribute, the ARIA attribute and the native pseudo-class (D26).

The alternative was to write every root and variant selector as a union of both forms. It needs no rewrite step, but it doubles those selectors in every kit, and a kit only ever has one target (B2).

## Panda

| # | Rule | Basis | Check |
|---|---|---|---|
| C25 | The skill shall generate a Panda preset whose `conditions` are the state matrix's conditions under their Panda names. | D16, D26 | Built: `scripts/panda.mjs`, tested against `references/states.json`; run through Panda 2.4 `cssgen` on 2026-11-13 |
| C26 | Every token path in the preset shall begin with `kit`, so that no variable Panda emits has the name of a kit variable. | Check 3 | Built: generator test |
| C27 | The preset shall not set `layers`. | D27: the kit already uses Panda's names | Built: generator test |

## Decisions this spec introduced

All fourteen were confirmed on 2026-11-13 and are recorded in [decisions.md](../decisions.md).

| # | Decision | Why |
|---|---|---|
| D49 | The kit's CSS reaches the page through one index, `kit.css`, linked ahead of any script. No script loads CSS (C3, C4). | It is the one delivery path D11 asks for, and it is what lets an undefined component already be styled (D43). |
| D50 | The kit writes only into the `reset`, `tokens` and `recipes` cascade layers (C2). | `base` and `utilities` then stay free for the project and for Panda. |
| D51 | Recipes paint with ui-materials' material tokens, not with ui-colors roles (T2, C10). | D4 ships Flat only, but a recipe that reads material tokens needs no change when another material arrives. |
| D52 | Geometry variables are generated from ui-geometry's rows, named after the row ids, literal per density, and limited to the rows recipes read (T3 to T5). | ui-geometry emits no CSS. Names taken from its ids need no second vocabulary and can be checked. |
| D53 | A recipe has one fixed shape: token block, variants, root, parts, conditions, environment. | One shape is what makes a lint possible. |
| D54 | A hover, active or variant token falls back to its own public token, then the base public token, then the kit's value (C7). A token for any other state falls back to its own public token, then the kit's value (C30). Amended on 2026-11-13. | An override then holds at rest, in every variant, on hover and when pressed, which is the point of D10; and a state that carries meaning, such as checked or disabled, stays visible when only the base token is set. |
| D55 | Conditions are written inside `:where()` and in a fixed order, with disabled last (C12, C13). | Check 7: otherwise specificity, not order, decides which state shows. |
| D56 | Parts are selected with the child combinator (C14). | Check 7: a descendant selector leaks into nested components. |
| D57 | A part with no content and no events should be a pseudo-element (C15). | It exists before the component is defined and never touches author content. |
| D58 | A variant block sets private tokens only (C9). | Every difference between variants is then something a consumer can override. |
| D59 | Recipes hold no literal colour and no literal length other than `0` (C10). | Every value then traces to a sibling skill. |
| D60 | Public tokens use the words `face`, `ink` and `line`, and `height`, `inset`, `gap` and `radius` (C11). | They are ui-materials' and ui-geometry's words. The brief's example `--button-color` becomes `--button-face`. |
| D61 | Transitions exist only for a ready root and only when motion is allowed (C18). | The first paint then never animates, and reduced motion needs no override. |
| D62 | For the React, Svelte and Solid targets the skill rewrites the root and variant selectors when it copies a recipe; a native root carries `data-<prefix>="<component id>"` (C23, C24). | A kit has one target, so one rewrite at copy time is cheaper than doubled selectors everywhere. |

## What is checked today

The nine recipes that exist (button, checkbox, the four of the tabs and the three of the menu button) are held to this contract by four checks. Each has a negative control.

- **The recipe lint,** `node scripts/lint-recipes.mjs`, reads each recipe and reports the rule it breaks. Its tests break one rule at a time in a copy of a real recipe and require the lint to name that rule: 37 cases. Two more tests show that the lint excuses a missing focus ring only on a root that takes no focus, and a missing forced-colours block only in a recipe that paints nothing.
- **The generator checks,** `node scripts/tokens.mjs --check` and `node scripts/props.mjs --check`, regenerate `tokens.css` and the prop schemas and compare.
- **The browser tests,** `tests/browser/recipes.test.js`, `recipes.tabs.test.js` and `recipes.menu.test.js` in three engines, and `recipes.touch.test.js` on an emulated touch screen in Chromium. They cover layout and paint before and after the components are defined, token overrides and the states an override must not erase, the order of states, density, a nested dark scope, the focus ring, motion, forced colours and hit areas.
- **The mutation runner,** `node tests/mutate.mjs <project-with-playwright> styles`, breaks one thing at a time in a served copy of a stylesheet and requires a browser test to fail: 72 cases. The runner uses Chromium, so a line that only WebKit needs, such as the two in the forced-colours blocks of the menu and its item, has a test in three engines and no mutation.

Not checked yet: T2's comparison with ui-materials' token catalogue. The rewrite of C24 is `scripts/rewrite-recipe.mjs`, tested on every recipe.

## Open

- **An overlay is placed with no script.** The menu button's root carries `anchor-name` and `anchor-scope` with one fixed name, and the menu's root names it in `position-anchor`. The scope keeps each menu to its own menu button, so the two recipes share a name and nothing else. Placement, the flip above the trigger and the minimum width hold in Chromium 156, Firefox 157 and WebKit 27.2, before and after the elements are defined. The browser's own `inset` and `margin` for a popover did not need resetting once `position-area` is set.
- **Forced colours differ by engine.** WebKit 27.2 keeps a `box-shadow` and does not recolour an outline in forced colours, where Chromium and Firefox do both. The recipes say both explicitly.
- **A root that cannot hold pseudo-elements.** The rewrite of C24 assumes the native root can do what the custom root does. A checkbox's mark is two pseudo-elements of its root, and a native `input` has none. The second target has to settle what its checkbox root is; the recipe may need the mark as an element part there.
- **A tab cannot see its list.** A recipe reads its own root's attributes only (C17), and private tokens do not cross recipes (C8). So a tab does not know whether its list is vertical. Its paint and its hit area are written to work both ways: the selected tab is a face, not an underline, and the hit area sits behind the tabs. Its label starts at the same edge in both. The tabs element, for the same reason, does not put a vertical list beside its panels.
- **A tray needs a ring in the dark scheme.** ui-materials gives a recess that sits on the base ground the ground's own fill there, and says it separates by its ring. Flat has no ring of its own, so the kit sets `--recessed-shadow` in `kit.config.json`, beside the two rings it already set.
- **A public token can name a part (D92).** `--meter-fill-face` is the face of the meter's fill: `--<component>-<part>-<word>`, with a state or variant after it as before. The part is one of the manifest's parts. A token with no part belongs to the root. This closes what was an open point; the checkbox's glyph ink is `--checkbox-mark-ink`.
- **Disabled has no token for a mark on a solid face.** ui-materials says a disabled part fades its marks and keeps its face. A neutral label has `--ink-faint`; a label on a solid face has nothing, so the primary button fades whole through `opacity`. By C30 its disabled ink is then the kit's `--on-solid` even when the consumer has set `--button-ink`, which a token for a faded mark would make unnecessary.
- **Two mechanisms can do one job.** Mutation testing showed it twice: the checked rule already overrides hover by its order, so the hover condition's guard for held states changes nothing in the checkbox; and the row's padding and line height already add up to its height, so its minimum height changes nothing either. Neither is wrong, but each rule is only tested where it is the one that decides.
- **Hover has no material token.** Recipes read ui-colors' hover roles directly (see C10). ui-materials would have to add hover tokens for recipes to be free of ui-colors roles.
- **Motion.** No sibling skill owns durations or easings, so the example above has a literal `100ms`, which C10 does not cover. The kit needs motion tokens from somewhere.
- **Type.** ui-geometry gives sizes and line heights. Font families belong to no sibling.
- **Long geometry names.** A name made from a row id can be long, such as `--controls-focus-ring-width-w`. Shorter names would need a mapping that ui-geometry does not have.
- **Font size and curvature at run time.** T5 covers density. A different font size or curvature for part of a page would need its own generated block.
- **The size of the colour section.** A default ui-colors system is about 300 KB of CSS. Which request a kit should use is a question for ui-colors.
- **`reset.css`.** Its contents are not specified. The spike writes the smallest one the four components need.
