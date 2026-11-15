# Vocabulary

Spec 1 of 4. Accepted on 2026-11-12.

What this project calls things. The terms are data in [references/terms.json](../../references/terms.json), in the same shape the sibling skills use. The tables below are generated from that file by `node scripts/docs.mjs`; edit the data, not the tables.

## Why these fifteen

A term is here only because the earlier kits or the sibling skills use two words for one thing, or one word for two things. Each entry in the data records that evidence. Four cases shaped the list:

- **Root replaces host.** ui-geometry already owns host, for a segmented control or a tab list. The React, Svelte and Solid targets also have no host at all, so the word could not serve all four targets.
- **Part is wider here than in ui-materials.** There a part is painted and has a layer, a relief and a face. Here a part is any named element of the anatomy, so a label or an icon is a part too; ui-materials calls those marks.
- **Cascade layer, never layer alone.** In ui-materials a layer is a part attribute, base or overlay.
- **Behaviour replaces trait.** Both earlier Web Components kits say trait, and in gen-ui-kit the word also means attachment by attribute, which D12 rules out.

The state words pressed and active also collide with ui-materials. The [state matrix](state-matrix.md#names-in-panda-and-in-ui-materials) records that mapping.

## Principles

<!-- generated:principles:start -->
| Rule | Why |
|---|---|
| A word names one concept, and a word a sibling skill owns keeps that skill's meaning. | ui-geometry owns host, slot, tier and item; ui-materials owns layer, relief, face and material; ui-colors owns role, mode, theme and surface. An agent that loads two of these skills reads one word one way. |
| A part, a state, a condition and a component token each have one name in all four targets. | The manifest, the recipe and the four implementations meet only through these names. A second name is a second contract. |
| ARIA role, cascade layer, Panda preset and Panda recipe always carry their qualifier. | Role, layer, preset and recipe each mean something else in this family of skills. |
<!-- generated:principles:end -->

## Terms

<!-- generated:terms:start -->
| Term | Meaning | It is not | Words to avoid |
|---|---|---|---|
| **Kit** | The set of components, recipes, tokens and behaviours this skill writes into one project, in one target with one styling system. | Not the skill, which produces kits. Not the core set, which is what the skill ships before a project adds to it. |  |
| **Target** | One of the four frameworks a kit can be implemented in: Web Components, React, Svelte or Solid. | Not a styling system. Plain CSS or Panda is chosen separately. | renderer (maison-ui's word for the same thing); framework (it also names the libraries themselves; use target for the choice a kit makes) |
| **Component** | A unit of a kit that has behaviour: a root, named parts, author attributes, states and keyboard handling, described by one manifest and styled by one recipe. | Not a recipe. A card or a badge has styles and no behaviour, so it is a recipe with no component. | control (ui-geometry's first tier; a dialog or a table is a component and not a control); owner (maison-ui's word); widget (APG's word for the pattern, not for the kit's unit) |
| **Recipe** | The style definition of one component or of one style-only item: a hand-written CSS file that reads component tokens and holds the rules for the root, the parts, the variants and the conditions. | Not a Panda recipe, which is a class-generating object in a Panda config. The kit authors none. | component recipe (in instrumental-modernism and massimo-ui it means a construction pattern); stylesheet (reset.css and tokens.css are stylesheets and not recipes) |
| **Root** | The outermost element of a component: the custom element in the Web Components target, a native element in the other three. It carries the author attributes, the ARIA role and the states. | Not ui-geometry's host, which is a segmented control or a tab list. | host (ui-geometry owns it, and there is no host in the React, Svelte or Solid targets) |
| **Part** | A named element of a component's anatomy. The manifest lists a component's parts, every target renders them under the same names, and the recipe selects them by name. | Wider than in ui-materials, where a part is a painted element with a layer, a relief and a face. An anatomy part that is only ink, such as a label or an icon, is a mark there and has none of the three. | slot (ui-geometry's S, the 5q box; also the HTML element, which light DOM does not use) |
| **Author attribute** | An attribute on the root that a component declares as its public API and that the person writing the markup sets: a variant, a value, or a state such as `disabled` or `checked`. | Not a managed attribute. Naming attributes such as `aria-label` also belong to the author, but they are platform API and not declared by the component. | prop (props are how the React, Svelte and Solid targets receive the same values; the contract is the attribute) |
| **Managed attribute** | An attribute a component writes on its own root or parts after it starts: the ARIA role, `tabindex`, the ARIA states that mirror author attributes, and the `data-*` states that have no ARIA name. | The author does not write a managed state attribute. A `role`, a `tabindex` or a naming attribute the author did write is left as written. |  |
| **Variant** | An author attribute that selects one of a closed set of appearances for a component and changes neither its behaviour nor its ARIA state. | Not a state. A variant does not change through interaction. |  |
| **State** | Something true of a root or a part for a while, through interaction, validation or the author, that a recipe may style: checked, disabled, expanded, hover. | Not a variant. Not a custom state set through `ElementInternals`, which the kit does not use for styling. |  |
| **Condition** | The one selector that says a state holds, written as a union of the author attribute, the managed attribute and the native pseudo-class. A recipe selects a state only through its condition. | An environment condition, such as reduced motion or forced colours, is a query about the device and not about an element. The state matrix lists those apart. |  |
| **Component token** | A custom property a recipe reads to paint or size a component. A public token (`--button-color`) is only ever read by the kit, with a fallback, so anyone may set it on the root or an ancestor. A private token (`--_bg`) is set by the recipe's own variant and condition rules. | Not a ui-materials material token and not a ui-colors role. Those are the global values a component token falls back to. |  |
| **Behaviour** | A framework-free function `(root, options) => cleanup` that adds one interaction the browser does not supply: roving focus, typeahead, dismissal, positioning. | Not a component and not a base class. A behaviour holds no markup and no styles. | trait (gen-ui-kit's and agent-ui's word; in gen-ui-kit it also means attachment by attribute, which the kit does not do); binding (maison-ui's word); controller (gen-ui-kit uses it for external state objects) |
| **Manifest** | The JSON file that states the contract of one component or one recipe (parts, author attributes, states, keys, component tokens, icons, behaviours, readiness per target) and from which props, the registry and the exports are generated. | Not documentation written after the fact. A manifest that only describes the code is a defect. | descriptor (agent-ui's word) |
| **Cascade layer** | One of the five CSS `@layer` names that every kit stylesheet declares in order before its rules. | Never shortened to layer where ui-materials could be meant. There, a layer is a part attribute: base or overlay. |  |
<!-- generated:terms:end -->

## Words other skills own

How this project says the nearby thing when a sibling skill, or Panda, already owns the word.

<!-- generated:foreign:start -->
| Word | Owner | Meaning there | Here |
|---|---|---|---|
| host | ui-geometry | a segmented control or a tab list that holds joined items | root |
| slot | ui-geometry | S, the 5q box that holds a label line or an icon | part |
| tier | ui-geometry | controls, collections, containers or layout | a manifest names a component's tier and takes ui-geometry's meaning |
| item | ui-geometry | an entry in a frame or a host, such as a menu row or a tab | used with ui-geometry's meaning |
| preset | ui-geometry | a set of geometry constants | Panda preset, always qualified, for the file a Panda consumer adds |
| layer | ui-materials | a part attribute: base or overlay | cascade layer |
| part | ui-materials | a painted element with a layer, a relief and a face | part is wider here: it includes marks |
| mark | ui-materials | ink or data printed on a face | a part with no layer, relief or face |
| material | ui-materials | a preset of lighting, transmission, delineation and chroma | the kit ships the Flat material only |
| role | ui-colors | a `--colors-<role>` variable | ARIA role, always qualified |
| mode | ui-colors | light, dark, dim and the contrast modes | used with ui-colors' meaning |
| theme | ui-colors | a named request that produces one colour system | used with ui-colors' meaning |
| surface | ui-colors | the neutral family of cards, panels and floating layers | not used for a part |
| recipe | Panda CSS | a class-generating style object in a Panda config | Panda recipe, always qualified |
<!-- generated:foreign:end -->

## Closed sets

<!-- generated:sets:start -->
| Set | Members |
|---|---|
| targets | `web-components`, `react`, `svelte`, `solid` |
| stylingSystems | `css`, `panda` |
| cascadeLayers | `reset`, `base`, `tokens`, `recipes`, `utilities` |
<!-- generated:sets:end -->

## Names

How names are formed. "Built" means a check exists and runs today. "Planned" names the spec or step that will add it.

| # | Rule | Basis | Check |
|---|---|---|---|
| N1 | A component id shall be lowercase words joined by hyphens, taken from the APG pattern name where one exists: `menu-button`, `radio-group`. An id is never reused. | D7 | Planned: manifest schema, with the spike |
| N2 | In the Web Components target, a root's tag shall be the kit prefix, a hyphen and the component id. The prefix defaults to `ui`. | D23 | Planned: registry build |
| N3 | A part name shall be lowercase words joined by hyphens. The name `root` belongs to the root and to no other part. | D8 | Planned: manifest schema |
| N4 | Every part except the root shall carry `data-part="<part name>"`, in every target. | D8, D17, D30 | Planned: the parity script of D17 |
| N5 | An author attribute shall take the HTML attribute name where HTML has one with the same meaning (`disabled`, `checked`, `required`, `readonly`, `open`, `selected`, `hidden`), and otherwise the ARIA state name without `aria-` (`pressed`, `expanded`, `current`, `orientation`). It shall never start with `data-` or `aria-`. | B11, D9 | Built: `scripts/docs.mjs` refuses two states with one author attribute. Planned: manifest schema |
| N6 | A managed attribute for a state shall be the ARIA attribute where ARIA names the state, and otherwise `data-<state id>`. | D9, D32 | Built: the fixtures in `checks/states/run.mjs` |
| N7 | A state id shall be lowercase words joined by hyphens. Its Panda condition name shall be the same words in camel case. | D26 | Built: `scripts/docs.mjs` refuses duplicate ids and duplicate Panda names |
| N8 | A public component token shall be `--<component id>-<property>`, with an optional `-<qualifier>`. A private component token shall be `--_<name>`. | B13, D10, D23 | Planned: recipe lint, with the CSS contract |
| N9 | A kit stylesheet shall use only the five cascade layer names in the closed set above. | D27, D28 | Planned: recipe lint, with the CSS contract |

## Decisions this spec introduced

All three were confirmed on 2026-11-12 and are recorded in [decisions.md](../decisions.md).

| # | Decision | Why |
|---|---|---|
| D29 | The word root replaces host everywhere, including in documents already written. | See "Root replaces host" above. |
| D30 | A part is marked with `data-part`, not with a class or a `slot` attribute. | agent-ui and massimo-ui already do this. A `slot` attribute borrows a word ui-geometry owns and an HTML feature light DOM does not use. A class cannot be told apart from the author's own classes. |
| D31 | Part keeps its wide meaning even though ui-materials uses the word more narrowly. | D8 was confirmed with this meaning, and the manifest needs one word for every named element. The data records the difference. |

## Changes made to earlier documents

Wording only. No decision id changed.

- `docs/decisions.md`: host became root in D1, D8, D9, D10, D12, D16, D18, D20 and D21, including the titles of D9 and D18. D11, D27 and D28 now say cascade layer.
- `docs/plan.md`: host became root in the foundation table, the "Across frameworks" note and the open questions.
- `docs/checks.md`: three sentences now say root.
- `docs/prior-art.md` is left as written. It describes the earlier kits in their own words.

## What is checked

`node scripts/docs.mjs --check` exits 1 when any of these fails:

- two concepts share an id, a term or an alias
- a concept lacks a definition, an intent or evidence, or is defined by its own label
- a `related` entry names a concept that does not exist
- a generated table in this file differs from the data
- a phrase the data lists under `avoidExact` appears in `docs/decisions.md`, `docs/plan.md` or a spec

Not checked yet: that source code and manifests use these terms. That check arrives with the first code, in the spike.

## Open

- **Variant names.** There is no shared list of variant attributes such as `variant`, `size` or `tone`. One will be added when two components need the same axis.
- **Root selector per target.** How a recipe addresses the root of a custom element and of a native element is still the open point of D16.
