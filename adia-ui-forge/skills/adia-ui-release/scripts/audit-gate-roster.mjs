#!/usr/bin/env node
// audit-gate-roster.mjs — §SelfAudit Axis 9 enforcement.
//
// Compares the `check:*` / `verify:*` / `smoke:*` / `test:*` scripts
// declared in the target repo's `package.json` against the gate roster
// documented in this skill's `references/gates-catalog.md`. Flags drift
// in either direction:
//   - Gates that exist in package.json but aren't documented (new
//     gate added without catalog update).
//   - Gates documented in the catalog but no longer in package.json
//     (gate removed without catalog cleanup).
//
// Usage (run from the @adia-ai-style monorepo root):
//   node audit-gate-roster.mjs
//   node audit-gate-roster.mjs --json
//   node audit-gate-roster.mjs --strict   # exit 1 on any drift
//   node audit-gate-roster.mjs --repo /path/to/monorepo
//
// Path resolution: the gate catalog ships with the skill. It is resolved
// via ${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-release/references/gates-catalog.md,
// with a fallback relative to this script (../references/gates-catalog.md)
// for when the plugin-root env var is not set.

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';

function parseArgs(argv) {
  const args = { json: false, strict: false, repo: process.cwd() };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--json') args.json = true;
    else if (argv[i] === '--strict') args.strict = true;
    else if (argv[i] === '--repo') args.repo = argv[++i];
    else if (argv[i] === '-h' || argv[i] === '--help') {
      console.log('Usage: node audit-gate-roster.mjs [--json] [--strict] [--repo <monorepo-root>]');
      process.exit(0);
    }
  }
  return args;
}

// The gate catalog is skill-owned (ships in references/). Resolve it via the
// plugin root, falling back to a path relative to this script.
function resolveCatalog() {
  const pluginRoot = process.env.CLAUDE_PLUGIN_ROOT;
  if (pluginRoot) {
    const p = path.join(pluginRoot, 'skills/adia-ui-release/references/gates-catalog.md');
    if (fs.existsSync(p)) return p;
  }
  const here = path.dirname(new URL(import.meta.url).pathname);
  return path.join(here, '..', 'references', 'gates-catalog.md');
}

// The catalog documents the gates the RELEASE FLOW runs — a curated set, NOT
// every quality script in package.json (which has many check:/verify:/smoke:/
// audit:/test: scripts, most of them component-authoring audits). Two universes:
//
//   - releaseGates (drives the UNDOCUMENTED check): the gates composed into the
//     `npm run check` pre-flight aggregate PLUS the roster gates run directly in
//     a cut (ROSTER_EXTRAS). A release-flow gate missing from the catalog is real
//     drift worth flagging.
//   - allScripts (drives the OBSOLETE check): every package.json script name. A
//     documented gate that no longer exists ANYWHERE has been removed/renamed —
//     real drift.
//
// This intentionally does NOT flag component-authoring `audit:*` scripts or
// `test:*` runner scripts as "undocumented" — they are not release-flow gates
// (audit:* are an authoring-side §SelfAudit domain, invoked indirectly via
// `check:dogfood-audits`).
const PREFLIGHT_AGGREGATE = 'check';
const ROSTER_EXTRAS = [
  'check:lockstep', 'verify:traits', 'smoke:engines', 'smoke:register-engine',
  'test:a2ui', 'test:unit', 'dogfood:status',
];

function loadScripts(repo) {
  const pkgJson = path.join(repo, 'package.json');
  if (!fs.existsSync(pkgJson)) {
    console.error(`error: ${pkgJson} not found (run from the monorepo root, or pass --repo)`);
    process.exit(2);
  }
  return JSON.parse(fs.readFileSync(pkgJson, 'utf8')).scripts || {};
}

// Gates the release flow runs: every `npm run <gate>` composed into the
// `npm run check` pre-flight aggregate, plus the roster gates run directly.
function loadReleaseGates(scripts) {
  const gates = new Set();
  const agg = scripts[PREFLIGHT_AGGREGATE] || '';
  const re = /\brun ([a-z][\w-]*(?::[\w-]+)+)/g;
  let m;
  while ((m = re.exec(agg)) !== null) gates.add(m[1]);
  for (const g of ROSTER_EXTRAS) if (scripts[g]) gates.add(g);
  return [...gates].sort();
}

function loadDocumentedGates(catalog) {
  if (!fs.existsSync(catalog)) {
    console.error(`error: ${catalog} not found`);
    process.exit(2);
  }
  const txt = fs.readFileSync(catalog, 'utf8');
  // Match ONLY heading-form gate documentation:
  //   ### `npm run <gate-name>`
  // NOT inline references to `npm run X` (which are typically
  // recovery commands cited in another gate's body).
  const matches = new Set();
  // Match `### `npm run X`` (Category 1-9 row form) OR
  //       `#### `npm run X`` (Category 10 stub form).
  const re = /^#{3,4} `npm run ([a-z][\w-]*(?::[\w-]+)+)`(.*)$/gm;
  let m;
  while ((m = re.exec(txt)) !== null) {
    // Skip explicitly forward-looking entries — a documented gate marked
    // "(NOT YET SHIPPED — recommended)" is an intentional recommendation, not
    // obsolete drift; it lives in the catalog before its script exists.
    if (/NOT YET SHIPPED|recommended/i.test(m[2])) continue;
    matches.add(m[1]);
  }
  return [...matches].sort();
}

// Suffix variants that count as documented if the base gate is documented.
// Per the §Suffix variant convention in references/gates-catalog.md.
const VARIANT_SUFFIXES = ['strict', 'fix', 'json', 'quiet', 'baseline', 'thinking', 'pro'];

function isCovered(gate, documentedSet) {
  if (documentedSet.has(gate)) return true;
  // Strip a single trailing variant suffix and check the base.
  const lastColon = gate.lastIndexOf(':');
  if (lastColon > 0) {
    const suffix = gate.slice(lastColon + 1);
    const base = gate.slice(0, lastColon);
    if (VARIANT_SUFFIXES.includes(suffix) && documentedSet.has(base)) {
      return true;
    }
  }
  return false;
}

function diff(releaseGates, allScripts, documented) {
  const allSet = new Set(allScripts);
  const documentedSet = new Set(documented);
  return {
    // Release-flow gate not in the catalog → document it.
    undocumented: releaseGates.filter((g) => !isCovered(g, documentedSet)),
    // Documented gate whose script no longer exists anywhere → remove the row.
    obsolete: documented.filter((g) => !allSet.has(g)),
    both: releaseGates.filter((g) => isCovered(g, documentedSet)),
  };
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const catalog = resolveCatalog();
  const scripts = loadScripts(args.repo);
  const releaseGates = loadReleaseGates(scripts);
  const allScripts = Object.keys(scripts);
  const documented = loadDocumentedGates(catalog);
  const d = diff(releaseGates, allScripts, documented);

  if (args.json) {
    console.log(JSON.stringify({
      releaseGates: releaseGates.length,
      documented: documented.length,
      both: d.both.length,
      undocumented: d.undocumented,
      obsolete: d.obsolete,
    }, null, 2));
  } else {
    console.log(`[audit-gate-roster] adia-ui-release §SelfAudit Axis 9`);
    console.log(`  release-flow gates (check + roster): ${releaseGates.length}`);
    console.log(`  documented in gates-catalog.md:      ${documented.length}`);
    console.log(`  both:                                ${d.both.length}`);
    console.log();
    if (d.undocumented.length === 0 && d.obsolete.length === 0) {
      console.log('  Clean — gate roster in sync.');
    } else {
      if (d.undocumented.length > 0) {
        console.log(`  Undocumented gates (${d.undocumented.length}) — exist in package.json but NOT in catalog:`);
        for (const g of d.undocumented) console.log(`      ${g}`);
        console.log(`    -> add a row in references/gates-catalog.md describing this gate.`);
      }
      if (d.obsolete.length > 0) {
        console.log(`  Obsolete catalog entries (${d.obsolete.length}) — in catalog but NO LONGER in package.json:`);
        for (const g of d.obsolete) console.log(`      ${g}`);
        console.log(`    -> remove the rows from references/gates-catalog.md.`);
      }
    }
  }

  if (args.strict && (d.undocumented.length > 0 || d.obsolete.length > 0)) {
    process.exit(1);
  }
}

main();
