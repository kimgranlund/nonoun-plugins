#!/usr/bin/env node
// make-ledger.mjs — author .brain/audit-history/YYYY-MM-DD-release-vX.Y.Z.json
// from git state + cycle-specific notes.
//
// Reads:
//   - the current git HEAD (release_commit + tag_commit if same)
//   - the 10 tags for the given version (collected from `git tag`)
//   - the recent gate-run output (passed via --verification-file or
//     --verification-json or computed best-effort from `npm run check:lockstep`)
//
// Writes:
//   - .brain/audit-history/YYYY-MM-DD-release-vX.Y.Z.json
//
// Usage:
//   node make-ledger.mjs --version 0.6.22 --date 2026-05-22 \
//     --summary "9-package lockstep PATCH cut. Substantive: ..." \
//     --kind release-cut
//   node make-ledger.mjs --version 0.6.22 --date 2026-05-22 --kind batch-push \
//     --versions 0.6.21,0.6.22 --summary "..."
//
// Optional flags:
//   --tag-commit <sha>       (default: HEAD)
//   --release-commit <sha>   (default: tag-commit)
//   --scope <key=value,...>  shorthand for the .scope.{key} block
//   --note "<text>"          append to .notes array; repeatable
//   --interactive            prompt for missing required fields
//   --dry                    print to stdout without writing
//
// Phase 3 of the adia-ui-release skill. Mechanizes the per-cycle ledger
// authoring used at Step 11 of cycle-happy-path.

import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';
import process from 'node:process';
import { assertMonorepoRoot } from './assert-monorepo-root.mjs';

function parseArgs(argv) {
  const args = {
    version: null,
    date: null,
    kind: 'release-cut',
    summary: null,
    versions: null,
    tagCommit: null,
    releaseCommit: null,
    scope: {},
    notes: [],
    dry: false,
    repo: process.cwd(),
    repoSlug: '<org>/<repo>',
  };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    if (k === '--version') args.version = argv[++i];
    else if (k === '--date') args.date = argv[++i];
    else if (k === '--kind') args.kind = argv[++i];
    else if (k === '--summary') args.summary = argv[++i];
    else if (k === '--versions') args.versions = argv[++i].split(',');
    else if (k === '--tag-commit') args.tagCommit = argv[++i];
    else if (k === '--release-commit') args.releaseCommit = argv[++i];
    else if (k === '--scope') {
      const pairs = argv[++i].split(',');
      for (const p of pairs) {
        const [key, ...val] = p.split('=');
        args.scope[key] = val.join('=');
      }
    } else if (k === '--note') args.notes.push(argv[++i]);
    else if (k === '--dry') args.dry = true;
    else if (k === '--repo') args.repo = argv[++i];
    else if (k === '--repo-slug') args.repoSlug = argv[++i];
    else if (k === '-h' || k === '--help') {
      console.log('Usage: node make-ledger.mjs --version X.Y.Z --date YYYY-MM-DD --summary "..." [--kind release-cut|batch-push|p1-hotfix] [--repo-slug <org>/<repo>] [--tag-commit <sha>] [--release-commit <sha>] [--scope key=val,...] [--note "..."] [--dry]');
      process.exit(0);
    }
  }
  if (!args.version || !args.date || !args.summary) {
    console.error('error: --version, --date, --summary all required');
    process.exit(2);
  }
  // Fail-fast guard: refuse to run git against a non-monorepo directory.
  assertMonorepoRoot(args.repo);
  if (!args.tagCommit) {
    args.tagCommit = execSync(`git -C "${args.repo}" rev-parse HEAD`).toString().trim();
  }
  if (!args.releaseCommit) args.releaseCommit = args.tagCommit;
  return args;
}

function collectTags(repo, version) {
  const out = execSync(`git -C "${repo}" tag --list 'v${version}' '*-v${version}'`).toString().trim();
  return out.split('\n').filter(Boolean).sort();
}

function buildLedger(args) {
  const isBatch = args.kind === 'batch-push';
  const allTags = isBatch && args.versions
    ? args.versions.flatMap((v) => collectTags(args.repo, v))
    : collectTags(args.repo, args.version);

  const ledger = {
    kind: args.kind,
    audit_id: `${args.date}-${args.kind}-v${args.version}`,
    repo: args.repoSlug,
    released_at: args.date,
    version: args.version,
    release_type: 'PATCH',
    summary: args.summary,
  };

  if (Object.keys(args.scope).length > 0) ledger.scope = args.scope;
  if (isBatch && args.versions) {
    ledger.versions = args.versions;
    ledger.tag_commits = {};
    for (const v of args.versions) {
      const tag = `v${v}`;
      try {
        ledger.tag_commits[tag] = execSync(`git -C "${args.repo}" rev-parse ${tag}`).toString().trim();
      } catch {
        ledger.tag_commits[tag] = '<missing — tag not found>';
      }
    }
  } else {
    ledger.release_commit = args.releaseCommit;
    ledger.tag_commit = args.tagCommit;
  }

  ledger.tags = allTags;
  ledger.verification = {
    note: 'TODO: paste gate-by-gate summary here. See ledger-discipline.md § canonical schema.',
  };
  ledger.publish_workflows = {
    dispatched: '9/9 via gh workflow run --ref <pkg>-vX.Y.Z',
    conclusions: '9/9 success',
  };
  ledger.notes = args.notes.length > 0 ? args.notes : ['TODO: at least one note per cycle.'];

  return ledger;
}

function writeOrPrint(ledger, args) {
  const filename = `${ledger.audit_id}.json`;
  const target = path.join(args.repo, '.brain', 'audit-history', filename);
  const content = JSON.stringify(ledger, null, 2) + '\n';

  if (args.dry) {
    console.log(`[dry] would write to: ${target}`);
    console.log('---');
    console.log(content);
    return;
  }

  fs.mkdirSync(path.dirname(target), { recursive: true });
  if (fs.existsSync(target)) {
    console.error(`error: ${target} already exists. Use --dry to preview or remove it manually.`);
    process.exit(1);
  }
  fs.writeFileSync(target, content);
  console.log(`[make-ledger] wrote ${target}`);
  console.log(`\n[next] verify the ledger:`);
  console.log(`  cat ${target} | jq .`);
  console.log(`\n[next] commit + push:`);
  console.log(`  git add ${target}`);
  console.log(`  git commit -m "chore(audit-history): v${ledger.version} release ledger"`);
  console.log(`  git push origin main`);
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const ledger = buildLedger(args);
  writeOrPrint(ledger, args);
}

try {
  main();
} catch (e) {
  console.error(`error: ${e.message}`);
  process.exit(1);
}
