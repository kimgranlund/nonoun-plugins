#!/usr/bin/env node
// tag-lockstep.mjs — create 10 lockstep tags (umbrella vX.Y.Z + 9
// per-package <pkg>-vX.Y.Z) at HEAD or at a specified SHA.
//
// Usage:
//   node tag-lockstep.mjs --version 0.6.22
//   node tag-lockstep.mjs --version 0.6.22 --at <sha>
//   node tag-lockstep.mjs --version 0.6.22 --delete     # delete existing tags
//   node tag-lockstep.mjs --version 0.6.22 --dry        # print commands without running
//
// Phase 2 of the adia-ui-release skill. Mechanizes the tag loop used
// every cycle.

import { execSync } from 'node:child_process';
import process from 'node:process';
import { assertMonorepoRoot } from './assert-monorepo-root.mjs';

const PER_PACKAGE_NAMES = [
  'web-components',
  'web-modules',
  'llm',
  'a2ui-runtime',
  'a2ui-compose',
  'a2ui-corpus',
  'a2ui-mcp',
  'a2ui-retrieval',
  'a2ui-validator',
];

function parseArgs(argv) {
  const args = { version: null, at: null, deleteMode: false, dry: false, repo: process.cwd() };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    if (k === '--version') args.version = argv[++i];
    else if (k === '--at') args.at = argv[++i];
    else if (k === '--delete') args.deleteMode = true;
    else if (k === '--dry') args.dry = true;
    else if (k === '--repo') args.repo = argv[++i];
    else if (k === '-h' || k === '--help') {
      console.log('Usage: node tag-lockstep.mjs --version X.Y.Z [--at <sha>] [--delete] [--dry] [--repo <path>]');
      process.exit(0);
    }
  }
  if (!args.version) {
    console.error('error: --version is required');
    process.exit(2);
  }
  return args;
}

function buildTagList(version) {
  return ['v' + version, ...PER_PACKAGE_NAMES.map((p) => `${p}-v${version}`)];
}

function run(cmd, repo, dry) {
  if (dry) {
    console.log(`  [dry] ${cmd}`);
    return '';
  }
  return execSync(cmd, { cwd: repo, encoding: 'utf8' });
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  // Fail-fast guard: refuse to run git against a non-monorepo directory.
  assertMonorepoRoot(args.repo);
  const tags = buildTagList(args.version);

  if (args.deleteMode) {
    console.log(`Deleting 10 tags for v${args.version}:`);
    for (const t of tags) {
      try {
        run(`git tag -d ${t}`, args.repo, args.dry);
        console.log(`  ${args.dry ? '[dry] ' : ''}deleted ${t}`);
      } catch (e) {
        console.error(`  WARN ${t} did not exist (no-op)`);
      }
    }
    console.log(`\n[tag-lockstep] ${tags.length} tags deleted ${args.dry ? '(dry)' : ''}`);
    return;
  }

  const targetSha = args.at || run('git rev-parse HEAD', args.repo, false).trim();
  console.log(`Creating 10 tags for v${args.version} at ${targetSha.slice(0, 9)}:`);
  for (const t of tags) {
    try {
      run(`git tag ${t} ${args.at || ''}`.trim(), args.repo, args.dry);
      console.log(`  ${args.dry ? '[dry] ' : ''}created ${t}`);
    } catch (e) {
      console.error(`  ERROR ${t}: ${e.message}`);
      process.exit(3);
    }
  }
  console.log(`\n[tag-lockstep] ${tags.length} tags created at ${targetSha.slice(0, 9)} ${args.dry ? '(dry)' : ''}`);

  if (!args.dry) {
    console.log(`\n[next] run F-N1:`);
    console.log(`  node scripts/release/check-release.mjs --all-pending`);
    console.log(`\n[next] when F-N1 is 9/9 clean, push:`);
    console.log(`  git push origin main`);
    console.log(`  git push origin ${tags.join(' \\\n    ')}`);
  }
}

try {
  main();
} catch (e) {
  console.error(`error: ${e.message}`);
  process.exit(1);
}
