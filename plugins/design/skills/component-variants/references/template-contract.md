# Standalone review integration contract

## Author the component; build the shell

The maintained `assets/review.html`, `assets/shell.css` and `assets/review-support.mjs` own the review interface. Create a source directory with `review.mjs` and local preview documents/assets. Build to a fresh directory:

```sh
node /path/to/component-variants/scripts/build.mjs SOURCE_DIRECTORY NEW_OUTPUT_DIRECTORY
```

Serve output over local HTTP. The builder copies source files without changing them, supplies `index.html` and the byte-for-byte helper, supplies `preview.css`, and records `ui-kit.lock.json`. Those four names are reserved at source-root level. Do not copy unrelated project files into the source directory. Keep source/output separate; earlier artifacts are never overwritten.

`review.mjs` exports a default configuration:

```js
export default {
  id: 'typeface-picker', revision: 3, title: 'Choose a typeface',
  brief: 'Compare ways to find one choice.',
  baseline: 'Describe the exact implementation, fixtures and token source.',
  context: () => ({stateModel: 'independent'}),
  variants: [{
    id: 'A', name: 'Compact popover',
    rationale: 'Keeps the form compact.', tradeoff: 'Results cover nearby content.',
    src: './popover.html', previewHeight: 420
  }]
};
```

Each preview is a complete local HTML document with its own tokens, assets and behavior. Link the builder-supplied `./preview.css` for box sizing, hidden-element behavior and hidden scrollbar chrome. Keep overflow scrolling functional. Place preview documents at source root for the paths below; nested documents adjust paths to the output root.

Use this small entry pattern (the builder provides both shared files; do not copy or rewrite them):

```html
<link rel="stylesheet" href="./tokens.css">
<link rel="stylesheet" href="./preview.css">
<script type="module">
import {registerPreview, phosphorIcon} from './review-support.mjs';
// Construct your component and load its fixtures here, then register it.
// Awaited fixture loading is supported: registerPreview signals readiness explicitly.
registerPreview({
  get element() { return dialog.open ? dialog : triggerSurface; },
  readState: () => ({selected, query: input.value, open: dialog.open, requestedWidth}),
  setTheme(scheme) { document.documentElement.dataset.theme = scheme; }
});
</script>
```

The shell accepts an API already exposed at frame load, or waits up to 10 seconds for `registerPreview`. A timeout reports failed startup; it never invents state. `element` must already exist and `readState` must be synchronous. Static local imports and HTML asset paths are checked at build time; computed URLs still require a browser check.

The helper sets the preview root's `color-scheme` and calls optional `setTheme` with resolved `light` or `dark`. System follows OS changes; manual choices override both shell and frames. A CSS `prefers-color-scheme` query still describes the OS: use scheme-aware tokens or the callback for explicit overrides. Open standalone starts a separate instance using the preview's own defaults; it does not transfer live state or feedback.

Previews fit body content automatically; avoid viewport-relative body heights. An optional finite positive `previewHeight` sets a minimum, not a fixed viewport; inspect scrolling rather than hiding overflow to make it pass. Dialogs stay inside their frame, so also test Open standalone when full-page modality matters. Preview width controls belong to the component document and must change the component being measured. No parent styles or full base-ui CSS are injected into previews. Same-origin frames are trusted local code, not a security sandbox.

## Shared behavior and context

One review per shell, initialized once. `initReview` retains legacy `mount(container)` support for same-document hosts; the standalone route uses `src` for isolation. Do not replace generated preference or note controls. Required shell IDs remain `theme`, `variants`, `combine`, `clear`, `copy`, `show`, `status`, `export`.

The component owns selection, keyboard behavior, focus and reset. `element` is the actual measurable component or open overlay, never the iframe. Width is the border box, including padding and borders, clamped to its viewport. `readState()` is synchronous and returns current structured-cloneable facts. For asynchronous state changes that do not emit a user event, dispatch `reviewstatechange` on the preview document so an open export refreshes. Live facts are always reread when exporting or editing notes.

The helper owns preferences, feedback persistence and snapshots. Notes retain their edit-time context; export separately includes current context. A dismissed overlay is closed by the time a note is typed. Use Part or state to describe an earlier view; do not substitute historical facts for live state. Component state is not persisted by the shell.

## Base-ui dependency

Install base-ui beside this skill. `scripts/build.mjs` verifies its descriptor, source integrity and the committed `ui-kit.lock.json` identity before output. It consumes `foundationCSS` and `compileControls()` through the kit API. The full component stylesheet is not used. Review feedback semantics and shell-specific styling remain owned here.

For an intentional base-ui update, inspect changes and run affected shell checks, then update this skill's lock with the reviewed `describeKit()` identity. Run `node scripts/check-build.mjs` for build/dependency/preservation guards; rendered checks remain separate. Generation never updates the lock, installs packages or copies compatibility files. No changes to base-ui or wireframe-review are required for normal variant authoring.

## Integration proof

Check each frame loads and exposes its API, then exercise actual component actions and Show feedback text by pointer and keyboard. Check both themes, narrow component and browser widths, note retention, snapshot versus current context, and clipboard success or selectable fallback. Compare preview computed styles with its standalone page to verify isolation. Inspect actual renders; source parity and kit identity do not prove usability. Report failed prerequisites and unexecuted checks separately.

For native modal focus order or ambiguous native-select keyboard results, use the targeted [native-control checks](native-control-checks.md). Classify programmatic value setters, `selectOption`, and dispatched events as **synchronization probes**, excluded from operability measurements; keep their narrower state-sync results.

## Popup visibility smoke

Execute `checkPopupVisibility` from the supplied helper against the actual generated popup during browser verification, and save its results for the exercised actions. Importing it, testing a separate fixture, or inspecting state flags is not evidence that the component passed. A verification-only observer may record results after real events without changing component state. After real pointer activation and a rendering frame, call `checkPopupVisibility({trigger, popup, open: true})`. After Escape, call it with `open: false` and verify focus returned to the trigger. Repeat with a no-results query, then reopen. It throws if expanded state disagrees with DOM visibility or an open surface is entirely outside the viewport. Also inspect clipping and usable controls; this small assertion does not prove accessibility or unobscured hit targets. Do not call component show/hide functions to simulate activation.

`previewHeight` is a minimum. The shared shell grows to fit document content and the registered component surface, avoiding a fixed-height iframe scrollbar. Keep preview body height content-driven (no `100vh` or percentage-height dependency on the growing frame). For ordinary pickers, only the results list should have a bounded scrolling region; chips and preview cards grow naturally. Explicit viewport-dependent modal behavior should be tested through Open standalone.
