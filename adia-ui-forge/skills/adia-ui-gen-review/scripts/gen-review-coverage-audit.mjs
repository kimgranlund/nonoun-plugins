#!/usr/bin/env node
/**
 * gen-review-coverage-audit.mjs — SelfAudit check 5 for adia-ui-gen-review.
 *
 * Verifies that every AdiaUI primitive tag (from component yamls) has
 * an entry in gen-review-decompose.mjs TAG_TO_COMPONENT. Reports any
 * gaps so the skill's primitive lookup table stays in sync with the
 * substrate as new components ship.
 *
 * This script is skill-owned. It reads two inputs:
 *   - the sibling gen-review-decompose.mjs (resolved relative to this file)
 *   - the monorepo's packages/web-components/components/*.yaml tags
 *     (resolved from the working directory — run from the monorepo root)
 *
 * Requires `js-yaml` available on the module resolution path (the monorepo's
 * node_modules). Imported as a bare specifier so it resolves wherever the
 * script is run.
 *
 * Usage (from the monorepo root):
 *   node ${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-gen-review/scripts/gen-review-coverage-audit.mjs           # report gaps
 *   node ${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-gen-review/scripts/gen-review-coverage-audit.mjs --strict  # exit 1 if gaps exist
 *   node ${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-gen-review/scripts/gen-review-coverage-audit.mjs --json    # machine-readable output
 */

import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { load as yamlLoad } from 'js-yaml';

const __dir = dirname(fileURLToPath(import.meta.url));   // the skill's scripts/ dir
const REPO_ROOT = process.cwd();                         // the monorepo root

const strict = process.argv.includes('--strict');
const jsonMode = process.argv.includes('--json');

// ── 1. Extract all tag names from component yamls ────────────────────────────

const COMPONENTS_DIR = join(REPO_ROOT, 'packages/web-components/components');
const allTags = new Map(); // tag → { yamlPath, name }

function walkComponents(dir) {
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) {
      walkComponents(full);
    } else if (entry.endsWith('.yaml') && !entry.includes('.a2ui.') && !entry.includes('schema')) {
      try {
        const raw = readFileSync(full, 'utf8');
        const doc = yamlLoad(raw);
        if (doc?.tag && typeof doc.tag === 'string' && doc.tag.endsWith('-ui')) {
          allTags.set(doc.tag, { yamlPath: full.replace(REPO_ROOT + '/', ''), name: doc.name ?? doc.tag });
        }
      } catch { /* skip unparseable */ }
    }
  }
}

walkComponents(COMPONENTS_DIR);

// ── 2. Extract TAG_TO_COMPONENT from the sibling decompose script ────────────

const SCRIPT_PATH = join(__dir, 'gen-review-decompose.mjs');
const scriptSrc = readFileSync(SCRIPT_PATH, 'utf8');

// Parse the TAG_TO_COMPONENT object by extracting quoted key entries
const tagInScript = new Set();
const tagRegex = /['"]([a-z][a-z0-9-]+-ui)['"]:\s*(?:'[^']*'|null)/g;
let m;
while ((m = tagRegex.exec(scriptSrc)) !== null) {
  tagInScript.add(m[1]);
}

// ── 3. Compute gaps ──────────────────────────────────────────────────────────

const missing = [];   // in yaml, not in script
const extra = [];     // in script, not in yaml (may be intentional like canvas-ui)

for (const [tag, meta] of allTags) {
  if (!tagInScript.has(tag)) {
    missing.push({ tag, ...meta });
  }
}

// Script entries that have no yaml (legacy, intentional shells, or typos)
for (const scriptTag of tagInScript) {
  if (!allTags.has(scriptTag)) {
    extra.push(scriptTag);
  }
}

// ── 4. Report ────────────────────────────────────────────────────────────────

const result = {
  totalYamlTags: allTags.size,
  coveredByScript: tagInScript.size,
  missingCount: missing.length,
  extraCount: extra.length,
  missing,
  extra,
  status: missing.length === 0 ? 'CLEAN' : 'GAPS_FOUND',
};

if (jsonMode) {
  console.log(JSON.stringify(result, null, 2));
} else {
  console.log(`\n[coverage-audit] TAG_TO_COMPONENT coverage`);
  console.log(`  Yaml tags:  ${allTags.size}`);
  console.log(`  In script:  ${tagInScript.size}`);
  console.log(`  Missing:    ${missing.length}`);
  console.log(`  Extra:      ${extra.length} (intentional shells / aliases)`);

  if (missing.length > 0) {
    console.log(`\nMISSING from TAG_TO_COMPONENT (add to gen-review-decompose.mjs):`);
    for (const { tag, name } of missing.sort((a,b) => a.tag.localeCompare(b.tag))) {
      console.log(`  '${tag}': '${name.replace(/^UI/, '')}',`);
    }
  } else {
    console.log(`\n✓ All yaml tags covered in TAG_TO_COMPONENT`);
  }

  if (extra.length > 0) {
    console.log(`\nIn script but no yaml (shells/aliases — verify intentional):`);
    for (const tag of extra.sort()) console.log(`  ${tag}`);
  }
}

process.exit(strict && missing.length > 0 ? 1 : 0);
