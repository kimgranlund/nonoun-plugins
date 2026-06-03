#!/usr/bin/env node
/**
 * teach-router.mjs — Portable branch-router for §Teach decision trees
 *
 * All rollup-family skills (kit, ops, authoring, release, a2ui) have
 * teach-protocol.md files with 7-8 branches each. Per-skill teach scripts
 * import this library to mechanize the routing.
 *
 * Usage (per-skill script):
 *   import { buildRouter } from '${CLAUDE_PLUGIN_ROOT}/bin/lib/teach-router.mjs';
 *   const router = buildRouter({ branches: MY_BRANCHES, defaultBranch: 'overview' });
 *   const { branch, target, confidence, label } = router(userPayload);
 *
 * @module teach-router
 */

import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

// ─── helpers ──────────────────────────────────────────────────────────────────

/**
 * Test whether a payload string matches a set of keywords.
 * Every keyword must appear (case-insensitive) in the payload.
 * @param {string} payload
 * @param {string[]} keywords
 * @returns {boolean}
 */
export function keywordsMatch(payload, keywords) {
  const lower = payload.toLowerCase();
  return keywords.every(kw => lower.includes(kw.toLowerCase()));
}

/**
 * Test whether a payload matches any of the supplied patterns.
 * Each pattern may be a string (case-insensitive includes) or a RegExp.
 * @param {string} payload
 * @param {Array<string|RegExp>} patterns
 * @returns {boolean}
 */
export function anyPattern(payload, patterns) {
  const lower = payload.toLowerCase();
  return patterns.some(p =>
    p instanceof RegExp ? p.test(payload) : lower.includes(p.toLowerCase())
  );
}

/**
 * Resolve a branch's match spec to a predicate function.
 * @param {string|string[]|RegExp|function} match
 * @returns {function(string): boolean}
 */
function resolveMatch(match) {
  if (typeof match === 'function') return match;
  if (match instanceof RegExp) return p => match.test(p);
  if (typeof match === 'string') return p => p.toLowerCase().includes(match.toLowerCase());
  if (Array.isArray(match)) {
    const preds = match.map(resolveMatch);
    return p => preds.some(fn => fn(p));
  }
  throw new TypeError(`Invalid match type: ${typeof match}`);
}

// ─── core exports ─────────────────────────────────────────────────────────────

/**
 * Build a router function from a branch definition array.
 *
 * Branch shape:
 *   {
 *     id: string,           // machine identifier, e.g. 'scaffold'
 *     label: string,        // human display name
 *     match: fn|RegExp|string|string[],
 *     target: string,       // path to landing file, relative to skill root
 *     confidence?: 'high'|'medium'|'low'
 *   }
 *
 * Branches are evaluated in order; first match wins.
 *
 * @param {{ branches: object[], defaultBranch: string }} config
 * @returns {function(string): { branch: string, target: string, confidence: string, label: string }}
 */
export function buildRouter({ branches, defaultBranch }) {
  if (!Array.isArray(branches) || branches.length === 0) {
    throw new Error('branches must be a non-empty array');
  }
  if (!defaultBranch) throw new Error('defaultBranch is required');

  // Pre-compile match predicates
  const compiled = branches.map(b => ({
    ...b,
    _pred: resolveMatch(b.match),
    confidence: b.confidence || 'medium',
  }));

  const fallback = compiled.find(b => b.id === defaultBranch);
  if (!fallback) throw new Error(`defaultBranch '${defaultBranch}' not found in branches`);

  /**
   * Route a payload string to its matching branch.
   * @param {string} payload
   * @returns {{ branch: string, target: string, confidence: string, label: string }}
   */
  function router(payload) {
    if (typeof payload !== 'string') payload = String(payload ?? '');
    for (const b of compiled) {
      if (b._pred(payload)) {
        return { branch: b.id, target: b.target, confidence: b.confidence, label: b.label };
      }
    }
    return {
      branch: fallback.id,
      target: fallback.target,
      confidence: 'low',
      label: fallback.label,
    };
  }

  return router;
}

/**
 * Return a human-readable summary of a router's branch table.
 * Useful for debug output or auto-generated documentation.
 *
 * @param {function} _router   — the router function (unused; kept for API symmetry)
 * @param {object[]} branches  — the same branches array passed to buildRouter
 * @returns {string}
 */
export function describeRouter(_router, branches) {
  const lines = ['Branch routing table:', ''];
  for (const b of branches) {
    const conf = b.confidence ? ` [${b.confidence}]` : '';
    const matchStr = b.match instanceof RegExp
      ? b.match.toString()
      : Array.isArray(b.match)
        ? `[${b.match.slice(0, 3).join(', ')}${b.match.length > 3 ? ', …' : ''}]`
        : typeof b.match === 'function'
          ? '<function>'
          : JSON.stringify(b.match);
    lines.push(`  ${b.id}${conf}`);
    lines.push(`    label:  ${b.label}`);
    lines.push(`    match:  ${matchStr}`);
    lines.push(`    target: ${b.target}`);
    lines.push('');
  }
  return lines.join('\n');
}

// ─── eval harness ─────────────────────────────────────────────────────────────

/**
 * Run an eval suite against a router.
 *
 * Case shape (teach-routing-cases.json format):
 *   { id, payload, expected_branch, expected_landing_pattern, rationale }
 *
 * @param {function} router
 * @param {object[]} branches
 * @param {object[]} cases
 * @returns {{ passed: number, failed: number, results: object[] }}
 */
export function runEval(router, branches, cases) {
  const results = [];
  let passed = 0;
  let failed = 0;

  for (const c of cases) {
    const { branch, target, confidence, label } = router(c.payload);
    const branchOk = branch === c.expected_branch;
    const landingOk = !c.expected_landing_pattern ||
      new RegExp(c.expected_landing_pattern).test(target);
    const ok = branchOk && landingOk;

    if (ok) passed++; else failed++;

    results.push({
      id: c.id,
      status: ok ? 'pass' : 'fail',
      payload: c.payload,
      expected_branch: c.expected_branch,
      got_branch: branch,
      expected_landing_pattern: c.expected_landing_pattern ?? null,
      got_target: target,
      confidence,
      label,
      rationale: c.rationale ?? null,
      ...(ok ? {} : {
        failure_reason: !branchOk
          ? `branch mismatch: expected '${c.expected_branch}', got '${branch}'`
          : `target '${target}' did not match /${c.expected_landing_pattern}/`,
      }),
    });
  }

  return { passed, failed, results };
}

// ─── CLI ──────────────────────────────────────────────────────────────────────

if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(import.meta.url.replace('file://', ''))) {
  const args = Object.fromEntries(
    process.argv.slice(2)
      .filter(a => a.startsWith('--'))
      .map(a => { const [k, ...v] = a.slice(2).split('='); return [k, v.join('=') || true]; })
  );

  const evalPath = args.eval;
  const routerPath = args.router;

  if (!evalPath || !routerPath) {
    console.error('Usage: node teach-router.mjs --eval=<cases.json> --router=<router.mjs>');
    process.exit(1);
  }

  const casesRaw = JSON.parse(fs.readFileSync(path.resolve(evalPath), 'utf8'));
  const cases = Array.isArray(casesRaw) ? casesRaw : casesRaw.cases ?? [];

  const req = createRequire(import.meta.url);
  // Dynamic import for ESM router modules
  const routerMod = await import(path.resolve(routerPath));
  const { router, branches } = routerMod;

  if (typeof router !== 'function' || !Array.isArray(branches)) {
    console.error('Router module must export: router (function), branches (array)');
    process.exit(1);
  }

  const { passed, failed, results } = runEval(router, branches, cases);

  for (const r of results) {
    const icon = r.status === 'pass' ? '✓' : '✗';
    const detail = r.status === 'fail' ? ` — ${r.failure_reason}` : '';
    console.log(`${icon} [${r.id}] branch:${r.got_branch} target:${r.got_target}${detail}`);
  }

  console.log(`\n${passed}/${passed + failed} passed`);
  if (failed > 0) process.exit(1);
}
