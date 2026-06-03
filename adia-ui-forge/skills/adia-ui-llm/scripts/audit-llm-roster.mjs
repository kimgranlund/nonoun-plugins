#!/usr/bin/env node
// audit-llm-roster.mjs — §SelfAudit enforcement for adia-ui-llm.
// Universal axes via the shared audit-axes lib; plus a skill-specific axis:
// provider-roster currency (each adapter the skill claims — anthropic, openai,
// gemini — must have a matching §ColdStartTriage/posture mention so the menu
// can't drift out of sync with the adapters the package actually ships).
//
// Shared lib resolution: ${CLAUDE_PLUGIN_ROOT}/bin/lib/audit-axes.mjs, with a
// fallback relative to this script (per the plugin path convention).
//
// Usage (from the plugin/repo root):
//   node skills/adia-ui-llm/scripts/audit-llm-roster.mjs
//   node skills/adia-ui-llm/scripts/audit-llm-roster.mjs --json
//   node skills/adia-ui-llm/scripts/audit-llm-roster.mjs --strict

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Plugin root: ${CLAUDE_PLUGIN_ROOT} if set, else 3 dirs up from this script
// (skills/adia-ui-llm/scripts/ → plugin root).
const PLUGIN_ROOT = process.env.CLAUDE_PLUGIN_ROOT
  ? path.resolve(process.env.CLAUDE_PLUGIN_ROOT)
  : path.resolve(__dirname, '..', '..', '..');

const LIB_URL = pathToFileURL(path.join(PLUGIN_ROOT, 'bin', 'lib', 'audit-axes.mjs')).href;
const { runUniversalAxes, formatResults } = await import(LIB_URL);

// Skill layout: skills/<name>/ under the plugin root (matches run-skill-evals.mjs).
const SKILL_DIR = path.join(PLUGIN_ROOT, 'skills', 'adia-ui-llm');
const SKILL_MD = path.join(SKILL_DIR, 'SKILL.md');
const SKILL_JSON = path.join(SKILL_DIR, 'skill.json');

// The provider adapters this skill maintains. Each MUST be referenced in
// SKILL.md so the cold-start menu / posture stays in sync with the package.
const PROVIDERS = ['anthropic', 'openai', 'gemini'];

function parseArgs(argv) {
  return { json: argv.includes('--json'), strict: argv.includes('--strict') };
}

function readSafe(p) {
  try { return fs.readFileSync(p, 'utf8'); } catch { return ''; }
}

function axisProviderRosterCurrency() {
  const md = readSafe(SKILL_MD);
  const findings = [];
  for (const name of PROVIDERS) {
    if (md.includes(name)) {
      findings.push({ type: 'provider-present', message: `${name}: referenced in SKILL.md — correct`, name });
    } else {
      findings.push({
        type: 'provider-missing',
        message: `${name}: adapter is shipped by the package but not referenced in SKILL.md`,
        name,
      });
    }
  }
  const driftCount = findings.filter(f => f.type !== 'provider-present').length;
  return {
    axis: 'providerRosterCurrency',
    axis_num: 9,
    status: driftCount > 0 ? 'drift' : 'ok',
    findings,
    summary: driftCount > 0 ? `${driftCount} provider(s) unreferenced` : 'all adapters referenced in SKILL.md',
  };
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const ctx = { skillDir: SKILL_DIR, skillMd: SKILL_MD, skillJson: SKILL_JSON, repoRoot: PLUGIN_ROOT };
  const { results: universal } = runUniversalAxes(ctx);
  const axis9 = axisProviderRosterCurrency();
  const allResults = [...universal, axis9];
  const driftCount = allResults.filter(r => r.status === 'drift').length;

  if (args.json) {
    console.log(JSON.stringify({ results: allResults, driftCount }, null, 2));
    if (args.strict && driftCount > 0) process.exit(1);
    return;
  }

  console.log(`[audit-llm-roster] adia-ui-llm §SelfAudit — ${driftCount} drifting axis/axes`);
  console.log(formatResults(allResults));
  if (driftCount === 0) console.log('\n✓ All clean.');
  if (args.strict && driftCount > 0) process.exit(1);
}

main();
