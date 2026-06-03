#!/usr/bin/env node
// dispatch-publish.mjs — dispatch the 9 publish workflows for a
// version, optionally waiting for an earlier batch to settle first.
//
// Usage:
//   # Single-version dispatch:
//   node dispatch-publish.mjs --version 0.6.22
//
//   # Batch push: dispatch v0.6.21 first, wait, then v0.6.22:
//   node dispatch-publish.mjs --version 0.6.21
//   # ... wait for completion ...
//   node dispatch-publish.mjs --version 0.6.22 --after 0.6.21
//
//   # Dry mode:
//   node dispatch-publish.mjs --version 0.6.22 --dry
//
// Phase 2 of the adia-ui-release skill. Mechanizes the dispatch loop
// + handles the npm-latest ordering rule for batch pushes.

import { execSync } from 'node:child_process';
import process from 'node:process';
import { assertMonorepoRoot } from './assert-monorepo-root.mjs';

// Instance data — fork-configurable. The npm scope the 9 packages publish under.
// Default preserves @adia-ai behavior; override via --scope or $ADIA_NPM_SCOPE.
const DEFAULT_SCOPE = '@adia-ai';

const PACKAGES = [
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
  const args = {
    version: null, after: null, dry: false, sleepBefore: 4,
    scope: process.env.ADIA_NPM_SCOPE || DEFAULT_SCOPE,
  };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    if (k === '--version') args.version = argv[++i];
    else if (k === '--after') args.after = argv[++i];
    else if (k === '--dry') args.dry = true;
    else if (k === '--sleep-before') args.sleepBefore = parseInt(argv[++i], 10);
    else if (k === '--scope') args.scope = argv[++i];
    else if (k === '-h' || k === '--help') {
      console.log('Usage: node dispatch-publish.mjs --version X.Y.Z [--after X.Y.Z-1] [--dry] [--sleep-before <seconds>] [--scope @org]');
      console.log('');
      console.log('--after  Verify npm latest is at the given version before dispatching this one.');
      console.log('         Used in batch push to ensure publish ordering.');
      console.log(`--scope  npm scope the packages publish under (default: ${DEFAULT_SCOPE};`);
      console.log('         or set $ADIA_NPM_SCOPE). The --after npm-latest check uses this scope.');
      process.exit(0);
    }
  }
  if (!args.version) {
    console.error('error: --version is required');
    process.exit(2);
  }
  return args;
}

function run(cmd, dry) {
  if (dry) {
    console.log(`  [dry] ${cmd}`);
    return '';
  }
  return execSync(cmd, { encoding: 'utf8' });
}

function checkAfter(afterVersion, scope) {
  console.log(`Checking npm latest is at ${afterVersion} before dispatching...`);
  try {
    const latest = execSync(`npm view ${scope}/web-components dist-tags.latest`, { encoding: 'utf8' }).trim();
    if (latest !== afterVersion) {
      console.error(`error: npm ${scope}/web-components latest is '${latest}', expected '${afterVersion}'`);
      console.error('  This means the previous batch hasn\'t completed publishing.');
      console.error('  Wait for the previous --version cycle to settle, then re-run.');
      process.exit(1);
    }
    console.log(`  ✓ npm latest = ${latest}`);
  } catch (e) {
    console.error(`error: failed to query npm latest: ${e.message}`);
    process.exit(2);
  }
}

function dispatch(pkg, version, dry) {
  const ref = `${pkg}-v${version}`;
  const cmd = `gh workflow run "publish-${pkg}.yml" --ref "${ref}"`;
  try {
    const out = run(cmd, dry);
    if (!dry && out) {
      const url = out.split('\n').find((l) => l.startsWith('http')) || '';
      console.log(`  ✓ dispatched ${pkg} (${url.trim()})`);
    } else if (dry) {
      // already printed by run()
    } else {
      console.log(`  ✓ dispatched ${pkg}`);
    }
    return true;
  } catch (e) {
    console.error(`  ✗ ERROR ${pkg}: ${e.message}`);
    return false;
  }
}

async function sleep(ms) {
  return new Promise((res) => setTimeout(res, ms));
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  // Fail-fast guard: refuse to run npm/gh against a non-monorepo directory.
  assertMonorepoRoot(process.cwd());
  if (args.after) checkAfter(args.after, args.scope);

  if (args.sleepBefore > 0 && !args.dry) {
    console.log(`Sleeping ${args.sleepBefore}s to let GH index the new tags...`);
    await sleep(args.sleepBefore * 1000);
  }

  console.log(`Dispatching 9 publish workflows for v${args.version}:`);
  let succeeded = 0;
  for (const pkg of PACKAGES) {
    if (dispatch(pkg, args.version, args.dry)) succeeded++;
  }
  console.log(`\n[dispatch] ${succeeded}/${PACKAGES.length} dispatched ${args.dry ? '(dry)' : ''}`);

  if (!args.dry) {
    console.log(`\n[next] wait for workflows to settle:`);
    console.log(`  until [ "$(gh run list --workflow=publish-a2ui-validator.yml --limit 1 --json status -q '.[0].status')" = "completed" ]; do sleep 5; done`);
    console.log(`\n[next] verify all 9 succeeded:`);
    console.log(`  for pkg in ${PACKAGES.join(' ')}; do`);
    console.log(`    gh run list --workflow=publish-$pkg.yml --limit 1 --json conclusion -q '.[0].conclusion'`);
    console.log(`  done`);
  }

  if (succeeded !== PACKAGES.length) process.exit(1);
}

main().catch((e) => {
  console.error(`error: ${e.message}`);
  process.exit(1);
});
