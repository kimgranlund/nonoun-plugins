---
name: ui-kit-inspector
description: Design and build a jig, a live panel that tunes the constants of a UI system on a real canvas and hands the result back as a portable change set, for any project or framework, but not plain Storybook stories, a design-token build pipeline or an ordinary settings page. Use when asked for a jig, an inspector panel, a token tuner, a design-system playground or a tweak panel, of kind system, component, layout or theme, or when checking one that exists.
---

# UI kit inspector

A jig is a live panel beside a real canvas. A person moves a constant of a UI system, sees every screen that derives from it change at once, and leaves with one change set that an agent or an engineer can apply and verify. This skill teaches how to design and build one for any project and any framework, in plain HTML, CSS and DOM terms.

Read this file whole. Then read only the reference for the kind of jig you are building.

## What a jig is

A jig has four parts that always travel together.

| Part | What it is |
|---|---|
| Canvas | The host project's own components, drawn at true pixels |
| Constants | One control for each value the system derives from |
| Checks | The host's own rules, and checks the jig proposes, shown apart |
| Change set | One portable object that says what moved, from what, against which base, and why |

What a jig is not:

- It is not a story with controls. Storybook Controls edits the arguments of one story. A jig edits system constants, so every component that reads them moves together.
- It is not a token build tool. It hands a change set to the token pipeline the project already has (Style Dictionary and Tokens Studio are neighbours of this kind) and never replaces one.
- It is not a design tool. It draws nothing new. It tunes what the host already has.
- It is not a product feature. It reads the host and writes nothing to it. The change set is the only thing that leaves.

## Who uses a jig and why

Designers, engineers and agents who own a UI system, or work inside one. They come with one of five jobs.

| Job | What the jig gives them |
|---|---|
| See a change in context before committing it | The real canvas moves as the constant moves |
| Find which constant drives a thing | Pick an element and the panel shows the constants it reads |
| Hand an exact change to an agent or an engineer | A change set with base, from, to, home and a reason |
| Test edges | Long content, narrow widths, every size, every state, both themes |
| Keep a system honest against its own rules | The host's rules run on every edit and name what broke |

When a request does not say which job it serves, build for the handoff. A tuned value that cannot leave the browser helps nobody.

## Posture

- Discover before building. Read the host's tokens, formulas, rules and components first. The panel is a view of the system that exists.
- The export is the product. A panel that keeps its state in the browser loses it. Build the change set and its copy actions in the first pass, and build everything else around them.
- Say what is missing. A constant with no home, a formula you could not find, a rule the host never wrote down: list each one in your report and in the change set. An honest gap is a finding the owner can act on.
- Stay inside the host. Use its components, its token names and its words for things.

## When this skill does not apply

Three requests look like a jig and are not one.

| The request | What to do |
|---|---|
| Plain Storybook stories: stories or controls for one component's arguments | Write the stories with the project's Storybook setup. A jig is for system constants. |
| A design-token build pipeline: turning token files into CSS, platform files or packages | Use the project's token build tool. A jig only hands a change set to it. |
| An ordinary settings page: preferences an end user saves in the product | Build it as a product screen with the project's form components. |

If the request is one of these, say so in one line and stop. Loading this skill is not a commitment to build a jig.

## Principles

1. Edit constants, never derived values. A wish for a derived value is an override: it is exported as a request, never as a new constant.
2. Discover the host system first: its real tokens, formulas and rules. Create a control only for a constant found in the host's source, and record where it was found as `home`. A value with no source gets `home: null` and is listed as a proposal.
3. Draw a live canvas at true pixels, built from the host project's own components where they exist.
4. Hand back one portable change set: the base it was made against (a hash or a version), the context it was made in, each change with the value it replaced, overrides, check results, effects, and a human note on why. It can be copied as JSON, copied as a prompt with instructions, and pasted back in. A change set made against a different base is refused.
5. Inspect in both directions: pick an element to see the constants it reads, and pick a constant to see what it drives. A selection releases on Esc or a click elsewhere, and explains itself in a tooltip on the page.
6. Use plain names for people, with letters and token names as hints. Keep a glossary, and give each group a help popover.
7. Put checks beside the controls: the system's own contract, and checks the jig proposes, clearly separated. A failing change set can still be copied, and it is marked as failing.
8. Give before and after, undo and redo, presets and a whole-system view, so a change is judged in context.
9. Group concepts in tabs, keep context always visible, fold actions into one menu, and keep the panel usable by keyboard and safe on a narrow screen.

## Workflow

1. Pick the kind from the table in Kinds of jig, and read only that reference.
2. Discover the host. Find its tokens, formulas, rules and components. Before you build anything, write the list: each constant with its `home`, each derived value with its formula, each rule with where it is stated. The reference for the kind says where to look.
3. Build the core loop to the jig contract in Checking a jig: the canvas, the constants, the change set and the checks. Keep three kinds of control visibly apart: context (a viewpoint that changes nothing), constants (the real knobs) and overrides (one derived value pinned, exported as a request).
4. Run the checker and read its exit code. Fix what fails before adding anything.
5. Add what the work asks for, one at a time, from [references/patterns.md](references/patterns.md): inspection in both directions, before and after, undo and redo, presets, a whole-system view, help. Run the checker again after each.
6. Hand off with Copy as prompt. Report the change set, the checker's verdict, and every gap you found: constants with no home, rules the host does not state, links you could not trace.

## Kinds of jig

| Kind | What it tunes | Reference |
|---|---|---|
| system | The constants a whole system derives from | [references/system-jig.md](references/system-jig.md) |
| component | The tokens one component reads, seen across its props, states and variants | [references/component-jig.md](references/component-jig.md) |
| layout | Breakpoints, containers and density, under content stress | [references/layout-jig.md](references/layout-jig.md) |
| theme | Palette, light and dark, contrast and brand variants | [references/theme-jig.md](references/theme-jig.md) |

The kind is the `kind` of the change set and the value of the panel's `data-jig` attribute. When a request spans two kinds, build one jig for the kind that owns the constants being changed.

Shared references, read when the step needs them:

- [references/change-set.md](references/change-set.md): every field, the refusal rules, the prompt export, and how the format sits beside existing ones.
- [references/patterns.md](references/patterns.md): scrub, pick, before and after, undo and redo, presets, tabs, labels and help.
- [references/prior-art.md](references/prior-art.md): the tools people use today, what each is for, and where they fall short, with sources.
- [examples/README.md](examples/README.md): a small worked jig that meets the contract, one large jig built for one system, and a plain-DOM inspector panel to start from.

## The change set

The format is `jig.changeset/1`. Every field is required unless marked.

| Field | What it holds |
|---|---|
| `$schema` | The constant `jig.changeset/1`. An importer keys on it. |
| `kind` | system, component, layout or theme |
| `base` | `system` and `source`, with `sha256` or `version` (or both), and an optional `revision` |
| `createdAt` | When it was exported, as a UTC or offset timestamp |
| `context` | The viewpoint: width, content, theme and the like. It changes nothing. |
| `changes` | Constants that moved: `path`, `from`, `to`, `home`, and optional `label` and `hint` |
| `overrides` | Derived values pinned off their formula: `target`, `from`, `to`, and optional `at`, `formula`, `reason` |
| `checks` | `contract` (the host's own rules, or null when it states none) and `proposed` (the jig's own) |
| `effects` | Derived values that moved as a result. For verifying, not for editing. |
| `note` | The human reason. It may be empty, and the panel always asks for it. |
| `extensions` | Optional. Free space for one tool's own data. |

The full account is in [references/change-set.md](references/change-set.md), and the schema is [schema/changeset.schema.json](schema/changeset.schema.json). Validate a change set with:

```
node scripts/validate-changeset.mjs <file.json>
```

It prints `valid` and exits 0, or prints one `invalid <json pointer>: <message>` line per error and exits 1, or prints `cannot validate: <reason>` and exits 2.

## Maintaining an existing inspector

When extending a host's established inspector, preserve its existing change-set schema, persistence and integration contract unless migration is explicitly part of the task. The skill's new-jig schema/checker is not evidence that an existing host needs replacement.

Keep stable setting IDs independent of display labels. Derive tab/section ownership from one canonical panel schema or the live panel, so exports follow rearrangements without duplicate routing tables. Use one committed-default diff for Copy changes, tab/section counts and empty-state disabling; omit UI-only navigation/debug state. Keep count decorations out of exported names. Preserve displayed units and exact before/after values, version any export-shape change, and treat persistence versioning separately. Reset scope must follow the same setting ownership. Test changed and unchanged groups, reset, restored settings and a round trip through the host's supported export consumer; do not add import functionality solely to satisfy a generic checker.

## Checking a jig

Every jig meets the jig contract, so a person, a script or another agent can check it. The contract is three attributes and two functions.

| Part | Where | Meaning |
|---|---|---|
| `data-jig="<kind>"` | The panel root | This is a jig of that kind |
| `data-jig-canvas` | The live canvas root | This is what the constants drive |
| `data-jig-constant="<path>"` | Each control that edits a constant | The `path` its change would have |
| `window.jig.changeSet()` | Function | Returns the current change set. It is valid at all times and has no changes at load. |
| `window.jig.importSet(text)` | Function | Takes the JSON, or a prompt that holds it in a fenced block. Returns an array of refusal reasons, empty when applied. A refusal applies nothing. |

Two scripts ship with the skill. Both paths are relative to the skill folder.

```
node scripts/check-jig.mjs <page.html or http URL> [--save <file>]
node scripts/validate-changeset.mjs <file.json>
```

If a relative path misses, resolve the skill folder first; do not conclude the script is absent. The skill folder is the folder that holds this file.

The verdict comes from running the script and reading its exit code. Reading the page's source and judging that it conforms is not a check.

| Exit | Meaning | What to do |
|---|---|---|
| 0 | Nothing failed | Read the lines anyway. A `skip` line is a check that did not run. |
| 1 | A check failed | Fix the jig and run it again. Each `fail` line names the check. |
| 2 | It could not run, and prints `cannot check: <reason>` | Walk the seven checks below by hand in a browser, and say in your report that the jig was not machine-checked. |

`check-jig.mjs` needs Playwright, which the skill does not ship. It loads it from the folder you run the command in, then from the page's folder, so run it from a project that has Playwright installed.

The seven checks, in order:

| Check | What passes |
|---|---|
| `load` | No console error and no uncaught page error, from navigation to the end of the run |
| `markers` | One `[data-jig]` with a known kind, one `[data-jig-canvas]`, at least one `[data-jig-constant]` |
| `changeset` | `window.jig.changeSet()` validates, its `kind` equals the `data-jig` value, and `changes` is empty at load |
| `edit` | ArrowUp in the first visible number constant gives exactly one change, with that control's path |
| `refuse-base` | `importSet` refuses that change set once its base identity is altered, and applies nothing |
| `refuse-from` | `importSet` refuses it once the first change's `from` is altered, and applies nothing |
| `round-trip` | `importSet` takes the unaltered change set, and `changes` equals what was exported |

The `edit` check looks for a control that is, or contains, `input[type=number]` or `[role=spinbutton]`. Give every jig at least one number constant of that shape, so `edit` and the three import checks run. With `--save`, the change set captured by `edit` is written to the file, ready for the validator.

A jig is done when the checker exits 0 with no `skip` line, the kind reference's Done when list holds, and the report names every gap.
