#!/usr/bin/env node
/**
 * validate-cycle-scores.mjs — Validates the monorepo's review/cycle-N/scores.json
 * against this skill's formal JSON schema (references/scores.schema.json).
 *
 * This script is skill-owned. The schema is resolved inside the plugin
 * (via ${CLAUDE_PLUGIN_ROOT}, with a fallback relative to this file); the
 * cycle scores it validates live in the monorepo's review tree, resolved
 * from the working directory — run from the monorepo root.
 *
 * Usage (from the monorepo root):
 *   node ${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-gen-review/scripts/validate-cycle-scores.mjs --cycle 1
 *   node ${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-gen-review/scripts/validate-cycle-scores.mjs --cycle 2
 *   node ${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-gen-review/scripts/validate-cycle-scores.mjs --all          # validate every cycle
 *   node ${CLAUDE_PLUGIN_ROOT}/skills/adia-ui-gen-review/scripts/validate-cycle-scores.mjs --all --strict # exit 1 on any error
 */

import { readFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dir = dirname(fileURLToPath(import.meta.url));   // the skill's scripts/ dir
const REPO  = process.cwd();                             // the monorepo root

// Schema ships with the skill. Resolve via ${CLAUDE_PLUGIN_ROOT} when set,
// else fall back to the references/ dir one level up from this script.
const PLUGIN_ROOT = process.env.CLAUDE_PLUGIN_ROOT;
const SCHEMA_PATH = PLUGIN_ROOT
  ? join(PLUGIN_ROOT, 'skills/adia-ui-gen-review/references/scores.schema.json')
  : join(__dir, '..', 'references', 'scores.schema.json');

const REVIEW_DIR = join(REPO, 'apps/genui/app/gen-ui-gallery/review');

const strict   = process.argv.includes('--strict');
const allCycles = process.argv.includes('--all');
const cycleArg  = (() => {
  const i = process.argv.indexOf('--cycle');
  return i >= 0 ? parseInt(process.argv[i + 1], 10) : null;
})();

// ── Load schema ───────────────────────────────────────────────────────────────

const schema = JSON.parse(readFileSync(SCHEMA_PATH, 'utf8'));

// ── Minimal inline validator (no ajv dep issues with ESM + draft-07 mixed) ───

function validate(doc, schemaRef) {
  const errors = [];

  // Check required top-level fields
  const topRequired = schemaRef.required || [];
  for (const field of topRequired) {
    if (doc[field] === undefined || doc[field] === null) {
      errors.push(`Missing required field: "${field}"`);
    }
  }

  // Check schemaVersion const
  const expectedVersion = schemaRef.properties?.schemaVersion?.const;
  if (expectedVersion && doc.schemaVersion !== expectedVersion) {
    errors.push(`schemaVersion mismatch: expected "${expectedVersion}", got "${doc.schemaVersion}"`);
  }

  // Check engine enum
  const engineEnum = schemaRef.properties?.engine?.enum;
  if (engineEnum && doc.engine && !engineEnum.includes(doc.engine)) {
    errors.push(`engine "${doc.engine}" not in enum [${engineEnum.join(', ')}]`);
  }

  // Check status enum
  const statusEnum = schemaRef.properties?.status?.enum;
  if (statusEnum && doc.status && !statusEnum.includes(doc.status)) {
    errors.push(`status "${doc.status}" not in enum [${statusEnum.join(', ')}]`);
  }

  // Check prompts array
  if (!Array.isArray(doc.prompts)) {
    errors.push('"prompts" must be an array');
    return errors;
  }

  const promptRequired = schemaRef.definitions?.PromptScore?.required || [];
  const validStatusEnum = schemaRef.definitions?.PromptScore?.properties?.status?.enum || [];
  const validCauseEnum  = schemaRef.definitions?.PromptScore?.properties
    ?.rootCauses?.items?.properties?.code?.enum || [];
  const causeRequired   = schemaRef.definitions?.PromptScore?.properties
    ?.rootCauses?.items?.required || [];
  const fixRequired     = schemaRef.definitions?.PromptScore?.properties
    ?.fixPlan?.items?.required || [];

  for (let i = 0; i < doc.prompts.length; i++) {
    const p   = doc.prompts[i];
    const pfx = `prompts[${i}] (${p.promptSlug ?? '?'})`;

    // Required prompt fields
    for (const field of promptRequired) {
      if (p[field] === undefined || p[field] === null) {
        errors.push(`${pfx}: missing required field "${field}"`);
      }
    }

    // Status enum
    if (p.status && !validStatusEnum.includes(p.status)) {
      errors.push(`${pfx}: invalid status "${p.status}"`);
    }

    // rubricScore.score max
    const maxScore = schemaRef.definitions?.PromptScore?.properties
      ?.rubricScore?.properties?.score?.maximum;
    if (maxScore !== undefined && p.rubricScore?.score > maxScore) {
      errors.push(`${pfx}: rubricScore.score ${p.rubricScore.score} exceeds maximum ${maxScore}`);
    }

    // rootCauses
    if (Array.isArray(p.rootCauses)) {
      for (let j = 0; j < p.rootCauses.length; j++) {
        const rc  = p.rootCauses[j];
        const rpfx = `${pfx} rootCauses[${j}]`;
        for (const field of causeRequired) {
          if (rc[field] === undefined || rc[field] === null) {
            errors.push(`${rpfx}: missing required field "${field}"`);
          }
        }
        if (rc.code && validCauseEnum.length && !validCauseEnum.includes(rc.code)) {
          errors.push(`${rpfx}: unknown code "${rc.code}" (valid: ${validCauseEnum.join(', ')})`);
        }
      }
    }

    // fixPlan
    if (Array.isArray(p.fixPlan)) {
      for (let j = 0; j < p.fixPlan.length; j++) {
        const fp   = p.fixPlan[j];
        const fpfx = `${pfx} fixPlan[${j}]`;
        for (const field of fixRequired) {
          if (fp[field] === undefined || fp[field] === null) {
            errors.push(`${fpfx}: missing required field "${field}"`);
          }
        }
      }
    }
  }

  return errors;
}

// ── Discover cycles to validate ───────────────────────────────────────────────

function getCycleNumbers() {
  if (!existsSync(REVIEW_DIR)) return [];
  return readdirSync(REVIEW_DIR)
    .filter(d => /^cycle-\d+$/.test(d) && statSync(join(REVIEW_DIR, d)).isDirectory())
    .map(d => parseInt(d.replace('cycle-', ''), 10))
    .sort((a, b) => a - b);
}

const cyclesToCheck = allCycles
  ? getCycleNumbers()
  : cycleArg !== null ? [cycleArg] : [];

if (cyclesToCheck.length === 0) {
  console.error('[validate-cycle-scores] No cycles specified. Use --cycle N or --all.');
  process.exit(1);
}

// ── Validate ──────────────────────────────────────────────────────────────────

let totalErrors = 0;

for (const n of cyclesToCheck) {
  const scoresPath = join(REVIEW_DIR, `cycle-${n}`, 'scores.json');

  if (!existsSync(scoresPath)) {
    console.log(`[cycle-${n}] scores.json not found — skipping`);
    continue;
  }

  let doc;
  try {
    doc = JSON.parse(readFileSync(scoresPath, 'utf8'));
  } catch (e) {
    console.error(`[cycle-${n}] JSON parse error: ${e.message}`);
    totalErrors++;
    continue;
  }

  const errors = validate(doc, schema);

  if (errors.length === 0) {
    console.log(`[cycle-${n}] ✓ scores.json valid (${doc.prompts?.length ?? 0} prompts, schema ${doc.schemaVersion})`);
  } else {
    console.error(`[cycle-${n}] ✗ ${errors.length} validation error(s):`);
    for (const e of errors) console.error(`  - ${e}`);
    totalErrors += errors.length;
  }
}

process.exit(strict && totalErrors > 0 ? 1 : 0);
