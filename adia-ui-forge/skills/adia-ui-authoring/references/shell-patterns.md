# Authoring shell components — Mode 3

Shell components are a distinct authoring shape from single-element primitives. They wrap an entire product surface — admin app, chat streaming surface, code/canvas editor, docs page, simple splash — and exist almost entirely to wire JS behaviors that CSS can't express on top of author-provided DOM.

The **canonical authoring shape is bespoke cluster-namespaced children with state-as-attribute semantics**, per ADR-0023 (bespoke shell-tier children). Every shell-specific concern earns its own custom element with a documented attribute API; state lives as reflected attributes; parent shells coordinate via `querySelector` + slot routing without centralizing child behavior.

Legacy `data-*` shapes (`[data-canvas]`, `<aside-ui slot="leading">`, `<dialog data-command>`) were retired per ADR-0024 (legacy shell shapes retired). A brief pedagogical summary is at §Legacy `data-*` shape (retired) below; new code should follow the bespoke vocabulary.

Absorbed from the legacy `bespoke-shell-children` skill (now a redirect; this file is the deep mode-3 reference).

---

## When to use mode 3

You're authoring a shell when:

- The component holds no visual content of its own — the page author provides everything inside it.
- The component's value is in _behavior_ — keyboard shortcuts, resize handles, ResizeObserver-driven breakpoints, localStorage persistence.
- More than one component instance on a page would feel wrong (one shell per surface).
- You're decomposing a new module-tier shell (chat / editor / simple / docs / future).
- You're adding a new bespoke child to an existing cluster (`<admin-*>`, `<chat-*>`, `<editor-*>`, `<simple-*>`).
- You're reviewing whether shell behavior should be promoted to a bespoke child vs. stay in the host.

You are NOT authoring a shell when:

- The component injects its own structure (header, body, footer slots filled with default markup) — that's a regular composite. Use the `card-ui` pattern (mode 1/2).
- The component renders a single semantic element with cosmetic variants — that's a leaf primitive. Use the button-ui / badge pattern (mode 1).
- You're extracting a cross-cluster reusable element (theme panel, command palette shared across shells) — that's mode 4 (module promotion); see [module-promotion.md](module-promotion.md).

## Architectural principles (read first)

1. **Web components ARE the abstraction.** No `data-*` proxy attributes when a custom element can own the concern.
2. **State-as-attribute.** Every consumer-queryable state is a **reflected attribute** on the relevant element. CSS `:has(<el>[state])`, JS `.hasAttribute('state')`. No threshold-math state inference.
3. **Cluster namespace.** Bespoke children use `<cluster-thing>` (no `-ui` suffix) per ADR-0015. `<admin-*>` for admin shell, `<chat-*>` for chat shell, `<editor-*>` for editor shell, `<simple-*>` for simple shell.
4. **Each child owns one concern.** If a child accumulates 3+ unrelated behaviors, split it.
5. **Backwards-compat window during introduction, then deprecate.** When introducing a NEW cluster's bespoke family, ship 1–2 patch releases where the host reads BOTH legacy and bespoke shapes via `:is()` selectors (so consumers can migrate). Then deprecate the legacy shape in the next MINOR cut — strip the host's legacy reads, drop legacy CSS lifts, document in an ADR. The admin/chat/editor families completed this cycle (ADR-0024) — legacy retired after a ~9-day compat window. Future cluster expansions should follow: introduce → migrate consumers → smoke-probe → deprecate.

## The 4-concern decomposition heuristic

When decomposing a shell, identify behavior in this order:

| Concern | Owner | Becomes |
| --- | --- | --- |
| 1. **Side-region behavior** (resize, collapse, persist, narrow-mode RO) | one child per side region | `<X-sidebar>` (mirrors `<admin-sidebar>`) |
| 2. **Keyboard-driven overlay** (palette, menu, search) | one child per overlay | `<X-command>` or `<X-search>` (mirrors `<admin-command>`) |
| 3. **Cluster-specific orchestration** (LLM streaming, canvas state, etc.) | the host OR a dedicated coordinator | stays in `<X-shell>` if cluster-tied; promote to coordinator if reusable |
| 4. **Structural composition** (chrome bars, scroll surfaces, page bands) | CSS-only stubs | one stub per region (mirrors `<admin-content>` / `<admin-topbar>` / etc.) |

**Default split for a 5-concern shell** — 2-3 JS-bearing + 5-7 CSS-only stubs = 7-10 bespoke children.

## File scaffold per child

### JS-bearing child (~150–250 LOC)

```text
packages/web-modules/<cluster>/<cluster>-<role>/
  <cluster>-<role>.js              # behavior + reflected attributes
  <cluster>-<role>.yaml            # SoT — props/events/slots/states/keywords
  <cluster>-<role>.a2ui.json       # GENERATED via npm run build:components
  <cluster>-<role>.html            # demo shell that fetches .examples.html
  <cluster>-<role>.examples.html   # living examples + behavior wiring tables
  <cluster>-<role>.test.js         # unit tests (8-10 minimum)
```

### CSS-only structural stub

```text
packages/web-modules/<cluster>/<cluster>-<role>/
  <cluster>-<role>.yaml            # SoT — slots only, no props/events
  <cluster>-<role>.a2ui.json       # GENERATED
  <cluster>-<role>.html            # demo shell
  <cluster>-<role>.examples.html   # composition snippet + slot vocabulary
```

NO `.js`, NO own `.css` for CSS-only stubs. They render as unknown `HTMLElement`; styling comes from the parent shell's CSS via tag-presence selectors.

## State-as-attribute conventions

| Pattern | When to use |
| --- | --- |
| **Reflected boolean** `[collapsed]` `[open]` `[streaming]` `[disabled]` `[resizing]` | The state is a binary the consumer might style on |
| **Reflected enum** `[status="connected\|connecting\|error"]` | The state has 2-5 distinct values |
| **Reflected string** `[name="..."]` `[shortcut="cmd+k\|ctrl+k\|both"]` | Author-supplied configuration that other code reads |
| **Property only (no reflect)** | Internal state, perf-sensitive, or values too varied to enumerate |

**Multi-word camelCase props** map to kebab-case attributes via `attribute: '...'` (NOT `attr:` — see Pitfall #1):

```js
static properties = {
  noShortcut: { type: Boolean, default: false, reflect: true, attribute: 'no-shortcut' },
  minWidth:   { type: String,  default: '',    reflect: true, attribute: 'min-width' },
};
```

## CSS bridge pattern

Each cluster's bespoke children get styled via a single bridge file:

```text
packages/web-modules/<cluster>/<cluster>-shell/css/<cluster>-shell.bespoke.css
```

Imported **last** in `<cluster>-shell.css` so its rules layer over the legacy CSS without modification. Don't expand `:is(legacy, slot-ui, ...)` selectors throughout the legacy CSS — that's invasive and makes Phase 3 (legacy removal) harder.

## Step-by-step procedure

### 1. Audit existing shell

Read the host's `.js` file. Identify the 4 concerns + which are already in primitive sub-elements (e.g., `<pane-ui resizable>` already owns pane resize — don't duplicate).

```bash
wc -l packages/web-modules/<cluster>/<cluster>-shell/<cluster>-shell.js
grep -nE 'connected|setup|wire|#' packages/web-modules/<cluster>/<cluster>-shell/<cluster>-shell.js
```

Document the decomposition before writing code. A simple mapping table from legacy author markup to bespoke vocabulary helps.

### 2. Author yamls first

For each bespoke child, write the yaml before the JS. The yaml is the SoT. This forces you to declare the contract before implementing.

### 3. Author the JS (JS-bearing children only)

```js
import { UIElement } from '../../../web-components/core/element.js';

class ChildName extends UIElement {
  static properties = {
    state:     { type: Boolean, default: false, reflect: true },
    config:    { type: String,  default: '',    reflect: true },
    camelProp: { type: String,  default: '',    reflect: true, attribute: 'kebab-prop' },
  };

  static template = () => null;  // stamp nothing — author owns DOM

  #cleanups = [];

  connected() {
    this.#setupBehavior1();
    this.#setupBehavior2();
  }

  disconnected() {
    for (const c of this.#cleanups) c();
    this.#cleanups = [];
  }

  toggle() { /* ... */ return this.state; }

  #setupBehavior1() { /* ... */ }
}

customElements.define('cluster-role', ChildName);
export { ChildName };
```

**The "cleanup-closure pile" pattern** (`#cleanups: [() => …, () => …]`) scales to N drag handles — each handle's setup pushes a closure that removes its specific listeners and undoes any body-level pointer-events mutation. `disconnected()` just drains the pile.

The path to `core/element.js` from `packages/web-modules/<cluster>/<cluster>-<role>/` is **`../../../web-components/core/element.js`** (3 levels up).

### 4. Author tests

Minimum 8-10 tests per JS-bearing child covering: registration, default reflected values, property-attribute round-trip, public API return values, event dispatch, disconnect cleanup, behavior under config attributes, persistence (if applicable).

**Critical test-setup pitfalls**:

```js
// happy-dom returns 0 from getBoundingClientRect — patch in beforeEach
HTMLElement.prototype.getBoundingClientRect = function () {
  const w = parseFloat(this.style?.width) || 240;
  return { width: w, height: 600, top: 0, left: 0, right: w, bottom: 600, x: 0, y: 0 };
};

// happy-dom doesn't ship ResizeObserver — stub it
globalThis.ResizeObserver = class {
  observe() {} unobserve() {} disconnect() {}
};

// happy-dom's <dialog> is partial — polyfill showModal / close / open getter
function patchDialogPolyfill(dialog) {
  let isOpen = false;
  Object.defineProperty(dialog, 'open', {
    get: () => isOpen, set: (v) => { isOpen = !!v; }, configurable: true,
  });
  dialog.showModal = function () { isOpen = true; };
  dialog.close = function () { isOpen = false; this.dispatchEvent(new Event('close')); };
}
```

### 5. Author CSS bridge

For each bespoke tag, declare structural CSS in `<cluster>-shell.bespoke.css`. Reuse tokens from the existing `<cluster>-shell.tokens.css`. Don't introduce new tokens unless the structural concern is genuinely new.

Shells follow the standard two-block `@scope` + L3 token + zero-raw-color rules from [css-patterns.md](css-patterns.md) and [token-contract.md](token-contract.md) — the shell tag stem prefixes its own tokens (`--admin-shell-sidebar-w`, `--chat-shell-header-h`).

### 6. Refactor the host to coordinate

The host loses behavior it used to centralize. It now reflects host-level config like `[mode]`, wires cross-sibling concerns, and forwards events for navigation routing.

**Once the cluster reaches Phase 3** (legacy deprecated, ADR-0024 pattern), the host queries ONLY the bespoke children:

```js
// Bespoke-only (post-Phase-3 — current state for admin/chat/editor):
#findSidebar(name) {
  return this.querySelector(`<cluster>-sidebar[slot="${name}"], <cluster>-sidebar[name="${name}"]`);
}

btn.addEventListener('click', () => {
  const sidebar = this.#findSidebar(name);
  sidebar?.toggle?.();  // direct .toggle() call on the bespoke child
});
```

**During the introduction window** (1–2 patch releases before deprecation), the host reads both shapes via `:is()` selectors with a typeof-check + legacyToggle fallback:

```js
// Compat window (Phase 1 + Phase 2 — pre-deprecation):
static SIDEBAR_SEL =
  ':is(<cluster>-sidebar[slot="leading"], <cluster>-sidebar[slot="trailing"], ' +
  '[data-<cluster>-sidebar], aside-ui[slot="leading"], aside-ui[slot="trailing"])';

btn.addEventListener('click', () => {
  const sidebar = this.querySelector(`:is(<cluster>-sidebar[slot="${name}"], [data-<cluster>-sidebar="${name}"])`);
  if (typeof sidebar.toggle === 'function') sidebar.toggle();
  else this.legacyToggle(sidebar, name);
});
```

**LOC pattern**: the host grows during compat (admin-shell hit ~305 LOC during introduction), then shrinks dramatically at deprecation (admin-shell dropped to ~87 LOC, ≈ −71%). The shrinkage is the architectural signal that the abstraction was correct.

### 7. Update the cluster's `index.js`

```js
export { ClusterShell }   from './cluster-shell/cluster-shell.js';
export { ClusterSidebar } from './cluster-sidebar/cluster-sidebar.js';
export { ClusterCommand } from './cluster-command/cluster-command.js';
// CSS-only stubs don't need exports — they don't register customElements
```

### 8. Run the build + verify gates

```bash
node scripts/build/components.mjs            # picks up new yamls, generates .a2ui.json
node scripts/build/components.mjs --verify   # must say "clean — N files up-to-date"
npm run check:lockstep
npm run verify:traits
npm run smoke:engines
npm run smoke:register-engine
npm run test:a2ui
npx vitest run packages/web-modules/<cluster>/<cluster>-<role>/<cluster>-<role>.test.js
```

### 9. Update the host's `examples.html`

Add a "Basic shape (bespoke — recommended)" section alongside the existing legacy section. Show the full bespoke composition. Add a "State as attribute" section with CSS `:has()` examples + JS API examples + ADR-0023 cross-reference.

### 10. Update sibling demo pages

Add a "Family pattern (forward-looking)" section to the shell's `<X>-shell.examples.html` showing planned bespoke children. This documents the family even before all children land.

### 11. Sweep verification (post-migration grep audit)

After landing a vocabulary migration or deprecation, run a comprehensive grep audit across **all extensions** for the legacy pattern set. Markup-only commits frequently leave **CSS selectors and JS comments** referencing the old vocabulary — they're in different files from the markup, so a markup-only commit looks complete but leaves drift.

```bash
LEGACY_PATTERNS=(
  'adia-editor-ui'  'adia-chat-ui'  'app-shell-ui'  'gen-ui-ui'
  '\[data-canvas\]' '\[data-chat-messages\]' '\[data-chat-input\]'
  '\[data-chat-empty\]' '\[data-sidebar=' '\[data-editor-body\]'
  '<aside-ui slot=' '<dialog data-command'
  'data-pane-side' 'data-pane-grow'  'data-app-shell-toggle'
)
for pat in "${LEGACY_PATTERNS[@]}"; do
  echo "=== $pat ==="
  grep -rln -E "$pat" apps --include='*.css' --include='*.html' \
    --include='*.js' --include='*.yaml' 2>/dev/null
done
```

**0 hits across all patterns** = sweep verified clean. Hits should be acted on:

- Markup hits → update to bespoke vocabulary
- CSS selector hits → update to bespoke selector (tag-name or new attribute)
- JS code hits → update query selectors + remove dead `customElements.whenDefined` deps
- JS comment hits → update to current vocabulary so future readers don't get misled by stale documentation

This step was added after a sweep revealed apps with leftover `adia-editor-ui` + `[data-canvas]` selectors that a markup-only migration missed.

#### Four additional categories the path-only sweep misses

After an apps/playgrounds/catalog reorg (ADR-0026) surfaced 4 categories that survived a full-path substitution sweep. **Full-path grep is necessary but insufficient.** Add these to any vocabulary migration's verification:

##### Category A — Bare-name prose mentions in narrative docs

```bash
LEGACY_NAMES=( 'old-folder-name' 'old-thing-name' )
for n in "${LEGACY_NAMES[@]}"; do
  echo "=== bare '$n' ==="
  grep -rn -E "\b${n}\b" . \
    --include='*.md' --include='*.yaml' \
    | grep -v '/CHANGELOG.md'
done
```

##### Category B — Skill directory names that follow folder-name convention

```bash
find . -type d -name '*-expert' -not -path '*/node_modules/*' \
  | grep -E '(old-name|stale-name)'

for skill in $(find . -name 'SKILL.md' -not -path '*/node_modules/*'); do
  dir=$(basename $(dirname "$skill"))
  name=$(grep '^name:' "$skill" | head -1 | sed 's/name: *//')
  [ "$dir" != "$name" ] && echo "MISMATCH: $skill (dir=$dir, name=$name)"
done
```

##### Category C — JSON metadata fields at filename granularity

Critical: full-path sweeps catch directory moves but miss **file renames within moved directories**.

```bash
# Corpus chunks, sitemaps, catalog manifests — any JSON with file paths.
LEGACY_FILENAMES=( 'old-name.html' 'old-name.contents.html' 'old-name.contents.js' )
for f in "${LEGACY_FILENAMES[@]}"; do
  grep -rn "$f" --include='*.json' \
    | grep -v '/dist/' | grep -v '/node_modules/'
done
```

This is the **highest-impact category** — corpus chunks with stale `source` or `page` fields cause silent harvest miss on the next rebuild (the chunk loads but won't be re-harvestable; no error).

##### Category D — Inventory tables in cross-cutting docs

```bash
grep -ln 'old-name' README.md AGENTS.md docs/ROADMAP.md docs/specs/INDEX.md
```

**Pre-rename verification check**: before the rename, take a snapshot:

```bash
grep -rln 'OLD_NAME' . --include='*.md' --include='*.json' \
  | sort > /tmp/pre-rename-refs.txt
```

After the rename + path sweep, take a fresh snapshot and diff — anything in the post-snapshot is a stale ref to investigate.

**ADR-0026 case study**: a corpus chunk's `page` field pointed at the pre-rename `app-shell.contents.html` inside the post-rename `/playgrounds/admin-shell/app/` directory. Full-path sweep caught the directory rename but missed the filename mismatch within it. Would have caused silent harvest miss on the next rebuild.

## Verification gates per child

| Gate | Where it runs |
| --- | --- |
| `components --verify` clean | local + CI |
| Custom element registers | per-child test file |
| Reflected attribute round-trip | per-child test file |
| Public API present + returns expected | per-child test file |
| Event dispatch | per-child test file |
| Cleanup on disconnect | per-child test file |
| Backwards-compat — legacy markup still works | manual visual smoke against `apps/<X>-shell/` or `site/` |

## Trigger-attribute conventions (bespoke-compatible)

Author-controlled action buttons that the shell wires up follow a consistent convention. These are TRIGGER attributes (on buttons), not state attributes (on shell children) — they still work in the bespoke world:

```html
<button-ui icon="list" data-sidebar-toggle="leading"></button-ui>
```

The shell finds these via `querySelectorAll('[data-sidebar-toggle]')` and binds click handlers that call `.toggle()` on the matching `<admin-sidebar>`. The author owns the button's appearance; the bespoke child owns the behavior.

Other trigger attributes:

- `[data-command-trigger]` — opens `<admin-command>` via `.show()`
- `[data-toolbar-action="<name>"]` — buttons inside `<editor-toolbar>` that bubble `toolbar-action` events

## Persistence (localStorage namespacing)

Sidebar-collapsed state, pane widths, drawer-open state — anything the user customizes — persists in `localStorage`, keyed by the cluster + region:

```js
const KEY = `adia-sidebar:${this.name}:width`;  // adia-sidebar:leading:width
localStorage.setItem(KEY, String(width));
```

Read on `connected()`, write on resize/toggle. Always wrap reads in try/catch — quota errors and disabled-storage modes happen.

```js
#restoreWidth() {
  try {
    const saved = localStorage.getItem(`adia-sidebar:${this.name}:width`);
    if (saved) this.style.setProperty('--width', `${saved}px`);
  } catch { /* storage unavailable */ }
}
```

**Each cluster's persisted state must use a cluster-distinct key prefix.** Admin uses `adia-sidebar-{name}`; chat uses `adia-chat-sidebar-{name}`. Without distinct prefixes, two sidebars sharing the same slot value (`leading`) on different shells would clobber each other.

## Document-level listeners belong to the shell, not the children

`Cmd+K` for the command palette, `Esc` for closing a drawer, `?` for a shortcuts overlay — these listen on `document`, not on the shell element. The shell binds them in `connected()` with `addEventListener` on `document`, removes them in `disconnected()`. NEVER attach `document`-level listeners from a child component (a button-ui etc.) — they'd persist after the child unmounts.

## Custom events for downstream consumers

Pane-resize, breakpoint-change, sidebar-collapse — fire `CustomEvent`s that bubble through the shell so consumers can react:

```js
this.dispatchEvent(new CustomEvent('sidebar-resize', {
  detail: { name: this.name, width },
  bubbles: true,
  composed: false,  // light-DOM: composed=false is the right default
}));
```

Consumers (CodeMirror layout, canvas redraw, dependent UI) listen on the shell or higher up the tree. The shell publishes; it doesn't know who subscribes.

## Pitfalls

1. **`attr:` vs `attribute:`.** The framework uses `attribute: '...'` for camelCase to kebab-case mapping. `attr:` is silently ignored — your custom element won't react to the kebab-case attribute. Always `attribute:`. Every JS-bearing bespoke child has at least one camelCase prop (`minWidth`, `noShortcut`, `proxyUrl`, etc.); the wrong key fails silently.

2. **Path depth in test imports.** From `packages/web-modules/<cluster>/<cluster>-<role>/`, `core/element.js` is **3 levels up** (`../../../web-components/core/element.js`), not 2.

3. **Tagged template literal for `static template = () =>`.** If you stamp a template, use `html` tagged template literal, not a plain backtick string. Plain string fails with "Cannot read 'length' of undefined" inside the framework's template parser. For light-DOM components (the convention here), use `static template = () => null` and construct DOM in `connected()` if needed.

4. **happy-dom `<dialog>` partial support.** Polyfill `showModal` / `close` / `open` getter in tests (see test pitfalls above). The real browser is fine.

5. **Spy timing for synchronous custom-element lifecycle.** `vi.spyOn(document, 'addEventListener')` set BEFORE `mount()` should still catch listeners added in `connected()`, but happy-dom's customElements lifecycle quirks sometimes break this. When in doubt, test the **behavior** (does Cmd+K toggle?) instead of the **mechanism** (was a listener added?).

6. **Don't expand legacy `:is()` selectors.** The temptation when introducing a new cluster is to add `, <X-sidebar>[slot=leading]` to every existing `:is([data-X-sidebar], aside-ui[slot=leading])` selector in the legacy CSS. Resist. Use a new bespoke.css bridge file instead — easier to drop at Phase 3 deprecation. (admin/chat/editor deprecation pass collapsed all `:is(legacy, bespoke)` lifts to bespoke-only in 6 layered CSS files via a single regex pass; would have been 100x more work if lifts were sprinkled inline.)

7. **Host LOC will grow during the compat window, then shrink at deprecation.** When introducing a new cluster's bespoke family, both code paths coexist in the host. Expected (admin-shell hit ~305 LOC during introduction). At deprecation (Phase 3 — see ADR-0024 for the canonical playbook), the host shrinks dramatically: admin-shell dropped to ~87 LOC (−71%). **Don't try to "consolidate" before deprecation lands** — the dual paths are intentional during the migration window.

8. **Sibling cluster siblings.** `web-modules/shell/admin-shell/` lives next to `web-modules/shell/admin-sidebar/` (cluster-namespace siblings). For chat — `web-modules/chat/chat-shell/` next to `web-modules/chat/chat-thread/`. The directory layout makes the cluster family visible at `ls`.

9. **localStorage namespace per cluster.** Each cluster's persisted state must use a cluster-distinct key prefix. Without distinct prefixes, two sidebars sharing the same slot value (`leading`) on different shells would clobber each other. Verify with a test that checks both namespaces are isolated.

10. **Bespoke event names ≠ legacy event names.** When a bespoke wrapper forwards an event from an inner primitive, give it a NEW name (e.g. `composer-submit` from `<chat-composer>` wrapping the inner `<chat-input-ui>`'s `submit` event). If the wrapper re-emits `submit`, the host's listener fires twice (once from the bubble, once from the re-emit). Lesson — pick a bespoke event name (`<wrapper>-<concept>` like `composer-submit`, `sidebar-toggle`, `command-select`) and document the legacy→bespoke mapping in the host's `connected()`.

11. **Delegate to primitives when they already own the concern, but don't lose state-as-attribute.** When a bespoke child wraps a primitive that already does the physical work (e.g. `<editor-sidebar>` wrapping `<pane-ui resizable>`), the bespoke tier still owns: cluster-namespace ID, state-as-attribute (`[collapsed]` reflected via `ResizeObserver` on inner pane), localStorage persistence, public API. Don't reimplement what the primitive does — but don't skip the bespoke tier just because the primitive exists. Principles 4 ("each child owns one concern") + 3 ("cluster namespace") combine here — the bespoke child owns the _cluster-specific framing_ of the primitive's work.

12. **Persist BEFORE snapping, not after.** When `.collapse()` is called on a sidebar, the persisted width must capture the pre-collapse expanded width so `.expand()` can restore it. If you persist after setting `style.width = SNAP_THRESHOLD`, you've overwritten storage with the collapsed value and `.expand()` falls through to its default. Pattern: `if (!this.collapsed) this.#persistWidth();` BEFORE the snap. Caught in editor-sidebar via the `expand() restores from stored width or defaults to 240` test.

13. **Stamping default content "to be helpful."** A shell that injects a default header / nav / footer commits the page author to the shell's visual language. They will copy-paste markup INTO the shell to override; you've now created two sources of truth. Stamp nothing (`static template = () => null`). The exception: a shell MAY append a tiny structural affordance the author can't reasonably write themselves — a resize-handle thumb, for instance. Keep it minimal and clean it up in `disconnected()`.

14. **Document-level keydown handlers on child components.** If a child wants to react to global keys, it should listen for an event the SHELL emits, not bind a document-level listener itself. Otherwise the child outlives its hosting shell, leaks its listener, and starts reacting to keys in surfaces it has no business seeing.

15. **ResizeObserver vs media queries.** Shells respond to _their own_ width, not the viewport. When the shell collapses (because main content gets crowded), the _shell instance_ is narrow — but the viewport may still be wide. Use a `ResizeObserver` on `this` (or on a bespoke child region) to compute breakpoints, and reflect the result as a reflected attribute the CSS can match. Container queries are a complementary tool; ResizeObserver fits when you need _imperative_ state (e.g. moving an element between inline and dropdown placement based on width).

## Examples — 4 canonical clusters

### admin cluster (canonical reference)

- **3 JS-bearing children** — `<admin-shell>` (host coordinator), `<admin-sidebar>` (resize+collapse+persist), `<admin-command>` (Cmd+K palette)
- **7 CSS-only structural children** — `<admin-content>`, `<admin-topbar>`, `<admin-statusbar>`, `<admin-scroll>`, `<admin-page>`, `<admin-page-header>`, `<admin-page-body>`
- **CSS bridge** — `packages/web-modules/shell/admin-shell/css/admin-shell.bespoke.css` (~240 LOC)
- **Tests** — `admin-sidebar.test.js` 10/10, `admin-command.test.js` 9/9

### chat cluster (replicated pattern)

- **3 JS-bearing children** — `<chat-shell>` (host coordinator), `<chat-thread>` (scroll+streaming+empty), `<chat-composer>` (input wrapper+disabled propagation), `<chat-sidebar>` (mirrors admin-sidebar geometry)
- **3 CSS-only structural children** — `<chat-header>`, `<chat-status>`, `<chat-empty>`
- **CSS bridge** — `packages/web-modules/chat/chat-shell/css/chat-shell.bespoke.css`
- **Replication notes** — `chat-sidebar.js` was a near-copy of `admin-sidebar.js` with mechanical `s/admin/chat/g` + cluster-distinct localStorage prefix. The thread and composer required new code because their concerns (scroll-to-bottom, `[streaming]` reflection, `composer-submit` forwarding) are chat-specific. **Pattern mechanically usable for clusters with structural-mirror needs (sidebars) + adapted for cluster-specific concerns.**

### editor cluster (third replication — confirms convention is locked in)

- **3 JS-bearing children** — `<editor-shell>` (host with `[focus-mode]` reflected), `<editor-toolbar>` (`[full-screen]` reflected, click-bubble for `[data-toolbar-action]`), `<editor-canvas>` (`[empty]` + `[focused]` reflected, zoom API), `<editor-sidebar>` (wraps `<pane-ui resizable>` rather than reimplementing drag — see Pitfall #11)
- **2 CSS-only structural children** — `<editor-statusbar>`, `<editor-canvas-empty>`
- **CSS bridge** — `packages/web-modules/editor/editor-shell/css/editor-shell.bespoke.css`
- **Replication notes** — Editor cluster has the **smallest bespoke family** of the three (5 children vs 9 admin / 7 chat) because:
  1. `<pane-ui resizable>` already owns drag (delegation — Pitfall #11)
  2. No command palette (different interaction model than admin)
  3. Toolbar + statusbar suffice for chrome bars (no separate header/status separation like chat)
- **Surfaces 2 new pitfalls** (#11 delegation, #12 persist-before-snap) caught at test time
- **Family pattern proven across 3 distinct shell archetypes** — admin (productivity), chat (LLM streaming), editor (design tooling). Convention is now canonical.

### Phase 3 complete — legacy deprecation

ADR-0024 closes the ADR-0023 arc. All three shell hosts dropped their priority-chain reads of legacy `data-*` / `<aside-ui slot>` / `<dialog data-command>` / `<header>` / `<footer>` shapes. The bespoke vocabulary is now the ONLY recognized authoring shape.

**LOC payoff at deprecation:**

- `admin-shell.js`: ~305 → ~87 LOC (−71%) — host now does only mode reflection + attribute-forwarding
- `chat-shell.js`: simpler `connected()` (drops 4-way `||` chains)
- `editor-shell.js`: simpler `connected()` (drops 2-way `||` chains)
- CSS layered files (`admin-shell.sidebar.css`, `chat-shell.empty.css`, etc.) all `:is(legacy, bespoke)` lifts collapsed to bespoke-only

**Lesson from deprecation:** the backwards-compat priority-chain reads were the right transition mechanism, but they accumulated 6 distinct private methods + 4 private fields + dual event-name listeners in `<admin-shell>` alone. **Keep the compat window short** — ~9 days was enough time to migrate all 6 consumers + prove the pattern via smoke probe, and avoiding longer kept the host code from rotting under the dual-shape burden.

### simple cluster (4th replication — pattern compounds)

The 4th cluster proves the pattern generalizes across **four distinct archetypes** now: admin (productivity), chat (LLM streaming), editor (design tooling), simple (minimal page). 23 bespoke shell-tier children total across the 4 clusters.

**Family:**

- `<simple-shell>` (JS-bearing host) — 2 reflected attrs: `[centered]` (vertical-center content), `[full-bleed]` (drops max-width)
- `<simple-content>` (CSS-only) — article-body container with token-correct vertical rhythm
- `<simple-hero>` (CSS-only) — optional top strip with 3 named slots: `heading`, `lede`, `actions`

**Deliberately minimal**: 1 host + 2 CSS-only children. No sidebars, no chrome bars, no command palette. Use cases: marketing splashes, error pages (404 / 500 / maintenance), thank-you pages, single-card flows (sign-in, password reset).

**Compounding insight:**

| Cluster | Approx. build time | Notes |
| --- | --- | --- |
| admin (1st) | ~4 hours | Inventing the pattern + 10 children |
| chat (2nd) | ~2 hours | Replication confirmed pattern works |
| editor (3rd) | ~2 hours | Confirms convention is canonical; introduces delegation (wraps `<pane-ui>`) |
| simple (4th) | **~30 minutes** | Mechanical follow-template; smallest cluster |

**Lesson**: each successive cluster is dramatically faster than the previous. The 4th cluster used this reference as a checklist + lifted demo HTMLs from the 3rd cluster + ran tests once at the end. **Skills compound when they're maintained.** If you're considering a 5th cluster (e.g., docs-shell — but see the decision-log note below about deferring it), expect ~20 minutes for a thin family or ~45 minutes for a richer one. The pattern is mechanically replicable.

**Decision-log note on docs-shell (deferred):**

A 5th cluster `docs-shell` was considered for documentation pages (markdown rendering, TOC right-rail, frontmatter strip). **Deferred** because `<admin-shell>` already serves the docs surface at `site/index.html` — the only differentiating concern (TOC right-rail) is better served by a `<docs-toc>` element placed in `<admin-shell slot="trailing">` than by a competing shell. Cluster proliferation is a real anti-pattern; introduce new clusters only when a distinct archetype emerges that admin/chat/editor/simple don't cover.

## Legacy `data-*` shape (retired)

The legacy shape used `data-*` region attributes (`[data-canvas]`, `<aside-ui slot="leading">`, `<dialog data-command>`) and CSS selectors that matched those data-attributes. **Retired per ADR-0024.**

Pedagogically the design philosophy was identical to the bespoke shape — behavior-only shells, author-owned DOM, persistence keyed by region, ResizeObserver for breakpoint signals, document-level listeners owned by the shell. The bespoke shape moves all of those concerns onto custom elements with reflected-attribute APIs instead of data-attribute sniffing. See ADR-0024 for the full deprecation rationale and the canonical "introduce → migrate → deprecate" timing.

When you encounter a legacy reference in old documentation or commit history, the migration map is:

| Legacy | Bespoke |
| --- | --- |
| `<aside-ui slot="leading">` inside `<app-shell-ui>` | `<admin-sidebar slot="leading">` inside `<admin-shell>` |
| `<dialog data-command>` | `<admin-command>` |
| `[data-canvas]` inside `<adia-editor-ui>` | `<editor-canvas>` inside `<editor-shell>` |
| `[data-chat-messages]` / `[data-chat-input]` / `[data-chat-empty]` | `<chat-thread>` / `<chat-composer>` / `<chat-empty>` |
| `[data-pane-side]` / `[data-pane-grow]` | `<editor-sidebar>` wrapping `<pane-ui resizable>` |
| `data-app-shell-toggle` (trigger) | unchanged — trigger attributes are still data-\* |

## After implementation

1. Update this reference if you discover new pitfalls
2. Record the cluster's family as an architectural milestone in the repo's journal / decision log
3. Cut a lockstep release using the **adia-ui-release** skill
4. Announce the new family in the team's usual channel
5. **When all consumers have migrated**, file an ADR for the deprecation (see ADR-0024 as the canonical template) and cut a breaking-change release. Don't let the compat window outlive its usefulness.

## Anti-patterns specific to shells (deduplicated)

- **Stamping default content "to be helpful."** Stamp nothing (Pitfall #13).
- **Hand-rolling toggle behavior in the page** instead of using `data-<shell>-toggle`. The shell wires localStorage persistence + the ResizeObserver breakpoint logic; rolling your own re-derives both badly. If the shell's trigger-attribute convention doesn't fit, the shell is missing a feature — request it, don't work around it.
- **Document-level keydown handlers on child components.** Pitfall #14.
- **Persisting state without a cluster-scoped key prefix.** Pitfall #9.
- **Stamping invasive `:is(legacy, bespoke)` lifts in legacy CSS.** Pitfall #6 — use a new bespoke.css bridge file instead.

## Cross-references

- [authoring-cycle.md](authoring-cycle.md) — general 5-step authoring procedure (modes 1 + 2); shell-specific rules layer on top
- [api-contract.md](api-contract.md) — prop naming, reflection policy
- [css-patterns.md](css-patterns.md) — two-block `@scope`, variants vs modes
- [lifecycle-patterns.md](lifecycle-patterns.md) — teardown patterns; the cleanup-closure pile and document-listener rules above layer on top
- [token-contract.md](token-contract.md) — zero-raw-color + L3 alias rules apply identically to shells
- [module-promotion.md](module-promotion.md) — mode 4, the _different_ activity of lifting a cross-cluster reusable element (theme panel, command palette) into a shared module
- ADR-0023 — bespoke shell-tier children architectural rationale
- ADR-0024 — legacy shell shapes retired (the canonical deprecation playbook)
- ADR-0015 — `<cluster-thing>` naming convention (no `-ui` suffix for bespoke children)
- the **adia-ui-factory** plugin — the _consumer_ view: how to compose with these shells once they exist
