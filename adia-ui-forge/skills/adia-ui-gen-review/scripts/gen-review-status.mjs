#!/usr/bin/env node
/**
 * gen-review-status.mjs — Reads cycle-ledger.json and reports the current
 * gen-review loop state: last cycle number, pass/fail/render-failure counts,
 * mean score, delta vs prior cycle, and whether the exit condition is met.
 *
 * Acts as the authoritative consumer of cycle-ledger.json so the ledger has
 * a real downstream reader (not just an append-only audit trail).
 *
 * This script is skill-owned but reads the @adia-ai monorepo's review ledger
 * (resolved from the working directory) — run it from the monorepo root.
 *
 * Usage (from the monorepo root):
 *   node ${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-gen-review/scripts/gen-review-status.mjs               # human-readable summary
 *   node ${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-gen-review/scripts/gen-review-status.mjs --json        # machine-readable JSON
 *   node ${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-gen-review/scripts/gen-review-status.mjs --check-exit  # exit 0 if condition met, 1 if not
 *
 * Exit-condition (from scores.schema.json + SKILL.md §ExitCondition):
 *   - Every prompt PASSING (p1Count = 0 AND rubricScore.score ≥ 92)
 *   - humanQA.passCount ≥ 4 (of 5 sampled)
 *   - No RENDER_FAILURE prompts
 *   - Cycle status = COMPLETE (not OPEN or INTERRUPTED)
 */

import { readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';

const REPO = process.cwd();   // the monorepo root

const LEDGER_PATH    = join(REPO, 'apps/genui/app/gen-ui-gallery/review/cycle-ledger.json');
const EXCELLENCE_THRESHOLD = 92;

const jsonMode  = process.argv.includes('--json');
const checkExit = process.argv.includes('--check-exit');

// ── Load ledger ───────────────────────────────────────────────────────────────

if (!existsSync(LEDGER_PATH)) {
  if (jsonMode) {
    console.log(JSON.stringify({ error: 'No cycle-ledger.json found. No cycles have been run yet.' }));
  } else {
    console.log('[gen-review-status] No cycles run yet. cycle-ledger.json not found.');
    console.log('  Run: node ${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-gen-review/scripts/gen-review-decompose.mjs --cycle 1');
    console.log('  Then invoke the adia-ui-gen-review skill to score.');
  }
  process.exit(checkExit ? 1 : 0);
}

const ledger = JSON.parse(readFileSync(LEDGER_PATH, 'utf8'));
const cycles = ledger.cycles || [];

if (cycles.length === 0) {
  console.log('[gen-review-status] Ledger exists but no cycles recorded.');
  process.exit(checkExit ? 1 : 0);
}

// Sort cycles descending so latest is first
const sorted = [...cycles].sort((a, b) => b.cycleNumber - a.cycleNumber);
const latest = sorted[0];
const prior  = sorted[1] ?? null;

// ── Load latest cycle's scores.json for per-prompt detail ────────────────────

const scoresPath = join(REPO, 'apps/genui/app/gen-ui-gallery/review',
  `cycle-${latest.cycleNumber}`, 'scores.json');

let scores = null;
let failingPrompts = [];
let renderFailures = [];

if (existsSync(scoresPath)) {
  scores = JSON.parse(readFileSync(scoresPath, 'utf8'));
  for (const p of (scores.prompts || [])) {
    if (p.status === 'FAILING')         failingPrompts.push(p.promptSlug);
    if (p.status === 'RENDER_FAILURE')  renderFailures.push(p.promptSlug);
  }
}

// ── Exit condition check ──────────────────────────────────────────────────────

function checkExitCondition() {
  const reasons = [];

  if (latest.status !== 'COMPLETE') {
    reasons.push(`Cycle ${latest.cycleNumber} status is "${latest.status}" (need COMPLETE)`);
  }

  if (!latest.humanQA) {
    reasons.push('Human QA gate not completed (humanQA block missing)');
  } else if (latest.humanQA.passCount < 4) {
    reasons.push(`Human QA pass count ${latest.humanQA.passCount}/5 (need ≥ 4)`);
  }

  const agg = latest.aggregate;
  if (agg?.failingCount > 0) {
    reasons.push(`${agg.failingCount} prompt(s) still FAILING`);
  }
  if (agg?.renderFailureCount > 0) {
    reasons.push(`${agg.renderFailureCount} RENDER_FAILURE prompt(s)`);
  }
  if (scores && scores.prompts) {
    const belowThreshold = scores.prompts.filter(
      p => p.status !== 'RENDER_FAILURE' && (p.rubricScore?.score ?? 0) < EXCELLENCE_THRESHOLD
    );
    if (belowThreshold.length > 0) {
      reasons.push(`${belowThreshold.length} prompt(s) below excellence threshold (${EXCELLENCE_THRESHOLD})`);
    }
    const hasP1 = scores.prompts.filter(p => (p.rubricCosmetic?.p1Count ?? 0) > 0);
    if (hasP1.length > 0) {
      reasons.push(`${hasP1.length} prompt(s) have P1 cosmetic findings`);
    }
  }

  return { met: reasons.length === 0, reasons };
}

const exitCheck = checkExitCondition();

// ── Output ────────────────────────────────────────────────────────────────────

const result = {
  latestCycle: latest.cycleNumber,
  engine: latest.engine,
  status: latest.status,
  totalCycles: cycles.length,
  aggregate: latest.aggregate,
  delta: latest.aggregate?.delta ?? null,
  priorCycle: prior ? { cycleNumber: prior.cycleNumber, meanScore: prior.aggregate?.meanScore } : null,
  failingPrompts,
  renderFailures,
  humanQA: latest.humanQA ?? null,
  exitCondition: exitCheck,
  topFindings: latest.topFindings ?? [],
  note: latest.note ?? null,
};

if (jsonMode) {
  console.log(JSON.stringify(result, null, 2));
} else {
  const agg = latest.aggregate;
  console.log(`\n[gen-review-status] Cycle ${latest.cycleNumber} — ${latest.status}`);
  console.log(`  Engine:       ${latest.engine}`);
  if (agg) {
    const scope = agg.sampledCount
      ? `${agg.sampledCount}/${agg.totalCount} prompts (SAMPLE)`
      : `${agg.totalCount} prompts`;
    console.log(`  Scope:        ${scope}`);
    console.log(`  Passing:      ${agg.passingCount ?? '?'}`);
    console.log(`  Failing:      ${agg.failingCount ?? '?'}`);
    console.log(`  Render fail:  ${agg.renderFailureCount ?? 0}`);
    console.log(`  Mean score:   ${agg.meanScore ?? '?'}`);
    if (agg.delta !== null && agg.delta !== undefined) {
      console.log(`  Δ vs prior:   ${agg.delta >= 0 ? '+' : ''}${agg.delta}`);
    }
  }

  if (failingPrompts.length > 0) {
    console.log(`\n  Still failing:`);
    for (const s of failingPrompts) console.log(`    - ${s}`);
  }

  if (latest.note) {
    console.log(`\n  Note: ${latest.note}`);
  }

  console.log(`\n  Exit condition: ${exitCheck.met ? '✓ MET' : '✗ NOT MET'}`);
  if (!exitCheck.met) {
    for (const r of exitCheck.reasons) console.log(`    - ${r}`);
  }

  if (prior) {
    console.log(`\n  Prior cycle ${prior.cycleNumber}: mean ${prior.aggregate?.meanScore ?? '?'}`);
  }
}

process.exit(checkExit && !exitCheck.met ? 1 : 0);
