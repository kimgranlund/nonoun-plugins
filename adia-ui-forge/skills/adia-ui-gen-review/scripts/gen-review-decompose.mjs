#!/usr/bin/env node
/**
 * gen-review-decompose.mjs — Phase 2 automation for adia-ui-gen-review.
 *
 * For each prompt in gallery-latest.json:
 *   1. Navigate to the gallery page and locate the canvas-ui for that prompt.
 *   2. Wait 2.5s for canvas-ui.processAll() to settle.
 *   3. Screenshot the .gallery-canvas-wrap element.
 *   4. Walk the canvas DOM tree and save raw JSON.
 *   5. Apply the primitive lookup table → sanitized decomposed.json.
 *
 * Trust boundary: this script produces the Phase 2→5 intermediate files.
 * decomposed.json contains ONLY allowlisted attributes (no data-*, aria-*
 * content). Phase 5 (fix plan writing) reads only decomposed.json.
 *
 * This script is skill-owned but operates on the @adia-ai monorepo: run it
 * from the monorepo root (it reads apps/genui/.../gallery-latest.json and
 * writes the review/cycle-N tree there). Requires `playwright` in the
 * monorepo's node_modules.
 *
 * Usage (from the monorepo root):
 *   node ${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-gen-review/scripts/gen-review-decompose.mjs --cycle 1
 *   node ${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-gen-review/scripts/gen-review-decompose.mjs --cycle 2 --group auth
 *   node ${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-gen-review/scripts/gen-review-decompose.mjs --cycle 1 --prompt login-form
 *   node ${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-gen-review/scripts/gen-review-decompose.mjs --cycle 1 --port 5174
 *   node ${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-gen-review/scripts/gen-review-decompose.mjs --dry-run   (validate inputs, no browser)
 *
 * Output (per prompt):
 *   review/cycle-{N}/screenshots/{slug}.png
 *   review/cycle-{N}/raw-dom/{slug}.json
 *   review/cycle-{N}/decomposed/{slug}.json  ← the trust-boundary file
 *
 * Exits 0 on success, 1 if any prompt has a RENDER_FAILURE.
 */

import { chromium } from 'playwright';
import { mkdir, writeFile, readFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { join } from 'node:path';

// The script lives inside the plugin but runs against the monorepo. All
// monorepo paths are resolved from the working directory (the monorepo root),
// not from the script location.
const REPO_ROOT = process.cwd();

// ── CLI ──────────────────────────────────────────────────────────────────────

const args = process.argv.slice(2);
const flag = k => args.includes(`--${k}`);
const opt  = k => { const i = args.indexOf(`--${k}`); return i >= 0 ? args[i + 1] : undefined; };

const cycleNum   = parseInt(opt('cycle') ?? '1', 10);
const groupFilter = opt('group')  ?? null;
const promptFilter = opt('prompt') ?? null;
const port        = opt('port')   ?? '5300';
const dryRun      = flag('dry-run');
const settleMs    = parseInt(opt('settle') ?? '2500', 10);

if (isNaN(cycleNum) || cycleNum < 1) {
  console.error('[decompose] --cycle must be a positive integer'); process.exit(1);
}

// ── Primitive lookup table (from loop-protocol.md §Phase 2) ─────────────────

const TAG_TO_COMPONENT = {
  'card-ui':         'Card',
  'col-ui':          'Column',
  'row-ui':          'Row',
  'grid-ui':         'Grid',
  'field-ui':        'Field',
  'input-ui':        'Input',
  'textarea-ui':     'Textarea',
  'select-ui':       'Select',
  'button-ui':       'Button',
  'badge-ui':        'Badge',
  'tag-ui':          'Tag',
  'text-ui':         'Text',
  'icon-ui':         'Icon',
  'stat-ui':         'Stat',
  'avatar-ui':       'Avatar',
  'list-ui':         'List',
  'list-item-ui':    'ListItem',
  'tabs-ui':         'Tabs',
  'tab-ui':          'Tab',
  'nav-ui':          'Nav',
  'nav-item-ui':     'NavItem',
  'nav-group-ui':    'NavGroup',
  'check-ui':        'Checkbox',
  'switch-ui':       'Switch',
  'slider-ui':       'Slider',
  'progress-ui':     'Progress',
  'progress-row-ui': 'ProgressRow',
  'skeleton-ui':     'Skeleton',
  'alert-ui':        'Alert',
  'modal-ui':        'Modal',
  'drawer-ui':       'Drawer',
  'popover-ui':      'Popover',
  'tooltip-ui':      'Tooltip',
  'divider-ui':      'Divider',
  'breadcrumb-ui':   'Breadcrumb',
  'pagination-ui':   'Pagination',
  'accordion-ui':    'Accordion',
  'timeline-ui':     'Timeline',
  'timeline-item-ui':'TimelineItem',
  'table-ui':        'Table',
  'feed-ui':         'Feed',
  'feed-item-ui':    'FeedItem',
  'empty-state-ui':  'EmptyState',
  'step-progress-ui':'StepProgress',
  'onboarding-checklist-ui': 'OnboardingChecklist',
  'mark-ui':         'Mark',
  'inline-edit-ui':  'InlineEdit',
  'tour-ui':         'Tour',
  'link-ui':         'Link',
  'code-ui':         'Code',
  'rating-ui':       'Rating',
  'image-ui':        'Image',
  'embed-ui':        'Embed',
  'search-ui':       'Search',
  'combobox-ui':     'Combobox',
  'tags-input-ui':   'TagsInput',
  'heatmap-ui':      'Heatmap',
  'chart-ui':        'Chart',
  'upload-ui':       'Upload',
  'visually-hidden-ui': 'VisuallyHidden',
  // Additional primitives
  'accordion-item-ui': 'AccordionItem',
  'action-item-ui':  'ActionItem',
  'action-list-ui':  'ActionList',
  'agent-artifact-ui': 'AgentArtifact',
  'agent-feedback-bar-ui': 'AgentFeedbackBar',
  'agent-questions-ui': 'AgentQuestions',
  'agent-reasoning-ui': 'AgentReasoning',
  'agent-suggestions-ui': 'AgentSuggestions',
  'agent-trace-ui':  'AgentTrace',
  'aside-ui':        'Aside',
  'avatar-group-ui': 'AvatarGroup',
  'block-ui':        'Block',
  'blockquote-ui':   'Blockquote',
  'calendar-grid-ui': 'CalendarGrid',
  'calendar-picker-ui': 'CalendarPicker',
  'chart-legend-ui': 'ChartLegend',
  'chat-input-ui':   'ChatInput',
  'chat-thread-ui':  'ChatThread',
  'color-input-ui':  'ColorInput',
  'color-picker-ui': 'ColorPicker',
  'command-ui':      'Command',
  'context-menu-ui': 'ContextMenu',
  'date-range-picker-ui': 'DateRangePicker',
  'datetime-picker-ui': 'DatetimePicker',
  'demo-toggle-ui':  'DemoToggle',
  'description-list-ui': 'DescriptionList',
  'fields-ui':       'Fields',
  'footer-ui':       'Footer',
  'header-ui':       'Header',
  'inline-message-ui': 'InlineMessage',
  'inspector-ui':    'Inspector',
  'integration-card-ui': 'IntegrationCard',
  'kbd-ui':          'Kbd',
  'list-window-ui':  'ListWindow',
  'loading-overlay-ui': 'LoadingOverlay',
  'menu-divider-ui': 'MenuDivider',
  'menu-item-ui':    'MenuItem',
  'menu-ui':         'Menu',
  'noodles-ui':      'Noodles',
  'number-format-ui': 'NumberFormat',
  'option-card-ui':  'OptionCard',
  'otp-input-ui':    'OtpInput',
  'page-ui':         'Page',
  'pane-ui':         'Pane',
  'password-strength-ui': 'PasswordStrength',
  'pipeline-status-ui': 'PipelineStatus',
  'qr-code-ui':      'QRCode',
  'radio-ui':        'Radio',
  'range-ui':        'Range',
  'relative-time-ui': 'RelativeTime',
  'richtext-ui':     'RichText',
  'section-ui':      'Section',
  'segment-ui':      'Segment',
  'segmented-ui':    'Segmented',
  'skip-nav-ui':     'SkipNav',
  'spinner-ui':      'Spinner',
  'stack-ui':        'Stack',
  'stepper-item-ui': 'StepperItem',
  'stepper-ui':      'Stepper',
  'stream-ui':       'Stream',
  'swatch-ui':       'Swatch',
  'swiper-ui':       'Swiper',
  'table-toolbar-ui': 'TableToolbar',
  'time-picker-ui':  'TimePicker',
  'toast-ui':        'Toast',
  'toc-ui':          'TableOfContents',
  'toggle-group-ui': 'ToggleGroup',
  'toggle-option-ui': 'ToggleOption',
  'toggle-scheme-ui': 'ToggleScheme',
  'toolbar-group-ui': 'ToolbarGroup',
  'toolbar-ui':      'Toolbar',
  'tour-step-ui':    'TourStep',
  'tree-item-ui':    'TreeItem',
  'tree-ui':         'Tree',
  // Native structural elements inside component light DOM — flag as native
  'header':          'NativeHeader',   // should be card-ui slot, not bare <header>
  'section':         'NativeSection',
  'footer':          'NativeFooter',
  'form':            'NativeForm',     // should be wrapped in a primitive
  'a':               'NativeLink',     // should be link-ui
  'ul':              'NativeList',
  'li':              'NativeListItem',
  'p':               'NativeParagraph',
  'span':            'NativeSpan',
  'img':             'NativeImage',    // should be image-ui
  'h1': 'NativeH1', 'h2': 'NativeH2', 'h3': 'NativeH3',
  'h4': 'NativeH4', 'h5': 'NativeH5', 'h6': 'NativeH6',
  // Shell tags — skip but descend
  'canvas-ui':       null,
  'a2ui-root':       null,
};

// Allowlisted attribute names (values from these are safe to include)
const ATTR_ALLOWLIST = new Set([
  'class', 'id', 'slot', 'text', 'label', 'value', 'variant', 'icon',
  'size', 'gap', 'columns', 'type', 'checked', 'disabled', 'readonly',
  'placeholder', 'heading', 'description', 'trend', 'change',
]);

// ── Load gallery data ────────────────────────────────────────────────────────

const galleryPath = join(REPO_ROOT, 'apps/genui/app/gen-ui-gallery/outputs/gallery-latest.json');
if (!existsSync(galleryPath)) {
  console.error('[decompose] gallery-latest.json not found. Run npm run gallery:generate first.');
  process.exit(1);
}

const gallery = JSON.parse(await readFile(galleryPath, 'utf8'));

// Validate required keys
for (const key of ['version', 'generatedAt', 'engines', 'groups']) {
  if (!(key in gallery)) {
    console.error(`[decompose] gallery-latest.json missing required key: "${key}"`);
    process.exit(1);
  }
}

// Build flat prompt list with optional filters
const allPrompts = [];
for (const group of gallery.groups) {
  if (groupFilter && group.slug !== groupFilter) continue;
  for (const prompt of group.prompts) {
    if (promptFilter && prompt.slug !== promptFilter) continue;
    for (const engineKey of Object.keys(prompt.engines ?? {})) {
      const engineData = prompt.engines[engineKey];
      if (!engineData || engineData.dryRun) continue;
      allPrompts.push({ group: group.slug, prompt: prompt.slug, engineKey, engineData });
    }
  }
}

if (allPrompts.length === 0) {
  console.error('[decompose] No prompts matched the specified filters.');
  process.exit(1);
}

// ── Output directories ───────────────────────────────────────────────────────

const outBase = join(REPO_ROOT, 'apps/genui/app/gen-ui-gallery/review', `cycle-${cycleNum}`);
const screenshotDir = join(outBase, 'screenshots');
const rawDomDir     = join(outBase, 'raw-dom');
const decomposedDir = join(outBase, 'decomposed');

if (!dryRun) {
  await mkdir(screenshotDir, { recursive: true });
  await mkdir(rawDomDir,     { recursive: true });
  await mkdir(decomposedDir, { recursive: true });
}

const galleryVersion = gallery.version ?? 'unknown';
const galleryGeneratedAt = gallery.generatedAt ?? null;

console.log(`\n[decompose] cycle-${cycleNum} | gallery-v${galleryVersion} | ${allPrompts.length} prompts | port ${port}${dryRun ? ' | DRY RUN' : ''}`);
if (dryRun) { console.log('[decompose] Dry run complete — no browser launched.'); process.exit(0); }

// Write cycle-manifest.json for provenance before any screenshots are taken
if (!dryRun) {
  const manifestPath = join(outBase, 'cycle-manifest.json');
  await writeFile(manifestPath, JSON.stringify({
    cycleNumber: cycleNum,
    galleryVersion,
    galleryGeneratedAt,
    decomposedAt: new Date().toISOString(),
    promptCount: allPrompts.length,
    port,
  }, null, 2));
}

// ── Playwright run ───────────────────────────────────────────────────────────

const galleryUrl = `http://localhost:${port}/apps/genui/app/gen-ui-gallery/gen-ui-gallery.html`;
const browser = await chromium.launch();
const page    = await browser.newPage();
await page.setViewportSize({ width: 1280, height: 900 });

// Verify gallery is reachable
const res = await page.goto(galleryUrl, { waitUntil: 'networkidle', timeout: 15000 }).catch(() => null);
if (!res || res.status() >= 400) {
  console.error(`[decompose] Cannot reach gallery at ${galleryUrl}. Is the dev server running on port ${port}?`);
  await browser.close();
  process.exit(1);
}
await page.waitForTimeout(1500); // initial render settle

const results = [];
let renderFailureCount = 0;
let idx = 0;

for (const { group, prompt: promptSlug, engineKey, engineData } of allPrompts) {
  idx++;
  const slug = `${group}-${promptSlug}-${engineKey}`;
  process.stdout.write(`  [${idx}/${allPrompts.length}] ${slug.padEnd(50)} `);

  // ── Locate the canvas-ui for this prompt ────────────────────────────────
  // The gallery renders prompts as .gallery-prompt sections with h3 headings.
  // Each has a .gallery-canvas-wrap containing a canvas-ui.
  // We identify by matching the group anchor + prompt h3 text.

  const promptLabel = promptSlug.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());

  // Scroll to the prompt section and wait for canvas settle
  await page.evaluate(({ groupSlug, label }) => {
    const section = document.getElementById(`group-${groupSlug}`);
    if (!section) return;
    const h3s = [...section.querySelectorAll('.gallery-prompt-heading')];
    const target = h3s.find(h => h.textContent.trim().toLowerCase() === label.toLowerCase());
    target?.closest('.gallery-prompt')?.scrollIntoView({ behavior: 'instant', block: 'center' });
  }, { groupSlug: group, label: promptLabel });

  await page.waitForTimeout(settleMs);

  // ── Screenshot ───────────────────────────────────────────────────────────

  const canvasWrapHandle = await page.evaluateHandle(({ groupSlug, label }) => {
    const section = document.getElementById(`group-${groupSlug}`);
    if (!section) return null;
    const h3s = [...section.querySelectorAll('.gallery-prompt-heading')];
    const h3 = h3s.find(h => h.textContent.trim().toLowerCase() === label.toLowerCase());
    return h3?.closest('.gallery-prompt')?.querySelector('.gallery-canvas-wrap') ?? null;
  }, { groupSlug: group, label: promptLabel });

  const canvasWrapEl = canvasWrapHandle.asElement();
  let renderFailure = false;
  let screenshotPath = null;

  if (canvasWrapEl) {
    const box = await canvasWrapEl.boundingBox();
    renderFailure = !box || box.height < 50;
    if (!renderFailure) {
      screenshotPath = join(screenshotDir, `${slug}.png`);
      await page.screenshot({ path: screenshotPath, clip: box });
    }
  } else {
    renderFailure = true;
  }

  // ── Raw DOM walk ─────────────────────────────────────────────────────────

  const rawDom = await page.evaluate(({ groupSlug, label }) => {
    const section = document.getElementById(`group-${groupSlug}`);
    if (!section) return null;
    const h3s = [...section.querySelectorAll('.gallery-prompt-heading')];
    const h3 = h3s.find(h => h.textContent.trim().toLowerCase() === label.toLowerCase());
    const wrap = h3?.closest('.gallery-prompt')?.querySelector('.gallery-canvas-wrap');
    if (!wrap) return null;

    function walk(node, depth) {
      if (depth > 8) return null;
      const tag = node.tagName?.toLowerCase() ?? '';
      if (!tag) return null;
      const attrs = {};
      for (const a of (node.attributes || [])) {
        attrs[a.name] = a.value;
      }
      const children = [...node.children]
        .map(c => walk(c, depth + 1))
        .filter(Boolean);
      return { tag, attrs, children };
    }

    // Walk inside canvas-ui (the a2ui-root subtree)
    const canvasUi = wrap.querySelector('canvas-ui');
    if (!canvasUi) return null;
    return walk(canvasUi, 0);
  }, { groupSlug: group, label: promptLabel });

  const rawDomPath = join(rawDomDir, `${slug}.json`);
  await writeFile(rawDomPath, JSON.stringify(rawDom, null, 2));

  // ── Overflow / clip detection (visual gate) ───────────────────────────────
  // Mechanically detects text truncation and element clipping within the
  // canvas. Runs only when the canvas rendered (renderFailure = false).
  // Results land in decomposed.json as `overflowElements` — a non-empty array
  // is treated as P1 in Phase 4 regardless of the Phase 3 structural score.

  const OVERFLOW_TAGS = new Set([
    'text-ui', 'stat-ui', 'badge-ui', 'field-ui', 'button-ui',
    'label', 'span', 'p', 'h1', 'h2', 'h3', 'h4',
  ]);

  let overflowElements = [];

  if (!renderFailure) {
    overflowElements = await page.evaluate(({ groupSlug, label, overflowTags }) => {
      const section = document.getElementById(`group-${groupSlug}`);
      if (!section) return [];
      const h3s = [...section.querySelectorAll('.gallery-prompt-heading')];
      const h3 = h3s.find(h => h.textContent.trim().toLowerCase() === label.toLowerCase());
      const wrap = h3?.closest('.gallery-prompt')?.querySelector('.gallery-canvas-wrap');
      if (!wrap) return [];

      const found = [];
      function walk(el) {
        const tag = el.tagName?.toLowerCase() ?? '';
        if (overflowTags.includes(tag)) {
          const style = getComputedStyle(el);
          const hasHidden = style.overflow === 'hidden' || style.overflowX === 'hidden';
          if (hasHidden && el.scrollWidth > el.clientWidth + 2) {
            found.push({ tag, clippedWidth: true });
          }
          if (hasHidden && el.scrollHeight > el.clientHeight + 2) {
            found.push({ tag, clippedHeight: true });
          }
        }
        for (const child of el.children) walk(child);
      }
      walk(wrap);
      return found;
    }, { groupSlug: group, label: promptLabel, overflowTags: [...OVERFLOW_TAGS] });
  }

  // ── Primitive lookup + sanitize ──────────────────────────────────────────

  const unknownElements = [];

  function lookupAndSanitize(node) {
    if (!node) return null;
    const tag = node.tag?.toLowerCase() ?? '';
    const component = TAG_TO_COMPONENT[tag];

    // Shell tags (canvas-ui, a2ui-root, plain div wrappers): skip the node
    // itself but descend into children to find the real component tree.
    if (component === null || tag === 'div') {
      const childResults = (node.children ?? []).map(lookupAndSanitize).filter(Boolean);
      if (childResults.length === 1) return childResults[0];
      if (childResults.length > 1) {
        // Multiple siblings at this level — return a synthetic wrapper
        return { component: 'Fragment', attrs: {}, children: childResults };
      }
      return null;
    }

    if (component === undefined) {
      if (tag && !tag.startsWith('#')) unknownElements.push(tag);
    }

    // Allowlisted attrs only — strip data-*, aria-*, and any non-allowlisted
    const safeAttrs = {};
    for (const [name, value] of Object.entries(node.attrs ?? {})) {
      if (ATTR_ALLOWLIST.has(name) && value && value.trim()) {
        safeAttrs[name] = value.trim().slice(0, 200); // cap length
      }
    }

    const children = (node.children ?? [])
      .map(lookupAndSanitize)
      .filter(Boolean);

    return { component: component ?? `UnknownElement:${tag}`, attrs: safeAttrs, children };
  }

  const sanitized = rawDom ? lookupAndSanitize(rawDom) : null;

  // Flatten to component list for decomposed.json
  function flatten(node, list = []) {
    if (!node) return list;
    list.push(node.component);
    for (const child of node.children ?? []) flatten(child, list);
    return list;
  }
  const componentList = sanitized ? flatten(sanitized) : [];

  // Detect root + layout primitive
  const rootComponent = sanitized?.component ?? null;
  const layoutPrimitive = componentList.find(c => ['Column', 'Row', 'Grid'].includes(c)) ?? null;

  // Extract slot positions (one level deep)
  const slotPositions = [];
  function extractSlots(node, parentComponent) {
    if (!node) return;
    const slot = node.attrs?.slot;
    if (slot && parentComponent) {
      slotPositions.push({ parent: parentComponent, slot, child: node.component });
    }
    for (const child of node.children ?? []) extractSlots(child, node.component);
  }
  if (sanitized) extractSlots(sanitized, null);

  // Key attr summary (button text, field labels, etc.)
  const keyAttrs = {};
  function extractKeyAttrs(node) {
    if (!node) return;
    const c = node.component;
    if (!keyAttrs[c] && Object.keys(node.attrs).length) keyAttrs[c] = node.attrs;
    for (const child of node.children ?? []) extractKeyAttrs(child);
  }
  if (sanitized) extractKeyAttrs(sanitized);

  // Write decomposed.json (the trust-boundary file)
  const decomposed = {
    promptSlug,
    groupSlug: group,
    engineKey,
    renderFailure,
    rootComponent,
    layoutPrimitive,
    components: componentList,
    slotPositions,
    attrs: keyAttrs,
    unknownElements: [...new Set(unknownElements)],
    overflowElements,
    screenshotPath: screenshotPath ? screenshotPath.replace(REPO_ROOT + '/', '') : null,
    rawDomPath: rawDomPath.replace(REPO_ROOT + '/', ''),
    generatedAt: new Date().toISOString(),
  };

  const decomposedPath = join(decomposedDir, `${slug}.json`);
  await writeFile(decomposedPath, JSON.stringify(decomposed, null, 2));

  if (renderFailure) {
    renderFailureCount++;
    process.stdout.write(`RENDER_FAILURE\n`);
  } else {
    const overflowNote = overflowElements.length > 0 ? ` | ⚠ ${overflowElements.length} overflow` : '';
    process.stdout.write(`✓ ${componentList.length} components | root: ${rootComponent ?? '?'}${overflowNote}\n`);
  }

  results.push({ slug, renderFailure, componentCount: componentList.length, rootComponent, overflowCount: overflowElements.length });
}

await browser.close();

// ── Summary ──────────────────────────────────────────────────────────────────

const passed = results.filter(r => !r.renderFailure).length;
const failed = results.filter(r =>  r.renderFailure).length;

const overflowPrompts = results.filter(r => r.overflowCount > 0);
console.log(`\n[decompose] Done — ${passed} ok, ${failed} RENDER_FAILURE (gallery-v${galleryVersion})`);
if (overflowPrompts.length > 0) {
  console.log(`  ⚠ ${overflowPrompts.length} prompts with overflow/clip (auto-P1 in Phase 4):`);
  overflowPrompts.forEach(r => console.log(`    ${r.slug} (${r.overflowCount} elements)`));
}
console.log(`  Screenshots → review/cycle-${cycleNum}/screenshots/`);
console.log(`  Raw DOM     → review/cycle-${cycleNum}/raw-dom/`);
console.log(`  Decomposed  → review/cycle-${cycleNum}/decomposed/`);
console.log(`  Manifest    → review/cycle-${cycleNum}/cycle-manifest.json`);

if (failed > 0) {
  console.log('\nRENDER_FAILURE prompts:');
  results.filter(r => r.renderFailure).forEach(r => console.log(' ', r.slug));
  process.exit(1);
}
