#!/usr/bin/env node
/**
 * run-skill-evals.mjs — Portable eval runner for rollup-family skills.
 *
 * Walks a skill's evals/ directory and scores each corpus type:
 *   routing-corpus.json     — heuristic routing accuracy (F1 score)
 *   adversarial-*.json      — structural validation + case count
 *   teach-routing-cases.json — branch routing eval (live or structural)
 *   evals.json              — structural validation + category counts
 *
 * Usage (from repo root):
 *   node ${CLAUDE_PLUGIN_ROOT}/bin/lib/run-skill-evals.mjs --skill=adia-ui-kit
 *   node ${CLAUDE_PLUGIN_ROOT}/bin/lib/run-skill-evals.mjs --skill=all
 *   node ${CLAUDE_PLUGIN_ROOT}/bin/lib/run-skill-evals.mjs --skill=adia-ui-kit --corpus=routing
 *   node ${CLAUDE_PLUGIN_ROOT}/bin/lib/run-skill-evals.mjs --skill=adia-ui-kit --json
 *   node ${CLAUDE_PLUGIN_ROOT}/bin/lib/run-skill-evals.mjs --skill=adia-ui-kit --strict
 *
 * Exit code: 0 = all pass (or warnings only), 1 = failures (in --strict mode
 * or when hard-failure thresholds are missed).
 *
 * Scoring note: routing scores are heuristic (keyword overlap, not real LLM
 * routing). Treat as a structural signal and vocabulary-drift detector — not
 * ground truth for harness routing accuracy.
 *
 * @module run-skill-evals
 */

import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import process from 'node:process';

// ─── constants ──────────────────────────────────────────────────────────────

const REPO = process.cwd();
const SKILLS_DIR = path.join(REPO, 'skills');

// Routing heuristic thresholds
const ROUTING_F1_PASS = 0.70;
const ROUTING_F1_WARN = 0.85;

// Stopwords excluded from token overlap
const STOPWORDS = new Set([
  'a', 'an', 'the', 'and', 'or', 'of', 'in', 'to', 'for', 'on', 'at',
  'is', 'are', 'was', 'with', 'this', 'that', 'it', 'its', 'be', 'as',
  'by', 'not', 'do', 'use', 'how', 'what', 'when', 'which', 'from',
  'into', 'about', 'after', 'over', 'can', 'has', 'have', 'all', 'any',
]);

// ─── helpers ────────────────────────────────────────────────────────────────

function readJson(p) {
  try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch { return null; }
}

function tokenize(text) {
  return text.toLowerCase().split(/\W+/).filter(w => w.length > 2 && !STOPWORDS.has(w));
}

/** Extract quoted trigger phrases from a skill description. */
function extractTriggerPhrases(description) {
  const triggers = [];
  // "Triggers on ..." section — extract quoted phrases
  const triggerBlock = description.match(/Triggers on\s+([\s\S]*?)(?:\.|Does NOT trigger|$)/i);
  if (triggerBlock) {
    const quotes = triggerBlock[1].matchAll(/"([^"]+)"/g);
    for (const m of quotes) triggers.push(m[1]);
  }
  return triggers;
}

/** Compute heuristic routing score for a phrase against a skill. */
function scorePhrase(phrase, descTokenSet, triggerPhrases) {
  // Explicit trigger phrase match → high-confidence positive
  for (const t of triggerPhrases) {
    if (phrase.toLowerCase().includes(t.toLowerCase())) return 1.0;
  }
  // Word overlap ratio: phrase tokens that appear in description vocabulary
  const phraseTokens = tokenize(phrase);
  if (phraseTokens.length === 0) return 0;
  const overlap = phraseTokens.filter(t => descTokenSet.has(t)).length;
  return overlap / phraseTokens.length;
}

/** Find calibrated threshold maximizing F1 on labeled data. */
function calibrateThreshold(scoredPhrases) {
  // Extract unique score values as candidate thresholds
  const candidates = [...new Set(scoredPhrases.map(p => p.score))].sort((a, b) => a - b);
  let bestF1 = -1;
  let bestT = 0.15;

  for (const t of candidates) {
    const { f1 } = computeF1(scoredPhrases, t);
    if (f1 > bestF1) { bestF1 = f1; bestT = t; }
  }
  return { threshold: bestT, calibratedF1: bestF1 };
}

function computeF1(scoredPhrases, threshold) {
  let tp = 0, fp = 0, fn = 0, tn = 0;
  for (const { score, expected } of scoredPhrases) {
    const predicted = score >= threshold;
    if (predicted && expected) tp++;
    else if (predicted && !expected) fp++;
    else if (!predicted && expected) fn++;
    else tn++;
  }
  const precision = tp + fp > 0 ? tp / (tp + fp) : 0;
  const recall = tp + fn > 0 ? tp / (tp + fn) : 0;
  const f1 = precision + recall > 0 ? 2 * precision * recall / (precision + recall) : 0;
  return { tp, fp, fn, tn, precision, recall, f1 };
}

// ─── corpus evaluators ──────────────────────────────────────────────────────

/**
 * Evaluate routing-corpus.json: heuristic phrase classification + F1.
 */
function evalRoutingCorpus(corpusPath, skillDir) {
  const corpus = readJson(corpusPath);
  if (!corpus) return { type: 'routing', status: 'error', message: 'Failed to parse corpus' };

  const phrases = corpus.phrases ?? [];
  if (phrases.length === 0) {
    return { type: 'routing', status: 'fail', message: 'No phrases found' };
  }

  // Detect label field (e.g. should_route_to_kit, should_route_to_ops)
  const firstPhrase = phrases[0];
  const labelField = Object.keys(firstPhrase).find(k => k.startsWith('should_route_to_'));
  if (!labelField) {
    return { type: 'routing', status: 'fail', message: 'No should_route_to_* field found in phrases' };
  }

  // Load skill description for heuristic scoring
  const skillJson = readJson(path.join(skillDir, 'skill.json')) ?? {};
  const description = skillJson.description ?? '';
  const descTokenSet = new Set(tokenize(description));
  const triggerPhrases = extractTriggerPhrases(description);

  // Score each phrase
  const scoredPhrases = phrases.map(p => ({
    id: p.id,
    phrase: p.phrase,
    score: scorePhrase(p.phrase, descTokenSet, triggerPhrases),
    expected: Boolean(p[labelField]),
    expected_alternative: p.expected_alternative ?? null,
  }));

  const positives = scoredPhrases.filter(p => p.expected);
  const adversarials = scoredPhrases.filter(p => !p.expected);

  // Calibrate threshold on labeled data
  const { threshold, calibratedF1 } = calibrateThreshold(scoredPhrases);
  const { tp, fp, fn, tn, precision, recall, f1 } = computeF1(scoredPhrases, threshold);

  // Check minimums
  const mins = corpus.minimums_per_spec ?? {};
  const minTrigger = mins.trigger_phrases ?? 10;
  const minAdversarial = mins.adversarial_phrases ?? 5;
  const minimumsMet = positives.length >= minTrigger && adversarials.length >= minAdversarial;

  const status = !minimumsMet ? 'fail'
    : f1 < ROUTING_F1_PASS ? 'fail'
    : f1 < ROUTING_F1_WARN ? 'warn'
    : 'pass';

  // Per-case results (only report misclassifications)
  const misclassified = scoredPhrases.filter(p => (p.score >= threshold) !== p.expected);

  return {
    type: 'routing',
    file: path.relative(skillDir, corpusPath),
    status,
    label_field: labelField,
    counts: { total: phrases.length, positives: positives.length, adversarials: adversarials.length },
    minimums: { trigger_phrases: { required: minTrigger, found: positives.length, ok: positives.length >= minTrigger },
                adversarial_phrases: { required: minAdversarial, found: adversarials.length, ok: adversarials.length >= minAdversarial } },
    heuristic: { threshold: +threshold.toFixed(3), trigger_phrases_extracted: triggerPhrases.length },
    scores: { tp, fp, fn, tn, precision: +precision.toFixed(3), recall: +recall.toFixed(3), f1: +f1.toFixed(3) },
    misclassified: misclassified.map(p => ({
      id: p.id, phrase: p.phrase, expected: p.expected, score: +p.score.toFixed(3),
    })),
    summary: `F1=${f1.toFixed(2)} (${tp} TP, ${fp} FP, ${fn} FN, ${tn} TN), ${positives.length}/${minTrigger} trigger, ${adversarials.length}/${minAdversarial} adversarial`,
  };
}

/**
 * Evaluate adversarial-*.json: structural validation + severity breakdown.
 */
function evalAdversarialCorpus(corpusPath, skillDir) {
  const corpus = readJson(corpusPath);
  if (!corpus) return { type: 'adversarial', status: 'error', message: 'Failed to parse corpus' };

  const cases = corpus.cases ?? corpus.phrases ?? [];
  const required = ['id', 'expected_behavior'];
  const invalid = cases.filter(c => required.some(f => !c[f]));

  const severityCounts = {};
  for (const c of cases) {
    const sev = c.severity ?? 'unknown';
    severityCounts[sev] = (severityCounts[sev] ?? 0) + 1;
  }

  const status = cases.length < 3 ? 'warn'
    : invalid.length > 0 ? 'warn'
    : 'pass';

  return {
    type: 'adversarial',
    file: path.relative(skillDir, corpusPath),
    status,
    counts: { total: cases.length, invalid: invalid.length },
    severity_breakdown: severityCounts,
    invalid_ids: invalid.map(c => c.id ?? '(no id)'),
    summary: `${cases.length} cases, severity: ${Object.entries(severityCounts).map(([k, v]) => `${v} ${k}`).join(', ')}`,
  };
}

/**
 * Evaluate teach-routing-cases.json: branch coverage + live routing if
 * scripts/teach-route.mjs exists in the skill directory.
 */
async function evalTeachRoutingCorpus(corpusPath, skillDir) {
  const corpus = readJson(corpusPath);
  if (!corpus) return { type: 'teach-routing', status: 'error', message: 'Failed to parse corpus' };

  const cases = corpus.cases ?? [];
  const mins = corpus.minimums_per_spec ?? {};
  const minTotal = mins.total_cases ?? 7;

  // Check branch coverage
  const branchCoverage = {};
  for (const c of cases) {
    const b = c.expected_branch ?? '?';
    branchCoverage[b] = (branchCoverage[b] ?? 0) + 1;
  }

  const teachScript = path.join(skillDir, 'scripts', 'teach-route.mjs');
  const scriptExists = fs.existsSync(teachScript);

  if (!scriptExists) {
    // Structural-only evaluation
    const status = cases.length < minTotal ? 'warn' : 'pass';
    return {
      type: 'teach-routing',
      file: path.relative(skillDir, corpusPath),
      status,
      live_run: false,
      counts: { total: cases.length, required: minTotal },
      branch_coverage: branchCoverage,
      summary: `${cases.length} cases, branches: ${Object.keys(branchCoverage).sort().join(',')} — teach-route.mjs not yet authored (pending Round 3)`,
    };
  }

  // Live routing evaluation: run teach-route.mjs --eval=<payload> for each case
  let passed = 0;
  let failed = 0;
  const results = [];

  for (const c of cases) {
    // Pass --json so teach-route.mjs emits structured output regardless of format
    const proc = spawnSync(process.execPath, [teachScript, `--payload=${c.payload}`, '--json'], {
      cwd: REPO, encoding: 'utf8', timeout: 5000,
    });
    const output = (proc.stdout ?? '').trim();
    let gotBranch = null;
    try {
      const parsed = JSON.parse(output);
      gotBranch = parsed.branch ?? parsed.id ?? null;
    } catch {
      // Fall back to parsing text output: "  branch:     A (name)" or leading capital
      const textMatch = output.match(/branch:\s*([A-Z])(?:\s|$)/m);
      gotBranch = textMatch?.[1] ?? output.match(/^([A-Z])\b/)?.[1] ?? null;
    }
    const ok = gotBranch === c.expected_branch;
    if (ok) passed++; else failed++;
    results.push({
      id: c.id, expected: c.expected_branch, got: gotBranch,
      status: ok ? 'pass' : 'fail',
      ...(!ok ? { failure_reason: `expected '${c.expected_branch}', got '${gotBranch}'` } : {}),
    });
  }

  const f1 = cases.length > 0 ? passed / cases.length : 0;
  const status = failed > 0 ? 'fail' : cases.length < minTotal ? 'warn' : 'pass';

  return {
    type: 'teach-routing',
    file: path.relative(skillDir, corpusPath),
    status,
    live_run: true,
    counts: { total: cases.length, passed, failed, required: minTotal },
    branch_coverage: branchCoverage,
    results,
    summary: `${passed}/${cases.length} passed (live routing via teach-route.mjs)`,
  };
}

/**
 * Evaluate evals.json: structural validation + category counts.
 * (Full behavioral execution requires an LLM — not run here.)
 */
function evalEvalsJson(corpusPath, skillDir) {
  const corpus = readJson(corpusPath);
  if (!corpus) return { type: 'evals', status: 'error', message: 'Failed to parse corpus' };

  const evals = corpus.evals ?? [];
  const invariants = corpus.non_eval_invariants ?? corpus.invariants ?? [];

  // Count by category
  const categoryCounts = {};
  for (const e of evals) {
    const cat = e.category ?? 'uncategorized';
    categoryCounts[cat] = (categoryCounts[cat] ?? 0) + 1;
  }

  const status = evals.length === 0 ? 'warn' : 'pass';

  return {
    type: 'evals',
    file: path.relative(skillDir, corpusPath),
    status,
    counts: { evals: evals.length, invariants: invariants.length },
    categories: categoryCounts,
    note: 'Structural check only — behavioral execution requires LLM',
    summary: `${evals.length} evals (${Object.entries(categoryCounts).map(([k, v]) => `${v} ${k}`).join(', ')}), ${invariants.length} invariants`,
  };
}

// ─── skill runner ────────────────────────────────────────────────────────────

async function runSkillEvals(skillName, corpusFilter) {
  const skillDir = path.join(SKILLS_DIR, skillName);
  const evalsDir = path.join(skillDir, 'evals');

  if (!fs.existsSync(skillDir)) {
    return { skill: skillName, status: 'error', message: `Skill directory not found: ${skillDir}` };
  }

  if (!fs.existsSync(evalsDir)) {
    return { skill: skillName, status: 'warn', message: 'No evals/ directory', corpora: [] };
  }

  const files = fs.readdirSync(evalsDir).filter(f => f.endsWith('.json'));
  if (files.length === 0) {
    return { skill: skillName, status: 'warn', message: 'evals/ directory is empty', corpora: [] };
  }

  const corpora = [];

  for (const file of files.sort()) {
    const fullPath = path.join(evalsDir, file);

    // Detect corpus type and apply filter
    let type;
    if (file === 'routing-corpus.json') type = 'routing';
    else if (file === 'teach-routing-cases.json') type = 'teach';
    else if (file.startsWith('adversarial-')) type = 'adversarial';
    else if (file === 'evals.json') type = 'evals';
    else type = 'unknown';

    if (corpusFilter && corpusFilter !== 'all' && type !== corpusFilter) continue;
    if (type === 'unknown') {
      corpora.push({ type: 'unknown', file, status: 'skip', summary: 'Unrecognized corpus type' });
      continue;
    }

    let result;
    if (type === 'routing') result = evalRoutingCorpus(fullPath, skillDir);
    else if (type === 'adversarial') result = evalAdversarialCorpus(fullPath, skillDir);
    else if (type === 'teach') result = await evalTeachRoutingCorpus(fullPath, skillDir);
    else if (type === 'evals') result = evalEvalsJson(fullPath, skillDir);

    corpora.push(result);
  }

  const statuses = corpora.map(c => c.status);
  const overallStatus = statuses.includes('error') ? 'error'
    : statuses.includes('fail') ? 'fail'
    : statuses.includes('warn') ? 'warn'
    : 'pass';

  return { skill: skillName, status: overallStatus, corpora };
}

// ─── formatting ──────────────────────────────────────────────────────────────

function icon(status) {
  return { pass: '✓', warn: '⚠', fail: '✗', error: '!', skip: '·' }[status] ?? '?';
}

function formatSkillResult(result) {
  const lines = [`[${result.skill}] ${icon(result.status)} ${result.status.toUpperCase()}`];

  if (result.message) {
    lines.push(`  ${result.message}`);
  }

  for (const corpus of result.corpora ?? []) {
    const ind = icon(corpus.status);
    lines.push(`  ${ind} ${corpus.file ?? corpus.type}: ${corpus.summary ?? corpus.message ?? ''}`);

    if (corpus.status === 'fail' || corpus.status === 'warn') {
      if (corpus.misclassified?.length) {
        lines.push(`    Misclassified (${corpus.misclassified.length}):`);
        for (const m of corpus.misclassified.slice(0, 5)) {
          lines.push(`      [${m.id}] score=${m.score} expected=${m.expected} — "${m.phrase}"`);
        }
        if (corpus.misclassified.length > 5) {
          lines.push(`      ... ${corpus.misclassified.length - 5} more`);
        }
      }
      if (corpus.invalid_ids?.length) {
        lines.push(`    Invalid cases: ${corpus.invalid_ids.join(', ')}`);
      }
      if (corpus.results?.filter(r => r.status === 'fail').length) {
        for (const r of corpus.results.filter(r => r.status === 'fail')) {
          lines.push(`    [${r.id}] ${r.failure_reason}`);
        }
      }
      if (corpus.minimums) {
        for (const [k, v] of Object.entries(corpus.minimums)) {
          if (!v.ok) lines.push(`    Minimum not met: ${k} requires ${v.required}, found ${v.found}`);
        }
      }
    }
  }

  return lines.join('\n');
}

// ─── main ────────────────────────────────────────────────────────────────────

async function main() {
  const rawArgs = process.argv.slice(2);
  const args = Object.fromEntries(
    rawArgs.filter(a => a.startsWith('--')).map(a => {
      const [k, ...v] = a.slice(2).split('=');
      return [k, v.length ? v.join('=') : true];
    })
  );

  const { skill: skillArg = 'all', corpus: corpusFilter, json: jsonMode, strict } = args;

  // Discover skills to run
  let skillNames;
  if (skillArg === 'all') {
    skillNames = fs.readdirSync(SKILLS_DIR).filter(name => {
      const d = path.join(SKILLS_DIR, name);
      return fs.statSync(d).isDirectory() && fs.existsSync(path.join(d, 'SKILL.md'));
    }).sort();
  } else {
    skillNames = [skillArg];
  }

  const results = [];
  for (const name of skillNames) {
    results.push(await runSkillEvals(name, corpusFilter ?? 'all'));
  }

  if (jsonMode) {
    const driftCount = results.filter(r => r.status === 'fail' || r.status === 'error').length;
    console.log(JSON.stringify({ results, driftCount }, null, 2));
  } else {
    const hasEvals = results.filter(r => r.corpora?.length > 0 || r.status === 'warn');
    const noEvals = results.filter(r => !r.corpora?.length && r.status !== 'warn' && r.message?.includes('No evals'));

    for (const r of hasEvals) console.log(formatSkillResult(r));

    if (noEvals.length && !corpusFilter) {
      console.log(`\n  (${noEvals.length} skill(s) have no evals/ yet: ${noEvals.map(r => r.skill).join(', ')})`);
    }

    const passed = results.filter(r => r.status === 'pass').length;
    const warned = results.filter(r => r.status === 'warn').length;
    const failed = results.filter(r => r.status === 'fail' || r.status === 'error').length;
    const withEvals = results.filter(r => r.corpora?.length > 0).length;
    console.log(`\n${withEvals} skill(s) with evals: ${passed} pass, ${warned} warn, ${failed} fail`);
  }

  const anyFail = results.some(r => r.status === 'fail' || r.status === 'error');
  if (strict && anyFail) process.exit(1);
}

main().catch(err => { console.error(err); process.exit(2); });
