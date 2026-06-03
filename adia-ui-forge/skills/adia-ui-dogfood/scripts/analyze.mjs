#!/usr/bin/env node
/**
 * Dogfooding analyzer — walks every `/site/components/*` demo page in a
 * headless browser and runs visual-correctness probes that type-checks
 * and tests don't catch.
 *
 * Probes:
 *   1. Zero-area     — `*-ui` elements that render at 0×0 (e.g. parent
 *                      `display:none`, children moved into an overflow
 *                      popover, contents collapsed).
 *   2. Transparent   — swatches/badges/indicators with known
 *                      "should-be-colored" semantics whose computed
 *                      background is `rgba(0,0,0,0)` (chart-legend bug
 *                      class — a fallback token that doesn't resolve).
 *   3. Empty-control — form controls (`input-ui`, `search-ui`, etc.)
 *                      whose `connected()` should have stamped an
 *                      `<input>` or `[contenteditable]` but didn't.
 *   4. Synonym-attr  — known synonym-attribute / synonym-slot drift
 *                      classes documented in
 *                      `docs/conventions/attribute-api-migration.md`.
 *   5. Console       — errors + deprecation warnings during page
 *                      load + 800ms settling.
 *
 * Output:
 *   docs/reports/dogfooding-YYYY-MM-DD.md  (or path from --out)
 *   Severity levels: critical (page broken), warning (likely-broken),
 *   info (drift, deprecation, non-blocking).
 *
 * Usage (run from the framework monorepo checkout):
 *   node "$SCRIPT" --filter chart-legend  # one page
 *   node "$SCRIPT" --port 5173            # custom port
 *   node "$SCRIPT" --out /tmp/report.md   # custom path
 *   node "$SCRIPT" --quiet                # report only
 * where SCRIPT is this file's path
 * (`${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-dogfood/scripts/analyze.mjs`).
 *
 * Repo root: the monorepo whose `site/sitemap.json` is swept. Resolved from
 * `$ADIA_REPO_ROOT` if set, else the current working directory — so the
 * script targets the user's checkout, not the plugin install location.
 *
 * Assumes the dev server is already running. Spin one up first:
 *   npm run dev    # in a separate terminal
 */

import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { join } from 'node:path';
import { chromium } from 'playwright';

// The framework monorepo whose demo pages are swept. The script ships inside
// the plugin but operates on the user's checkout, so the repo root is the
// invocation cwd (or $ADIA_REPO_ROOT) — never a path relative to this file.
const REPO_ROOT = process.env.ADIA_REPO_ROOT || process.cwd();

// ── Args ──────────────────────────────────────────────────────────────────

const args = process.argv.slice(2);
const argVal = (flag) => {
  const i = args.indexOf(flag);
  return i >= 0 && args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : null;
};
const FILTER = argVal('--filter');
const PORT = parseInt(argVal('--port') || '5173', 10);
const QUIET = args.includes('--quiet');
const today = new Date().toISOString().slice(0, 10);
const OUT = argVal('--out') || join(REPO_ROOT, 'docs/reports', `dogfooding-${today}.md`);

const log = (...m) => { if (!QUIET) console.error(...m); };

// ── Component contracts (what each component MUST stamp at render) ────────
//
// Narrow on purpose: most AdiaUI components are *the* interactive surface
// (role="button" + tabindex + own listeners), not host-of-native-control.
// Listing them here as "must have a <button> child" produces 300+ false
// positives. The genuinely-stamping components are input-ui (creates an
// `<input>` or `<span contenteditable>`) and search-ui (wraps input-ui).

const STAMP_CONTRACTS = {
  'input-ui': {
    reason: 'connected() should stamp <input slot="text"> or <span slot="text" contenteditable>',
  },
  'search-ui': {
    reason: 'connected() should stamp <input-ui type="search"> internally',
  },
};

// ── Selectors that should resolve to a non-transparent background ─────────
//
// `[data-swatch]`, semantic-variant pills/buttons, and chart indicators.
// rgba(0,0,0,0) on these = bug (the chart-legend class).

const COLORED_SELECTORS = [
  // chart-legend / chart-tooltip swatches
  '[data-swatch]',
  '[data-indicator]',
  // semantic variants on tag-ui / button-ui / alert-ui
  'tag-ui[variant=primary]',
  'tag-ui[variant=success]',
  'tag-ui[variant=warning]',
  'tag-ui[variant=danger]',
  'tag-ui[variant=info]',
  'button-ui[variant=primary]:not([disabled])',
  'button-ui[color=danger]:not([disabled])',
];

// ── Synonym-attribute / synonym-slot drift markers ────────────────────────
//
// Mirrors `docs/conventions/attribute-api-migration.md`. These run via
// querySelectorAll; matching elements are flagged as info-level.

const DRIFT_MARKERS = [
  { selector: 'avatar-ui[name]', message: '<avatar-ui name=…> is deprecated; use text=…' },
  { selector: 'grid-ui[cols]', message: '<grid-ui cols=…> is the synonym; canonical is columns=…' },
  { selector: 'stepper-ui[current]', message: '<stepper-ui current=…> is the synonym; canonical is step=…' },
  { selector: 'stepper-item-ui[state]', message: '<stepper-item-ui state=…> is the synonym; parent <stepper-ui step> drives it' },
  { selector: 'card-ui [slot="meta"]', message: 'card-ui has no slot="meta" rule — tag falls into bare grid cell and stretches' },
];

// ── Probes (all run in-page via page.evaluate) ────────────────────────────

async function runProbes(page) {
  return await page.evaluate(({ COLORED_SELECTORS, DRIFT_MARKERS }) => {
    const findings = [];
    const push = (severity, kind, detail) => findings.push({ severity, kind, ...detail });

    // 1. Zero-area
    // Walk artifact items; skip elements that are intentionally hidden
    // (any display:none / visibility:hidden / [hidden] ancestor — e.g.
    // avatar-group's overflow children, popover panels, drawer contents)
    // or that are "rendered-on-demand" components which only paint when
    // opened (drawers, modals, popovers, tooltips, toasts).
    const ON_DEMAND_TAGS = new Set([
      'drawer-ui', 'modal-ui', 'popover-ui', 'tooltip-ui', 'toast-ui',
      'context-menu-ui', 'sheet-ui', 'dialog-ui',
    ]);
    const isIntentionallyHidden = (el) => {
      let p = el;
      while (p && p.nodeType === 1) {
        if (p.hasAttribute?.('hidden')) return true;
        if (p.hasAttribute?.('popover')) return true; // popover API closed
        if (p.tagName === 'DIALOG' && !p.open) return true;
        if (ON_DEMAND_TAGS.has(p.tagName?.toLowerCase())) return true;
        const cs = getComputedStyle(p);
        if (cs.display === 'none' || cs.visibility === 'hidden') return true;
        // Stop walking at the artifact-item boundary.
        if (p.matches?.('[data-artifact-item]')) return false;
        p = p.parentElement;
      }
      return false;
    };
    document.querySelectorAll('[data-artifact-item] *').forEach((el) => {
      if (!el.tagName.endsWith('-UI')) return;
      if (ON_DEMAND_TAGS.has(el.tagName.toLowerCase())) return;
      if (isIntentionallyHidden(el)) return;
      const r = el.getBoundingClientRect();
      // Only flag elements that should have rendered something — skip those
      // with no children, no text, and no [icon]/[text] attrs.
      const hasIntent =
        el.children.length > 0 ||
        (el.textContent || '').trim().length > 0 ||
        el.hasAttribute('icon') ||
        el.hasAttribute('text') ||
        el.hasAttribute('label');
      if (hasIntent && (r.width === 0 || r.height === 0)) {
        push('critical', 'zero-area', {
          tag: el.tagName.toLowerCase(),
          label: el.closest('[data-artifact-label]')?.dataset.artifactLabel || null,
          rect: { w: Math.round(r.width), h: Math.round(r.height) },
          hint: el.parentElement?.tagName === 'TOOLBAR-UI'
            ? 'parent toolbar-ui — likely overflow="menu" spilled it into the popover'
            : null,
        });
      }
    });

    // 2. Transparent-where-colored
    for (const selector of COLORED_SELECTORS) {
      document.querySelectorAll(selector).forEach((el) => {
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) return; // already flagged or hidden
        const cs = getComputedStyle(el);
        const bg = cs.backgroundColor;
        const borderTop = cs.borderTopColor;
        const isTransparent = bg === 'rgba(0, 0, 0, 0)' || bg === 'transparent';
        const borderTransparent = !borderTop || borderTop === 'rgba(0, 0, 0, 0)';
        // [data-swatch] for shape="dashed" intentionally has transparent bg
        // and paints via border-top instead. Test that directly: any
        // colored top border with non-zero width is "by design".
        const paintsViaBorder =
          el.matches('[data-swatch]') &&
          parseFloat(cs.borderTopWidth) > 0 &&
          !borderTransparent;
        if (paintsViaBorder) return;
        if (isTransparent) {
          push('critical', 'transparent-fill', {
            selector,
            tag: el.tagName.toLowerCase(),
            label: el.closest('[data-artifact-label]')?.dataset.artifactLabel || null,
            inlineSwatchVar: el.style.getPropertyValue('--swatch-color') || null,
          });
        }
      });
    }

    // 3. Synonym-attr / synonym-slot drift
    for (const { selector, message } of DRIFT_MARKERS) {
      document.querySelectorAll(selector).forEach((el) => {
        push('info', 'drift', {
          selector,
          message,
          tag: el.tagName.toLowerCase(),
          label: el.closest('[data-artifact-label]')?.dataset.artifactLabel || null,
        });
      });
    }

    // 4. Multi-child rich content inside alert-ui (no col-ui wrap)
    document.querySelectorAll('alert-ui').forEach((alert) => {
      const direct = Array.from(alert.children).filter(
        (c) => !c.hasAttribute('slot'),
      );
      if (direct.length >= 2 && direct.every((c) => c.tagName === 'TEXT-UI')) {
        push('warning', 'alert-flex-row', {
          tag: 'alert-ui',
          label: alert.closest('[data-artifact-label]')?.dataset.artifactLabel || null,
          message: 'multiple bare <text-ui> inside alert-ui lay out as flex-row — wrap in <col-ui slot="content">',
        });
      }
    });

    // 5. Missing component CSS — for each unique *-ui tag rendered on
    //    the page, verify a stylesheet matching `/components/{prefix}/{prefix}.css`
    //    is loaded. Catches the "swap to <select-ui> but forget to <link>
    //    select.css" class — markup looks right, JS registers the element,
    //    every other probe passes, but the listbox renders unstyled.
    //
    //    Demo pages under /site/components/<X>/ usually embed all sibling
    //    components transitively (their docs router shell loads tokens.css
    //    + a barrel, so most components resolve). When this probe fires
    //    on a demo page, it's signaling a real authoring miss — either
    //    a link tag was dropped or a new component on the page wasn't
    //    added to the shell loader.
    // Components / infra elements that legitimately ship without a sibling
    // {prefix}/{prefix}.css under packages/web-components/components/. Two
    // groups:
    //
    //   1. CSS-only components (yaml + a2ui.json only, styled by parent slot
    //      rules — per `feedback_css_only_components`). Source of truth:
    //      `for d in components/*/; do n="${d%/}"; [ ! -f "$d$n.css" ] &&
    //      echo "$n"; done` enumerates them.
    //
    //   2. Infrastructure elements registered outside components/ (e.g.
    //      `router-ui` from core/provider.js). They have inline / shell
    //      stylesheets that don't match the path pattern.
    //
    // When this list grows: re-run the source-of-truth grep above + audit
    // `customElements.define(...)` calls under packages/web-components/core/.
    const COMPONENTS_WITHOUT_OWN_CSS = new Set([
      // CSS-only components (no .css sibling) — styled by parent slot rules
      'aside-ui', 'footer-ui', 'header-ui', 'section-ui', 'stat-ui',
      // Co-located siblings (CSS lives in the parent component's directory)
      'tab-ui',      // css + js in components/tabs/, not components/tab/
      // Module-tier composites with no own CSS (styled by shell/parent)
      'chat-thread-ui',
      // Infrastructure elements (registered outside components/)
      'router-ui',
    ]);
    const allCustomTags = new Set();
    document.querySelectorAll('*').forEach((el) => {
      if (el.tagName.endsWith('-UI') && !ON_DEMAND_TAGS.has(el.tagName.toLowerCase())) {
        allCustomTags.add(el.tagName.toLowerCase());
      }
    });
    const loadedHrefs = Array.from(document.styleSheets)
      .map((s) => { try { return s.href || ''; } catch { return ''; } })
      .filter(Boolean);
    for (const tag of allCustomTags) {
      if (COMPONENTS_WITHOUT_OWN_CSS.has(tag)) continue;
      const prefix = tag.replace(/-ui$/, '');
      const expected = `/components/${prefix}/${prefix}.css`;
      const linked = loadedHrefs.some((h) => h.includes(expected));
      if (linked) continue;
      // Heuristic fallback: if at least one conventional component-prefixed
      // CSS custom property resolves on a rendered instance, the stylesheet
      // probably loaded under a different URL pattern (bundled / aliased).
      const inst = document.querySelector(tag);
      let resolved = false;
      if (inst) {
        const cs = getComputedStyle(inst);
        // Primary probe: standard token naming convention
        const probeNames = [
          `--${prefix}-bg`, `--${prefix}-fg`, `--${prefix}-pad`,
          `--${prefix}-radius`, `--${prefix}-size`, `--${prefix}-gap`,
          `--${prefix}-border`,
        ];
        resolved = probeNames.some((n) => cs.getPropertyValue(n).trim().length > 0);
        // Broader fallback: scan all custom properties for any --{prefix}-* token.
        // Catches components that use sub-namespaced tokens (e.g. --menu-popover-bg,
        // --toggle-option-gap) rather than the flat --{prefix}-bg convention.
        if (!resolved) {
          const propPrefix = `--${prefix}-`;
          for (const prop of cs) {
            if (prop.startsWith(propPrefix) && cs.getPropertyValue(prop).trim().length > 0) {
              resolved = true;
              break;
            }
          }
        }
      }
      if (!resolved) {
        push('critical', 'missing-component-css', {
          tag,
          label: inst?.closest('[data-artifact-label]')?.dataset.artifactLabel || null,
          message: `<${tag}> rendered but no stylesheet matching ${expected} loaded — controls render unstyled (popover bg transparent, listbox = raw text). Add the <link rel="stylesheet"> in the page or shell.`,
          expectedHref: expected,
        });
      }
    }

    // 6. Unstyled popover — runtime check for [popover]:popover-open
    //    whose computed background is transparent + zero padding. This
    //    is the visual symptom of missing-component-css for a popover-
    //    bearing primitive (select-ui listbox, tooltip-ui, etc.). Catches
    //    the case from a different angle in case the URL heuristic above
    //    didn't match a particular bundling scheme.
    // Popovers whose host element is intentionally transparent — visual
    // background comes from child elements, not the host itself.
    const TRANSPARENT_HOST_POPOVERS = new Set([
      'feed-ui',   // toast feed: host is transparent; feed-item-ui children carry bg
    ]);
    document.querySelectorAll('[popover]').forEach((el) => {
      if (!el.matches?.(':popover-open')) return;
      if (TRANSPARENT_HOST_POPOVERS.has(el.tagName.toLowerCase())) return;
      const cs = getComputedStyle(el);
      const transparent = cs.backgroundColor === 'rgba(0, 0, 0, 0)' || cs.backgroundColor === 'transparent';
      const noPad = parseFloat(cs.paddingTop) === 0 && parseFloat(cs.paddingLeft) === 0;
      if (transparent && noPad) {
        push('critical', 'unstyled-popover', {
          tag: el.tagName.toLowerCase(),
          host: el.parentElement?.tagName?.toLowerCase() || null,
          label: el.closest('[data-artifact-label]')?.dataset.artifactLabel || null,
          message: 'open popover has transparent bg + zero padding — host component CSS likely missing',
        });
      }
    });

    return findings;
  }, { COLORED_SELECTORS, DRIFT_MARKERS });
}

async function runStampContractProbe(page) {
  // Functions don't survive page.evaluate serialization — pass tag+reason
  // pairs only and re-implement the predicate in-page below.
  const reasons = Object.fromEntries(
    Object.entries(STAMP_CONTRACTS).map(([k, v]) => [k, v.reason]),
  );
  return await page.evaluate((contracts) => {
    const findings = [];
    for (const [tag, reason] of Object.entries(contracts)) {
      document.querySelectorAll(`${tag}`).forEach((el) => {
        // Skip elements clearly outside artifact frames (icons in nav, etc.).
        if (!el.closest('[data-artifact-item]')) return;
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.height === 0) return;
        // Re-implement contracts in-page (functions don't survive serialization).
        let ok = true;
        if (tag === 'input-ui') ok = !!el.querySelector('[slot="text"]');
        else if (tag === 'search-ui') ok = !!el.querySelector('input-ui');
        if (!ok) {
          findings.push({
            severity: 'critical',
            kind: 'empty-control',
            tag,
            label: el.closest('[data-artifact-label]')?.dataset.artifactLabel || null,
            reason,
          });
        }
      });
    }
    return findings;
  }, reasons);
}

// ── Sweep ─────────────────────────────────────────────────────────────────

async function loadComponentRoutes() {
  const sitemap = JSON.parse(await readFile(join(REPO_ROOT, 'site/sitemap.json'), 'utf8'));
  const routes = [];
  // Sitemap shape varies by section; recurse over every key generically
  // and pick up nodes that have a `/site/components/*` path + content.
  const walk = (node, depth = 0) => {
    if (!node || depth > 12) return;
    if (Array.isArray(node)) return node.forEach((n) => walk(n, depth));
    if (typeof node !== 'object') return;
    if (node.path?.startsWith('/site/components/') && node.content) {
      routes.push({ path: node.path, content: node.content, name: node.path.split('/').pop() });
    }
    for (const v of Object.values(node)) walk(v, depth + 1);
  };
  walk(sitemap);
  return FILTER ? routes.filter((r) => r.name.includes(FILTER)) : routes;
}

async function probePage(browser, base, route) {
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await ctx.newPage();
  const consoleEntries = [];
  page.on('console', (msg) => {
    const type = msg.type();
    if (type === 'error' || type === 'warning') {
      consoleEntries.push({ type, text: msg.text().slice(0, 240) });
    }
  });
  page.on('pageerror', (err) => consoleEntries.push({ type: 'error', text: err.message.slice(0, 240) }));

  // Hit the route path (not the raw `content` HTML) — the docs shell is
  // what loads the component bundle. Visiting the raw HTML directly leaves
  // every `*-ui` element inert and makes every probe report 0×0.
  const url = `${base}${route.path}`;
  try {
    await page.goto(url, { waitUntil: 'networkidle', timeout: 15000 });
  } catch (err) {
    await ctx.close();
    return {
      route: route.path,
      error: `navigation failed: ${err.message}`,
      findings: [],
      consoleEntries: [],
    };
  }
  // Settle: components often stamp on connected() + microtasks.
  await page.waitForTimeout(800);

  const probeFindings = await runProbes(page);
  const stampFindings = await runStampContractProbe(page);
  const findings = [...probeFindings, ...stampFindings];

  await ctx.close();
  return { route: route.path, findings, consoleEntries };
}

// ── Report ────────────────────────────────────────────────────────────────

function severityOrder(s) {
  return { critical: 0, warning: 1, info: 2 }[s] ?? 3;
}

function renderReport(results, base) {
  const all = results.flatMap((r) =>
    r.findings.map((f) => ({ ...f, route: r.route })),
  );
  const errors = results.filter((r) => r.error);
  const consoleErrors = results.flatMap((r) =>
    r.consoleEntries
      .filter((e) => e.type === 'error')
      .map((e) => ({ ...e, route: r.route })),
  );
  const consoleWarnings = results.flatMap((r) =>
    r.consoleEntries
      .filter((e) => e.type === 'warning')
      .map((e) => ({ ...e, route: r.route })),
  );

  const bySeverity = (sev) =>
    all.filter((f) => f.severity === sev).sort((a, b) => a.route.localeCompare(b.route));
  const critical = bySeverity('critical');
  const warning = bySeverity('warning');
  const info = bySeverity('info');

  const renderFinding = (f) => {
    const head = `- **${f.kind}** on \`${f.route}\``;
    const labelBit = f.label ? ` (${f.label})` : '';
    const detailBits = [];
    if (f.tag) detailBits.push(`tag=\`${f.tag}\``);
    if (f.selector) detailBits.push(`selector=\`${f.selector}\``);
    if (f.rect) detailBits.push(`rect=${f.rect.w}×${f.rect.h}`);
    if (f.inlineSwatchVar) detailBits.push(`swatch=\`${f.inlineSwatchVar}\``);
    if (f.hint) detailBits.push(f.hint);
    if (f.reason) detailBits.push(f.reason);
    if (f.message) detailBits.push(f.message);
    return `${head}${labelBit} — ${detailBits.join(' · ')}`;
  };

  const lines = [];
  lines.push(`# Dogfooding report — ${today}`);
  lines.push('');
  lines.push(`Sweep of every \`/site/components/*\` demo page against ${base}.`);
  lines.push('Generated by the `adia-ui-dogfood` skill analyzer (`scripts/analyze.mjs`).');
  lines.push('');
  lines.push('## Summary');
  lines.push('');
  lines.push(`| Severity | Count |`);
  lines.push(`|----------|------:|`);
  lines.push(`| critical | ${critical.length} |`);
  lines.push(`| warning  | ${warning.length} |`);
  lines.push(`| info     | ${info.length} |`);
  lines.push(`| console errors  | ${consoleErrors.length} |`);
  lines.push(`| console warnings | ${consoleWarnings.length} |`);
  lines.push(`| pages scanned   | ${results.length} |`);
  lines.push(`| navigation errors | ${errors.length} |`);
  lines.push('');

  if (critical.length) {
    lines.push(`## Critical (${critical.length})`);
    lines.push('');
    lines.push('Page is visibly broken — element collapsed, swatch transparent, control un-stamped.');
    lines.push('');
    critical.forEach((f) => lines.push(renderFinding(f)));
    lines.push('');
  }

  if (warning.length) {
    lines.push(`## Warning (${warning.length})`);
    lines.push('');
    lines.push('Likely-broken composition the layout will silently mis-render.');
    lines.push('');
    warning.forEach((f) => lines.push(renderFinding(f)));
    lines.push('');
  }

  if (info.length) {
    lines.push(`## Info (${info.length})`);
    lines.push('');
    lines.push('Synonym-attribute / deprecation drift. Not breaking; sweep when convenient.');
    lines.push('');
    info.forEach((f) => lines.push(renderFinding(f)));
    lines.push('');
  }

  if (consoleErrors.length) {
    lines.push(`## Console errors (${consoleErrors.length})`);
    lines.push('');
    consoleErrors.slice(0, 50).forEach((e) =>
      lines.push(`- \`${e.route}\` — ${e.text}`),
    );
    if (consoleErrors.length > 50) {
      lines.push(`- … ${consoleErrors.length - 50} more truncated`);
    }
    lines.push('');
  }

  if (errors.length) {
    lines.push(`## Navigation errors (${errors.length})`);
    lines.push('');
    errors.forEach((r) => lines.push(`- \`${r.route}\` — ${r.error}`));
    lines.push('');
  }

  lines.push('---');
  lines.push('');
  lines.push('## Probe coverage');
  lines.push('');
  lines.push('1. **Zero-area** — `*-ui` element with intent (children, text, icon attr) but `getBoundingClientRect()` width or height = 0.');
  lines.push('2. **Transparent fill** — `[data-swatch]`, semantic-variant pills/buttons, chart indicators with `background-color: rgba(0,0,0,0)`. Bug class: chart-legend `--chart-N` fallback that doesn\'t resolve standalone.');
  lines.push('3. **Empty control** — `input-ui`, `search-ui`, `button-ui`, `select-ui`, `tag-ui` whose `connected()` should have stamped internals but didn\'t.');
  lines.push('4. **Synonym-attr / synonym-slot drift** — markers documented in `docs/conventions/attribute-api-migration.md`.');
  lines.push('5. **Alert flex-row** — `alert-ui` with multiple bare `<text-ui>` children (need `<col-ui slot="content">` wrap).');
  lines.push('6. **Console** — every `console.error` and `console.warn` during page load + 800ms settling.');
  lines.push('');

  return lines.join('\n');
}

// ── Main ──────────────────────────────────────────────────────────────────

async function main() {
  const base = `http://localhost:${PORT}`;
  const routes = await loadComponentRoutes();
  log(`▶ Dogfooding sweep — ${routes.length} component pages against ${base}`);

  const browser = await chromium.launch({ headless: true });
  const results = [];
  let i = 0;
  for (const route of routes) {
    i += 1;
    log(`  [${i}/${routes.length}] ${route.path}`);
    try {
      const r = await probePage(browser, base, route);
      results.push(r);
    } catch (err) {
      results.push({ route: route.path, error: err.message, findings: [], consoleEntries: [] });
    }
  }
  await browser.close();

  const report = renderReport(results, base);
  await mkdir(dirname(OUT), { recursive: true });
  await writeFile(OUT, report, 'utf8');

  const total = results.reduce((acc, r) => acc + r.findings.length, 0);
  const critical = results.reduce(
    (acc, r) => acc + r.findings.filter((f) => f.severity === 'critical').length,
    0,
  );
  log(`✔ ${total} findings (${critical} critical) → ${OUT}`);

  // Exit code: 1 if any critical, 0 otherwise. CI-friendly.
  process.exit(critical > 0 ? 1 : 0);
}

main().catch((err) => {
  console.error('dogfood analyzer crashed:', err);
  process.exit(2);
});
