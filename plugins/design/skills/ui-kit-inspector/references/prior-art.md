# Prior art

What people use today to tune and inspect a UI, what each tool is for, and where each stops. Read this when you need to explain what a jig adds, or when a host already uses one of these tools and the jig must sit beside it.

The sources were read on 2026-10-13. Tools change, so read a source again before you build on a detail. Where this file is silent about a tool's behaviour, the research did not confirm it.

## Three groups that do not meet

| Group | Tools | What the group does |
|---|---|---|
| Parameter panels | Storybook Controls, Leva, Tweakpane, dat.GUI, lil-gui, Theatre.js | Change a parameter and see the result at once |
| Inspectors | Chrome DevTools, Firefox DevTools, Figma Dev Mode | Show what styles and variables an element has |
| Token pipelines | Figma variables, Tokens Studio, Style Dictionary | Hold token values and turn them into outputs |

None of the pages read carries a change as from, to, base and reason in one portable object. A jig joins the three: a panel over system constants, inspection in both directions, and a change set a pipeline or an agent can take.

## Parameter panels

| Tool | What it is for | What leaves it | Source |
|---|---|---|---|
| Storybook Controls | A panel to interact with a component's arguments live, without writing code | A change can be saved as a new story or back into the story file. Complex values such as JSX do not sync or fit in the URL. | https://storybook.js.org/docs/essentials/controls |
| Storybook args in a URL | Carrying args as `args=key:value;key:value` | Limited to alphanumerics, spaces, underscores and dashes | https://storybook.js.org/docs/writing-stories/args |
| Leva | A React GUI built on a `useControls` hook, with many input kinds, keyboard access and plugins | Not stated in the pages read | https://github.com/pmndrs/leva and https://github.com/pmndrs/leva/blob/main/docs/getting-started/introduction.md |
| Tweakpane | A compact pane for fine-tuning parameters and monitoring value changes | State goes out and back through `exportState()` and `importState()` | https://tweakpane.github.io/docs/ and https://tweakpane.github.io/docs/misc/ |
| dat.GUI | A lightweight controller library for JavaScript | `getSaveObject` returns the state as JSON, `load` takes a saved state, and `preset` names a set of saved values | https://raw.githubusercontent.com/dataarts/dat.gui/master/API.md |
| lil-gui | An interface for changing the properties of any JavaScript object at runtime | `gui.save()` returns current values only and `gui.load()` restores them. `reset()` returns to initial values. Dedicated presets were dropped in favour of save and load. | https://lil-gui.georgealways.com/ |
| Theatre.js Studio | A development-only editor | State lives as JSON in `localStorage` while the studio is open. It is exported as a file and passed to the project for production. | https://www.theatrejs.com/docs/latest/manual/projects and https://www.theatrejs.com/docs/latest/manual/Studio |

lil-gui also separates `onChange`, which fires on every change, from `onFinishChange`, which fires once the change is done, and `listen()` shows values changed outside the panel.

The line between a jig and Storybook Controls: Controls is scoped to one component's args. A jig edits system constants, so the change is to the system and not to one story.

## Inspectors

| Tool | What it is for | Source |
|---|---|---|
| Chrome DevTools, Changes panel | Shows a diff of CSS, JS and HTML edits made inside DevTools, with copy and revert per file. Edits vanish on reload unless Local overrides or Workspaces are used. | https://developer.chrome.com/docs/devtools/changes |
| Chrome DevTools, Styles | Hovering a custom property shows its value, a `var()` link jumps to the declaration, and `:hov` forces element states | https://developer.chrome.com/docs/devtools/css/reference |
| Firefox DevTools | The Computed view expands a property to the rule that set the value, with file and line. Its Changes pane tracks rules-view edits only and offers Copy Rule. Hovering a CSS variable name shows the stored value. | https://firefox-source-docs.mozilla.org/devtools-user/page_inspector/how_to/examine_and_edit_css/index.html |
| Figma Dev Mode | Inspect shows the styles and variables on a selected layer, with generated code. Compare changes diffs a frame against earlier versions. Annotations carry designer notes, and Ready for dev marks handoff state. | https://help.figma.com/hc/en-us/articles/15023124644247-Guide-to-Dev-Mode |

## Token pipelines

| Tool | What it is for | Source |
|---|---|---|
| Figma variables | Reusable values with collections and modes, for example light and dark. They can reference other variables and be scoped. Import and export go through the plugin and REST APIs. | https://help.figma.com/hc/en-us/articles/15339657135383-Guide-to-variables-in-Figma |
| Tokens Studio | A Figma plugin to change tokens and see the changes applied to the whole document or its styles. It supports references and math in values, themes, Git sync, and DTCG or legacy export. | https://docs.tokens.studio/ |
| Style Dictionary | A build pipeline driven by config, not a live editor: parse, merge, preprocess, transform, resolve aliases, format, run actions | https://styledictionary.com/info/architecture/ |
| Style Dictionary, `outputReferences` | Keeps references in CSS, SCSS and Less output, but not JSON. The docs advise against it when a token was transitively transformed or its target was filtered out. | https://styledictionary.com/reference/hooks/formats/ |

Style Dictionary and Tokens Studio are the neighbours a change set is handed to. A jig never replaces them.

Design-system playgrounds published by design systems are not covered here. The research could not read a primary source for one.

## The job people come with

Across the panels, the stated job is the same: change a parameter and see the result at once, without editing code. Sources: https://storybook.js.org/docs/essentials/controls, https://tweakpane.github.io/docs/ and https://lil-gui.georgealways.com/.

## Common failures, and what the jig does about each

| Failure | Evidence | What the jig does |
|---|---|---|
| A change cannot be handed off | DevTools edits are lost on reload by default (https://developer.chrome.com/docs/devtools/changes). Theatre.js state sits in localStorage until exported (https://www.theatrejs.com/docs/latest/manual/projects). | The export is the product: Copy JSON and Copy as prompt are built first |
| No record of what a value replaced, or why | lil-gui's save object and a JSON Patch `replace` hold new values only (https://lil-gui.georgealways.com/, https://www.rfc-editor.org/rfc/rfc6902). Among the tools read, only the DevTools Changes diff and Figma's Compare changes show before and after, and neither has a reason field (https://help.figma.com/hc/en-us/articles/15023124644247-Guide-to-Dev-Mode). | Every change carries `from`, and the change set carries `note` |
| Edits land on derived values | An inference from two sources: DevTools edits the declaration on an element, and its Changes panel copies CSS for a file, so nothing steers the edit to the constant a value derives from (https://developer.chrome.com/docs/devtools/css/reference). Style Dictionary shows the same tension from the build side, where a kept reference can undo a transform (https://styledictionary.com/reference/hooks/formats/). | Controls exist for constants only. A wish for a derived value is an override. |
| The panel drifts from the real system | Practitioner articles name hard-coded values under deadline, renames that do not propagate, and code-only changes as causes. A vendor audit of 375 sites reports a median of 38% of CSS values referencing tokens (https://www.designsystemscollective.com/token-drift-is-real-452d63fd8dcc, https://www.designsystemscollective.com/design-token-drift-we-audited-375-sites-only-7-5-got-it-right-78890bfbb9de). These are secondary and vendor sources, so treat them as directional. | The canvas is the host's real components, and every control has a `home` in the host's source |

## Formats for carrying a change

| Format | Status and shape | What it has no place for | Source |
|---|---|---|---|
| DTCG Format Module 2025.10 | A Final Community Group Report dated 28 October 2025, considered stable. A token is an object with `$value`. Aliases are `{group.token}` or a JSON Pointer `$ref`. Files are `.tokens` or `.tokens.json`, media type `application/design-tokens+json`. | A diff, an old value, a base version or hash, an intent field, formulas or computed values. `$extensions` is the place for tool data, under a vendor key (a reverse domain name is recommended). | https://www.designtokens.org/tr/2025.10/format/ |
| DTCG Resolver Module 2025.10 | Handles contexts such as light and dark with sets, modifiers and a `resolutionOrder` in which later entries override earlier ones | A token base: its `version` field names the format version | https://www.designtokens.org/tr/2025.10/resolver/ |
| JSON Patch, RFC 6902 | An ordered list of `add`, `remove`, `replace`, `move`, `copy` and `test` operations, media type `application/json-patch+json`. `test` asserts the value at a path, and a failed test leaves the document unchanged. | An old value on `replace`, a base identity, a reason. The RFC's base check is the HTTP `If-Match` header, outside the patch. | https://www.rfc-editor.org/rfc/rfc6902 |
| JSON Merge Patch, RFC 7396 | A partial document that mirrors the target, media type `application/merge-patch+json`. `null` means remove, and arrays are replaced whole. | An old value, a base identity, intent | https://www.rfc-editor.org/rfc/rfc7396 |

The DTCG editor's draft (https://www.designtokens.org/tr/drafts/format/) says not to implement it. Use 2025.10.

A `test` followed by a `replace` on the same path expresses from and to, and refuses a mismatched base value. That reading is an inference from the two operation definitions in RFC 6902. How the change set uses these formats is in [change-set.md](change-set.md).

## Interaction patterns and where they come from

| Pattern | Precedent | Source |
|---|---|---|
| Scrub | Bret Victor named it in 2011: adjust a number by dragging sideways on it, with results recalculated at once | https://worrydream.com/ScrubbingCalculator/ |
| Keyboard steps | Chrome and Firefox agree: Up or Down is 1, Shift is 10, Alt on Mac (Ctrl in Firefox on Windows and Linux) is 0.1, and a further modifier gives 100. Chrome's drag-to-change on length values is deprecated as of Chrome 123. | https://developer.chrome.com/docs/devtools/css/reference and https://firefox-source-docs.mozilla.org/devtools-user/page_inspector/how_to/examine_and_edit_css/index.html |
| Element to constant | Firefox Computed view to rule, Chrome `var()` link to declaration, Figma Inspect listing the variables on a layer | The three inspector sources above |
| Constant to elements | None of the pages read shows it. It is the jig's own pattern. | None |
| Before and after | The DevTools Changes diff with revert, and Figma's Compare changes | https://developer.chrome.com/docs/devtools/changes |
| Presets and reset | dat.GUI `preset`, lil-gui save and load with `reset()`, and Storybook saving a control state as a named story | The parameter panel sources above |

How to build each pattern is in [patterns.md](patterns.md).
