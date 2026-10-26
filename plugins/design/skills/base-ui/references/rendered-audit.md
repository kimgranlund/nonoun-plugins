# Consumer contract retrieval and geometry audit

Map the components needed by the next feature to contract IDs before implementation. Retrieve `component-context.mjs --shared` once and exact records in bounded batches. Repeat for newly introduced families, including JavaScript-created content. Do not assume a native element has no kit contract: details/summary maps to disclosure; buttons map to actions. Known correct markup is `details.disclosure__root > summary + div.disclosure__body.flow__root`. List spacing does not provide internal spacing for each list item; use an inner flow for multi-part evidence steps.

## Discover and audit the generated app

Use the browser resolver described in SKILL.md once. The commands below require its installed Playwright module path. `--executable /known/browser` supports an explicitly located installed Chromium when the default bundled binary is absent; no downloads occur. A missing browser leaves rendered verification unverified.

```
python3 scripts/run.py audit-rendered.mjs /absolute/app.html /absolute/playwright --discover
python3 scripts/run.py component-context.mjs --records actions,disclosure --record-only
python3 scripts/run.py audit-rendered.mjs /absolute/app.html /absolute/playwright --contracts actions,disclosure
```

Use the IDs actually retrieved, including other detected families. Discovery reports families from declared kit classes plus common native controls in the current DOM; it is a backstop, not an exhaustive semantic classifier or evidence that records were read. Review undiscovered custom components manually. The commands execute the authored local application, so use only the task's trusted artifact.

The audit exits nonzero on findings. It checks initial and individually expanded disclosures at320,390,768 and1440 widths, each with normal and doubled computed text, retaining observed states. Missing body wrappers, body margin drift, touching/overlapping vertically stacked body or evidence-list content, and body-width overflow are actionable. Gap findings require inspection when touching content is intentional. Sidebar disclosure composition is excluded from standalone disclosure rules.

This is a bounded consumer audit, not a replacement for task interaction tests. It does not navigate filters, choose records, load application data, or prove every component's geometry. For a dynamic app, exercise those states through user interactions and run the audit on the resulting DOM. Import the serializable function into the existing browser check:

```js
import {auditRendered} from '/absolute/base-ui/scripts/lib/audit-rendered.mjs';
// families comes from references/style/components/contract.json, read in Node.
// retrieved contains only family IDs whose records were read during authoring.
await page.getByText('Evidence', {exact:true}).click();
const result = await page.evaluate(auditRendered, {families, retrieved});
assert.equal(result.issues.length, 0, JSON.stringify(result));
assert(result.disclosureStates.some(s => s.open && s.visible));
await page.screenshot({path: '/absolute/output/expanded-evidence.png'});
```

Capture and inspect the screenshot while the affected content is still open. Switching decisions or filtering may replace it. Test the final content at narrow/wide widths and relevant schemes; successful clicks or no document overflow alone do not establish correct spacing. Keep closed/open coverage separate. The CLI cannot prove retrieval, visual inspection, unvisited states, all-browser behavior, or author compliance. Report those limits explicitly.

## Build boundary

compileControls (and therefore build.mjs) enforces the disclosure markupRule from the component registry for static markup, with the declared sidebar exception. Malformed anatomy fails before writing an artifact and points to the exact contract retrieval command. Controller-generated DOM is not statically parsed: use the rendered audit after those states are created. Both checks consume the same registry rule. This is disclosure structural enforcement, not general geometry certification.

Nested prose also needs a width budget: base-ui provides `reading-flow__root` on one outer padded region; see `base-ui/references/reading-regions.md`. Narrow regions share one inline margin rather than accumulating it at every depth. The rendered audit enforces a bounded 24ch prose floor in expanded states.

Before each geometry audit, await `document.fonts.ready`, including after dynamically introducing font roles. Offline face verification is documented in `references/bundled-fonts.md`.

Compact table selection cells also report `SELECTION_COLUMN_OVERFLOW` when visible text extends beyond its cell. Use the collections selectionColumn contract for accessible naming; horizontal table scrolling does not excuse content overlapping adjacent cells.

Maintained interval-timeline renderers expose numeric endpoints/domain. The audit checks proportional span/offset independently of label width and reports `INTERVAL_DOMAIN` or `INTERVAL_GEOMETRY`. Time-label truth and missing-data interpretation remain application responsibilities.

For final visual composition acceptance, use the [rubric index and review checklist](review/index.md). Record alignment, grouping, density and wrapping observations on the delivered artifact; zero audit findings do not establish those judgments.

SELECT_ANATOMY checks single-value native selects, including dynamic markup, for the native-select wrapper and decorative indicator. FIELD_ACTION_ANATOMY and FIELD_ACTION_ALIGNMENT check the opt-in field-action__root composition; they do not infer the intent of arbitrary toolbars.

CONTROL_TEXT_RAIL checks actual text starts in opt-in control-rail__root compositions. Inspect boxed and narrow flat modes; matching border edges does not prove label alignment.

`SELECT_TEXT_FIT` measures every native single-select option against the computed closed-control content width, including letter spacing. Wait for fonts; exercise dynamic option sets and enlarged text. This is a conservative text-width check, not inspection of the platform popup. Retrieve native-select.contentFit for repair choices.

The maintained CLI now applies the text-size matrix by default; importing auditRendered alone still checks only the current DOM. Reuse `scripts/lib/text-scale.mjs` in task tests to apply a non-compounding computed-text probe. This is not native browser zoom and does not replace theme/state/visual review.

ACTION_APPEARANCE catches the unsupported ghost class on kit buttons; use data-appearance="ghost". Passing color contrast does not establish correct action emphasis.

A direct `li > details.disclosure__root` intentionally joins summary and body at one boundary. The list-content gap check excludes that boundary; expanded body anatomy, margins and internal content gaps remain audited.

SELECT_INDICATOR_BOUNDS checks the rendered decorative indicator against the native select frame. Wrapper anatomy alone cannot catch a consumer width:auto override that leaves the caret outside the control. Keep the select filling its wrapper; size the wrapper when needed.

## Artifact capture workflow

The maintained reference-site workflow is documented in `/Users/kimba/Projects/ui-kit/apps/site/docs/artifact-review.md`. Run its artifact-review runner after rebuilding, inspect the gallery across all inventoried pages/canvases and explicit expanded states, and retain visual judgments independently of rendered-contract findings. Home textarea/composer and interaction-state examples require canvas boundaries. Dedicated keyboard, geometry and responsive checks remain part of verification.

Native Select label-fit: fixed-width controls check all visible option labels against the available text width. A `field-sizing: content` control checks the current selected label, because choosing another option changes its width. Consumers must visit alternate selections for full coverage; unvisited selections are not certified.
