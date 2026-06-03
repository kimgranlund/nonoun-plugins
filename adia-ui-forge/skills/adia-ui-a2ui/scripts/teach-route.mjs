#!/usr/bin/env node
// teach-route.mjs — Mechanized §Teach decision tree for adia-ui-a2ui.
// Maps a "make sure the skill knows about X" payload to its landing target.
// Composes from the shared teach-router lib; the prose tree in
// references/teach-protocol.md mirrors these branches for human readers.
//
// Shared lib resolution: ${CLAUDE_PLUGIN_ROOT}/bin/lib/teach-router.mjs, with a
// fallback relative to this script.
//
// Usage (from the plugin/repo root):
//   node skills/adia-ui-a2ui/scripts/teach-route.mjs "add a new compose strategy"
//   node skills/adia-ui-a2ui/scripts/teach-route.mjs --list
//   # eval the router against the corpus:
//   node ${CLAUDE_PLUGIN_ROOT}/bin/lib/run-skill-evals.mjs --skill=adia-ui-a2ui --corpus=teach

import path from 'node:path';
import process from 'node:process';
import { fileURLToPath, pathToFileURL } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const PLUGIN_ROOT = process.env.CLAUDE_PLUGIN_ROOT
  ? path.resolve(process.env.CLAUDE_PLUGIN_ROOT)
  : path.resolve(__dirname, '..', '..', '..');

const LIB_URL = pathToFileURL(path.join(PLUGIN_ROOT, 'bin', 'lib', 'teach-router.mjs')).href;
const { buildRouter, describeRouter } = await import(LIB_URL);

// Branches: first match wins. `target` is the landing file (relative to skill
// root) — or "(substrate)" / "(journal)" / "SKILL.md" for non-reference landings.
export const branches = [
  {
    id: 'substrate-chunk',
    label: 'Chunk fact (corpus is the source of truth, not a skill landing)',
    match: [/chunk (json|metadata|field|content)/i, 'corpus chunk', 'chunk corpus data'],
    target: '(substrate) packages/a2ui/corpus/chunks/',
    confidence: 'high',
  },
  {
    id: 'mcp-tool',
    label: 'New MCP tool / tool schema',
    match: ['mcp tool', 'mcp server', /new tool/i, 'tool schema', 'generate_ui', 'compose_from_chunks', 'refine_composition', 'report_issue', 'validate_schema', 'search_chunks'],
    target: 'references/mcp-tool-reference.md',
    confidence: 'high',
  },
  {
    id: 'mcp-workflow',
    label: 'MCP operator workflow / pipeline run',
    match: ['mcp pipeline', 'mcp workflow', 'operator workflow', 'feedback loop'],
    target: 'references/mcp-pipeline-ops.md',
    confidence: 'medium',
  },
  {
    id: 'strategy',
    label: 'New compose strategy / engine',
    match: ['strategy', 'engine', /compose strategy/i, 'free-form', 'monolithic', 'dogfood engine'],
    target: 'references/strategy-engines.md',
    confidence: 'high',
  },
  {
    id: 'calibration',
    label: 'Calibration constant / threshold tune',
    match: ['calibration', 'threshold', 'strong_match', 'strong_retrieval', 'pre_search', 'scope_drift', 'constant'],
    target: 'references/zettel-calibration.md',
    confidence: 'high',
  },
  {
    id: 'semantic-fail',
    label: 'Semantic-fail recovery pattern',
    match: ['semantic fail', 'sem fail', 'dominant pattern', /lift.*fail/i],
    target: 'references/semantic-fail-lifting.md',
    confidence: 'high',
  },
  {
    id: 'fragment',
    label: 'Fragment extraction / fragment-graph node type',
    match: ['fragment', 'leverage rule', '$fragment', 'extraction'],
    target: 'references/fragment-graph.md',
    confidence: 'medium',
  },
  {
    id: 'chunk-authoring',
    label: 'Chunk authoring rule',
    match: ['chunk authoring', 'author a chunk', 'harvest', 'html-first', 'training signal'],
    target: 'references/chunk-authoring.md',
    confidence: 'medium',
  },
  {
    id: 'corpus-pitfall',
    label: 'Cross-cut corpus / retrieval pitfall',
    match: ['corpus pitfall', 'retrieval pitfall', 'keyword coverage', 'metadata', 'synonym'],
    target: 'references/corpus-discipline.md',
    confidence: 'medium',
  },
  {
    id: 'anti-pattern',
    label: 'New pipeline anti-pattern rule',
    match: ['anti-pattern', 'anti pattern', 'check_anti_patterns'],
    target: 'references/anti-patterns.md',
    confidence: 'high',
  },
  {
    id: 'eval-gap',
    label: 'Eval-gap diagnosis pattern',
    match: ['eval gap', 'eval regression', 'eval diagnosis', 'coverage drop', 'avgscore', 'mrr'],
    target: 'references/eval-diagnostics.md',
    confidence: 'medium',
  },
  {
    id: 'pipeline-stage',
    label: 'Pipeline-stage fact (generator / retrieval / runtime)',
    match: ['pipeline stage', 'generator.js', 'pattern-library', 'retrieval flow', 'runtime'],
    target: 'references/pipeline-overview.md',
    confidence: 'medium',
  },
  {
    id: 'methodology',
    label: 'Methodology / posture shift (inline SKILL.md)',
    match: ['posture', 'methodology', 'principle', 'mission', 'new selfaudit axis'],
    target: 'SKILL.md',
    confidence: 'medium',
  },
  {
    id: 'journal',
    label: 'One-off arc story (NEGATIVE — journal, not the skill)',
    match: ['arc story', 'debugging story', 'one-off', 'how i debugged', 'journal'],
    target: '(journal) docs/journal/',
    confidence: 'high',
  },
];

export const router = buildRouter({ branches, defaultBranch: 'pipeline-stage' });

// ─── CLI ──────────────────────────────────────────────────────────────────────

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2);
  if (args.includes('--list')) {
    console.log(describeRouter(router, branches));
    process.exit(0);
  }
  // Accept either `--payload=<x>` (used by the shared eval runner) or a bare
  // positional payload string.
  const payloadFlag = args.find(a => a.startsWith('--payload='));
  const payload = payloadFlag
    ? payloadFlag.slice('--payload='.length)
    : args.filter(a => !a.startsWith('--')).join(' ');
  if (!payload) {
    console.error('Usage: node teach-route.mjs "<payload describing the new knowledge>"');
    console.error('       node teach-route.mjs --payload="<payload>" [--json]');
    console.error('       node teach-route.mjs --list');
    process.exit(1);
  }
  const { branch, target, confidence, label } = router(payload);
  // JSON output always carries `branch` (the key the eval runner reads).
  console.log(JSON.stringify({ payload, branch, label, target, confidence }, null, 2));
}
