#!/usr/bin/env node
// assert-monorepo-root.mjs — shared fail-fast guard for the release scripts.
//
// Several scripts in this dir shell `git`/`npm`/`gh`/`curl` (commits, tags,
// publishes, deploys) against a target monorepo they resolve from `process.cwd()`
// or `--repo`. Run from the wrong directory, they would silently act on the wrong
// repo. This guard asserts the target is an @adia-ai-style lockstep monorepo
// checkout (it contains `packages/web-components`) and FAILS LOUDLY otherwise —
// BEFORE any git/npm/network action.
//
// Usage:
//   import { assertMonorepoRoot } from './assert-monorepo-root.mjs';
//   assertMonorepoRoot(targetDir);   // throws if packages/web-components is absent

import fs from 'node:fs';
import path from 'node:path';

// The lockstep monorepo's defining marker. `packages/web-components` is the
// keystone package every cycle in this skill bumps/tags/publishes; its absence
// means the target dir is not an @adia-ai-style checkout.
const MONOREPO_MARKER = path.join('packages', 'web-components');

/**
 * Assert that `dir` is an @adia-ai-style lockstep monorepo checkout.
 * Throws a clear Error (with the resolved path + how to fix) if the marker
 * directory `packages/web-components` is absent or is not a directory.
 *
 * @param {string} dir  the target monorepo root (typically process.cwd() or --repo)
 * @returns {string}    the resolved absolute path, on success
 */
export function assertMonorepoRoot(dir) {
  const resolved = path.resolve(dir || '.');
  const marker = path.join(resolved, MONOREPO_MARKER);
  let ok = false;
  try {
    ok = fs.statSync(marker).isDirectory();
  } catch {
    ok = false;
  }
  if (!ok) {
    throw new Error(
      `not an @adia-ai-style monorepo checkout: '${resolved}'\n` +
      `  expected to find '${MONOREPO_MARKER}/' (the lockstep keystone package), but it is absent.\n` +
      `  This guard blocks git/npm/gh/curl actions against the wrong directory.\n` +
      `  Run from the monorepo root, or pass the correct path (e.g. --repo <root>).`
    );
  }
  return resolved;
}
