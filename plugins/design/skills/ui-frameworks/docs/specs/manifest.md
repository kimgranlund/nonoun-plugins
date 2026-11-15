# Manifest and registry

Spec 5. Extracted on 2026-11-13 from the nine manifests the spike wrote, and accepted the same day.

A manifest is the source of one component's contract (D13). This spec says what a manifest holds, which rules tie it to the component's code, and what the generated registry carries. Terms such as component, part, state and behaviour are defined in the [vocabulary](vocabulary.md).

The shape is in `references/manifest.schema.json`, a JSON Schema that carries a description of every field. This spec does not repeat it. `node scripts/manifests.mjs` checks every manifest and writes the registry; with `--check` it writes nothing and fails on a broken rule or a stale registry.

## What a manifest holds

One file per component, `kit/components/<id>/<id>.manifest.json`. Its fields fall into six groups, in reading order.

| Group | Fields | A reader uses it to |
|---|---|---|
| Identity | `id`, `kind`, `family`, `tier` | find the component and place it |
| Intent | `summary` | decide whether it is the one they need |
| Contract | `role`, `focus`, `tabindex`, `formAssociated`, `attributes`, `resets`, `states`, `parts`, `tokens`, `behaviours`, `keys`, `events`, `messages` | use it, and generate from it |
| Relations | `family`, `uses`, `writes` | know what else comes with it and what touches what |
| Guidance | `guidance`, `notYet` | avoid the known mistakes and the known gaps |
| Provenance | `pattern`, `schema`, `targets` | see what it follows and what is built |

Three relations exist, and each permits only what its definition says.

- **`family`** is the id of the component that leads the pattern: `tabs` for the four tabs components, `menu-button` for the three of the menu button. A component alone is its own family. Components of one family are installed together.
- **`uses`** names a component outside the family that the author's markup needs with this one. A menu button uses a button.
- **`writes`** names the attributes this component writes on another component's root, by that component's id. It also lists what the component writes on its own root beyond its role, its tabindex and the attributes of its states.

## Rules for a manifest

| # | Rule | Basis | Check |
|---|---|---|---|
| H1 | A manifest's `id` shall be the name of its folder and of its file. | D48; ids are stable | `scripts/manifests.mjs` |
| H2 | A manifest shall be valid against `references/manifest.schema.json`. The schema shall allow no field it does not describe, and shall declare every closed set once. | D13; context-system: every closed set is declared once in a schema | The checker, with a negative control per kind of violation |
| H3 | `tabindex` shall be a number when `focus` is `own`, and null otherwise. | D74: the recipe lint asks for a focus ring from `focus` | The checker |
| H4 | Every entry of `states` shall be a state of the state matrix, and a state an attribute sets shall be listed in `states`. | D9, D26 | The checker |
| H5 | An attribute of type `enum` shall have `values` and a `default` that is one of them. No other type shall have `values`. | E7 | The checker |
| H6 | `resets` shall name attributes of the component, and only a form-associated component shall have any. | F6 | The checker |
| H7 | Every entry of `tokens` shall start with `--<id>-`, and the list shall be exactly the public tokens the recipe reads. | D10, D13 | The checker for the prefix; the recipe lint for the match |
| H8 | Every entry of `behaviours` shall be a file in `kit/behaviours`, and the list shall be exactly the behaviours the class imports and mounts. | B5 | The checker for the file; the test of B5 for the match |
| H9 | The part named `root` shall have kind `root`, and no other part shall. An element part shall give its tag and its place; a pseudo part shall say which pseudo-element it is. | D40, D41, D57 | The checker |
| H10 | `family` shall be the id of a component whose own family is itself. `uses` shall name components outside the family. Each key of `writes` shall be the component itself, a member of its family, or a component it uses. | D65, D66, D67 | The checker |
| H11 | A target marked `built` shall have its files. For the Web Components target those are the five files of D48, or for a style-only recipe its recipe and its manifest. | D48; a status states evidence | The checker |
| H15 | A manifest of kind `recipe` shall name the native element it is written for, and shall have no tabindex, no behaviour, no form association and no attribute other than a variant. A manifest of kind `component` shall name no native element. | D91, D93: a style-only recipe has no script | The checker |

A status is `planned` or `built`. `built` is a claim about evidence: the files exist and the target's tests pass. The checker holds the first half; the test suites hold the second.

## The registry

`kit/registry.json` is generated from the manifests and never edited. It is what a consumer, or the skill that copies a component into a project, reads first.

| # | Rule | Basis | Check |
|---|---|---|---|
| H12 | The registry shall be exactly what `scripts/manifests.mjs` generates from the manifests. | One home per fact: the manifest | `node scripts/manifests.mjs --check`, and a test that edits the registry and expects a failure |
| H13 | The registry shall have one entry per manifest and none without one. An entry shall keep `kind`, `family`, `tier`, `role` and `focus` unchanged, carry the summary and the path of the manifest, and name only files that exist. The registry shall say that it is generated. | context-system: a registry keeps every field consumers route by | A test, and context-system's `check_registry.py` with a negative control |
| H14 | An entry shall list, under `with`, the other members of the component's family and then what it uses; under `writtenBy`, each component that writes an attribute on it, with the attributes; and under `modules`, every module its defining module loads, however indirectly. | D3: a component is copied in with everything it needs | Test |

`with`, `writtenBy` and `modules` are derived, which is why no manifest states them. A manifest used to say in prose who writes its attributes; that is now the other side of a `writes`, computed once.

## What the manifest generates and what is held against it

| From the manifest | Produced or checked | By |
|---|---|---|
| `attributes`, `parts`, `role`, `tabindex`, `resets` | `<id>.props.js`, generated | `scripts/props.mjs` |
| `tokens`, `focus` | Held against the recipe | `scripts/lint-recipes.mjs` |
| `behaviours`, `states` | Held against the class | `kit/components/components.test.js` |
| Identity, relations, `targets` | `kit/registry.json`, generated | `scripts/manifests.mjs` |

## Decisions this spec introduced

The spike's manifests grew field by field. Extracting the schema meant settling five things, first listed here as W1 to W5. All five were confirmed on 2026-11-13 and are recorded in [decisions.md](../decisions.md).

| # | Decision | Why |
|---|---|---|
| D80 | A manifest is JSON held to a JSON Schema, `references/manifest.schema.json`, and names the version of that schema it is written to. The schema allows no unknown field. | context-system: prefer JSON with a schema as the source; every tool and agent reads it with no build. A closed schema is what turns a mistyped field into an error. |
| D81 | `family` is one id, not a list of members repeated in every member. The members, what a component comes `with` and who writes its attributes are derived in the registry. `uses` and `writes` are the only other relations. | One home per fact. The list of four tabs components was written in four manifests. |
| D82 | `focus` is required and is one of `own`, `roving` and `none`. | The recipe lint and the registry both route by it, and it could not be read from `tabindex` alone. |
| D83 | A target's status is `planned` or `built`, and `built` needs the target's files. `in progress` is gone. | A status that states no evidence cannot be checked. |
| D84 | The registry is `kit/registry.json`, generated, with one entry per component: the routing fields, the summary, the tag, the files and every module the component loads. | D3: the skill copies a component into a project, and has to know what to copy without reading source. |

## Open

- **The other three targets.** `built` has files for the Web Components target only. Each other target gets its list when its first component exists.
- **Relief and face** are free text in a part's material, because ui-materials owns those sets and the kit has no copy of them to check against.
- **The per-target selector mapping and the icon contract** are the rest of step 4 of the plan, and are not in this spec.
