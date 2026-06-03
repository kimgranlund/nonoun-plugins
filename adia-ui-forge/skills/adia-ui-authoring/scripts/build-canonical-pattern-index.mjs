#!/usr/bin/env node
/**
 * build-canonical-pattern-index.mjs — Auto-build canonical-pattern-index.md
 *
 * Walks apps/, catalog/, and playgrounds/ for `.contents.html` files and
 * emits a grouped markdown index used by Mode 8 (composite-demo-protocol.md)
 * Phase 2 (Canonical Survey).
 *
 * Run from the framework monorepo root (the dirs it scans — apps/, catalog/,
 * playgrounds/ — are monorepo roots):
 *
 *   node scripts/build-canonical-pattern-index.mjs
 *
 * The output `references/canonical-pattern-index.md` is checked in so agents
 * reading the skill always see the current state without running the script
 * first. REPO_ROOT defaults to the current working directory; OUTPUT is
 * resolved relative to this script (into the skill's own references/).
 */

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = process.env.REPO_ROOT
  ? path.resolve(process.env.REPO_ROOT)
  : process.cwd();
const OUTPUT = path.join(__dirname, '..', 'references', 'canonical-pattern-index.md');

const ROOTS = [
  { path: 'apps/saas/app', label: 'SaaS app dashboards' },
  { path: 'apps/genui/app', label: 'GenUI app routes' },
  { path: 'apps/user-flow/app', label: 'User-flow templates' },
  { path: 'catalog/ui-patterns/app', label: 'UI-pattern atomics (catalog)' },
  { path: 'catalog/page-shells/app', label: 'Page-shell templates (catalog)' },
  { path: 'playgrounds', label: 'Playgrounds' },
];

function walkContentsHtml(root) {
  const results = [];
  const abs = path.join(REPO_ROOT, root);
  if (!fs.existsSync(abs)) return results;
  function recurse(dir) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        recurse(full);
      } else if (entry.name.endsWith('.contents.html')) {
        results.push(path.relative(REPO_ROOT, full));
      }
    }
  }
  recurse(abs);
  return results.sort();
}

function lineCount(rel) {
  try {
    return fs.readFileSync(path.join(REPO_ROOT, rel), 'utf8').split('\n').length;
  } catch {
    return 0;
  }
}

function inferUiType(rel) {
  const segments = rel.split('/');
  const slug = segments[segments.length - 2] ?? '';

  // Heuristics — categorize by slug fragments
  if (/billing|invoice|payment|plan-picker|subscription/i.test(slug)) return 'billing';
  if (/dashboard|kpi|metrics|admin-dashboard/i.test(slug)) return 'dashboard';
  if (/settings|preferences|notification/i.test(slug)) return 'settings';
  if (/onboarding|welcome|first-action/i.test(slug)) return 'onboarding-wizard';
  if (/registration|sign-up|profile/i.test(slug)) return 'registration-wizard';
  if (/sign-in|password|mfa|otp|oauth|forgot|reset/i.test(slug)) return 'auth-flow';
  if (/error|404|500|forbidden|locked|expired|deleted/i.test(slug)) return 'error-page';
  if (/email-change|verify|callback/i.test(slug)) return 'auth-flow';
  if (/integration|connector|api/i.test(slug)) return 'integrations-list';
  if (/members|users|team/i.test(slug)) return 'list-with-detail';
  if (/security|privacy/i.test(slug)) return 'settings';
  if (/marketing|hero|cta|landing/i.test(slug)) return 'marketing';
  if (/agent|reasoning|trace/i.test(slug)) return 'agent-activity';
  if (/chat|conversation|message/i.test(slug)) return 'chat';
  if (/editor|code|preview/i.test(slug)) return 'editor';
  if (/kanban|board/i.test(slug)) return 'kanban';
  if (/table|grid|data/i.test(slug)) return 'data-table';
  if (/command|palette|search/i.test(slug)) return 'command';
  if (/funnel|conversion|step/i.test(slug)) return 'multi-step-funnel';
  if (/modal|confirm|destructive/i.test(slug)) return 'overlay';
  if (/profile-card|user-card/i.test(slug)) return 'list-with-detail';
  if (/feed|activity|timeline/i.test(slug)) return 'feed';
  if (/render|stream|css-channel|a2ui/i.test(slug)) return 'demo-playground';
  return 'other';
}

const UI_TYPE_ORDER = [
  'billing', 'dashboard', 'settings', 'auth-flow', 'onboarding-wizard',
  'registration-wizard', 'list-with-detail', 'integrations-list', 'agent-activity',
  'chat', 'editor', 'kanban', 'data-table', 'command', 'overlay',
  'multi-step-funnel', 'feed', 'marketing', 'error-page', 'demo-playground', 'other',
];

const UI_TYPE_GUIDANCE = {
  billing: 'Billing dashboards (current plan, invoices, payment methods, usage). Lift card-ui + section + col-ui + field-ui chain from billing.contents.html.',
  dashboard: 'Admin dashboards (KPI grids, overview cards). Lift grid-ui responsive columns from admin-dashboard.contents.html.',
  settings: 'Settings pages (preferences, security, appearance). Lift card-ui per setting group + col-ui spacing.',
  'auth-flow': 'Authentication flows (sign-in, MFA, OAuth, password reset). Lift single-column form layout from sign-in.contents.html siblings.',
  'onboarding-wizard': 'Onboarding multi-step wizards. Lift step-progress + section + cta-row pattern.',
  'registration-wizard': 'Registration multi-step flows. Lift wizard step + form composition.',
  'list-with-detail': 'List + detail compositions (entity rows + drawer/modal detail). Lift entity-item + drawer pattern.',
  'integrations-list': 'Searchable integration/connector grids. Lift grid-ui + card-ui + empty-state-inside-card pattern.',
  'agent-activity': 'Agent activity / reasoning feeds. Lift activity-feed scroll + collapsed-reasoning pattern.',
  chat: 'Chat surfaces (thread, composer, sidebar). Lift chat-streaming-surface composition.',
  editor: 'Editor panes (code, preview, toolbar). Lift editor-shell composition.',
  kanban: 'Kanban / column-based boards. Lift kanban-board-3col pattern.',
  'data-table': 'Data tables with badges/inline actions. Lift users-table-badge composition.',
  command: 'Command palette / global search. Lift command-palette overlay pattern.',
  overlay: 'Modals, drawers, popovers. Lift destructive-confirm-modal pattern for confirmations.',
  'multi-step-funnel': 'Multi-step conversion funnels. Lift conversion-funnel-6step composition.',
  feed: 'Activity / event feeds. Lift activity-feed composition.',
  marketing: 'Marketing pages, hero CTAs. Lift marketing-hero-cta composition.',
  'error-page': 'Error states (404, 500, forbidden, expired). Lift centered single-card error pattern.',
  'demo-playground': 'Internal demo + playground surfaces. Use these as reference for composition style; not always production-grade.',
  other: 'Misc canonicals. Inspect contents.html to determine UI type.',
};

function buildMarkdown(grouped) {
  const lines = [
    '# Canonical Pattern Index — survey targets for Mode 8 (composite-demo-protocol.md)',
    '',
    '**Auto-generated** by `scripts/build-canonical-pattern-index.mjs`. Do not edit by hand — re-run the build script after adding new canonicals to `apps/`, `catalog/`, or `playgrounds/`.',
    '',
    `**Total canonical \`.contents.html\` files**: ${grouped.totalFiles}`,
    '',
    '## How to use this index',
    '',
    '1. From Phase 1 of [composite-demo-protocol.md](composite-demo-protocol.md), name the UI type.',
    '2. Find the matching section below.',
    '3. Read every `.contents.html` listed (or the closest 2-3 if the section has many).',
    '4. Extract primitive composition per Phase 3 of the protocol.',
    '5. Cite the path in your demo\'s `<!-- Pattern source: ... -->` comment.',
    '',
    '---',
    '',
  ];

  for (const uiType of UI_TYPE_ORDER) {
    const files = grouped.byType[uiType];
    if (!files || files.length === 0) continue;
    lines.push(`## ${uiType} (${files.length})`);
    lines.push('');
    lines.push(`> ${UI_TYPE_GUIDANCE[uiType]}`);
    lines.push('');
    for (const f of files) {
      const lc = lineCount(f.path);
      lines.push(`- \`${f.path}\` — ${lc} lines (from ${f.root})`);
    }
    lines.push('');
  }

  lines.push('---');
  lines.push('');
  lines.push('## Maintenance');
  lines.push('');
  lines.push('Re-build this index:');
  lines.push('');
  lines.push('```bash');
  lines.push('node scripts/build-canonical-pattern-index.mjs');
  lines.push('```');
  lines.push('');
  lines.push('If a heuristic misclassifies a path (the file lands in `other` or the wrong UI type), update the `inferUiType()` regex in `scripts/build-canonical-pattern-index.mjs`.');
  lines.push('');
  return lines.join('\n');
}

function main() {
  const grouped = { byType: {}, totalFiles: 0 };

  for (const { path: rootPath, label } of ROOTS) {
    const files = walkContentsHtml(rootPath);
    for (const f of files) {
      const uiType = inferUiType(f);
      (grouped.byType[uiType] ??= []).push({ path: f, root: label });
      grouped.totalFiles++;
    }
  }

  const md = buildMarkdown(grouped);
  fs.writeFileSync(OUTPUT, md);
  console.log(`Wrote ${OUTPUT}`);
  console.log(`  ${grouped.totalFiles} canonical .contents.html files indexed`);
  for (const uiType of UI_TYPE_ORDER) {
    const count = (grouped.byType[uiType] || []).length;
    if (count > 0) console.log(`    ${uiType}: ${count}`);
  }
}

main();
