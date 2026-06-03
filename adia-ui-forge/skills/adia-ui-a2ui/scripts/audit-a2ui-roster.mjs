#!/usr/bin/env node
// audit-a2ui-roster.mjs — §SelfAudit enforcement for adia-ui-a2ui.
// Universal axes via the shared audit-axes lib; plus a skill-specific axis:
// absorbed-skill roster currency (the three absorbed standalones and their
// predecessors must stay absorbed — not resurrected as live skill dirs).
//
// Shared lib resolution: ${CLAUDE_PLUGIN_ROOT}/bin/lib/audit-axes.mjs, with a
// fallback relative to this script (per the plugin path convention).
//
// Usage (from the plugin/repo root):
//   node skills/adia-ui-a2ui/scripts/audit-a2ui-roster.mjs
//   node skills/adia-ui-a2ui/scripts/audit-a2ui-roster.mjs --json
//   node skills/adia-ui-a2ui/scripts/audit-a2ui-roster.mjs --strict

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Plugin root: ${CLAUDE_PLUGIN_ROOT} if set, else 3 dirs up from this script
// (skills/adia-ui-a2ui/scripts/ → plugin root).
const PLUGIN_ROOT = process.env.CLAUDE_PLUGIN_ROOT
  ? path.resolve(process.env.CLAUDE_PLUGIN_ROOT)
  : path.resolve(__dirname, '..', '..', '..');

const LIB_URL = pathToFileURL(path.join(PLUGIN_ROOT, 'bin', 'lib', 'audit-axes.mjs')).href;
const { runUniversalAxes, formatResults } = await import(LIB_URL);

// Skill layout: skills/<name>/ under the plugin root (matches run-skill-evals.mjs).
const SKILL_DIR = path.join(PLUGIN_ROOT, 'skills', 'adia-ui-a2ui');
const SKILL_MD = path.join(SKILL_DIR, 'SKILL.md');
const SKILL_JSON = path.join(SKILL_DIR, 'skill.json');
const SKILLS_ROOT = path.join(PLUGIN_ROOT, 'skills');

// Absorbed skills + predecessors — must NOT exist as live skill directories.
const ABSORBED = [
  'a2ui-pipeline',
  'adia-ui-training',
  'zettel-internals',
  'fragment-extraction',
  'training-data-flow',
  'eval-gap-diagnosis',
  'semantic-fail-lifting',
];

function parseArgs(argv) {
  return { json: argv.includes('--json'), strict: argv.includes('--strict') };
}

function axisAbsorbedRosterCurrency() {
  const findings = [];
  for (const name of ABSORBED) {
    const dir = path.join(SKILLS_ROOT, name);
    if (fs.existsSync(dir)) {
      findings.push({
        type: 'unexpected-directory',
        message: `${name}/ exists but was absorbed into adia-ui-a2ui — should not be a live skill dir`,
        name,
      });
    } else {
      findings.push({ type: 'absorbed-clean', message: `${name}: absorbed, no live dir — correct`, name });
    }
  }
  const driftCount = findings.filter(f => f.type !== 'absorbed-clean').length;
  return {
    axis: 'absorbedRosterCurrency',
    axis_num: 9,
    status: driftCount > 0 ? 'drift' : 'ok',
    findings,
    summary: driftCount > 0 ? `${driftCount} absorbed-skill issue(s)` : 'all absorbed-skill entries clean',
  };
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const ctx = { skillDir: SKILL_DIR, skillMd: SKILL_MD, skillJson: SKILL_JSON, repoRoot: PLUGIN_ROOT };
  const { results: universal } = runUniversalAxes(ctx);
  const axis9 = axisAbsorbedRosterCurrency();
  const allResults = [...universal, axis9];
  const driftCount = allResults.filter(r => r.status === 'drift').length;

  if (args.json) {
    console.log(JSON.stringify({ results: allResults, driftCount }, null, 2));
    if (args.strict && driftCount > 0) process.exit(1);
    return;
  }

  console.log(`[audit-a2ui-roster] adia-ui-a2ui §SelfAudit — ${driftCount} drifting axis/axes`);
  console.log(formatResults(allResults));
  if (driftCount === 0) console.log('\n✓ All clean.');
  if (args.strict && driftCount > 0) process.exit(1);
}

main();
