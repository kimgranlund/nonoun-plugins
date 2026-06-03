#!/usr/bin/env node
// bump.mjs — bump 9 @adia-ai/* package.json from --from to --to.
//
// Idempotent. Stops on the first mismatch (a package not at --from) so
// you can investigate before any mutation lands.
//
// Usage:
//   node bump.mjs --from 0.6.20 --to 0.6.21
//   node bump.mjs --from 0.6.20 --to 0.6.21 --dry
//
// Phase 1 of the adia-ui-release skill. Replaces the /tmp/vXXX-prep.mjs
// improvisation pattern from the v0.6.13 → v0.6.21 cycles.
//
// Exits:
//   0  — all 9 bumped successfully (or --dry succeeded)
//   1  — at least one package not at --from (no mutation)
//   2  — bad args / file I/O error
//   3  — partial mutation (shouldn't happen if --from validation passes)

import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';

const PACKAGES = [
  'packages/web-components',
  'packages/web-modules',
  'packages/llm',
  'packages/a2ui/compose',
  'packages/a2ui/corpus',
  'packages/a2ui/mcp',
  'packages/a2ui/retrieval',
  'packages/a2ui/runtime',
  'packages/a2ui/validator',
];

function parseArgs(argv) {
  const args = { from: null, to: null, dry: false, repo: process.cwd() };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--from') args.from = argv[++i];
    else if (argv[i] === '--to') args.to = argv[++i];
    else if (argv[i] === '--dry') args.dry = true;
    else if (argv[i] === '--repo') args.repo = argv[++i];
    else if (argv[i] === '-h' || argv[i] === '--help') {
      console.log('Usage: node bump.mjs --from X.Y.Z --to X.Y.Z+1 [--dry] [--repo <path>]');
      process.exit(0);
    }
  }
  if (!args.from || !args.to) {
    console.error('error: both --from and --to are required (e.g. --from 0.6.20 --to 0.6.21)');
    process.exit(2);
  }
  if (!/^\d+\.\d+\.\d+(-[\w.]+)?$/.test(args.from) || !/^\d+\.\d+\.\d+(-[\w.]+)?$/.test(args.to)) {
    console.error('error: --from and --to must be semver (e.g. 0.6.21 or 0.6.22-rc.1)');
    process.exit(2);
  }
  return args;
}

function loadPackageJsons(repo) {
  const result = [];
  for (const pkg of PACKAGES) {
    const p = path.join(repo, pkg, 'package.json');
    if (!fs.existsSync(p)) {
      console.error(`error: missing ${p}`);
      process.exit(2);
    }
    const txt = fs.readFileSync(p, 'utf8');
    const json = JSON.parse(txt);
    result.push({ pkg, path: p, txt, version: json.version });
  }
  return result;
}

function validateAllAtFrom(packages, from) {
  const wrong = packages.filter((p) => p.version !== from);
  if (wrong.length > 0) {
    console.error(`error: ${wrong.length}/${packages.length} package(s) NOT at ${from}:`);
    for (const w of wrong) {
      console.error(`  ${w.pkg}: ${w.version}`);
    }
    return false;
  }
  return true;
}

function bumpAll(packages, from, to, dry) {
  const FROM_PATTERN = new RegExp(`"version":\\s*"${from.replace(/\./g, '\\.')}"`);
  const TO_LITERAL = `"version": "${to}"`;
  let bumped = 0;
  for (const p of packages) {
    const out = p.txt.replace(FROM_PATTERN, TO_LITERAL);
    if (out === p.txt) {
      console.error(`error: ${p.pkg} — regex did not match (corrupted package.json?)`);
      return -1;
    }
    if (!dry) fs.writeFileSync(p.path, out);
    bumped++;
    console.log(`  ${dry ? '[dry] ' : ''}bumped ${p.pkg}: ${from} → ${to}`);
  }
  return bumped;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const packages = loadPackageJsons(args.repo);
  if (!validateAllAtFrom(packages, args.from)) process.exit(1);
  const bumped = bumpAll(packages, args.from, args.to, args.dry);
  if (bumped < 0) process.exit(3);
  console.log(`\n[bump] ${bumped}/9 ${args.dry ? '(dry — no files written)' : 'bumped'}`);
  if (!args.dry) {
    console.log(`\n[next] regenerate the lockfile:`);
    console.log(`  npm install --package-lock-only --no-audit --no-fund`);
    console.log(`\n[next] verify lockstep:`);
    console.log(`  npm run check:lockstep`);
  }
}

main();
