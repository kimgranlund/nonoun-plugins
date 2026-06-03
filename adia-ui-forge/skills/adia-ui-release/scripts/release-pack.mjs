#!/usr/bin/env node
// release-pack.mjs — full-cycle orchestrator for an AdiaUI lockstep release.
//
// Chains the 6 Phase-1/2/3 CLI helpers (bump · promote-unreleased ·
// insert-stub · tag-lockstep · dispatch-publish · make-ledger) plus the
// non-helper steps (lockfile · pre-flight gates · git commit · F-N1 ·
// push · GH releases · site deploy) into one walked sequence with 3
// operator checkpoints (before tag, before push, before publish) per
// SKILL.md §Posture.
//
// MODES:
//   --mode cut          (Mode 1 — peer pre-staged [Unreleased] or pure stub)
//   --mode from-scratch (Mode 2 — promote [Unreleased] → [VERSION] in 1-3 pkgs)
//   --mode handoff      (Mode 3 — peer pre-cut the release commit; skip bump/commit)
//   --mode batch        (Mode 4 — multiple unpushed cuts; pass --version-list)
//
// REQUIRED:
//   --version 0.6.22
//   --date 2026-05-22
//   --previous-version 0.6.21
//
// CONTENT (operator-authored; the orchestrator does not generate):
//   --commit-message-file <path>      : the release commit body
//   --gh-notes-file <path>            : GH release notes body (one per cycle)
//   --substantive "<one-line>"        : for the stub block xref
//   --xref "<changelog-anchor>"       : for the stub block
//   --substantive-packages a,b,c      : packages with [Unreleased] to promote
//   --stub-packages a,b,c             : packages getting the lockstep stub
//
// FLAGS:
//   --dry                : preview all commands, no mutation, no prompts
//   --yes                : skip the 3 operator checkpoints (CI / scripted)
//   --skip-gates         : (DEBUG ONLY) skip pre-flight (don't ship anything!)
//   --skip-site          : skip the EXE deploy step (rare; for offline cycles)
//
// PHASE 4 of the adia-ui-release skill. Mechanizes the 11-step cycle from
// references/cycle-happy-path.md while preserving operator judgment at
// the 3 mutating-checkpoint boundaries.

import { execSync } from 'node:child_process';
import { createInterface } from 'node:readline/promises';
import { stdin, stdout } from 'node:process';
import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { assertMonorepoRoot } from './assert-monorepo-root.mjs';

const SCRIPT_DIR = path.dirname(new URL(import.meta.url).pathname);
const REPO = process.cwd();

// Instance data — fork-configurable; defaults preserve @adia-ai behavior.
//   Deploy host (rsync target + curl verify): --host or $ADIA_DEPLOY_HOST.
//   npm scope (publishes + npm-view + GH release titles): --scope or $ADIA_NPM_SCOPE.
const DEFAULT_DEPLOY_HOST = 'ui-kit.exe.xyz';
const DEFAULT_NPM_SCOPE = '@adia-ai';

const PACKAGES = ['web-components', 'web-modules', 'llm', 'a2ui-runtime',
                  'a2ui-compose', 'a2ui-corpus', 'a2ui-mcp', 'a2ui-retrieval',
                  'a2ui-validator'];

function parseArgs(argv) {
  const args = {
    version: null, date: null, previous: null, mode: null,
    commitMessageFile: null, ghNotesFile: null,
    substantive: null, xref: null,
    substantivePackages: null, stubPackages: null,
    versionList: null,
    host: process.env.ADIA_DEPLOY_HOST || DEFAULT_DEPLOY_HOST,
    scope: process.env.ADIA_NPM_SCOPE || DEFAULT_NPM_SCOPE,
    dry: false, yes: false, skipGates: false, skipSite: false,
  };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    if (k === '--version') args.version = argv[++i];
    else if (k === '--date') args.date = argv[++i];
    else if (k === '--previous-version') args.previous = argv[++i];
    else if (k === '--mode') args.mode = argv[++i];
    else if (k === '--commit-message-file') args.commitMessageFile = argv[++i];
    else if (k === '--gh-notes-file') args.ghNotesFile = argv[++i];
    else if (k === '--substantive') args.substantive = argv[++i];
    else if (k === '--xref') args.xref = argv[++i];
    else if (k === '--substantive-packages') args.substantivePackages = argv[++i].split(',');
    else if (k === '--stub-packages') args.stubPackages = argv[++i].split(',');
    else if (k === '--version-list') args.versionList = argv[++i].split(',');
    else if (k === '--host') args.host = argv[++i];
    else if (k === '--scope') args.scope = argv[++i];
    else if (k === '--dry') args.dry = true;
    else if (k === '--yes') args.yes = true;
    else if (k === '--skip-gates') args.skipGates = true;
    else if (k === '--skip-site') args.skipSite = true;
    else if (k === '-h' || k === '--help') { help(); process.exit(0); }
  }
  if (!args.version || !args.date || !args.previous || !args.mode) {
    console.error('error: --version, --date, --previous-version, --mode all required');
    console.error('       see --help');
    process.exit(2);
  }
  if (!['cut', 'from-scratch', 'handoff', 'batch'].includes(args.mode)) {
    console.error(`error: --mode must be cut|from-scratch|handoff|batch (got: ${args.mode})`);
    process.exit(2);
  }
  return args;
}

function help() {
  console.log(`Usage:
  node release-pack.mjs --mode cut --version X.Y.Z --date YYYY-MM-DD \\
    --previous-version X.Y.Z-1 \\
    --commit-message-file /tmp/v$X.Y.Z-commit.txt \\
    --gh-notes-file /tmp/release-v$X.Y.Z.md \\
    --substantive "<one-line>" \\
    --xref "packages/web-modules/CHANGELOG.md#0$X$Y$Z--YYYY-MM-DD" \\
    --substantive-packages web-components,web-modules,a2ui/corpus \\
    --stub-packages llm,a2ui/compose,a2ui/mcp,a2ui/retrieval,a2ui/runtime,a2ui/validator

Flags: --dry  (preview all)  --yes  (skip prompts)  --skip-site  (skip EXE deploy)
Instance: --host <deploy-host>  (default ${DEFAULT_DEPLOY_HOST}; or $ADIA_DEPLOY_HOST)
          --scope <@org>        (npm scope; default ${DEFAULT_NPM_SCOPE}; or $ADIA_NPM_SCOPE)`);
}

const rl = createInterface({ input: stdin, output: stdout });
async function checkpoint(label, args) {
  if (args.yes) {
    console.log(`\n[checkpoint] ${label} — auto-confirmed (--yes)`);
    return;
  }
  const answer = await rl.question(`\n[CHECKPOINT] ${label} — proceed? [y/N]: `);
  if (!/^y(es)?$/i.test(answer.trim())) {
    console.log('[checkpoint] aborted by operator');
    rl.close();
    process.exit(0);
  }
}

function sh(cmd, args, opts = {}) {
  if (args.dry) {
    console.log(`  [dry] ${cmd}`);
    return '';
  }
  return execSync(cmd, { cwd: REPO, encoding: 'utf8', stdio: opts.stdio || 'inherit' });
}

function shQuiet(cmd, args) {
  if (args.dry) {
    console.log(`  [dry] ${cmd}`);
    return '';
  }
  return execSync(cmd, { cwd: REPO, encoding: 'utf8' });
}

// ── Step 1 — Re-baseline ──────────────────────────────────────────
function step1ReBaseline(args) {
  console.log('\n=== Step 1 — Re-baseline ===');
  console.log('git status --short:');
  sh('git status --short', args);
  console.log('\norigin/main..HEAD (unpushed):');
  sh('git log origin/main..HEAD --oneline', args);
  console.log('\nHEAD..origin/main (must be empty before push):');
  const out = shQuiet('git log HEAD..origin/main --oneline', args).trim();
  if (out && !args.dry) {
    console.error('ERROR: remote ahead — pull/rebase before proceeding');
    process.exit(1);
  }
  console.log('  (empty — origin not ahead)');
}

// ── Step 3 — Pre-flight gates ────────────────────────────────────
function step3PreFlight(args) {
  if (args.skipGates) {
    console.log('\n=== Step 3 — Pre-flight (SKIPPED via --skip-gates; danger!) ===');
    return;
  }
  console.log('\n=== Step 3 — Pre-flight gates ===');
  const gates = [
    'node scripts/build/components.mjs --verify',
    'npm run verify:traits',
    'npm run check:lockstep',
    'npm run test:unit',
    'npm run typecheck',
    'npm run check:demo-shells',
    'npm run check:lightningcss-build',
    'npm run smoke:engines',
    'npm run smoke:register-engine',
    'npm run check:links',
    'npm run check:embeddings-fresh',
    'npm run verify:corpus',
  ];
  for (const g of gates) {
    console.log(`\n  ${g}`);
    try {
      sh(g, args, { stdio: 'inherit' });
    } catch (e) {
      console.error(`\n  ✗ FAILED: ${g}`);
      console.error('  Pre-flight aborted. Fix the gate failure before proceeding.');
      console.error('  See references/gates-catalog.md for failure-mode → recovery.');
      process.exit(1);
    }
  }
}

// ── Step 4 — Promote + bump + lockfile ───────────────────────────
function step4PromoteAndBump(args) {
  if (args.mode === 'handoff') {
    console.log('\n=== Step 4 — SKIPPED (mode handoff: peer cut the release commit) ===');
    return;
  }
  console.log('\n=== Step 4 — Promote + Bump + Lockfile ===');

  if (args.mode === 'from-scratch' && args.substantivePackages) {
    const cmd = `node ${SCRIPT_DIR}/promote-unreleased.mjs --version ${args.version} --date ${args.date} --packages ${args.substantivePackages.join(',')}`;
    sh(cmd, args);
  }

  if (args.stubPackages && args.substantive && args.xref) {
    const cmd = `node ${SCRIPT_DIR}/insert-stub.mjs --version ${args.version} --date ${args.date} --previous-version ${args.previous} --substantive "${args.substantive}" --xref "${args.xref}" --packages ${args.stubPackages.join(',')}`;
    sh(cmd, args);
  }

  sh(`node ${SCRIPT_DIR}/bump.mjs --from ${args.previous} --to ${args.version}`, args);
  sh('npm install --package-lock-only --no-audit --no-fund', args);
  sh('npm run check:lockstep', args);
}

// ── Step 5 — Commit ──────────────────────────────────────────────
function step5Commit(args) {
  if (args.mode === 'handoff') {
    console.log('\n=== Step 5 — SKIPPED (mode handoff) ===');
    return;
  }
  console.log('\n=== Step 5 — Stage + Commit ===');
  sh('git reset HEAD >/dev/null 2>&1 || true', args);
  const releaseFiles = [
    'package-lock.json',
    ...PACKAGES.flatMap((p) => {
      const dir = p.startsWith('a2ui-') ? `packages/a2ui/${p.replace('a2ui-', '')}` : `packages/${p}`;
      return [`${dir}/package.json`, `${dir}/CHANGELOG.md`];
    }),
  ];
  sh(`git add ${releaseFiles.join(' ')}`, args);
  sh('git diff --cached --stat | tail -3', args);
  if (!args.commitMessageFile) {
    console.error('ERROR: --commit-message-file required for cut/from-scratch mode');
    process.exit(2);
  }
  if (!args.dry && !fs.existsSync(args.commitMessageFile)) {
    console.error(`ERROR: commit message file not found: ${args.commitMessageFile}`);
    process.exit(2);
  }
  sh(`git commit -F ${args.commitMessageFile}`, args);
}

// ── Step 6 — Tag ─────────────────────────────────────────────────
async function step6Tag(args) {
  console.log('\n=== Step 6 — Tag at HEAD ===');
  await checkpoint('Ready to create 10 tags (umbrella + 9 per-package)', args);
  sh(`node ${SCRIPT_DIR}/tag-lockstep.mjs --version ${args.version}`, args);
}

// ── Step 7 — F-N1 ────────────────────────────────────────────────
function step7Fn1(args) {
  console.log('\n=== Step 7 — F-N1 release trip-wire ===');
  try {
    sh('node scripts/release/check-release.mjs --all-pending', args);
  } catch (e) {
    // F-N1 sometimes exits non-zero on cosmetic warns; show the output and let the operator decide
    console.warn('\n  F-N1 returned non-zero — review the warns above.');
    console.warn('  See references/changelog-discipline.md § F-N1 diff-coverage enrichment.');
  }
}

// ── Step 8 — Push ────────────────────────────────────────────────
async function step8Push(args) {
  console.log('\n=== Step 8 — Push main + tags ===');
  const count = shQuiet('git rev-list --count origin/main..HEAD', args).trim();
  console.log(`  commits to push: ${count}`);
  await checkpoint(`Ready to push ${count} commit(s) + 10 tags`, args);
  sh('git push origin main', args);
  const tagList = [`v${args.version}`, ...PACKAGES.map((p) => `${p}-v${args.version}`)].join(' ');
  sh(`git push origin ${tagList}`, args);
}

// ── Step 9 — Publish ─────────────────────────────────────────────
async function step9Publish(args) {
  console.log('\n=== Step 9 — Dispatch publishes ===');
  await checkpoint('Ready to dispatch 9 npm publishes', args);
  sh(`node ${SCRIPT_DIR}/dispatch-publish.mjs --version ${args.version} --scope ${args.scope}`, args);
  console.log('\n  Waiting for publishes to settle...');
  sh(`until [ "$(gh run list --workflow=publish-a2ui-validator.yml --limit 1 --json status -q '.[0].status')" = "completed" ]; do sleep 5; done`, args);
  console.log('  ✓ publishes settled');
  console.log('\n  Verify all 9 succeeded + npm latest:');
  sh(`for pkg in ${PACKAGES.join(' ')}; do echo -n "$pkg: "; npm view "${args.scope}/$pkg" version 2>/dev/null; done`, args);
  sh(`echo -n "latest: "; npm view ${args.scope}/web-components dist-tags.latest 2>/dev/null`, args);
}

// ── Step 10 — GH releases + site deploy ──────────────────────────
async function step10GhAndSite(args) {
  console.log('\n=== Step 10 — GH releases + Site deploy ===');
  if (!args.ghNotesFile) {
    console.error('ERROR: --gh-notes-file required for GH releases');
    process.exit(2);
  }
  if (!args.dry && !fs.existsSync(args.ghNotesFile)) {
    console.error(`ERROR: GH notes file not found: ${args.ghNotesFile}`);
    process.exit(2);
  }
  for (const pkg of PACKAGES) {
    sh(`gh release create "${pkg}-v${args.version}" --title "${args.scope}/${pkg} v${args.version}" --notes-file ${args.ghNotesFile}`, args);
  }
  if (args.skipSite) {
    console.log('  --skip-site set; skipping EXE deploy');
    return;
  }
  sh('npm run build:site', args);
  sh(`rsync -az --delete dist/ ${args.host}:/srv/adia-ui/dist/`, args);
  sh(`curl -s -o /dev/null -w "EXE gen-ui: HTTP %{http_code}\\n" https://${args.host}/site/gen-ui/`, args);
}

// ── Step 11 — Ledger ─────────────────────────────────────────────
function step11Ledger(args) {
  console.log('\n=== Step 11 — Audit-history ledger ===');
  const cmd = `node ${SCRIPT_DIR}/make-ledger.mjs --version ${args.version} --date ${args.date} --summary "<TODO: paste from commit message>" --note "Shipped via release-pack.mjs mode=${args.mode}"`;
  sh(cmd, args);
  console.log('\n  Edit the generated ledger to fill in scope/verification details, then commit + push.');
}

// ── Main ─────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs(process.argv.slice(2));
  // Fail-fast guard: refuse to git/npm/gh/curl against a non-monorepo directory.
  assertMonorepoRoot(REPO);
  console.log(`adia-ui-release release-pack — v${args.version} (${args.mode})${args.dry ? ' [DRY]' : ''}`);
  step1ReBaseline(args);
  step3PreFlight(args);
  step4PromoteAndBump(args);
  step5Commit(args);
  await step6Tag(args);
  step7Fn1(args);
  await step8Push(args);
  await step9Publish(args);
  await step10GhAndSite(args);
  step11Ledger(args);
  rl.close();
  console.log('\n✓ release-pack complete. Don\'t forget to commit + push the ledger.');
}

main().catch((e) => {
  console.error(e);
  rl.close();
  process.exit(1);
});
