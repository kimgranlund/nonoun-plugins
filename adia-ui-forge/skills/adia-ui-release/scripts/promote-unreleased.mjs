#!/usr/bin/env node
// promote-unreleased.mjs — promote `## [Unreleased]` → `## [vX.Y.Z] — DATE`
// in N package CHANGELOGs.
//
// Idempotent. Stops if any target already has the [vX.Y.Z] heading
// (means you've already run this; would create a duplicate block).
//
// Usage:
//   node promote-unreleased.mjs --version 0.6.22 --date 2026-05-22 \
//     --packages web-components,web-modules,a2ui/corpus
//   node promote-unreleased.mjs --version 0.6.22 --date 2026-05-22 \
//     --packages web-components,web-modules --dry
//
// Phase 2 of the adia-ui-release skill. Replaces the inline heading-swap
// pattern used across v0.6.18 / v0.6.19 / v0.6.20 / v0.6.21 cycles.
//
// Exits:
//   0  — all targets promoted (or --dry succeeded)
//   1  — at least one target missing [Unreleased] OR already has [vX.Y.Z]
//   2  — bad args / file I/O error

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';

function parseArgs(argv) {
  const args = { version: null, date: null, packages: null, dry: false, repo: process.cwd() };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--version') args.version = argv[++i];
    else if (argv[i] === '--date') args.date = argv[++i];
    else if (argv[i] === '--packages') args.packages = argv[++i].split(',').map((s) => s.trim());
    else if (argv[i] === '--dry') args.dry = true;
    else if (argv[i] === '--repo') args.repo = argv[++i];
    else if (argv[i] === '-h' || argv[i] === '--help') {
      console.log('Usage: node promote-unreleased.mjs --version X.Y.Z --date YYYY-MM-DD --packages comma,list [--dry] [--repo <path>]');
      process.exit(0);
    }
  }
  if (!args.version || !args.date || !args.packages) {
    console.error('error: --version, --date, --packages all required');
    process.exit(2);
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

function promote(repo, pkg, version, date, dry) {
  const p = path.join(repo, 'packages', pkg, 'CHANGELOG.md');
  if (!fs.existsSync(p)) {
    console.error(`  ERROR ${pkg} — CHANGELOG.md not found at ${p}`);
    return 'missing';
  }
  const txt = fs.readFileSync(p, 'utf8');
  const newHeading = `## [${version}] — ${date}`;
  if (txt.includes(newHeading)) {
    console.error(`  ERROR ${pkg} — already has ${newHeading} (already promoted)`);
    return 'already-promoted';
  }
  if (!txt.includes('## [Unreleased]')) {
    console.error(`  ERROR ${pkg} — no '## [Unreleased]' heading found`);
    return 'no-unreleased';
  }
  const out = txt.replace('## [Unreleased]', newHeading);
  if (!dry) fs.writeFileSync(p, out);
  console.log(`  ${dry ? '[dry] ' : ''}promoted ${pkg}: [Unreleased] → [${version}] — ${date}`);
  return 'promoted';
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const results = args.packages.map((pkg) => promote(args.repo, pkg, args.version, args.date, args.dry));
  const promoted = results.filter((r) => r === 'promoted').length;
  const failed = results.filter((r) => r !== 'promoted').length;
  console.log(`\n[promote] ${promoted}/${args.packages.length} ${args.dry ? '(dry)' : 'promoted'}`);
  if (failed > 0) {
    console.error(`[promote] ${failed} target(s) did not promote — see ERRORs above`);
    process.exit(1);
  }
}

main();
