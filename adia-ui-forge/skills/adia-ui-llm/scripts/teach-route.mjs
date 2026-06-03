#!/usr/bin/env node
// teach-route.mjs — Mechanized §Teach decision tree for adia-ui-llm.
// Maps a "make sure the skill knows about X" payload to its landing target.
// Composes from the shared teach-router lib; the prose tree in
// references/teach-protocol.md mirrors these branches for human readers.
//
// Shared lib resolution: ${CLAUDE_PLUGIN_ROOT}/bin/lib/teach-router.mjs, with a
// fallback relative to this script.
//
// Usage (from the plugin/repo root):
//   node skills/adia-ui-llm/scripts/teach-route.mjs "add a new provider adapter"
//   node skills/adia-ui-llm/scripts/teach-route.mjs --list
//   node skills/adia-ui-llm/scripts/teach-route.mjs --payload="<payload>" [--json]

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
// root) — or "(source)" / "(journal)" / "SKILL.md" for non-reference landings.
// Mirrors the table in references/teach-protocol.md.
export const branches = [
  {
    id: 'source-edit',
    label: 'Per-adapter field/value the source encodes (NOT a skill landing)',
    match: [/response field/i, /model id/i, 'default value', /new field/i, 'source edit', 'parseresponse field'],
    target: '(source) packages/llm/src/',
    confidence: 'high',
  },
  {
    id: 'add-provider',
    label: 'New step / gotcha in adding a 4th provider',
    match: ['add a provider', 'add a new provider', '4th provider', 'fourth provider', 'new adapter step'],
    target: 'references/add-a-provider.md',
    confidence: 'high',
  },
  {
    id: 'streaming',
    label: 'SSE parser / StreamChunk protocol / chunk type',
    match: ['sse', 'stream chunk', 'streamchunk', 'chunk type', '[done]', 'snapshot', 'streaming protocol', /stream(ing)? parser/i],
    target: 'references/streaming-sse.md',
    confidence: 'high',
  },
  {
    id: 'model-registry',
    label: 'MODELS shape / DEFAULT_MODEL / detectProvider rule',
    match: ['models catalog', 'model registry', 'default_model', 'detectprovider', 'detect provider', 'grouped options', 'chat-input'],
    target: 'references/model-registry.md',
    confidence: 'high',
  },
  {
    id: 'bridge-facade',
    label: 'Facade / bridge / stub / maxTokens / lazy-load',
    match: ['createadapter', 'create adapter', 'createclient', 'create client', 'bridge', 'stub', 'maxtokens', 'max tokens', 'lazy-load', 'lazy load', 'chatresult', 'chatopts'],
    target: 'references/bridge-facade.md',
    confidence: 'high',
  },
  {
    id: 'proxy-boundary',
    label: 'Proxy flavors / production-host path / key-in-browser safety',
    match: ['proxy', 'passthrough', 'smart proxy', 'proxyurl', 'production host', 'browser key', 'key in browser', 'cors'],
    target: 'references/browser-proxy-boundary.md',
    confidence: 'high',
  },
  {
    id: 'adapter-contract',
    label: 'Cross-adapter shape rule / usage mapping / raw stopReason / buildRequest (DEFAULT)',
    match: ['adapter contract', 'buildrequest', 'build request', 'usage mapping', 'stopreason', 'stop reason', 'parseresponse', 'adapter shape'],
    target: 'references/adapter-contract.md',
    confidence: 'medium',
  },
  {
    id: 'methodology',
    label: 'Posture / mission shift or new §SelfAudit axis (inline SKILL.md)',
    match: ['posture', 'methodology', 'principle', 'mission', 'new selfaudit axis', 'self-audit axis'],
    target: 'SKILL.md',
    confidence: 'medium',
  },
  {
    id: 'journal',
    label: 'One-off arc story (NEGATIVE — journal, not the skill)',
    match: ['arc story', 'debugging story', 'one-off', 'how i debugged', 'journal'],
    target: '(journal)',
    confidence: 'high',
  },
];

export const router = buildRouter({ branches, defaultBranch: 'adapter-contract' });

// ─── CLI ──────────────────────────────────────────────────────────────────────

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2);
  if (args.includes('--list')) {
    console.log(describeRouter(router, branches));
    process.exit(0);
  }
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
  console.log(JSON.stringify({ payload, branch, label, target, confidence }, null, 2));
}
