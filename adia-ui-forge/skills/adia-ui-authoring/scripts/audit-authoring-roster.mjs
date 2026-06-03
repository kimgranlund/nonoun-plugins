#!/usr/bin/env node
// audit-authoring-roster.mjs — §SelfAudit enforcement for adia-ui-authoring.
// Universal axes via the shared audit-axes lib; plus a skill-specific
// absorbed-skill roster-currency axis.
//
// Usage (from anywhere):
//   node scripts/audit-authoring-roster.mjs
//   node scripts/audit-authoring-roster.mjs --json
//   node scripts/audit-authoring-roster.mjs --strict
//
// Resolves the shared lib via ${CLAUDE_PLUGIN_ROOT}/bin/lib/audit-axes.mjs,
// with a fallback relative to this script (skills/<name>/scripts → bin/lib).

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SKILL_DIR = path.resolve(__dirname, '..');            // skills/adia-ui-authoring
const SKILLS_ROOT = path.resolve(SKILL_DIR, '..');          // skills/
const PLUGIN_ROOT = process.env.CLAUDE_PLUGIN_ROOT
  ? path.resolve(process.env.CLAUDE_PLUGIN_ROOT)
  : path.resolve(SKILL_DIR, '..', '..');                    // plugin root

const SKILL_MD = path.join(SKILL_DIR, 'SKILL.md');
const SKILL_JSON = path.join(SKILL_DIR, 'skill.json');

// Resolve the shared audit-axes library from the plugin root, falling back
// to the script-relative location if the env var isn't set.
const auditAxesPath = (() => {
  const fromEnv = path.join(PLUGIN_ROOT, 'bin', 'lib', 'audit-axes.mjs');
  if (fs.existsSync(fromEnv)) return fromEnv;
  return path.resolve(__dirname, '..', '..', '..', 'bin', 'lib', 'audit-axes.mjs');
})();

const { runUniversalAxes, formatResults } = await import(pathToFileURL(auditAxesPath).href);

// [name, expected-redirect-path or null if already-gone]. The legacy
// skills these absorbed were never carried into this plugin, so every
// entry is expected to be absorbed-clean (no directory present).
const ABSORBED = [
  ['primitive-audit',            null],
  ['component-token-audit',      null],
  ['llm-bridge-extension',       null],
  ['adia-ui-code-bestpractices', null],
  ['bespoke-shell-children',     null],
  ['promote-inline-to-module',   null],
];

const CLEAN_STATUSES = ['absorbed-clean', 'absorbed-clean-deleted', 'redirect-ok'];

function parseArgs(argv) {
  if (argv.includes('--help') || argv.includes('-h')) {
    console.log(`audit-authoring-roster.mjs — adia-ui-authoring §SelfAudit.

USAGE
  node scripts/audit-authoring-roster.mjs [--json] [--strict]

FLAGS
  --json     Emit findings as JSON instead of human text
  --strict   Exit 1 on any drifting axis
  --help     Show this help

AXES (universal axes from \${CLAUDE_PLUGIN_ROOT}/bin/lib/audit-axes.mjs)
  1  Manifest enforcement     — skill.json files[] matches disk (recursive)
  2  Reference graph          — every markdown link inside SKILL.md resolves
  3  Capability-menu drift    — every §ColdStartTriage row's entry reference exists
  4  Version-literal parity   — SKILL.md frontmatter version matches skill.json
  5  Phase-label absence      — no stale Phase N annotations in skill prose
  6  Fence-leak detection     — no orphan fence markers
  7  Content currency         — references cited by skill.json exist on disk
  8  CLI helper currency      — npm scripts cited by SKILL.md (skips substrate-only)

  9  Authoring-roster currency (skill-specific) — every absorbed skill has a
     redirect SKILL.md at the expected path or is absorbed-clean (no directory).

EXIT CODES
  0   All axes clean
  1   At least one axis drifting (with --strict)
`);
    process.exit(0);
  }
  return { json: argv.includes('--json'), strict: argv.includes('--strict') };
}

function axis9_authoringRosterCurrency() {
  const findings = [];
  for (const [name, redirectPath] of ABSORBED) {
    if (redirectPath === null) {
      const dir = path.join(SKILLS_ROOT, name);
      if (fs.existsSync(dir)) {
        findings.push({ type: 'unexpected-directory', message: `${name}/ exists but was claimed absorbed-and-gone`, name });
      } else {
        findings.push({ type: 'absorbed-clean', message: `${name}: no directory — correct`, name });
      }
    } else {
      const full = path.join(PLUGIN_ROOT, redirectPath);
      if (!fs.existsSync(full)) {
        const dir = path.dirname(full);
        findings.push({
          type: fs.existsSync(dir) ? 'redirect-missing' : 'absorbed-clean-deleted',
          message: fs.existsSync(dir)
            ? `${name}: expected redirect at ${redirectPath} — not found`
            : `${name}: fully deleted post-soak`,
          name,
        });
      } else {
        const txt = fs.readFileSync(full, 'utf8');
        findings.push(
          /status:\s*redirect/m.test(txt)
            ? { type: 'redirect-ok', message: `${name}: redirect ok`, name }
            : { type: 'redirect-not-tagged', message: `${name}: ${redirectPath} lacks 'status: redirect'`, name }
        );
      }
    }
  }
  const driftCount = findings.filter(f => !CLEAN_STATUSES.includes(f.type)).length;
  return {
    axis: 'authoringRosterCurrency',
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
  const axis9 = axis9_authoringRosterCurrency();
  const allResults = [...universal, axis9];
  const driftCount = allResults.filter(r => r.status === 'drift').length;

  if (args.json) {
    console.log(JSON.stringify({ results: allResults, driftCount }, null, 2));
    if (args.strict && driftCount > 0) process.exit(1);
    return;
  }

  console.log(`[audit-authoring-roster] adia-ui-authoring §SelfAudit — ${driftCount} drifting axis/axes`);
  console.log(formatResults(allResults));
  if (driftCount === 0) console.log('\n✓ All clean.');
  if (args.strict && driftCount > 0) process.exit(1);
}

main();
