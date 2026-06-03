#!/usr/bin/env node
// insert-stub.mjs — insert the ride-along lockstep stub block into N
// package CHANGELOGs above the previous version's heading.
//
// Idempotent. Stops if any target already has the [vX.Y.Z] heading.
//
// Usage:
//   node insert-stub.mjs --version 0.6.22 --date 2026-05-22 \
//     --substantive "<one-line summary>" \
//     --xref "packages/web-modules/CHANGELOG.md#0622--2026-05-22" \
//     --previous-version 0.6.21 \
//     --packages llm,a2ui/compose,a2ui/mcp,a2ui/retrieval,a2ui/runtime,a2ui/validator
//
// Phase 2 of the adia-ui-release skill. Replaces the inline stub-
// insertion pattern used across v0.6.18 / v0.6.19 / v0.6.20 / v0.6.21
// cycles.

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';

function parseArgs(argv) {
  const args = {
    version: null,
    date: null,
    substantive: null,
    xref: null,
    previous: null,
    packages: null,
    dry: false,
    repo: process.cwd(),
  };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    if (k === '--version') args.version = argv[++i];
    else if (k === '--date') args.date = argv[++i];
    else if (k === '--substantive') args.substantive = argv[++i];
    else if (k === '--xref') args.xref = argv[++i];
    else if (k === '--previous-version') args.previous = argv[++i];
    else if (k === '--packages') args.packages = argv[++i].split(',').map((s) => s.trim());
    else if (k === '--dry') args.dry = true;
    else if (k === '--repo') args.repo = argv[++i];
    else if (k === '-h' || k === '--help') {
      console.log('Usage: node insert-stub.mjs --version X.Y.Z --date YYYY-MM-DD --substantive "..." --xref "..." --previous-version X.Y.Z-1 --packages comma,list [--dry] [--repo <path>]');
      process.exit(0);
    }
  }
  for (const [k, v] of Object.entries(args)) {
    if (v === null && k !== 'dry') {
      console.error(`error: --${k.replace(/([A-Z])/g, '-$1').toLowerCase()} is required`);
      process.exit(2);
    }
  }
  if (!/^\d+\.\d+\.\d+(-[\w.]+)?$/.test(args.version)) {
    console.error('error: --version must be semver');
    process.exit(2);
  }
  if (!/^\d{4}-\d{2}-\d{2}$/.test(args.date)) {
    console.error('error: --date must be YYYY-MM-DD');
    process.exit(2);
  }
  return args;
}

function buildStub(version, date, substantive, xref) {
  return `## [${version}] — ${date}

### Maintenance
- **Lockstep version bump only.** No source changes in this package; bumped to maintain the 9-package version coherence enforced by \`scripts/release/check-lockstep.mjs\`. Substantive v${version} work shipped in ${substantive}. See \`${xref}\` for details.

`;
}

function insertStub(repo, pkg, anchor, stubBlock, version, dry) {
  const p = path.join(repo, 'packages', pkg, 'CHANGELOG.md');
  if (!fs.existsSync(p)) {
    console.error(`  ERROR ${pkg} — CHANGELOG.md not found at ${p}`);
    return 'missing';
  }
  const txt = fs.readFileSync(p, 'utf8');
  if (txt.includes(`## [${version}]`)) {
    console.error(`  ERROR ${pkg} — already has [${version}] heading`);
    return 'already-present';
  }
  if (!txt.includes(anchor)) {
    console.error(`  ERROR ${pkg} — anchor '${anchor}' not found`);
    return 'no-anchor';
  }
  const out = txt.replace(anchor, stubBlock + anchor);
  if (!dry) fs.writeFileSync(p, out);
  console.log(`  ${dry ? '[dry] ' : ''}stub inserted: ${pkg}`);
  return 'inserted';
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  // Anchor — find this in each CHANGELOG, insert ABOVE it.
  // Read previous date from the actual anchor's line (auto-detect) — we
  // only know the previous version, not the date. So we look for any
  // line matching `## [<previous>] — `.
  const PREV_HEADING_RE = new RegExp(`^## \\[${args.previous.replace(/\./g, '\\.')}\\] — \\d{4}-\\d{2}-\\d{2}$`, 'm');
  const stubBlock = buildStub(args.version, args.date, args.substantive, args.xref);
  const results = args.packages.map((pkg) => {
    const p = path.join(args.repo, 'packages', pkg, 'CHANGELOG.md');
    if (!fs.existsSync(p)) {
      console.error(`  ERROR ${pkg} — not found`);
      return 'missing';
    }
    const txt = fs.readFileSync(p, 'utf8');
    const m = txt.match(PREV_HEADING_RE);
    if (!m) {
      console.error(`  ERROR ${pkg} — no '## [${args.previous}] — YYYY-MM-DD' heading found`);
      return 'no-anchor';
    }
    const anchor = m[0];
    return insertStub(args.repo, pkg, anchor, stubBlock, args.version, args.dry);
  });
  const inserted = results.filter((r) => r === 'inserted').length;
  const failed = results.filter((r) => r !== 'inserted').length;
  console.log(`\n[insert-stub] ${inserted}/${args.packages.length} ${args.dry ? '(dry)' : 'inserted'}`);
  if (failed > 0) {
    console.error(`[insert-stub] ${failed} target(s) failed — see ERRORs above`);
    process.exit(1);
  }
}

main();
